// Real loopback HTTP/1.1 contracts. No external DNS, TLS, proxy or packet capture.
import http from 'node:http';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '../..');
const out = path.join(directory, 'results');
const hash = value => createHash('sha256').update(value).digest('hex');
const deferred = () => Promise.withResolvers();

async function guarded(promise, label) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`Guard exceeded: ${label}`)), 5000);
    })]);
  } finally { clearTimeout(timer); }
}

async function fixture() {
  const epoch = performance.now();
  const now = () => performance.now() - epoch;
  const trace = [], connections = [], responses = [], requests = [];
  const sockets = new Map(), holds = new Map(), markers = new Map(), responseClosed = new Map();
  const socketCloses = [];
  const log = (event, fields = {}) => trace.push({ at_ms: now(), event, ...fields });
  const agent = new http.Agent({ keepAlive: true, maxSockets: 1, maxTotalSockets: 1,
    maxFreeSockets: 1, scheduling: 'fifo' });
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    const id = url.pathname.slice(1);
    const connectionId = sockets.get(req.socket).id;
    const body = Buffer.from(url.searchParams.has('large') ? 'x'.repeat(65536) : `ok:${id}`);
    const record = { id, method: req.method, connection_id: connectionId, http_version: req.httpVersion,
      request_at_ms: now(), expected_bytes: body.length, expected_sha256: hash(body) };
    responses.push(record);
    const closed = deferred(); responseClosed.set(id, closed.promise);
    log('server_request', { id, connection_id: connectionId });
    if (url.searchParams.has('marker')) {
      markers.set(id, 'applied-in-memory');
      log('server_memory_marker_applied', { id });
    }
    res.on('finish', () => { record.finished_at_ms = now(); log('server_response_finish', { id }); });
    res.on('close', () => {
      record.closed_at_ms = now(); record.writable_finished_at_close = res.writableFinished;
      log('server_response_close', { id, writable_finished: res.writableFinished });
      closed.resolve();
    });
    res.writeHead(200, { 'Content-Type': 'application/octet-stream', 'Content-Length': body.length,
      'X-Lab-Connection': String(connectionId) });
    if (url.searchParams.has('hold')) {
      holds.set(id, () => { holds.delete(id); res.end(body); });
      res.flushHeaders();
    } else { res.end(body); }
  });
  server.keepAliveTimeout = 60000;
  server.headersTimeout = 65000;
  server.on('connection', socket => {
    const record = { id: connections.length + 1, accepted_at_ms: now(),
      server_port: socket.localPort, client_port: socket.remotePort };
    connections.push(record); sockets.set(socket, record);
    const closed = deferred(); socketCloses.push(closed.promise);
    log('server_connection', { connection_id: record.id });
    socket.on('close', hadError => {
      record.closed_at_ms = now(); record.had_error_at_close = hadError;
      log('server_socket_close', { connection_id: record.id, had_error: hadError });
      closed.resolve();
    });
  });
  server.listen(0, '127.0.0.1');
  await guarded(once(server, 'listening'), 'listen');
  const port = server.address().port;

  function start(id, { hold = false, large = false, marker = false,
    autoConsume = true, fresh = false } = {}) {
    const headers = deferred(), done = deferred();
    // Retain errors as outcomes even if they arrive before a caller awaits them.
    headers.promise.catch(() => {});
    const record = { id, created_at_ms: now(), socket_assigned: false, completed: false };
    requests.push(record);
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries({ hold, large, marker })) if (value) params.set(key, '1');
    const req = http.request({ hostname: '127.0.0.1', port, path: `/${id}?${params}`,
      method: marker ? 'POST' : 'GET',
      agent: fresh ? false : agent, ...(fresh ? { headers: { Connection: 'close' } } : {}) });
    let response, consuming = false;
    const chunks = [];
    const fail = error => {
      if (record.error) {
        (record.additional_errors ||= []).push({ code: error.code || null, message: error.message });
        return;
      }
      record.error = { code: error.code || null, message: error.message };
      record.error_at_ms = now(); headers.reject(error); done.resolve(record);
      log('client_error', { id, ...record.error });
    };
    function consume() {
      assert.ok(response, 'Need response headers before consumption');
      if (consuming) return;
      consuming = true; record.consume_at_ms = now(); log('client_consume', { id });
      response.on('data', chunk => chunks.push(chunk));
      response.resume();
    }
    req.on('socket', socket => {
      record.socket_assigned = true; record.socket_at_ms = now(); record.reused_socket = req.reusedSocket;
      log('client_socket_assigned', { id, reused_socket: req.reusedSocket });
      socket.once('close', hadError => log('client_socket_close', { id, had_error: hadError }));
    });
    req.on('error', fail);
    req.on('response', res => {
      response = res; record.headers_at_ms = now(); record.http_version = res.httpVersion;
      record.status = res.statusCode; record.connection_id = Number(res.headers['x-lab-connection']);
      log('client_headers', { id, connection_id: record.connection_id });
      res.on('error', fail);
      res.on('end', () => {
        const body = Buffer.concat(chunks);
        record.completed = true; record.end_at_ms = now(); record.bytes = body.length;
        record.sha256 = hash(body); log('client_end', { id }); done.resolve(record);
      });
      headers.resolve(res);
      if (autoConsume) consume();
    });
    req.end();
    return { req, record, headers: headers.promise, done: done.promise, consume,
      get response() { return response; } };
  }

  const queued = () => Object.values(agent.requests).reduce((n, items) => n + items.length, 0);
  const free = () => Object.values(agent.freeSockets).reduce((n, items) => n + items.length, 0);
  async function cleanup() {
    for (const release of [...holds.values()]) release();
    agent.destroy();
    const closed = once(server, 'close');
    server.close(); server.closeAllConnections();
    await guarded(closed, 'server cleanup');
    await guarded(Promise.all(socketCloses), 'owned sockets close');
    log('fixture_closed', { listening: server.listening });
  }
  return { start, queued, free, server, agent, holds, markers, responseClosed, trace, connections,
    responses, requests, now, log, cleanup };
}

const cases = {
  async reuse(f, check) {
    for (let i = 0; i < 3; i++) await guarded(f.start(`reuse-${i}`).done, 'reuse body');
    check('one_connection_for_three_requests', f.connections.length === 1);
    check('same_server_connection', new Set(f.requests.map(r => r.connection_id)).size === 1);
  },
  async close_each(f, check) {
    for (let i = 0; i < 3; i++) await guarded(f.start(`close-${i}`, { fresh: true }).done, 'fresh body');
    check('three_connections_for_three_requests', f.connections.length === 3);
    check('different_server_connections', new Set(f.requests.map(r => r.connection_id)).size === 3);
  },
  async pool_wait(f, check) {
    const first = f.start('held', { hold: true });
    await guarded(first.headers, 'held headers');
    const second = f.start('queued');
    const snapshot = { queued: f.queued(), second_socket_assigned: second.record.socket_assigned,
      second_reached_server: f.responses.some(r => r.id === 'queued') };
    f.log('pool_wait_snapshot', snapshot);
    check('second_queued_before_socket', snapshot.queued === 1 && !snapshot.second_socket_assigned);
    check('second_not_yet_at_server', !snapshot.second_reached_server);
    f.holds.get('held')();
    await guarded(Promise.all([first.done, second.done]), 'pool drain');
    check('reuse_after_first_body', first.record.connection_id === second.record.connection_id);
    check('second_assignment_after_first_end', second.record.socket_at_ms >= first.record.end_at_ms);
  },
  async unread_body(f, check) {
    const first = f.start('unread', { large: true, autoConsume: false });
    const res = await guarded(first.headers, 'unread headers');
    const second = f.start('behind-unread');
    const snapshot = { queued: f.queued(), readable_ended: res.readableEnded,
      second_socket_assigned: second.record.socket_assigned, consume_started: 'consume_at_ms' in first.record };
    f.log('unread_body_snapshot', snapshot);
    check('unconsumed_response_holds_slot', snapshot.queued === 1 && !snapshot.readable_ended
      && !snapshot.second_socket_assigned && !snapshot.consume_started);
    first.consume();
    await guarded(Promise.all([first.done, second.done]), 'consume then reuse');
    check('full_64k_body_read', first.record.bytes === 65536);
    check('reuse_after_consumption', first.record.connection_id === second.record.connection_id);
    check('second_assignment_after_body_end', second.record.socket_at_ms >= first.record.end_at_ms);
  },
  async idle_close(f, check) {
    const first = f.start('before-idle-close');
    await guarded(first.done, 'first idle response');
    check('socket_in_free_pool', f.free() === 1);
    const closed = once(first.req.socket, 'close');
    f.log('explicit_server_close_idle'); f.server.closeIdleConnections();
    await guarded(closed, 'client observes idle close');
    check('closed_socket_removed_from_pool', f.free() === 0 && first.req.socket.destroyed);
    const second = f.start('after-idle-close');
    await guarded(second.done, 'reconnect response');
    check('new_connection_after_observed_close', f.connections.length === 2
      && first.record.connection_id !== second.record.connection_id);
  },
  async timeout_notice(f, check) {
    const request = f.start('notice-only', { hold: true });
    await guarded(request.headers, 'notice headers');
    const timedOut = deferred();
    request.req.setTimeout(25, () => {
      request.req.setTimeout(0);
      f.log('timeout_notice_snapshot', { destroyed: request.req.destroyed,
        completed: request.record.completed, held_on_server: f.holds.has('notice-only') });
      timedOut.resolve();
    });
    await guarded(timedOut.promise, 'inactivity timeout notice');
    check('timeout_did_not_destroy_request', !request.req.destroyed && !request.record.completed);
    check('server_response_still_held', f.holds.has('notice-only'));
    f.holds.get('notice-only')(); await guarded(request.done, 'notice later completion');
    check('body_completed_after_notice', request.record.completed && !request.record.error);
  },
  async timeout_destroy(f, check) {
    const request = f.start('destroy-after-marker', { hold: true, marker: true });
    await guarded(request.headers, 'destroy headers');
    const responseRecord = f.responses.find(r => r.id === 'destroy-after-marker');
    const timedOut = deferred();
    request.req.setTimeout(25, () => {
      f.log('explicit_client_destroy', { marker: f.markers.get('destroy-after-marker') });
      request.req.destroy(Object.assign(new Error('Local inactivity budget'), { code: 'LAB_TIMEOUT' }));
      timedOut.resolve();
    });
    await guarded(timedOut.promise, 'destroy timeout');
    await guarded(request.done, 'destroy outcome');
    await guarded(f.responseClosed.get('destroy-after-marker'), 'server observes client close');
    check('explicit_destroy_ended_client', request.req.destroyed && request.record.error?.code === 'LAB_TIMEOUT');
    check('server_response_not_finished', responseRecord.writable_finished_at_close === false);
    check('memory_marker_not_rolled_back', f.markers.get('destroy-after-marker') === 'applied-in-memory');
    f.log('marker_after_client_close', { value: f.markers.get('destroy-after-marker') });
  },
};

async function runCase(name, repeat) {
  const f = await fixture(), checks = {};
  const check = (label, value) => { checks[label] = value; assert.equal(value, true, `${name}: ${label}`); };
  try {
    await cases[name](f, check);
    const completed = f.requests.filter(r => r.completed);
    check('expected_request_outcomes', name === 'timeout_destroy'
      ? f.requests.length === 1 && !f.requests[0].completed && f.requests[0].error?.code === 'LAB_TIMEOUT'
      : f.requests.every(r => r.completed && !r.error));
    if (completed.length) check('completed_bodies_match_server', completed.every(request => {
      const response = f.responses.find(r => r.id === request.id);
      return request.bytes === response.expected_bytes && request.sha256 === response.expected_sha256
        && request.status === 200 && request.http_version === '1.1';
    }));
    check('all_client_requests_terminal', f.requests.every(r => r.completed || r.error));
  } finally { await f.cleanup(); }
  check('fixture_stopped', !f.server.listening);
  return { name, repeat, checks, connections: f.connections, requests: f.requests,
    server_responses: f.responses, trace: f.trace };
}

function freeze() {
  const files = {};
  for (const name of ['lab.mjs', 'results/results.json', 'results/run.txt']) {
    const file = path.join(directory, name), bytes = readFileSync(file);
    files[path.relative(root, file).split(path.sep).join('/')] = { bytes: bytes.length, sha256: hash(bytes) };
  }
  writeFileSync(path.join(out, 'manifest.json'), JSON.stringify({ recorded_date: '2026-10-19', files }, null, 2) + '\n');
}

if (process.argv.includes('--freeze-manifest')) {
  freeze();
} else {
  const checkOnly = process.argv.includes('--check'), runs = [];
  for (let repeat = 1; repeat <= (checkOnly ? 1 : 3); repeat++) {
    for (const name of Object.keys(cases)) {
      const run = await runCase(name, repeat); runs.push(run);
      console.log(`PASS ${repeat} ${name}: ${Object.keys(run.checks).length} checks, ${run.requests.length} requests, ${run.connections.length} TCP connections`);
    }
  }
  if (!checkOnly) {
    mkdirSync(out, { recursive: true });
    writeFileSync(path.join(out, 'results.json'), JSON.stringify({ recorded_at: new Date().toISOString(),
      runtime: { node: process.version, platform: os.platform(), release: os.release(), arch: os.arch() },
      scope: 'Loopback plain HTTP/1.1 only; no DNS, TLS, packet capture, load benchmark or real database transaction.',
      configuration: { host: '127.0.0.1', port: 'ephemeral per case', maxSockets: 1, maxTotalSockets: 1,
        maxFreeSockets: 1, keepAlive: true, server_keep_alive_ms: 60000, inactivity_notice_ms: 25,
        guard_ms: 5000, unread_body_bytes: 65536 }, runs }, null, 2) + '\n');
  }
  console.log(`PASS: ${runs.length} scenarios; ${runs.reduce((n, r) => n + Object.keys(r.checks).length, 0)} check results.`);
}

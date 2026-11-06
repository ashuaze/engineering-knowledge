import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { parseArgs } from 'node:util';
import { once } from 'node:events';

const { values } = parseArgs({ options: {
  'browser-executable': { type: 'string' }, output: { type: 'string', default: '.cache/browser-long-tasks' },
  runs: { type: 'string', default: '3' }
} });
const repeats = Number(values.runs);
assert.ok(Number.isInteger(repeats) && repeats >= 1 && repeats <= 10, '--runs must be 1..10');
const output = path.resolve(values.output);
await mkdir(output, { recursive: true });
const html = await readFile(new URL('./lab.html', import.meta.url));
const server = createServer((request, response) => {
  if (request.url !== '/') { response.writeHead(404); response.end(); return; }
  response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
  response.end(html);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({ headless: true, executablePath: values['browser-executable'] });
  const context = await browser.newContext({ viewport: { width: 1100, height: 850 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  let started;
  await page.exposeBinding('notifyLabStarted', (_, event) => started?.(event));
  await page.goto(`http://127.0.0.1:${server.address().port}/`, { waitUntil: 'networkidle' });
  const capabilities = await page.evaluate(() => window.lab.capabilities());
  assert.ok(capabilities.longTasks, 'This experiment requires Long Tasks observation');
  const calibration = await page.evaluate(() => window.lab.calibrate());
  const probe = await page.locator('#probe').boundingBox();
  const report = { recordedAt: new Date().toISOString(), browser: browser.version(),
    node: process.version, playwright: JSON.parse(await readFile(new URL('../../node_modules/playwright/package.json', import.meta.url))).version,
    platform: process.platform, arch: process.arch, logicalCpus: os.cpus().length,
    headless: true, cpuThrottling: false, capabilities, calibration,
    scope: 'Synthetic pointerdown waiting, task/RAF opportunities and identical arithmetic work; not INP or a production benchmark.',
    runs: [], checks: {} };
  const modes = ['sync', 'microtask', ...(capabilities.schedulerYield ? ['yield'] : []), 'timer', 'heavy'];
  for (let repeat = 0; repeat < repeats; repeat++) {
    // Rotate execution order while keeping the work and calibration identical.
    const order = [...modes.slice(repeat % modes.length), ...modes.slice(0, repeat % modes.length)];
    for (const mode of order) {
      const runId = `${repeat + 1}-${mode}`;
      await page.locator('#mode').selectOption(mode);
      await page.evaluate(runId => { window.labRunId = runId; }, runId);
      const cdp = await context.newCDPSession(page);
      const trace = [];
      cdp.on('Tracing.dataCollected', event => trace.push(...event.value));
      await cdp.send('Tracing.start', { categories: 'devtools.timeline,blink.user_timing', transferMode: 'ReportEvents' });
      const begin = new Promise(resolve => { started = resolve; });
      // A real browser click starts the workload. DevTools evaluation is not
      // itself a suitable source of observable browser Long Tasks.
      const work = page.locator('#start').click();
      await begin;
      await new Promise(resolve => setTimeout(resolve, 40));
      // Dispatch coordinates directly; an actionability check or an awaited
      // mouse move could postpone injection until the busy main thread is free.
      const input = { x: probe.x + probe.width / 2, y: probe.y + probe.height / 2,
        button: 'left', clickCount: 1 };
      const pointer = cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', ...input });
      await work;
      await pointer;
      await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...input });
      await page.waitForFunction(() => window.lab.snapshot()?.phase === 'finished');
      await page.waitForFunction(() => window.lab.snapshot().probes.length > 0);
      await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 100)));
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const run = await page.evaluate(() => window.lab.snapshot());
      const done = once(cdp, 'Tracing.tracingComplete');
      await cdp.send('Tracing.end');
      await done;
      await cdp.detach();
      assert.equal(run.probes.length, 1, `${runId}: missing or duplicate input`);
      assert.ok(run.probes[0].trusted, `${runId}: input must come from the browser`);
      assert.ok(run.probes[0].pointerdownToHandlerMs >= 0, `${runId}: incompatible timestamp origin`);
      run.workElapsedMs = run.finishedAt - run.startedAt;
      run.timerDuringWork = run.timerAt < run.finishedAt;
      run.frameDuringWork = run.frameAt < run.finishedAt;
      run.traceFile = `${runId}.trace.json`;
      run.traceEventCounts = Object.fromEntries(['EventDispatch', 'UpdateLayoutTree', 'Layout', 'Paint', 'FunctionCall']
        .map(name => [name, trace.filter(event => event.name === name).length]));
      await writeFile(path.join(output, run.traceFile), JSON.stringify({ traceEvents: trace }));
      report.runs.push(run);
      console.log(`${runId}: ${run.workElapsedMs.toFixed(1)}ms, pointer wait ${run.probes[0].pointerdownToHandlerMs.toFixed(1)}ms, long tasks ${run.longTasks.length}`);
    }
  }
  report.checks.sameBusinessResult = new Set(report.runs.map(run => run.checksum)).size === 1;
  report.checks.syncAndMicrotaskDeferTimer = report.runs.filter(run => ['sync', 'microtask', 'heavy'].includes(run.mode))
    .every(run => !run.timerDuringWork);
  report.checks.timerFallbackAllowsOtherTask = report.runs.filter(run => run.mode === 'timer').every(run => run.timerDuringWork);
  report.checks.heavyJobExceedsSliceBudget = report.runs.filter(run => run.mode === 'heavy')
    .every(run => Math.max(...run.jobDurationsMs) > calibration.sliceBudgetMs);
  report.checks.blockingModesProduceLongTasks = report.runs.filter(run => ['sync', 'microtask', 'heavy'].includes(run.mode))
    .every(run => run.longTasks.some(task => task.duration >= 50));
  report.checks.noPageErrors = errors.length === 0;
  report.errors = errors;
  // Save the raw observations even if a mechanism check fails on another environment.
  await writeFile(path.join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  await page.screenshot({ path: path.join(output, 'page.png'), fullPage: true });
  for (const [name, passed] of Object.entries(report.checks)) assert.ok(passed, name);
  console.log(`PASS: ${report.runs.length} runs; checksum, scheduling boundaries, heavy-job limit and browser input verified. Results: ${path.join(output, 'results.json')}`);
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}

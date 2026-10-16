import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { createMarkdownRenderer } from 'vitepress';
import { getSiteSettings, sourceLink, repositoryLinks, docsRoot } from '../docs/.vitepress/site.mjs';
import { tokenize } from '../docs/.vitepress/search.mjs';

test('deployment paths follow repository names and support custom domains', () => {
  assert.equal(getSiteSettings({}).base, '/engineering-knowledge/');
  assert.equal(getSiteSettings({ GITHUB_REPOSITORY: 'alice/notes' }).base, '/notes/');
  assert.equal(getSiteSettings({ GITHUB_REPOSITORY: 'alice/alice.github.io' }).base, '/');
  assert.equal(getSiteSettings({ SITE_REPOSITORY: 'https://github.com/alice/notes.git' }).repositoryUrl, 'https://github.com/alice/notes');
  assert.equal(getSiteSettings({ SITE_BASE: '/', SITE_URL: 'https://notes.example.com' }).base, '/');
  assert.throws(() => getSiteSettings({ SITE_BASE: '/notes/../' }));
  assert.throws(() => getSiteSettings({ SITE_BASE: '/notes/', SITE_URL: 'https://example.com/wrong' }));
});

test('repository file links use the actual build revision without changing article links', () => {
  const settings = getSiteSettings({ SITE_REPOSITORY: 'alice/notes', SITE_SOURCE_REF: 'release/october' });
  const article = path.join(docsRoot, 'knowledge/api/idempotency.md');
  assert.equal(sourceLink('../../../examples/idempotency/lab.py', article, settings), 'https://github.com/alice/notes/blob/release%2Foctober/examples/idempotency/lab.py');
  assert.equal(sourceLink('idempotency-lab.md', article, settings), 'idempotency-lab.md');
  assert.equal(sourceLink('https://example.com', article, settings), 'https://example.com');
  assert.throws(() => sourceLink('../../../.env', article, settings));
});

test('local source links receive exactly one deployment prefix during Markdown rendering', async () => {
  const settings = getSiteSettings({});
  const md = await createMarkdownRenderer(docsRoot, { config(md) { md.use(repositoryLinks(settings)); } }, settings.base);
  const html = md.render('[实验](../../../examples/idempotency/lab.py) [正文](idempotency-lab.md)', {
    path: path.join(docsRoot, 'knowledge/api/idempotency.md'),
    relativePath: 'knowledge/api/idempotency.md', cleanUrls: false
  });
  assert.match(html, /href="\/engineering-knowledge\/_source\/examples\/idempotency\/lab\.py\.txt"/);
  assert.match(html, /href="\.\/idempotency-lab\.html"/);
});

test('Chinese and English search tokenization is identical after browser serialization', () => {
  const browserTokenizer = Function(`return (${tokenize.toString()})`)();
  for (const query of ['幂等性', '重试预算', '协程', 'Outbox', 'HTTP/2']) {
    assert.deepEqual(browserTokenizer(query), tokenize(query));
    assert.ok(tokenize(query).length > 0);
  }
  assert.ok(tokenize('超时与重试预算：失败边界').includes('试预'));
  assert.deepEqual(tokenize('Outbox'), ['outbox']);
});

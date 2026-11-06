import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { createMarkdownRenderer } from 'vitepress';
import { getSiteSettings, sourceLink, repositoryLinks, docsRoot } from '../docs/.vitepress/site.mjs';
import { tokenize } from '../docs/.vitepress/search.mjs';
import { readLibrary, createSearchDocuments, articleMetadata } from '../docs/.vitepress/library.mjs';
import { prepareDocuments, searchDocuments } from '../docs/.vitepress/theme/search-core.mjs';

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

test('local search ranks titles and aliases, preserves full text and requires every query part', () => {
  const documents = prepareDocuments([
    { title: '请求结果未知', aliases: 'Idempotency 幂等性', description: '安全处理重复请求', text: '工作进程丢失响应后，仍须保留业务标识。', url: '/unknown.html' },
    { title: '幂等性', aliases: '', description: '重复请求', text: '处理工作进程的确认边界。', url: '/idempotency.html' },
    { title: '并发', aliases: 'Concurrency', description: '', text: '工作进程的执行交错。', url: '/concurrency.html' }
  ]);
  assert.equal(searchDocuments(documents, '幂等性')[0].url, '/idempotency.html');
  assert.deepEqual(searchDocuments(documents, 'ＩＤＥＭＰＯＴＥＮＣＹ').map(item => item.url), ['/unknown.html']);
  assert.deepEqual(searchDocuments(documents, '丢失响应 业务标识').map(item => item.url), ['/unknown.html']);
  assert.deepEqual(searchDocuments(documents, '幂等性 Concurrency'), []);
  assert.deepEqual(searchDocuments(documents, '   '), []);
  assert.deepEqual(searchDocuments(documents, '没有这个词'), []);
  assert.equal(searchDocuments(documents, '工作进程', 1).length, 1);
  assert.ok(!('normalizedText' in searchDocuments(documents, '工作进程')[0]));
});

test('search corpus contains every article and term with stable local destinations', () => {
  const library = readLibrary();
  const documents = createSearchDocuments(library);
  assert.equal(documents.filter(document => document.kind === '文章').length, library.articles.length);
  assert.equal(documents.filter(document => document.kind === '术语').length, library.terms.length);
  assert.equal(new Set(documents.map(document => document.url)).size, documents.length);
  assert.ok(documents.every(document => document.url.startsWith('/') && !document.url.includes('..')));
  assert.ok(documents.some(document => document.url === '/glossary/api.html#api.idempotency'));
  assert.ok(documents.every(document => !document.url.startsWith('/handbook/') && !document.url.includes('VALIDATION')));
  assert.ok(documents.find(document => document.url === '/knowledge/api/idempotency.html').text.length > 1000);
  const rag = searchDocuments(prepareDocuments(documents), 'RAG');
  assert.match(rag[0].title, /RAG/i);
  assert.ok(!rag.some(document => document.title === 'CPU Time / Utilization / Load Average'));
});

test('English acronym and prefix search does not match the middle of unrelated words', () => {
  const documents = prepareDocuments([
    { title: 'Load Average', aliases: 'Storage', description: '', text: '', url: '/load' },
    { title: 'RAG 与依据', aliases: 'Retrieval', description: '', text: '', url: '/rag' }
  ]);
  assert.deepEqual(searchDocuments(documents, 'RAG').map(document => document.url), ['/rag']);
  assert.deepEqual(searchDocuments(documents, 'retriev').map(document => document.url), ['/rag']);
});

test('article metadata follows its title and is not inserted in navigation pages', async () => {
  const md = await createMarkdownRenderer(docsRoot);
  md.use(articleMetadata);
  assert.match(md.render('---\nid: "article"\n---\n# 阅读正文\n\n内容'), /<\/h1>\s*<ArticleMeta\s*\/>/);
  assert.doesNotMatch(md.render('# 导航\n\n内容', { frontmatter: {} }), /ArticleMeta/);
});

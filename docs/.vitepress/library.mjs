import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { gzipSync } from 'node:zlib';
import { docsRoot, root } from './site.mjs';

export function readDocument(file) {
  let body = readFileSync(file, 'utf8');
  const metadata = {};
  const frontmatter = body.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (frontmatter) {
    for (const line of frontmatter[1].split(/\r?\n/)) {
      const match = line.match(/^([\w-]+):\s*(.*)$/);
      if (!match) continue;
      try { metadata[match[1]] = JSON.parse(match[2]); }
      catch { metadata[match[1]] = match[2]; }
    }
    body = body.slice(frontmatter[0].length);
  }
  return { metadata, body };
}

export function plainText(markdown) {
  return markdown
    .replace(/<!--[^]*?-->/g, ' ')
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]*>/g, ' ')
    .replace(/^\s*```.*$/gm, '')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/[#*_`|>]/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

export function readLibrary() {
  const domains = JSON.parse(readFileSync(path.join(root, 'data/domains.json'), 'utf8'));
  const terms = JSON.parse(readFileSync(path.join(root, 'data/terms.json'), 'utf8'));
  const articles = domains.flatMap(domain => readdirSync(path.join(docsRoot, 'knowledge', domain.id))
    .filter(file => file.endsWith('.md') && file !== 'index.md')
    .map(file => {
      const { metadata, body } = readDocument(path.join(docsRoot, 'knowledge', domain.id, file));
      return { ...metadata, url: `/knowledge/${domain.id}/${file.replace(/\.md$/, '.html')}`, body };
    }));
  return { domains, terms, articles };
}

export function libraryOverview(library) {
  return {
    articleCount: library.articles.length,
    termCount: library.terms.length,
    domains: library.domains.map(domain => ({ ...domain,
      count: library.articles.filter(article => article.domain === domain.id).length
    })),
    latest: [...library.articles].sort((a, b) => b.updated.localeCompare(a.updated) || a.title.localeCompare(b.title, 'zh-CN'))
      .slice(0, 3).map(({ title, url, updated, summary }) => ({ title, url, updated, summary }))
  };
}

export function createSearchDocuments(library = readLibrary()) {
  const domainNames = new Map(library.domains.map(domain => [domain.id, domain.title]));
  const articleAliases = new Map();
  for (const term of library.terms) for (const file of term.articles) {
    const url = '/' + file.replace(/^docs\//, '').replace(/\.md$/, '.html');
    articleAliases.set(url, [...(articleAliases.get(url) || []), term.name, ...term.aliases]);
  }
  const documents = library.articles.map(article => ({
    title: article.title, url: article.url, description: article.summary,
    domain: domainNames.get(article.domain), kind: '文章',
    aliases: [...new Set(articleAliases.get(article.url) || [])].join(' '),
    text: plainText(article.body)
  }));
  for (const term of library.terms) documents.push({
    title: term.name, url: `/glossary/${term.domain}.html#${term.id}`,
    description: term.definition, domain: domainNames.get(term.domain), kind: '术语',
    aliases: term.aliases.join(' '),
    text: [term.explanation, term.example].filter(Boolean).join(' ')
  });
  for (const file of ['problems.md', 'paths/index.md', 'map.md', 'articles.md', 'glossary.md', 'glossary/index.md']) {
    const { body } = readDocument(path.join(docsRoot, file));
    const title = body.match(/^#\s+(.+)$/m)?.[1] || file;
    documents.push({ title, url: '/' + file.replace(/index\.md$/, '').replace(/\.md$/, '.html'),
      description: plainText(body).slice(title.length, title.length + 120).trim(),
      domain: '阅读导航', kind: '导航', aliases: '', text: plainText(body) });
  }
  return documents;
}

export function knowledgeSearchPlugin(base) {
  let cached;
  let compressed;
  const getIndex = () => cached ??= JSON.stringify({ version: 1, documents: createSearchDocuments() });
  const getCompressedIndex = () => compressed ??= gzipSync(getIndex(), { level: 9 });
  return {
    name: 'fieldnotes-search-index',
    configureServer(server) {
      const invalidate = file => {
        if ((file.startsWith(docsRoot) && file.endsWith('.md')) || file.startsWith(path.join(root, 'data'))) { cached = undefined; compressed = undefined; }
      };
      server.watcher.on('change', invalidate);
      server.watcher.on('add', invalidate);
      server.watcher.on('unlink', invalidate);
      server.middlewares.use((request, response, next) => {
        const url = request.url?.split('?')[0];
        if (![`${base}search-index.json`, `${base}search-index.bin`].includes(url)) return next();
        const binary = url.endsWith('.bin');
        response.setHeader('Content-Type', binary ? 'application/octet-stream' : 'application/json; charset=utf-8');
        response.setHeader('Cache-Control', 'no-cache');
        response.end(binary ? getCompressedIndex() : getIndex());
      });
    },
    generateBundle(options) {
      if (options.format !== 'es') return;
      this.emitFile({ type: 'asset', fileName: 'search-index.json', source: getIndex() });
      this.emitFile({ type: 'asset', fileName: 'search-index.bin', source: getCompressedIndex() });
    }
  };
}

export function articleMetadata(md) {
  const close = md.renderer.rules.heading_close || ((tokens, index, options, env, self) => self.renderToken(tokens, index, options));
  md.renderer.rules.heading_close = (tokens, index, options, env, self) => {
    const html = close(tokens, index, options, env, self);
    return tokens[index].tag === 'h1' && env.frontmatter?.id ? `${html}\n<ArticleMeta />\n` : html;
  };
  md.renderer.rules.table_open = () => '<div class="table-region" role="region" aria-label="数据表格" tabindex="0"><table>\n';
  md.renderer.rules.table_close = () => '</table></div><p class="table-scroll-hint" aria-hidden="true">左右滑动查看完整表格</p>\n';
}

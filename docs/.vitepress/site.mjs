import { readFileSync, readdirSync, mkdirSync, copyFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../../', import.meta.url));
export const docsRoot = path.join(root, 'docs');

// Only these public supporting files may be exposed by the local preview.
export const sourceFiles = [
  'VALIDATION.md',
  'examples/idempotency/lab.py', 'examples/idempotency/test_lab.py',
  'examples/retry_budget/lab.py', 'examples/retry_budget/test_lab.py',
  'examples/object_authorization/lab.py', 'examples/object_authorization/test_lab.py'
];

export function getSiteSettings(env = process.env) {
  const repository = (env.SITE_REPOSITORY || env.GITHUB_REPOSITORY || '')
    .replace(/^https:\/\/github\.com\//, '').replace(/\.git\/?$/, '').replace(/\/$/, '');
  if (repository && !/^[\w.-]+\/[\w.-]+$/.test(repository)) {
    throw new Error('SITE_REPOSITORY must be owner/repository or its GitHub HTTPS URL.');
  }
  const [owner, name] = repository.split('/');
  const base = env.SITE_BASE || (name
    ? (name.toLowerCase() === `${owner}.github.io`.toLowerCase() ? '/' : `/${name}/`)
    : '/engineering-knowledge/');
  if (!/^\/(?:[\w.-]+\/)*$/.test(base) || base.split('/').some(p => p === '.' || p === '..')) {
    throw new Error('SITE_BASE must be a slash-delimited path such as /engineering-knowledge/ or /.');
  }
  const siteUrl = env.SITE_URL?.replace(/\/$/, '');
  if (siteUrl) {
    const parsed = new URL(siteUrl);
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.search || parsed.hash ||
        parsed.pathname !== (base === '/' ? '/' : base.slice(0, -1))) {
      throw new Error('SITE_URL must be the full HTTPS site URL matching SITE_BASE.');
    }
  }
  return {
    base, siteUrl,
    repositoryUrl: repository ? `https://github.com/${repository}` : '',
    sourceRef: env.SITE_SOURCE_REF || env.GITHUB_SHA || env.GITHUB_REF_NAME || 'HEAD'
  };
}

export function sourceLink(href, sourcePath, settings) {
  if (!href || /^(?:[a-z][\w+.-]*:|\/|#)/i.test(href)) return href;
  const match = href.match(/^([^?#]+)(.*)$/);
  if (!match) return href;
  const target = path.resolve(path.dirname(sourcePath), decodeURIComponent(match[1]));
  const relative = path.relative(root, target).split(path.sep).join('/');
  if (target.startsWith(docsRoot + path.sep)) return href;
  if (!sourceFiles.includes(relative)) {
    throw new Error(`Unsupported repository link in ${sourcePath}: ${href}`);
  }
  const encoded = relative.split('/').map(encodeURIComponent).join('/');
  return settings.repositoryUrl
    ? `${settings.repositoryUrl}/blob/${encodeURIComponent(settings.sourceRef)}/${encoded}${match[2]}`
    : `/_source/${encoded}.txt${match[2]}`;
}

export function repositoryLinks(settings) {
  return md => {
    // Run before VitePress resolves internal Markdown links and collects dead links.
    md.core.ruler.after('inline', 'repository-source-links', state => {
      if (!state.env.path) return;
      const visit = tokens => {
        for (const token of tokens) {
          if (token.type === 'link_open') {
            const href = token.attrGet('href');
            const rewritten = sourceLink(href, state.env.path, settings);
            if (rewritten !== href) token.attrSet('href', rewritten);
          }
          if (token.children) visit(token.children);
        }
      };
      visit(state.tokens);
    });
  };
}

export function supportingSources(settings) {
  const prefix = `${settings.base}_source/`;
  return {
    name: 'fieldnotes-supporting-sources',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const pathname = new URL(req.url || '/', 'http://localhost').pathname;
        if (!pathname.startsWith(prefix)) return next();
        const file = decodeURIComponent(pathname.slice(prefix.length)).replace(/\.txt$/, '');
        if (!sourceFiles.includes(file)) return next();
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.end(readFileSync(path.join(root, file)));
      });
    }
  };
}

export function copySupportingSources(outDir) {
  for (const file of sourceFiles) {
    const target = path.join(outDir, '_source', `${file}.txt`);
    mkdirSync(path.dirname(target), { recursive: true });
    copyFileSync(path.join(root, file), target);
  }
}

export function getDomains() {
  return JSON.parse(readFileSync(path.join(root, 'data/domains.json'), 'utf8'));
}

export function getDomainNavigation(domain) {
  const directory = path.join(docsRoot, 'knowledge', domain.id);
  return {
    text: domain.title,
    collapsed: true,
    items: [
      { text: '领域概览', link: `/knowledge/${domain.id}/` },
      ...readdirSync(directory).filter(file => file.endsWith('.md') && file !== 'index.md').sort().map(file => {
        const content = readFileSync(path.join(directory, file), 'utf8');
        const title = JSON.parse(content.match(/^title: (.+)$/m)[1]);
        return { text: title, link: `/knowledge/${domain.id}/${file.replace(/\.md$/, '.html')}` };
      })
    ]
  };
}

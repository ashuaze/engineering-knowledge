"""Check emitted HTML links, fragments and assets under the actual deployment base.

This checks local build output, not external websites or JavaScript behavior.
"""
from argparse import ArgumentParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import os
import sys

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.icon = None
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'link' and attrs.get('rel') == 'icon':
            self.icon = attrs.get('href')
        for name in ('href', 'src', 'poster'):
            if attrs.get(name):
                self.links.append((attrs[name], self.getpos()[0]))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / 'docs/.vitepress/dist')
    parser.add_argument('--base', default=os.environ.get('SITE_BASE'))
    args = parser.parse_args()
    output = args.directory.resolve()
    pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
    home = pages.get(output / 'index.html')
    if not home or not home.icon:
        print('Build output or its favicon is missing. Run npm run docs:build first.', file=sys.stderr)
        return 1
    base = args.base or urlsplit(home.icon).path.rsplit('/', 1)[0] + '/'
    if not base.startswith('/') or not base.endswith('/'):
        parser.error('--base must start and end with /.')
    errors = []
    checked = 0
    targets = {}
    for file, page in pages.items():
        route = base + file.relative_to(output).as_posix()
        for href, line in page.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            url = urlsplit(urljoin('https://site.invalid' + route, href))
            label = f'{file.relative_to(output)}:{line}: {href}'
            if not url.path.startswith(base):
                errors.append(f'{label}: outside deployment base {base}')
                continue
            relative = unquote(url.path[len(base):])
            if relative not in targets:
                target = (output / relative).resolve()
                if target.is_relative_to(output) and target.is_dir():
                    target = target / 'index.html'
                targets[relative] = (target, target.is_file())
            target, exists = targets[relative]
            if not target.is_relative_to(output):
                errors.append(f'{label}: outside build output')
                continue
            if not exists:
                errors.append(f'{label}: missing file')
            elif url.fragment and target.suffix == '.html':
                if unquote(url.fragment) not in pages[target].ids:
                    errors.append(f'{label}: missing fragment')
            checked += 1
    if errors:
        print('\n'.join(errors[:30]), file=sys.stderr)
        print(f'FAIL: {len(errors)} broken local references.', file=sys.stderr)
        return 1
    print(f'PASS: {len(pages)} HTML pages, {checked} local links/assets/fragments, base {base}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

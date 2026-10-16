"""Validate content metadata and local Markdown file/fragment targets.

Not a Markdown parser, a website build, remote-link crawler, or technical review.
"""
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import unicodedata
from common import ROOT, load_json, articles


def strip_fences(text):
    return re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)


def anchors(text):
    result = set(re.findall(r'<a\s+id="([^"]+)"', text))
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', strip_fences(text), re.M):
        heading = re.sub(r'[`*_]', '', heading.lower())
        slug = ''.join(c for c in heading if c in '-_' or not unicodedata.category(c).startswith('P'))
        slug = re.sub(r'\s', '-', slug.strip())
        count = counts.get(slug, 0)
        result.add(slug + (f'-{count}' if count else ''))
        counts[slug] = count + 1
    return result


def main():
    errors = []
    domains = load_json('domains.json')
    domain_ids = [d['id'] for d in domains]
    if len(domain_ids) != len(set(domain_ids)):
        errors.append('Duplicate domain ids')
    pages = articles()
    ids = [m.get('id') for _,m,_ in pages]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate article ids')
    article_paths = {p.relative_to(ROOT).as_posix() for p,_,_ in pages}
    required = {'id','title','kind','domain','status','summary','created','updated','last_verified','verification','prerequisites','related','tags'}
    for path,m,body in pages:
        label=path.relative_to(ROOT).as_posix()
        if required-set(m):
            errors.append(f'{label}: missing {sorted(required-set(m))}')
            continue
        if not re.fullmatch(r'kb-[a-z0-9-]+',m['id']):
            errors.append(f'{label}: invalid id')
        if m['domain'] not in domain_ids or path.parent.name != m['domain']:
            errors.append(f'{label}: invalid domain/path')
        if m['kind'] not in {'concept','comparison','pattern','case','lab','decision'}:
            errors.append(f'{label}: invalid kind')
        if m['status'] not in {'evolving','reviewed','deprecated'}:
            errors.append(f'{label}: invalid status')
        if m['verification'] not in {'source-checked','tested','design-proposal'}:
            errors.append(f'{label}: invalid verification')
        try:
            created=date.fromisoformat(m['created']); updated=date.fromisoformat(m['updated'])
            if created>updated:
                errors.append(f'{label}: created > updated')
            if m['last_verified'] is not None:
                if date.fromisoformat(m['last_verified'])>updated:
                    errors.append(f'{label}: last_verified > updated')
            elif m['verification'] != 'design-proposal':
                errors.append(f'{label}: verification needs last_verified')
        except (ValueError,TypeError):
            errors.append(f'{label}: invalid ISO date')
        for field in ('prerequisites','related','tags'):
            values=m[field]
            if not isinstance(values,list) or any(not isinstance(x,str) for x in values):
                errors.append(f'{label}: invalid {field}')
                continue
            if len(values)!=len(set(values)):
                errors.append(f'{label}: duplicate {field}')
            if field!='tags':
                for ident in values:
                    if ident not in ids or ident == m['id']:
                        errors.append(f'{label}: unresolved/self reference {ident}')
        if not body.startswith('# '+m['title']+'\n'):
            errors.append(f'{label}: H1 differs from metadata title')

    terms=load_json('terms.json'); term_ids=[t['id'] for t in terms]
    if len(term_ids)!=len(set(term_ids)):
        errors.append('Duplicate term ids')
    for t in terms:
        if t['domain'] not in domain_ids or not t['id'].startswith(t['domain']+'.'):
            errors.append(f"{t['id']}: invalid term domain")
        if not t['name'] or not t['definition'] or not t['aliases']:
            errors.append(f"{t['id']}: missing term text")
        if t['priority'] not in {'P0','P1','P2'}:
            errors.append(f"{t['id']}: invalid priority")
        for target in t['articles']:
            if target not in article_paths:
                errors.append(f"{t['id']}: missing article {target}")

    markdown=list((ROOT/'docs').rglob('*.md'))+list((ROOT/'templates').glob('*.md'))+list(ROOT.glob('*.md'))
    links_checked=0
    for path in markdown:
        text=strip_fences(path.read_text(encoding='utf-8'))
        for raw in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',text):
            url=urlsplit(raw)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith('/'):
                errors.append(f'{path.relative_to(ROOT)}: use relative source link: {raw}')
                continue
            target=(path.parent/unquote(url.path)).resolve() if url.path else path.resolve()
            if not target.is_relative_to(ROOT):
                errors.append(f'{path.relative_to(ROOT)}: path escapes repository: {raw}')
            elif not target.is_file():
                errors.append(f'{path.relative_to(ROOT)}: missing target: {raw}')
            elif url.fragment and target.suffix=='.md' and unquote(url.fragment) not in anchors(target.read_text(encoding='utf-8')):
                errors.append(f'{path.relative_to(ROOT)}: missing fragment: {raw}')
            links_checked+=1
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print(f'PASS: {len(pages)} articles, {len(domains)} domains, {len(terms)} grouped terms, {links_checked} local links in {len(markdown)} Markdown files.')
    print('Scope: flat metadata + ordinary inline local links/fragments; no remote links, Markdown rendering or website build.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())

"""Link the first unambiguous prose mention of each glossary group per page.

Conservative source rewriter, not a full Markdown parser: fenced/indented code,
frontmatter, headings, inline code, HTML, URLs and existing links are protected.
Run before generate_indexes.py; generated navigation is linked by its generator.
"""
from collections import defaultdict
from datetime import date
from pathlib import Path
import argparse
import os
import re
import sys
from common import ROOT, DOCS, load_json


# These aliases are useful for search, but ordinary prose cannot disambiguate
# them reliably. They remain visible in the glossary without automatic linking.
PROSE_EXCLUSIONS = {
    'any', 'unknown', 'clean', 'dirty', 'strong', 'unit', 'load', 'stress',
    'horizontal', 'short-term', 'semantic', 'development set', '图', '树', '栈',
    '封装', '布局', '绘制', '合成', '日志', '指标', '采样', 'time', 'nonce',
    '不变量', 'invariant', '误报', '假阳性', 'false positive', '状态转移', 'hash',
    '检查点', 'checkpoint',
}

# Some aliases have other established meanings outside their subject area.
# Keep them as search terms, but require context before inserting a prose link.
ALIAS_DOMAINS = {
    'rfc': {'engineering'},
    'scope': {'runtime', 'frontend'}, '作用域': {'runtime', 'frontend'},
    'abi': {'systems'},
    '实体': {'architecture'}, 'entity': {'architecture'},
    'aba': {'systems', 'runtime', 'distributed', 'cache-search'},
    '同步': {'runtime', 'frontend'}, '异步': {'runtime', 'frontend'},
    'sync': {'runtime', 'frontend'}, 'async': {'runtime', 'frontend'},
    '聚合': {'architecture'}, 'aggregate': {'architecture'},
    '会话': {'security'}, 'session': {'security'},
    '路由': {'ai'}, 'routing': {'ai'}, '交接': {'ai'}, '编排': {'ai'},
    '子网': {'devops'}, 'subnet': {'devops'},
    '最长前缀匹配': {'networking'}, 'longest prefix match': {'networking'},
    '控制平面': {'networking'}, '数据平面': {'networking'},
    '临时地址': {'networking'}, '接入防护': {'networking'},
    'service': {'devops'},
    '重排': {'cache-search', 'ai'},
    '事件流': {'messaging', 'distributed'},
    '组件身份': {'frontend'},
    'cls': {'frontend', 'performance'}, 'lcp': {'frontend', 'performance'},
    'inp': {'frontend', 'performance'},
    '队列': {'algorithms', 'systems', 'runtime', 'frontend', 'performance', 'messaging', 'ai', 'cache-search'},
    'queue': {'algorithms', 'systems', 'runtime', 'frontend', 'performance', 'messaging', 'ai', 'cache-search'},
    '租约': {'distributed', 'cache-search'}, 'lease': {'distributed', 'cache-search'},
    '数组': {'algorithms', 'runtime', 'frontend', 'performance', 'systems'},
    '兼容性': {'api'},
    '分片': {'database', 'distributed', 'cache-search'},
    '分区键': {'messaging'}, 'partition key': {'messaging'},
    '冗余': {'reliability', 'devops'}, 'redundancy': {'reliability', 'devops'},
    '可用性': {'reliability', 'devops'}, 'availability': {'reliability', 'devops'},
    '可靠性': {'reliability', 'devops'},
    '碰撞': {'algorithms'},
    '局部性': {'systems', 'performance', 'runtime', 'algorithms'},
    '扇出': {'algorithms'}, 'fanout': {'algorithms'},
    '超时': {'api', 'reliability'}, 'timeout': {'api', 'reliability'},
    '函数调用': {'ai'}, '扩容': {'algorithms'},
    '异常': {'runtime', 'frontend'}, 'exception': {'runtime', 'frontend'},
    'hash': {'security'}, '可达性': {'runtime'}, 'reachability': {'runtime'},
    'select': {'systems'}, 'poll': {'systems'},
    'offset': {'messaging'}, 'token': {'ai'},
    '分页': {'systems'}, '分区': {'database'}, '配额': {'api'},
    '排序': {'algorithms'}, '流水线': {'performance'},
    '误报': {'algorithms', 'cache-search'},
    'namespace': {'systems', 'devops'}, '命名空间': {'systems', 'devops'},
    'signal': {'systems', 'devops'}, '控制循环': {'devops'},
    '消费者': {'messaging'}, '生产者': {'messaging'},
    '重试': {'api', 'networking', 'reliability', 'ai', 'performance', 'messaging', 'distributed', 'devops'},
    '执行计划': {'database'},
    'rto': {'reliability', 'database', 'devops'},
    'undo': {'database'},
    '闭包': {'runtime', 'frontend'}, 'ordering': {'messaging'},
    '消息顺序': {'messaging'}, '下一跳': {'networking'},
    '预热': {'performance'},
    '打包': {'frontend'},
    '容器': {'devops', 'systems'}, 'container': {'devops', 'systems'},
    '幂等性': {'api', 'database', 'messaging', 'reliability', 'ai', 'architecture'},
    '幂等': {'api', 'database', 'messaging', 'reliability', 'ai', 'architecture'},
    'idempotency': {'api', 'database', 'messaging', 'reliability', 'ai', 'architecture'},
    '消费组': {'messaging'}, 'consumer group': {'messaging'},
    '字节流': {'networking'}, '数据报': {'networking'}, '消息队列': {'messaging'},
    '并发': {'systems', 'runtime', 'frontend', 'performance'},
    '异步处理': {'messaging'},
    'event time': {'messaging'}, '事件时间': {'messaging'},
    'processing time': {'messaging'}, '处理时间': {'messaging'},
    'watermark': {'messaging'}, '水位线': {'messaging'},
    'window': {'messaging'}, '窗口': {'messaging'},
    'trigger': {'messaging'}, '触发器': {'messaging'},
    'pane': {'messaging'},
    '阻塞': {'systems', 'runtime', 'networking', 'performance', 'frontend'},
    'blocking': {'systems', 'runtime', 'networking', 'performance', 'frontend'},
    '非阻塞': {'systems', 'runtime', 'networking', 'performance', 'frontend'},
    'non-blocking': {'systems', 'runtime', 'networking', 'performance', 'frontend'},
}


def glossary_path(term):
    return DOCS / 'glossary' / f"{term['domain']}.md"


def term_link(source, term):
    relative = Path(os.path.relpath(glossary_path(term), source.parent)).as_posix()
    return f"{relative}#{term['id']}"


class GlossaryLinker:
    def __init__(self, terms):
        self.terms = {t['id']: t for t in terms}
        self.by_alias = defaultdict(set)
        for term in terms:
            # Split only spaced slashes; HTTP/2 and I/O are indivisible aliases.
            for alias in [*term['aliases'], *term['name'].split(' / ')]:
                key = alias.casefold()
                if len(alias) > 1 and key not in PROSE_EXCLUSIONS:
                    self.by_alias[key].add(term['id'])
        alternatives = []
        for alias in sorted(self.by_alias, key=lambda a: (-len(a), a)):
            pattern = re.escape(alias)
            if re.match(r'[a-z0-9_]', alias[0]):
                pattern = r'(?<![a-z0-9_])' + pattern
            if re.match(r'[a-z0-9_]', alias[-1]):
                pattern += r'(?![a-z0-9_])'
            alternatives.append(pattern)
        self.pattern = re.compile('|'.join(alternatives), re.I)

    def resolve(self, alias, path):
        domain = path.parent.name if path.parent.parent == DOCS / 'knowledge' else None
        if alias.casefold() in ALIAS_DOMAINS and domain not in ALIAS_DOMAINS[alias.casefold()]:
            return None
        candidates = [self.terms[i] for i in self.by_alias[alias.casefold()]]
        if len(candidates) == 1:
            return candidates[0]
        local = [t for t in candidates if t['domain'] == domain]
        if len(local) == 1:
            return local[0]
        related = [t for t in candidates if path.relative_to(ROOT).as_posix() in t['articles']]
        return related[0] if len(related) == 1 else None

    def link(self, text, path):
        seen = set()

        def replace_plain(plain):
            def replace(match):
                # An authenticator is a credential-bearing mechanism, not the
                # authentication event or assurance claim named by this alias.
                if match.group().endswith('认证') and plain[match.end():].startswith('器'):
                    return match.group()
                term = self.resolve(match.group(), path)
                if not term or term['id'] in seen:
                    return match.group()
                seen.add(term['id'])
                return f'[{match.group()}]({term_link(path, term)})'
            return self.pattern.sub(replace, plain)

        result = []
        for protected, value in markdown_segments(text):
            if protected:
                # Count an existing glossary reference where it appears in source.
                existing = value if value.startswith('[') else ''
                for ident in re.findall(r'glossary/[\w-]+\.md#([\w.-]+)', existing):
                    if ident in self.terms:
                        seen.add(ident)
                result.append(value)
            else:
                result.append(replace_plain(value))
        return ''.join(result)


def bracket_end(text, start, opener, closer):
    """Return the end of a balanced label/destination, honoring escapes."""
    depth = 0
    pos = start
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == opener:
            depth += 1
        elif text[pos] == closer:
            depth -= 1
            if depth == 0:
                return pos + 1
        pos += 1
    return None


def inline_segments(text):
    start = pos = 0
    while pos < len(text):
        end = None
        if text[pos] == '\\':
            end = min(pos + 2, len(text))
        elif text[pos] == '`':
            run = re.match(r'`+', text[pos:]).group()
            closing = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', text[pos + len(run):])
            if closing:
                end = pos + len(run) + closing.end()
        elif text[pos] == '<':
            if text.startswith('<!--', pos):
                closing = text.find('-->', pos + 4)
                end = closing + 3 if closing >= 0 else len(text)
            else:
                # Includes HTML attributes and Markdown autolinks.
                tag = re.match(r'<(?:[^>"\']|"[^"]*"|\'[^\']*\')*>', text[pos:])
                if tag:
                    end = pos + tag.end()
        elif text[pos] in '![':
            label_start = pos + 1 if text.startswith('![', pos) else pos
            if text[label_start:label_start + 1] == '[':
                label_end = bracket_end(text, label_start, '[', ']')
                if label_end:
                    if text[label_end:label_end + 1] == '(':
                        end = bracket_end(text, label_end, '(', ')')
                    elif text[label_end:label_end + 1] == '[':
                        end = bracket_end(text, label_end, '[', ']')
                    else:
                        # Protect shortcut references too, even if unresolved.
                        end = label_end
        elif text.startswith(('https://', 'http://', 'mailto:'), pos):
            end = pos + re.match(r'[^\s<>]+', text[pos:]).end()
        if end:
            if start < pos:
                yield False, text[start:pos]
            yield True, text[pos:end]
            pos = start = end
        else:
            pos += 1
    if start < len(text):
        yield False, text[start:]


def markdown_segments(text):
    lines = text.splitlines(keepends=True)
    frontmatter = bool(lines and lines[0].strip() == '---')
    fence = None
    html_block = None
    prose = []

    def flush():
        if prose:
            value = ''.join(prose)
            prose.clear()
            return list(inline_segments(value))
        return []

    for index, line in enumerate(lines):
        protected = False
        setext_heading = (bool(line.strip()) and index + 1 < len(lines)
                          and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[index + 1]))
        if frontmatter:
            protected = True
            if index and line.strip() == '---':
                frontmatter = False
        elif fence:
            protected = True
            if re.match(r'^\s*(?:>\s*)?' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*$', line):
                fence = None
        elif html_block:
            protected = True
            if html_block in line.lower():
                html_block = None
        else:
            opening = re.match(r'^\s*(?:>\s*)?(`{3,}|~{3,})', line)
            html = re.match(r'^\s*<(script|style|pre|code|a)\b', line, re.I)
            if opening:
                fence = (opening[1][0], len(opening[1]))
                protected = True
            elif html:
                closing = f'</{html[1].lower()}>'
                html_block = None if closing in line.lower() else closing
                protected = True
            elif setext_heading or re.match(r'^(?: {4}|\t)|^\s*(?:>\s*)?#{1,6}\s|^\s*\[[^\]]+\]:|^\s*(?:=+|-+)\s*$', line):
                protected = True
        if protected:
            yield from flush()
            yield True, line
        else:
            prose.append(line)
    yield from flush()


def source_pages():
    # Reader-facing pages plus the repository entry point. Authoring manuals,
    # changelog and templates are outside the prose linking scope.
    candidates = [ROOT / 'README.md', *(DOCS / 'knowledge').rglob('*.md'),
                  DOCS / 'index.md', DOCS / 'problems.md', *(DOCS / 'paths').rglob('*.md')]
    return sorted(p for p in candidates if p.is_file())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='report prose still requiring links')
    args = parser.parse_args()
    linker = GlossaryLinker(load_json('terms.json'))
    changed = []
    for path in source_pages():
        original = path.read_text(encoding='utf-8')
        if original.startswith('<!-- GENERATED:'):
            continue
        content = linker.link(original, path)
        if content != original:
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                if content.startswith('---\n'):
                    content = re.sub(r'^updated: "\d{4}-\d{2}-\d{2}"$',
                                     f'updated: "{date.today().isoformat()}"',
                                     content, count=1, flags=re.M)
                path.write_text(content, encoding='utf-8')
    if args.check and changed:
        print('Missing glossary links:\n' + '\n'.join(changed), file=sys.stderr)
        return 1
    print('Glossary prose links are current.' if args.check else f'Linked glossary terms in {len(changed)} pages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

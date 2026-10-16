"""Regenerate the map, glossary, domain pages and article catalog."""
from pathlib import Path
import argparse
import os
import sys
from common import ROOT, DOCS, load_json, articles

KINDS = {'concept': '概念', 'comparison': '对比', 'pattern': '模式',
         'case': '案例', 'lab': '实验', 'decision': '决策'}


def link_from(destination, source):
    return Path(os.path.relpath(source, destination.parent)).as_posix()


def render():
    domains = load_json('domains.json')
    terms = load_json('terms.json')
    pages = articles()
    by_path = {p.relative_to(ROOT).as_posix(): (p, m) for p, m, _ in pages}
    output = {}
    generated_note = '<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->\n\n'
    target = DOCS / 'map.md'
    lines = ['# 工程知识地图', '', 'P0：核心；P1：应理解并应用；P2：按方向深入。以上为默认学习建议，可按岗位、已有基础和当前任务调整。', '',
             '这份领域清单用于知识索引。建议从[实际工程问题](problems.md)进入，定位关联概念，再理解机制、边界与取舍，以原理解释、实现或诊断证据记录进展。', '',
             '| 领域 | 优先级 | 学习目标 |', '| --- | --- | --- |']
    for d in domains:
        lines.append(f"| [{d['title']}](knowledge/{d['id']}/index.md) | {d['priority']} | {d['goal']} |")
    lines += ['', '[术语索引](glossary.md) · [文章目录](articles.md) · [问题导航](problems.md) · [学习路径](paths/index.md)']
    output[target] = generated_note + '\n'.join(lines) + '\n'

    target = DOCS / 'glossary.md'
    covered = sum(bool(t['articles']) for t in terms)
    lines = ['# 术语索引', '', f'当前有 {len(terms)} 组术语条目，覆盖 {len(domains)} 个领域；其中 {covered} 组已连接正文。每组可能包含多个相关缩写，不能当作独立概念数量。', '',
             '“已收录”表示已有索引简释；“有正文”表示可继续阅读深入文章。简释用于定位，不替代机制、边界和版本说明。P0/P1/P2 为默认学习建议，可按岗位、已有基础和当前任务调整。', '',
             '术语清单作为知识索引；[实际工程问题](problems.md)作为学习入口。阅读时结合具体约束理解概念，重点积累底层原理、系统设计、故障诊断和技术权衡能力。', '',
             ' · '.join(f"[{d['title']}](#{d['id']})" for d in domains), '']
    for d in domains:
        lines += [f'<a id="{d["id"]}"></a>', '', f'## {d["title"]}', '', '| ID / 术语 | 简释 | 优先级 | 覆盖 |', '| --- | --- | --- | --- |']
        for t in [x for x in terms if x['domain'] == d['id']]:
            refs = []
            for p in t['articles']:
                path, meta = by_path[p]
                refs.append(f"[{KINDS[meta['kind']]}]({link_from(target, path)})")
            coverage = '有正文：' + '、'.join(refs) if refs else '已收录'
            lines.append(f"| `{t['id']}`<br>{t['name']} | {t['definition']} | {t['priority']} | {coverage} |")
        lines.append('')
    output[target] = generated_note + '\n'.join(lines).rstrip() + '\n'

    target = DOCS / 'articles.md'
    lines = ['# 深入文章目录', '', f'共 {len(pages)} 篇正文。领域索引页和术语简释不计入正文数量。', '',
             '| 文章 | 类型 | 状态 | 核查方式 | 更新日期 |', '| --- | --- | --- | --- | --- |']
    for path, m, _ in pages:
        lines.append(f"| [{m['title']}]({link_from(target,path)}) | {KINDS[m['kind']]} | {m['status']} | {m['verification']} | {m['updated']} |")
    lines += ['', '`source-checked`：核查来源机制；`tested`：随附实验已执行；`design-proposal`：设计提案或教学推演。详情与局限以正文为准。']
    output[target] = generated_note + '\n'.join(lines) + '\n'

    for d in domains:
        target = DOCS / 'knowledge' / d['id'] / 'index.md'
        selected = [(p,m) for p,m,_ in pages if m['domain'] == d['id']]
        lines = [f'# {d["title"]}', '', f'建议优先级：{d["priority"]}。目标：{d["goal"]}', '',
                 '下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。', '',
                 '## 一个核心问题', '', d['question'], '', '## 已有正文', '']
        if selected:
            for path,m in selected:
                lines.append(f"- [{m['title']}]({link_from(target,path)})：{m['summary']}")
        else:
            lines.append('当前已有术语简释，深入文章尚待积累。下列条目构成研究范围。')
        lines += ['', '## 术语范围', '', '| 术语 | 简释 |', '| --- | --- |']
        for t in [x for x in terms if x['domain'] == d['id']]:
            lines.append(f"| {t['name']} | {t['definition']} |")
        lines += ['', '## 练习与验收', '', '选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。', '',
                  '[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)']
        output[target] = generated_note + '\n'.join(lines) + '\n'
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='fail if generated pages differ')
    args = parser.parse_args()
    mismatches = []
    for path, content in render().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                mismatches.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if mismatches:
        print('Stale generated pages:\n'+'\n'.join(mismatches), file=sys.stderr)
        return 1
    print('Generated indexes are current.' if args.check else 'Generated 20 navigation/index pages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Repository helpers: flat YAML with JSON values, no third-party dependencies."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def load_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def read_article(path):
    text = path.read_text(encoding='utf-8')
    parts = text.split('---\n', 2)
    if len(parts) != 3 or parts[0] != '':
        raise ValueError(f'{path.relative_to(ROOT)}: missing frontmatter')
    meta = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        key, separator, raw = line.partition(':')
        if not separator or key in meta:
            raise ValueError(f'{path.relative_to(ROOT)}: invalid/duplicate field {key!r}')
        meta[key] = json.loads(raw.strip())
    return meta, parts[2].lstrip()


def articles():
    result = []
    for path in sorted((DOCS / 'knowledge').glob('*/*.md')):
        if path.name == 'index.md':
            continue
        meta, body = read_article(path)
        result.append((path, meta, body))
    return result

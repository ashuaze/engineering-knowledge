"""Local transaction experiment, not a payment service or production HTTP API."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import platform
import re
import sqlite3


class Conflict(Exception):
    pass


class ReplyLost(Exception):
    pass


def initialize(db):
    conn=sqlite3.connect(str(db),isolation_level=None)
    try:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.executescript('''
        CREATE TABLE orders (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          scope TEXT NOT NULL,
          item TEXT NOT NULL,
          amount_minor INTEGER NOT NULL CHECK (amount_minor > 0)
        );
        CREATE TABLE idempotency (
          scope TEXT NOT NULL,
          key TEXT NOT NULL,
          fingerprint TEXT NOT NULL,
          response TEXT NOT NULL,
          PRIMARY KEY (scope, key)
        );
        ''')
    finally:
        conn.close()


def normalized_payload(payload):
    if not isinstance(payload,dict) or set(payload)!={'item','amount_minor'}:
        raise ValueError('Only item and amount_minor are supported')
    if not isinstance(payload['item'],str) or not payload['item'].strip() or len(payload['item'])>120:
        raise ValueError('item must be a non-empty string of at most 120 characters')
    amount=payload['amount_minor']
    if type(amount) is not int or not 0<amount<=1_000_000_000:
        raise ValueError('amount_minor must be a bounded positive integer')
    return dict(item=payload['item'].strip(),amount_minor=amount)


def submit(db,scope,key,payload,*,fail_after_insert=False,lose_reply=False):
    # Real HTTP adapters derive scope from authenticated identity and operation.
    if not isinstance(scope,str) or not scope or len(scope)>200:
        raise ValueError('invalid scope')
    if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,120}',key):
        raise ValueError('invalid key')
    data=normalized_payload(payload)
    canonical=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    digest=hashlib.sha256(canonical.encode()).hexdigest()
    conn=sqlite3.connect(str(db),timeout=5,isolation_level=None)
    try:
        # Entire SQLite writer is serialized, not just one idempotency key.
        conn.execute('BEGIN IMMEDIATE')
        existing=conn.execute('SELECT fingerprint,response FROM idempotency WHERE scope=? AND key=?',(scope,key)).fetchone()
        if existing:
            if existing[0]!=digest:
                raise Conflict('same scoped key with different business input')
            result=json.loads(existing[1])
        else:
            cursor=conn.execute('INSERT INTO orders(scope,item,amount_minor) VALUES (?,?,?)',(scope,data['item'],data['amount_minor']))
            if fail_after_insert:
                raise RuntimeError('injected exception before transaction commit')
            result=dict(order_id=cursor.lastrowid,**data)
            conn.execute('INSERT INTO idempotency(scope,key,fingerprint,response) VALUES (?,?,?,?)',
                         (scope,key,digest,json.dumps(result,ensure_ascii=False,sort_keys=True)))
        conn.execute('COMMIT')
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()
    if lose_reply:
        raise ReplyLost('commit succeeded; simulated response loss')
    return result


def counts(db):
    conn=sqlite3.connect(str(db))
    try:
        return tuple(conn.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in ('orders','idempotency'))
    finally:
        conn.close()


def main():
    print(f'Python {platform.python_version()}, SQLite {sqlite3.sqlite_version}')
    with TemporaryDirectory() as temp:
        db=Path(temp)/'lab.sqlite'; initialize(db)
        payload={'item':'book','amount_minor':2500}
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda _:submit(db,'demo:POST:/orders','demo-key-0001',payload),range(8)))
        assert len({r['order_id'] for r in results})==1 and counts(db)==(1,1)
        print('8 concurrent attempts ->',counts(db)[0],'order; same response:',all(r==results[0] for r in results))
        try:
            submit(db,'demo:POST:/orders','demo-key-0002',payload,lose_reply=True)
        except ReplyLost:
            pass
        recovered=submit(db,'demo:POST:/orders','demo-key-0002',payload)
        print('Recovered committed result after simulated reply loss:',recovered)
        assert counts(db)==(2,2)


if __name__=='__main__':
    main()

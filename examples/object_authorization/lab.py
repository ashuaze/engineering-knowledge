"""Local authorization fixtures. No login, JWT verification or HTTP service."""
from dataclasses import dataclass
import sqlite3


class Denied(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    # In a real adapter this must be created from verified server-side identity.
    user_id: str


def initialize():
    conn = sqlite3.connect(':memory:')
    conn.executescript('''
        CREATE TABLE memberships (
          user_id TEXT NOT NULL,
          tenant_id TEXT NOT NULL,
          role TEXT NOT NULL CHECK (role IN ('reader', 'editor')),
          active INTEGER NOT NULL CHECK (active IN (0, 1)),
          PRIMARY KEY (user_id, tenant_id)
        );
        CREATE TABLE documents (
          id INTEGER PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          owner_id TEXT NOT NULL,
          title TEXT NOT NULL
        );
        INSERT INTO memberships VALUES ('alice', 'tenant-a', 'editor', 1);
        INSERT INTO memberships VALUES ('bob', 'tenant-a', 'reader', 1);
        INSERT INTO documents VALUES (1, 'tenant-a', 'alice', 'Alice report');
        INSERT INTO documents VALUES (2, 'tenant-a', 'bob', 'Bob report');
        INSERT INTO documents VALUES (3, 'tenant-b', 'alice', 'Other tenant');
    ''')
    return conn


def _identity(principal):
    if principal is None or not principal.user_id:
        raise Denied('not authorized')
    return principal.user_id


def list_documents(conn, principal, selected_tenant):
    user_id = _identity(principal)
    # Scope is constrained before fetching results, not after pagination.
    return conn.execute('''
        SELECT d.id, d.title FROM documents d
        JOIN memberships m ON m.tenant_id = d.tenant_id AND m.user_id = ?
        WHERE m.active = 1 AND d.owner_id = ? AND d.tenant_id = ?
        ORDER BY d.id
    ''', (user_id, user_id, selected_tenant)).fetchall()


def read_document(conn, principal, selected_tenant, document_id):
    user_id = _identity(principal)
    row = conn.execute('''
        SELECT d.id, d.title FROM documents d
        JOIN memberships m ON m.tenant_id = d.tenant_id AND m.user_id = ?
        WHERE m.active = 1 AND d.owner_id = ?
          AND d.tenant_id = ? AND d.id = ?
    ''', (user_id, user_id, selected_tenant, document_id)).fetchone()
    if row is None:
        raise Denied('not authorized')
    return row


def rename_document(conn, principal, selected_tenant, document_id, title):
    user_id = _identity(principal)
    if not isinstance(title, str) or not title.strip() or len(title) > 120:
        raise ValueError('invalid title')
    cursor = conn.execute('''
        UPDATE documents SET title = ?
        WHERE id = ? AND tenant_id = ? AND owner_id = ?
          AND EXISTS (
            SELECT 1 FROM memberships m
            WHERE m.user_id = ? AND m.tenant_id = documents.tenant_id
              AND m.active = 1 AND m.role = 'editor'
          )
    ''', (title.strip(), document_id, selected_tenant, user_id, user_id))
    if cursor.rowcount != 1:
        raise Denied('not authorized')
    conn.commit()


def main():
    conn = initialize()
    try:
        alice = Principal('alice')
        print('authorized list:', list_documents(conn, alice, 'tenant-a'))
        for tenant, document_id in [('tenant-a', 2), ('tenant-b', 3)]:
            try:
                read_document(conn, alice, tenant, document_id)
            except Denied:
                print('denied:', tenant, document_id)
        conn.execute("UPDATE memberships SET active = 0 WHERE user_id = 'alice'")
        conn.commit()
        try:
            read_document(conn, alice, 'tenant-a', 1)
        except Denied:
            print('denied after membership revocation')
    finally:
        conn.close()


if __name__ == '__main__':
    main()

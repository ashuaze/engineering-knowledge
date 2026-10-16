import unittest
from lab import Denied, Principal, initialize, list_documents, read_document, rename_document


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.conn = initialize()
        self.addCleanup(self.conn.close)
        self.alice = Principal('alice')
        self.bob = Principal('bob')

    def test_owner_in_active_tenant_can_read(self):
        self.assertEqual(read_document(self.conn, self.alice, 'tenant-a', 1),
                         (1, 'Alice report'))

    def test_same_tenant_does_not_grant_another_owners_object(self):
        with self.assertRaises(Denied):
            read_document(self.conn, self.alice, 'tenant-a', 2)

    def test_owner_name_without_tenant_membership_is_insufficient(self):
        with self.assertRaises(Denied):
            read_document(self.conn, self.alice, 'tenant-b', 3)

    def test_list_query_applies_same_scope(self):
        self.assertEqual(list_documents(self.conn, self.alice, 'tenant-a'),
                         [(1, 'Alice report')])
        self.assertEqual(list_documents(self.conn, self.alice, 'tenant-b'), [])

    def test_revocation_is_checked_on_next_request(self):
        read_document(self.conn, self.alice, 'tenant-a', 1)
        self.conn.execute("UPDATE memberships SET active = 0 WHERE user_id = 'alice'")
        self.conn.commit()
        with self.assertRaises(Denied):
            read_document(self.conn, self.alice, 'tenant-a', 1)
        with self.assertRaises(Denied):
            rename_document(self.conn, self.alice, 'tenant-a', 1, 'new title')

    def test_reader_can_read_but_cannot_edit_own_object(self):
        self.assertEqual(read_document(self.conn, self.bob, 'tenant-a', 2)[0], 2)
        with self.assertRaises(Denied):
            rename_document(self.conn, self.bob, 'tenant-a', 2, 'changed')
        self.assertEqual(read_document(self.conn, self.bob, 'tenant-a', 2)[1],
                         'Bob report')

    def test_anonymous_principal_is_denied(self):
        with self.assertRaises(Denied):
            read_document(self.conn, None, 'tenant-a', 1)
        with self.assertRaises(Denied):
            list_documents(self.conn, None, 'tenant-a')

    def test_denied_write_has_no_business_effect(self):
        with self.assertRaises(Denied):
            rename_document(self.conn, self.alice, 'tenant-a', 2, 'stolen')
        self.assertEqual(self.conn.execute('SELECT title FROM documents WHERE id=2')
                         .fetchone()[0], 'Bob report')

    def test_authorized_editor_can_update_owned_object(self):
        rename_document(self.conn, self.alice, 'tenant-a', 1, 'Revised report')
        self.assertEqual(read_document(self.conn, self.alice, 'tenant-a', 1),
                         (1, 'Revised report'))

    def test_missing_object_has_same_denial_class(self):
        with self.assertRaises(Denied):
            read_document(self.conn, self.alice, 'tenant-a', 999)


if __name__ == '__main__':
    unittest.main()

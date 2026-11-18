import os
import sqlite3
import tempfile
import unittest

import app as app_module


class AppInitDbTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_attendance_system.db")
        app_module.DB_NAME = self.db_path

    def tearDown(self):
        app_module.DB_NAME = "attendance_system.db"
        self.temp_dir.cleanup()

    def test_init_db_creates_default_admin_user(self):
        app_module.init_db()

        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            user = conn.execute(
                "SELECT username, password FROM users WHERE username = ?",
                ("admin",),
            ).fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "admin")
        self.assertEqual(user["password"], "admin123")


if __name__ == "__main__":
    unittest.main()

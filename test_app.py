import unittest
import json
import sqlite3
from app import app, conn, cursor
from werkzeug.security import generate_password_hash

class UserApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.db = conn
        self.cursor = cursor

        # Ensure users table exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Clean up before each test
        self.cursor.execute("DELETE FROM users")
        self.db.commit()

        # Insert a test user
        self.cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                            ("Test User", "test@example.com", generate_password_hash("test123")))
        self.db.commit()

        self.test_user_id = self.cursor.execute("SELECT id FROM users WHERE email = 'test@example.com'").fetchone()[0]

    def test_home(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn("User Management System", res.get_data(as_text=True))

    def test_get_all_users(self):
        res = self.client.get('/users')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(isinstance(data, list))
        self.assertGreaterEqual(len(data), 1)

    def test_get_user_success(self):
        res = self.client.get(f'/user/{self.test_user_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn("email", res.get_json())

    def test_get_user_not_found(self):
        res = self.client.get('/user/9999')
        self.assertEqual(res.status_code, 404)

    def test_create_user_success(self):
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "alicepass"
        }
        res = self.client.post('/users', data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_create_user_duplicate(self):
        payload = {
            "name": "Duplicate",
            "email": "test@example.com",
            "password": "pass123"
        }
        res = self.client.post('/users', data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_create_user_invalid_input(self):
        res = self.client.post('/users', data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_update_user_success(self):
        payload = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        res = self.client.put(f'/user/{self.test_user_id}', data=json.dumps(payload),
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_update_user_invalid_input(self):
        res = self.client.put(f'/user/{self.test_user_id}', data=json.dumps({}),
                              content_type='application/json')
        self.assertEqual(res.status_code, 400)


    def test_delete_user_not_found(self):
        res = self.client.delete('/user/9999')
        self.assertEqual(res.status_code, 404)

    def test_search_user_found(self):
        res = self.client.get('/search?name=Test')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.get_json(), list))

    def test_search_user_missing_param(self):
        res = self.client.get('/search')
        self.assertEqual(res.status_code, 400)

    def test_login_success(self):
        payload = {
            "email": "test@example.com",
            "password": "test123"
        }
        res = self.client.post('/login', data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertIn("status", res.get_json())

    def test_login_failure(self):
        payload = {
            "email": "test@example.com",
            "password": "wrongpass"
        }
        res = self.client.post('/login', data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 401)

if __name__ == '__main__':
    unittest.main()

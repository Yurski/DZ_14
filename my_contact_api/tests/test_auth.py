import unittest
from app.security import get_password_hash, verify_password

class TestAuth(unittest.TestCase):

    def test_get_password_hash(self):
        password = "test_password"
        hashed = get_password_hash(password)
        self.assertTrue(verify_password(password, hashed))

if __name__ == "__main__":
    unittest.main()

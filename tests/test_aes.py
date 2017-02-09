import unittest
from nefit import NefitClient


class AesTest(unittest.TestCase):
    client = None

    def setUp(self):
        self.client = NefitClient(123456789, "abc1abc2abc3abc4", "passworddddd")

    def test_crypt(self):
        text = "super_secret"
        text_encrypted = self.client.encrypt(text)
        text_decrypted = self.client.decrypt(text_encrypted)
        self.assertEqual(text, text_decrypted)


if __name__ == '__main__':
    unittest.main()

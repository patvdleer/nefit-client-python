import unittest
from nefit import NefitClient


class AesTest(unittest.TestCase):
    client = None

    def setUp(self):
        self.client = NefitClient(123456789, "abc1abc2abc3abc4", "passworddddd")


if __name__ == '__main__':
    unittest.main()

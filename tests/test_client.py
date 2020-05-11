import os
import unittest
from nefit import NefitClient, NefitResponseException


class ClientTest(unittest.TestCase):
    def test_exceptions(self):
        client = NefitClient(
            os.environ.get("NEFIT_SERIAL", 123456789),
            os.environ.get("NEFIT_ACCESS_KEY", "abc1abc2abc3abc4"),
            "asddasadsasdcx"
        )
        client.connect()
        with self.assertRaises(NefitResponseException):
            client.get_display_code()
        client.disconnect()


if __name__ == '__main__':
    unittest.main()

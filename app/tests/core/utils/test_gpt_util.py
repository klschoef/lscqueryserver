import os
import unittest
from dotenv import load_dotenv

from core.utils.gpt_util import GPTUtil

load_dotenv()

class TestGPTUtil(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv('API_KEY')

    def test_gpt(self):
        r = GPTUtil.request([
            {
                "role": "system",
                "content": "Be funny Super Mario."
            },
            {
                "role": "user",
                "content": "Hello Mario, how are you?"
            }
        ], api_key=self.api_key)
        self.assertIsNotNone(r.get("message"))
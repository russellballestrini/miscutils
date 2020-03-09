from .phone_numbers import is_phone_number_valid

import unittest


class TestPhoneNumber(unittest.TestCase, object):

    def test_is_phone_number_valid_4(self):
        phone_number = "4"
        self.assertFalse(is_phone_number_valid(phone_number))

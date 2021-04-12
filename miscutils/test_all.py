from .phone_numbers import is_phone_number_valid

from . import dollars_to_cents, cents_to_dollars

import unittest


class TestPhoneNumber(unittest.TestCase, object):
    def test_is_phone_number_valid_4(self):
        phone_number = "4"
        self.assertFalse(is_phone_number_valid(phone_number))


class TestDollarCentConversions(unittest.TestCase, object):
    def test_dollars_to_cents(self):
        self.assertEqual(342, dollars_to_cents(3.42))
        self.assertEqual(342, dollars_to_cents("3.42"))

    def test_cents_to_dollars(self):
        self.assertEqual(3.42, cents_to_dollars(342))
        self.assertEqual(3.42, cents_to_dollars("342"))

from unittest import TestCase
from utils.validate import check_phone

class TetCheckPhone(TestCase):
    def test_phone_not_digit(self):
        phone = "0913abc2244"
        success , message = check_phone(phone)
        self.assertEqual(success, False)
        self.assertEqual(message, "phone must be a number")

    def test_phone_not_equal_length(self):
        phone = "0913"
        success , message = check_phone(phone)
        self.assertEqual(success, False)
        self.assertEqual(message, "phone is not valid")

    def test_phone_strat_without_zero_nine(self):
        phone = "12345678900"
        success , message = check_phone(phone)
        self.assertEqual(success, False)
        self.assertEqual(message, "phone must start with <09>")

    def test_correct_phone(self):
        phone = "09135558811"
        success , message = check_phone(phone)
        self.assertEqual(success, True)
        self.assertEqual(message, "")
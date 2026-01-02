from unittest.mock import Mock, MagicMock
import unittest
from core.manage_code import CodeManager, CodeMangerException
import datetime


class CodeMangerTest(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.session = MagicMock()
        self.request.session.save = Mock()
        self.key = '09123456789'

        self.data = {
            "request": self.request,
            "key": self.key,
            "expire_time": 10,
            "number": 10,
        }
        self.code_manager = CodeManager(**self.data)

    def test_exceptions(self):
        list_exceptions = [
            ("number", 0),
            ("expire_time", -1),
            ("expire_time", "abc"),
            ("number", "abc"),
        ]

        for exception in list_exceptions:
            dict_exceptions = dict()
            dict_exceptions[exception[0]] = exception[1]

            with self.assertRaises(CodeMangerException):
                CodeManager(request=self.request, key=self.key, **dict_exceptions)

    def test_generate_code(self):
        now = datetime.datetime.now()
        code = self.code_manager.generate_code()

        # Save method must be called
        self.request.session.save.assert_called()

        self.assertEqual(len(code), self.data["number"])
        time = datetime.datetime.strptime(self.code_manager.get_expire_code_time, "%Y-%m-%d %H:%M:%S")

        self.assertTrue(time > now)

        self.assertTrue(self.request.session[self.key].get("code"))
        self.assertTrue(self.request.session[self.key].get("expire_time"))

    def test_load_code_success(self):
        code_before = self.code_manager.generate_code()
        expire_time_before = self.code_manager.get_expire_code_time

        # mock get method
        self.request.session.get = MagicMock(return_value={"code": code_before, "expire_time": expire_time_before})

        self.code_manager = CodeManager(**self.data)
        self.assertTrue(self.code_manager.load_code())

        code_after = self.code_manager.get_code
        expire_time_after = self.code_manager.get_expire_code_time

        self.assertEqual(code_before, code_after)
        self.assertEqual(expire_time_before, expire_time_after)

    def test_load_code_fail(self):
        # mock get method
        self.request.session.get = MagicMock(return_value={})

        self.assertFalse(self.code_manager.load_code())

    def test_invalid_save_in_session(self):
        with self.assertRaises(CodeMangerException):
            self.code_manager.save_in_session()

    def test_valid_save_in_session(self):
        self.code_manager.generate_code()
        self.assertEqual(self.request.session.save.call_count, 1)

        self.assertTrue(self.code_manager.save_in_session())
        self.assertEqual(self.request.session.save.call_count,2)

        self.code_manager = CodeManager(**self.data)
        self.code_manager.load_code()
        self.assertTrue(self.code_manager.save_in_session())
        self.assertEqual(self.request.session.save.call_count, 3)

    def test_check_expire_code_method_with_bad_key(self):
        # mock
        self.request.session.get = MagicMock(return_value=None)
        with self.assertRaises(KeyError):
            self.code_manager._check_expire_code()

    def test_expired_code(self):
        code = self.code_manager.generate_code()

        time = datetime.datetime.strptime(self.code_manager.get_expire_code_time, "%Y-%m-%d %H:%M:%S")
        expire_time = time - datetime.timedelta(minutes=self.data.get('expire_time'))
        expire_time = datetime.datetime.strftime(expire_time, "%Y-%m-%d %H:%M:%S")

        self.request.session.get = MagicMock(return_value={
            "code": code,
            "expire_time": expire_time,
        })
        self.assertFalse(self.code_manager._check_expire_code())

    def test_correct_expire_time(self):
        code = self.code_manager.generate_code()
        self.request.session.get = MagicMock(return_value={
            "code": code,
            "expire_time": self.code_manager.get_expire_code_time
        })
        self.assertTrue(self.code_manager._check_expire_code())

    def test_incorrect_code(self):
        code = self.code_manager.generate_code()
        self.request.session.get = MagicMock(return_value={
            "code": code,
            "expire_time": self.code_manager.get_expire_code_time
        })
        self.assertFalse(self.code_manager.check_code("abb"))

    def test_correct_code(self):
        code = self.code_manager.generate_code()
        self.request.session.get = MagicMock(return_value={
            "code": code,
            "expire_time": self.code_manager.get_expire_code_time
        })
        self.assertTrue(self.code_manager.check_code(code))

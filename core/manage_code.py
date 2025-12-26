import random
import datetime


class CodeManager:
    def __init__(self, request, key, number=6, expire_time=2):
        # initialize
        self.number = number
        self.expire_time = expire_time
        self.request = request
        self.key = key
        self._code = None
        self._expire = None

    def generate_code(self):
        self._code = "".join(random.choices("0987654321", k=self.number))
        self._expire = ((datetime.datetime.now() + datetime.timedelta(minutes=self.expire_time)).
                        strftime("%Y-%m-%d %H:%M:%S"))

        self.save_in_session()
        return self._code

    def load_code(self):
        data = self.request.session[self.key]

        self._code = data["code"]
        self._expire = data["expire_time"]


    def save_in_session(self):
        data = {
            "code": self._code,
            "expire_time": self._expire
        }
        self.request.session[self.key] = data

        self._save_session()

    def _check_expire_code(self):
        data = self.request.session.get(self.key)
        if data:
            expire_time = data.get("expire_time")
            expire_time = datetime.datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
            if expire_time > datetime.datetime.now():
                return True
            else:
                return False
        else:
            raise KeyError(f"key {self.key} not found!")

    def check_code(self,code):
        if self._check_expire_code():
            if code == self._code:
                return True
        return False


    def _save_session(self):
        self.request.session.save()
        return True

    @property
    def get_code(self):
        return self._code

    @property
    def get_expire_time(self):
        return self._expire

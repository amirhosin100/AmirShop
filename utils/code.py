import random


def create_code():
    return ''.join(random.choices('1234567890', k=6))

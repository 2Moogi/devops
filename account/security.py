import string
import random


def create_email_code():
    LENGTH = 6

    result = ""
    for i in range(LENGTH):
        result += random.choice(string.digits)
    return result

import random
import string


def generatePassword(length):
    password = ""
    characters = string.ascii_letters + string.digits + string.punctuation
    for i in range(length):
        password += random.choice(characters)
    return password

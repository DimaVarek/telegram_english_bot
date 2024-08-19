from random import randint


def random_name():
    name = "".join([str(randint(0, 9)) for i in range(8)]) + ".mp3"
    return name

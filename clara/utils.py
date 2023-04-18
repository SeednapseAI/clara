from .console import console
from .consts import DEBUG


def console_log(*args):
    if DEBUG:
        console.log(*args)


def null_log(*args):
    pass


log = console_log if DEBUG else null_log

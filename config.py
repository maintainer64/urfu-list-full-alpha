from datetime import datetime

IS_DEBUG = True


def log(*args):
    print(f"[{datetime.now()}]", *args)

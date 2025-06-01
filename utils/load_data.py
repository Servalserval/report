import json
from filelock import FileLock

def load_data(lockfile, lock = False):
    if not lock:
        f = open(lockfile, "r")
        data = json.load(f)
        f.close()
    else:
        lock = FileLock(lockfile + ".lock")
        with lock:
            f = open(lockfile, "r")
            data = json.load(f)
            f.close()
    return data
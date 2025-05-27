from filelock import FileLock
import json

def output_data(data, lockfile):
    lock = FileLock(lockfile + ".lock")
    with lock:
        f = open(lockfile, "w")
        json.dump(data, f, indent = 4)
        f.close()
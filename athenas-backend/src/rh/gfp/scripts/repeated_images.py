# -*- coding: utf-8 -*-

import fnmatch
import hashlib
import os


def hashing_file(path):
    hasher = hashlib.md5()
    with open(path, "rb") as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        files.sort()
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def repeated_files(source=".", target="."):
    repeateds_source = {}
    repeateds_target = {}
    ordered = []
    print("WAITING PROCCESS FILES...")
    for filename in find_files(source, "*.png"):
        filename = "./%s" % os.path.relpath(filename)
        hash_file = hashing_file(filename)
        if hash_file not in ordered:
            ordered.append(hash_file)
            repeateds_source[hash_file] = [filename]
        else:
            repeateds_source[hash_file].append(filename)

    if source != target:
        for filename in find_files(target, "*.png"):
            filename = "./%s" % os.path.relpath(filename)
            hash_file = hashing_file(filename)
            if hash_file in ordered and filename not in repeateds_source[hash_file]:
                if hash_file not in repeateds_target:
                    repeateds_target[hash_file] = [filename]
                else:
                    repeateds_target[hash_file].append(filename)

    print("PROCCESS SUCCESSFULLY...")

    for i in ordered:
        if len(repeateds_source[i]) > 1 or i in repeateds_target:
            print(
                "%s >> %s"
                % (
                    repeateds_source[i],
                    repeateds_target[i] if i in repeateds_target else "",
                )
            )

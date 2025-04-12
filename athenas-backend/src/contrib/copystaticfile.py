import os
import rest_framework
import shutil


def collect_static():
    static_dir = "/app/var/www/static"

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    root = os.path.dirname(rest_framework.__file__) + "/static"
    for name in [
        pathname for pathname in os.listdir(root) if pathname not in ["build"]
    ]:
        path = os.path.join(root, name)

        dst = os.path.join(static_dir, name)
        if os.path.isdir(dst):
            shutil.rmtree(dst)

        print("copy %s -> %s " % (path, dst))
        if os.path.isdir(path):
            shutil.copytree(path, dst)
        else:
            shutil.copy2(path, dst)


def main():
    collect_static()


if __name__ == "__main__":
    main()

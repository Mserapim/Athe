#!/usr/bin/python3 -u

import base64
import glob
import hashlib
import json
import multiprocessing as mp
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import zlib
from time import time

ENV_PY_VERSION = os.environ.get("ENV_PY_VERSION", "3.9")
ENV_NAME = "env-%s" % ENV_PY_VERSION

APP_HOME = "/app"
APP_ETC = os.path.join(APP_HOME, "etc")
APP_VAR = os.path.join(APP_HOME, "var")
APP_ENV = os.path.join(APP_HOME, ENV_NAME)
APP_DEFAULT_ENV = os.path.join(APP_HOME, "env")
APP_BIN = os.path.join(APP_ENV, "bin")
APP_ROOT = os.path.join(APP_HOME, "root")
APP_USER_ID = os.environ.get("APP_USER_ID", "1000")
APP_GROUP_ID = os.environ.get("APP_GROUP_ID", "1000")

DCVS_DRIVER = os.environ.get("DCVS_DRIVER", "git")
DCVS_HOST = os.environ.get("DCVS_HOST", "gitlab.mpto.mp.br")
DCVS_USER = os.environ.get("DCVS_USER", "mpto")
DCVS_PORT = os.environ.get("DCVS_PORT", "3022")
DCVS_BRANCH = os.environ.get("DCVS_BRANCH", "master")

RELOAD_ON = "0" if os.environ.get("RELOAD") == "0" else "1"

PTVSD_ON = os.environ.get("PTVSD_ON", "off")
PTVSD_TIMEOUT = os.environ.get("PTVSD_TIMEOUT", "30")

celery_template = "".join(
    [
        "eNp9jzFrwzAUhHf9CkEHtaW2O5ZAB0fRYOzaQVaGthThyErixNUTTyql/75OQrIU",
        "+qbH3Xdwd0OT+4Qa6Ae3ndGvuEmejgohc9mUQuqVrOgzZZ/gttCvZ1l2+jJjR4s/",
        "+pERLiohX7UU7apSep7zUtSL/yOXTPGybKRqJ/iW0OmYARdxWKdoPWAM7OEs2x5M",
        "SD1CBAMjpLELhxR3Gu3GonXGXkDcnb1vwIMfu79GGEznOz/Jd9cWOediqTRvaiVq",
        "NZV5Z/sAjn1cCZW3pW6FLPKqeBPyOO5EkF8Ii17c",
    ]
)

location_template = "".join(
    [
        "eNqdkU0KwjAQRvc5RS5gR9Bdl649xJAMOtpkShJtoXh3I/GHCi20s8y8730DUY0Y",
        "TCxegyPLCOzwRFEPSufBhjFqwLaFOwboum5EQV2oWxL2lnotvlYPpX5OTGfyGCGm",
        "/GDgEoH6BNP2vN3sqn21XaM213xbkjDj/yJr9GLJcQizBYcMHQu0tOIjHQUmat6R",
        "P2H5myWeknhpni9wqs8=",
    ]
)

urls_template = "".join(
    [
        "eNpVj90KgzAMRu/7FIENolC6+4GXe41B1dR19I+2uj3+alGZucuXc0KiorcwvqWb",
        "vBi8U2KOJoG2wccMQeZM0SUO2g1mHolDGTN1dnLU/W7I0WrHWKF2F7pjTYPIGZS6",
        "wOMrbTCU7ltfhCbi84ocUIYgFk2fJF7eUkmctNRhbVp+Fnrjpxse9zW4BvUHbAtb",
        "4Q2tp/2zNRBJZ6rCyrfsB/JpV4g=",
    ]
)


def _git_make_dsn(project):
    params = {}
    params.update(vars())
    params.update(globals())

    return (
        "ssh://git@%(DCVS_HOST)s:%(DCVS_PORT)s/%(DCVS_USER)s/%(project)s.git" % params
    )


def _undef_make_dsn(project):
    return "undef"


def _hg_make_dsn(project):
    params = {}
    params.update(vars())
    params.update(globals())

    return "ssh://%(DCVS_USER)s@%(DCVS_HOST)s:%(DCVS_PORT)s/repo/%(project)s" % params


def dcvs_make_dsn(project):
    drivers = {"hg": _hg_make_dsn, "git": _git_make_dsn}

    return drivers.get(DCVS_DRIVER, _undef_make_dsn)(project)


def dcvs_clone(project, dest):
    drivers = {"hg": _hg_clone, "git": _git_clone}

    return drivers.get(DCVS_DRIVER, _undef_clone)(project, dest)


def _hg_clone(project, dest):
    translate = {"core": "athenas"}

    project = translate.get(project, project)

    if not os.path.exists(os.path.join(dest, ".hg")) and not os.path.exists(dest):
        print('cloning "%s"' % project)
        print(" ".join(["/usr/bin/hg", "clone", dcvs_make_dsn(project), dest]))
        subprocess.call(
            ["/usr/bin/hg", "clone", dcvs_make_dsn(project), "-r", DCVS_BRANCH, dest],
            shell=False,
        )
    elif not os.path.exists(os.path.join(dest, ".hg")) and os.path.exists(dest):
        if not os.path.exists(os.path.join(dest, ".hg", "hgrc")):
            with open(os.path.exists(os.path.join(dest, ".hg", "hgrc"), "wt")) as fd:
                fd.write(
                    "\n".join(["[paths]", "default = %s" % dcvs_make_dsn(project)])
                )
        subprocess.call(
            ["/usr/bin/hg", "pull", "-u", dcvs_make_dsn(project), "-r", DCVS_BRANCH],
            shell=False,
        )


def _undef_clone(project, dest):
    pass


def _git_clone(project, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)

    current_directory = os.getcwd()
    os.chdir(dest)

    if not os.path.isdir(os.path.join(dest, ".git")):
        subprocess.call(["/usr/bin/git", "init"], shell=False)
        subprocess.call(["/usr/bin/git", "checkout", "-b", DCVS_BRANCH], shell=False)

    subprocess.call(
        ["/usr/bin/git", "remote", "add", "origin", dcvs_make_dsn(project)], shell=False
    )
    subprocess.call(["/usr/bin/git", "pull", "origin", DCVS_BRANCH], shell=False)

    os.chdir(current_directory)


def compress(data):
    mdata = base64.b64encode(zlib.compress(data, 9))
    compressed = [str(mdata[i : i + 64]) for i in range(0, len(mdata), 64)]
    return compressed


def decompress(data):
    return zlib.decompress(base64.b64decode(data)).decode()


def cmd_not_found(name):
    print('command "%s" not found' % name)


def mkdir(path):
    if not os.path.isdir(os.path.dirname(path)):
        mkdir(os.path.dirname(path))
    os.mkdir(path)


def cmd_start():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    os.environ.update(PYTHONPATH="/app/root")

    cmd = [
        os.path.join(APP_BIN, "gunicorn"),
        "--bind",
        "0.0.0.0:3000",
        "--chdir",
        APP_ROOT,
        "--workers",
        os.environ.get("ATHENAS_WORKERS", "1"),
        "--threads",
        os.environ.get("ATHENAS_THREADS", str(os.cpu_count() - 1)),
        "--capture-output",
        "--access-logfile",
        "-",
        "--disable-redirect-access-to-syslog",
        "app.wsgi",
    ]

    if PTVSD_ON == "on":
        cmd.extend(["--timeout", PTVSD_TIMEOUT])

    if RELOAD_ON == "1":
        cmd.extend(["--reload", "--reload-engine=inotify"])
        extra_modules = glob.glob(
            os.path.join(APP_ROOT, "**/*[!__].py"), recursive=True
        )
        register_extra_mods = list()

        for mod in extra_modules:
            dir_mod = os.path.dirname(mod)
            sys_modules = [
                "".join(module.__path__)
                for module in sys.modules.values()
                if getattr(module, "__file__", None)
                and getattr(module, "__path__", None)
            ]
            if dir_mod not in sys_modules:
                register_extra_mods.extend(["--reload-extra-file", f"{mod}"])

        cmd += register_extra_mods

    subprocess.call(cmd, shell=False)


def cmd_celery():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    os.chdir(APP_ROOT)
    os.environ.update(HOME=APP_HOME)

    cmd = [
        os.path.join(APP_BIN, "celery"),
        "--config",
        "app.celeryconf",
        "worker",
        "-B",
        "-E",
        "-s",
        "/tmp/celery_heartbeat",
        "--loglevel",
        "INFO",
    ]

    if "CELERY_QUEUES" in os.environ:
        for queue in os.environ.get("CELERY_QUEUES", "").split(","):
            cmd.append("-Q")
            cmd.append(queue)

    subprocess.call(cmd, shell=False)


def cmd_daphne():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    os.chdir(APP_ROOT)
    os.environ.update(HOME=APP_HOME)

    if os.environ.get("DEV_MODE", "0") == "0":
        print("in production mode")
        __cmd_daphne_prod()
    else:
        print("in development mode")
        __cmd_daphne_dev()


def __cmd_daphne_dev():
    subprocess.call(
        [
            os.path.join(APP_BIN, "python"),
            "-u",
            os.path.join(APP_ROOT, "manage.py"),
            "runserver",
            "0.0.0.0:7000",
        ],
        shell=False,
    )


def __cmd_daphne_prod():
    subprocess.Popen(
        [
            os.path.join(APP_BIN, "python"),
            "-u",
            os.path.join(APP_ROOT, "manage.py"),
            "runworker",
            "-v",
            "2",
            "default",
        ],
        shell=False,
    )

    subprocess.call(
        [
            os.path.join(APP_BIN, "daphne"),
            "-b",
            "0.0.0.0",
            "-p",
            os.environ.get("ASGI_PORT", "7000"),
            "app.asgi.py3:application",
        ],
        shell=False,
    )


def cmd_flower():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    os.chdir(APP_ROOT)
    os.environ.update(HOME=APP_HOME)

    subprocess.call(
        [
            os.path.join(APP_BIN, "celery"),
            "--config",
            "app.celeryconf",
            "flower",
            "--port=8001",
            "--enable-events",
            "--inspect=true",
            "--inspect-timeout=3000 ",
            "--auto-refresh=true",
            "--log-to-stderr",
            "--logging=info",
        ],
        shell=False,
    )


def fix_path_owner(path, recursive=True):
    # owner = '.'.join([APP_USER_ID, APP_GROUP_ID])
    owner = ":".join([APP_USER_ID, APP_GROUP_ID])
    cmd = ["/bin/chown", owner, path]

    if recursive:
        cmd.append("-R")

    t1 = time()
    subprocess.call(cmd)
    t2 = time()
    print("[%0.3f ms]" % (t2 - t1))


def fix_user():
    cmd = ["groupadd", "-g", APP_GROUP_ID, "system"]

    print("fix user: %s " % " ".join(cmd))
    subprocess.call(cmd)

    cmd = [
        "useradd",
        "-u",
        APP_USER_ID,
        "-g",
        APP_GROUP_ID,
        "-d",
        APP_HOME,
        "-s",
        "/bin/bash",
        "system",
    ]

    print("fix user: %s " % " ".join(cmd))
    subprocess.call(cmd)


def cmd_shell():
    fix_user()
    fix_path_owner(APP_HOME, False)
    fix_path_owner(os.path.join(APP_HOME, ".cache"))

    # _configure_permissions()

    print("shell is started...")

    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    os.chdir(APP_ROOT)

    subprocess.call(
        " ".join(
            [
                "/bin/bash",
                "--rcfile",
                "/etc/profile",
                "--init-file",
                os.path.join(APP_BIN, "activate"),
            ]
        ),
        shell=True,
    )


def cmd_minifier(watch=True):
    print("minifier is started...")
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))
    os.chdir(APP_ROOT)
    os.environ.update(HOME=APP_HOME)

    build_path = os.path.join(APP_VAR, "www", "static", "build")

    if not os.path.exists(build_path):
        mkdir(build_path)

    cmd = [
        os.path.join(APP_BIN, "python3"),
        "-u",
        os.path.join(APP_ROOT, "manage.py"),
        "minify",
        "--uglify",
        "all",
        "--jsout",
        os.path.join(build_path, "%s.min.js"),
    ]

    if watch:
        cmd.append("--watch")

    return_code = subprocess.call(cmd, shell=False)
    if return_code != 0:
        sys.exit(return_code)


def _configure_permissions(force_simples=False):
    fix_path_owner(APP_HOME, False)

    if not os.path.isdir("/root/.cache"):
        os.mkdir("/root/.cache")

    fix_path_owner("/root/.cache", True)
    fix_path_owner(f"{APP_HOME}/var/www/", True)
    fix_path_owner(f"{APP_HOME}/var/log/", True)
    # fix_path_owner(f"{APP_HOME}/var/.cache/locks/", True)
    # fix_path_owner(f"{APP_HOME}/var/.cache/", True)

    if not force_simples:
        fix_path_owner(APP_ETC, True)


def cmd_configure(skip_install=True):
    for dirpath in [APP_VAR, APP_ETC]:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    os.chdir(APP_HOME)
    if not os.path.isdir(APP_ENV):
        print("create virtualenv now in (%s)..." % APP_ENV)
        subprocess.call(
            ["python%s" % ENV_PY_VERSION, "-m", "venv", ENV_NAME], shell=False
        ) == 0 or sys.exit(1)
        subprocess.call(
            [
                os.path.join(APP_BIN, "pip"),
                "install",
                "-U",
                "wheel",
                "setuptools-rust",
                "pip",
            ],
            shell=False,
        ) == 0 or sys.exit(1)
        skip_install = False

    subprocess.call(
        ["/bin/ln", "-sf", APP_ENV, APP_DEFAULT_ENV], shell=False
    ) == 0 or sys.exit(1)

    if not os.path.exists(os.path.join(APP_VAR, "storage")):
        mkdir(os.path.join(APP_VAR, "storage"))

    if not os.path.exists(os.path.join(APP_ROOT, "app")):
        mkdir(os.path.join(APP_ROOT, "app"))
        open(os.path.join(APP_ROOT, "app", "__init__.py"), "wt")

    if not os.path.isfile(os.path.join(APP_ROOT, "app", "urls.py")):
        print("create urls.py...")
        with open(os.path.join(APP_ROOT, "app", "urls.py"), "wt") as fd:
            fd.write(decompress(urls_template))

    if not os.path.isfile(os.path.join(APP_ETC, "upstream.json")):
        print("create upstream.json...")
        with open(os.path.join(APP_ETC, "upstream.json"), "wt") as fd:
            fd.write("[]")

    if not os.path.isfile(os.path.join(APP_ETC, "location.conf")):
        print("create location.conf...")
        with open(os.path.join(APP_ETC, "location.conf"), "wt") as fd:
            fd.write(decompress(location_template))

    _requirements_install(skip_install)
    # _configure_permissions()


def _requirements_install(skip_install):
    olderhashvalue = ""
    if os.path.exists(os.path.join(APP_ROOT, "requirements.md5")):
        with open(os.path.join(APP_ROOT, "requirements.md5"), "rt") as fd:
            olderhashvalue = fd.read()

    eng = hashlib.new("md5")
    hashvalue = ""
    with open(os.path.join(APP_ROOT, "requirements.txt"), "rb") as fd:
        for chunk in iter(lambda: fd.read(8192), b""):
            eng.update(chunk)

        hashvalue = eng.hexdigest()

    if not skip_install or olderhashvalue != hashvalue:
        subprocess.call(
            [
                os.path.join(APP_BIN, "pip"),
                "install",
                "-U",
                "-r",
                os.path.join(APP_ROOT, "requirements.txt"),
            ],
            shell=False,
        ) == 0 or sys.exit(1)

        with open(os.path.join(APP_ROOT, "requirements.md5"), "wt") as fd:
            fd.write(hashvalue)

    if os.path.exists(os.path.join(APP_ROOT, "requirements.dev")):
        subprocess.call(
            [
                os.path.join(APP_BIN, "pip"),
                "install",
                "-U",
                "-r",
                os.path.join(APP_ROOT, "requirements.dev"),
            ],
            shell=False,
        ) == 0 or sys.exit(1)


def unregister_signal(signum, frame):
    print("unregister")
    if signal.SIGTERM or True:
        data = json.load(open(os.path.join(APP_ETC, "upstream.json")))
        if platform.node() in data:
            data.pop(data.index(platform.node()))

            upstream = "\n".join(
                [
                    "upstream athenas {",
                    "\n".join(["    server %s:3000;" % host for host in data]),
                    "}",
                ]
            )

            with open(os.path.join(APP_ETC, "upstream.conf"), "wt") as fd:
                fd.write(upstream)

            with open(os.path.join(APP_ETC, "upstream.json"), "wt") as fd:
                json.dump(data, fd, indent=4)


def is_alive(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False


def cmd_register():
    try:
        data = json.load(open(os.path.join(APP_ETC, "upstream.json")))
    except Exception:
        data = []

    if not platform.node() in data:
        data.append(platform.node())

        with open(os.path.join(APP_ETC, "upstream.json"), "wt") as fd:
            json.dump(
                [hostname for hostname in data if is_alive(hostname)], fd, indent=4
            )

        signal.signal(signal.SIGINT, unregister_signal)
        signal.signal(signal.SIGTERM, unregister_signal)
    else:
        print("not need register")


def cmd_collect_static():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    static_dir = "/app/var/www/static"

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    root = "/app/root/static"
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

    root = "/app/root"
    for dirname in os.listdir(root):
        path = os.path.join(root, dirname, "static")

        if os.path.isdir(path):
            dst = os.path.join(static_dir, dirname)
            if os.path.isdir(dst):
                shutil.rmtree(dst)

            print("copy %s -> %s " % (path, dst))
            shutil.copytree(path, dst)


def cmd_fix_permission():
    _configure_permissions(force_simples=True)


def cmd_migrate():
    if os.getuid() == 0:
        os.setgid(int(APP_GROUP_ID or 1000))
        os.setuid(int(APP_USER_ID or 1000))

    subprocess.call(
        [
            os.path.join(APP_BIN, "python"),
            "-u",
            os.path.join(APP_ROOT, "manage.py"),
            "migrate",
            "--force-color",
        ],
        shell=False,
    )


def cmd_requirementsdev():
    if os.path.exists(os.path.join(APP_ROOT, "requirements.dev")):
        subprocess.call(
            [
                os.path.join(APP_BIN, "pip"),
                "install",
                "-U",
                "-r",
                os.path.join(APP_ROOT, "requirements.dev"),
            ],
            shell=False,
        )


def launcher(name):
    _configure_permissions()

    cmd_map = {
        "collectstatic": cmd_collect_static,
        "jsbuild": lambda: cmd_minifier(False),
        "migrate": cmd_migrate,
        "shell": cmd_shell,
        "fix": cmd_fix_permission,
        "start": cmd_start,
        "celery": cmd_celery,
        "flower": cmd_flower,
        "daphne": cmd_daphne,
        "register": cmd_register,
        "minifier": cmd_minifier,
        "configure": cmd_configure,
        "requirementsdev": cmd_requirementsdev,
    }

    os.environ.update(HOME=APP_HOME)
    command = cmd_map.get(name, lambda: cmd_not_found(name))
    debug = os.environ.get("DEBUG", "0")
    print(f"DEBUG: {debug}")
    command()

    return None


def main():
    os.environ.update(IPYTHONDIR=os.path.join(APP_ETC, ".ipython"))
    os.environ.update(HISTFILE=os.path.join(APP_ETC, ".bash_history"))

    print(sys.argv)

    if len(sys.argv) == 2:
        launcher(sys.argv[1])
    else:
        script_path = sys.argv[0]
        for command in sys.argv[1:]:
            subprocess.call([script_path, command], shell=False)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# from __future__ import print_function, unicode_literals

import os
import re
import json

try:
    from StringIO import StringIO  # for Python 2
except ImportError:
    from io import StringIO  # for Python 3
from fabric import task

APP_HOME = "/app"
APP_ENV = os.path.join(APP_HOME, "env")
APP_ETC = os.path.join(APP_HOME, "etc")
APP_WATCH = os.path.join(APP_HOME, "var", "watch")
APP_BIN = os.path.join(APP_ENV, "bin")
APP_PYTHON = os.path.join(APP_BIN, "python")
APP_PIP = os.path.join(APP_BIN, "pip")
APP_ROOT = os.path.join(APP_HOME, "root")
APP_MANAGE = os.path.join(APP_ROOT, "manage.py")


__repos_cache = None


def repos():
    global __repos_cache
    if not __repos_cache:
        base_path = os.getcwd()

        __repos_cache = {"core": {"path": base_path}}

        for dirname in [
            p
            for p in os.listdir(base_path)
            if os.path.isdir(p) and os.path.isdir(os.path.join(p, ".git"))
        ]:
            __repos_cache.update({dirname: {"path": os.path.join(APP_ROOT, dirname)}})

        __repos_cache.update(all={"aliases": __repos_cache.keys()})

    return __repos_cache


@task(optional=("repo", "ref", "header"))
def pull(remote, repo="all", ref="origin", header="master"):
    """
    Test of documentation method.
    """

    selected = repos().get(repo, None)
    if "aliases" in selected:
        for alias in selected.get("aliases"):
            pull(remote, repo=alias)
    else:
        remote_path = selected.get("path")
        with remote.cd(remote_path):
            remote.run("git pull %(ref)s %(header)s" % locals())


@task(optional=("repo", "ref", "header"))
def checkout(remote, repo="all", ref="origin", header="master"):
    """
    Test of documentation method.
    """

    selected = repos().get(repo, None)
    if "aliases" in selected:
        for alias in selected.get("aliases"):
            pull(remote, repo=alias)
    else:
        remote_path = selected.get("path")
        with remote.cd(remote_path):
            remote.run("git checkout %(header)s" % locals())


@task(optional=("repo",))
def branch(remote, repo="all"):
    """
    Test of documentation method.
    """

    selected = repos().get(repo, None)
    if "aliases" in selected:
        for alias in selected.get("aliases"):
            branch(remote, repo=alias)
    else:
        print("repo %(repo)s " % locals())
        remote_path = selected.get("path")
        with remote.cd(remote_path):
            remote.run("git branch")
        print("")


@task(optional=("repo",))
def minify(remote, repo="all"):
    """
    Test of documentation method.
    """
    with remote.cd(APP_ROOT):
        remote.run(
            " ".join(
                [
                    APP_PYTHON,
                    APP_MANAGE,
                    "minify",
                    "--uglify",
                    repo,
                    "--jsout",
                    os.path.join(APP_ROOT, "static", "build", "%s.min.js"),
                ]
            )
        )


@task()
def install(remote):
    """
    Test of documentation method.
    """
    print("install task")


def __build_print(data):
    print("Build: %(build)d" % data)
    print("DVCS: %(dvcs)s" % data)


def __build_show(remote):
    data = {"build": 0, "dvcs": "undefined"}
    try:
        buffer = StringIO()
        remote.get(os.path.join(APP_ROOT, "sysinfo.json"), buffer)
        buffer.seek(0)

        data = json.load(buffer)
    except IOError:
        pass
    finally:
        __build_print(data)


def __build_update(remote):
    data = {"build": 0}

    try:
        buffer = StringIO()
        remote.get(os.path.join(APP_ROOT, "sysinfo.json"), buffer)
        buffer.seek(0)

        data = json.load(buffer)
    except IOError:
        pass
    finally:
        data.update(dvcs="git", build=data.get("build", 0) + 1)

        buffer = StringIO()
        json.dump(data, buffer, indent=2)
        buffer.seek(0)

        remote.put(buffer, os.path.join(APP_ROOT, "sysinfo.json"))
        __build_print(data)


def __build_not_found(remote, command):
    print('The command "%s" not is um command of build' % command)


@task(optional=("command",))
def build(remote, command="show"):
    """
    Test of documentation method.
    """
    commands = {"show": __build_show, "update": __build_update}

    _command = commands.get(command, lambda r: __build_not_found(r, command))
    _command(remote)


@task(optional=("target",))
def restart(remote, target="all"):
    """
    Test of documentation method.
    """
    targets = {
        "celery": ("celery",),
        "flower": ("flower",),
        "worker": ("worker",),
        "all": (
            "celery",
            "flower",
            "worker",
        ),
    }

    selected = targets.get(target, [])
    if selected:
        buffer = StringIO()
        buffer.write(" ".join(selected))
        buffer.seek(0)
        remote.put(buffer, os.path.join(APP_WATCH, "command.txt"))
        print("foi enviado o comando de restart para %s" % ", ".join(selected))
    else:
        print('O alvo "%s" não é um alvo conhecido.' % target)


def __migrate(remote, repo, version):
    with remote.cd(APP_ROOT):
        command = [APP_PYTHON, APP_MANAGE, "migrate", repo]

        if version:
            command.append(version)

        remote.run(" ".join(command))


@task(optional=("target",))
def migrate(remote, target="all"):
    """
    Test of documentation method.
    """
    version = None
    test = re.compile("^.*\+(\d{4})")
    sre = test.match(target)

    if sre:
        target, version = target.split("+")

    __migrate(remote, target, version)

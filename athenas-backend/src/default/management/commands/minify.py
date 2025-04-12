# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import ssl
import sys
import subprocess as sp
import urllib.request
from datetime import datetime
from functools import partial
from importlib import import_module
from time import time

from django.core.management.base import BaseCommand
from inotify.adapters import Inotify

from contrib.utils import getLogger
from default.views import Application

log = getLogger(__name__)


class Command(BaseCommand):

    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument("--relpath", dest="relpath", help="Relative path")

        parser.add_argument("--jsout", dest="jsout", help="JavaScript output filename")

        parser.add_argument("--cssout", dest="cssout", help="CSS output filename")

        parser.add_argument(
            "--list-libraries",
            dest="list_libraries",
            help="List JS libraries of athenas",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "--uglify", dest="uglify", help="List JS libraries of athenas"
        )

        parser.add_argument(
            "--watch",
            dest="watch",
            help="Minify watch changes in files for update minifed files.",
            action="store_true",
            default=False,
        )

    @classmethod
    def get_css_filename(cls, relpath, context, metainfo):
        metainfo = metainfo % {"context": context}

        rst = re.match(
            r"^.*/static/(?P<app>([a-z]|[A-Z]|[0-9]|_|-)+)/(?P<filename>.*)$", metainfo
        )

        if rst is not None and rst.groupdict().get("app") != "js":
            metainfo = os.path.sep.join(
                [
                    relpath,
                    rst.groupdict().get("app"),
                    "static",
                    rst.groupdict().get("filename"),
                ]
            )
        elif rst is not None and rst.groupdict().get("app") == "css":
            metainfo = os.path.sep.join(
                [
                    relpath,
                    "static",
                    rst.groupdict().get("app"),
                    rst.groupdict().get("filename"),
                ]
            )
        else:
            log.info("no match for %s" % metainfo)
            log.info(metainfo)

        return metainfo

    def get_buffer(self, filename):
        try:
            return open(filename, "rb").read()
        except Exception as e:
            return "/* Exception for %s\n%s\n*/" % (filename, e)

    def _command(self, typeof, infile, outfile):
        return [
            os.path.sep.join([self.java_home, "bin", "java"]),
            "-jar",
            self.ycompressor,
            "--type",
            typeof,
            "-o",
            outfile,
            infile,
        ]

    def _css_minify_file(self, filename, outfile):
        sp.call(" ".join(self._command("css", filename, outfile)), shell=True)

    def js_files_for_library(self, name):
        from django.conf import settings

        context = os.getcwd()[1:]

        paths = [
            path for path, lib in Application.collections.get("js", []) if lib == name
        ]

        rules = getattr(settings, "MINIFY_JS_RULES", [])

        file_list = []
        c_w = 0
        for uri in paths:
            path = uri.split(os.path.sep)[3:]
            basedir = getattr(settings, "BASE_DIR")
            fn = None

            for exp, cPath, cFn in rules:
                if exp.match(os.path.join(*path)):
                    basedir = cPath
                    fn = cFn
                    break

            fullpath = os.path.join(
                basedir,
                os.path.join(
                    *(fn if fn else lambda a: a[:1] + ["static"] + a[1:])(path)
                ),
            )

            if not os.path.exists(fullpath):
                print('Warning: resource "%s" not found' % uri)
                c_w += 1
            else:
                file_list.append(fullpath)

        return file_list

    def uglify(self, name, output, file_list=False):
        from django.conf import settings

        print('- minify for "%s" writing %s' % (name, output))
        file_list = self.js_files_for_library(name) if not file_list else file_list
        if name in Application.js_libraries():
            command = ["/usr/local/bin/uglifyjs", "-c", "-o", output] + file_list
            t_start = time()
            if not getattr(settings, "DEBUG", False):
                return_code = sp.call(command, shell=False)
                if return_code != 0:
                    sys.exit(return_code)
            else:
                with open(output, "wt") as fd:
                    for filepath in file_list:
                        fd.write("\n".join(["/*", " * src: %s" % filepath, " */", ""]))
                        with open(filepath, "r") as fdread:
                            for chunk in iter(partial(fdread.read, 8192), ""):
                                fd.write(chunk)
                        fd.write("\n")
            t_end = time()

            cachedata = None
            cachefile = os.path.join(os.path.dirname(output), "cache.json")

            try:
                cachedata = json.load(open(cachefile))
            except Exception as e:
                cachedata = {}
            finally:
                eng = hashlib.new("md5")
                with open(output, "rb") as fd:
                    for chunk in iter(partial(fd.read, 8192), b""):
                        eng.update(chunk)
                    cachedata.update({name: eng.hexdigest()})
                json.dump(cachedata, open(cachefile, "wt"), indent=4)
            print('- "%s" is done after %0.3f seconds.' % (output, (t_end - t_start)))
        else:
            print('the library "%s" doest exists.' % name)

    def uglify_with_watch(self, name, output):
        files = []
        rel_files = {}

        watcher = Inotify()
        for name in [
            a for a in Application.js_libraries() if a == name or name == "all"
        ]:
            rel_files.update({name: self.js_files_for_library(name)})
            files += rel_files.get(name)
            self.uglify(name, output % name, rel_files.get(name))

        for path in files:
            watcher.add_watch(path)

        effective_events = {"IN_CLOSE_WRITE", "IN_MOVE_SELF"}
        try:
            for event in watcher.event_gen():
                if event:
                    (header, type_names, watch_path, filename) = event
                    if set(type_names).intersection(effective_events):
                        print("changed %s" % (filename or watch_path))

                        filepath = filename or watch_path
                        selected_name = None
                        selected_files = None
                        for name, paths in list(rel_files.items()):
                            if filepath in paths:
                                selected_name = name
                                selected_files = paths
                                break

                        if selected_name:
                            self.uglify(
                                selected_name, output % selected_name, selected_files
                            )
                        else:
                            print('file "%s" not found in libraries' % filepath)
                    if "IN_MOVE_SELF" in type_names:
                        print('readd to watch "%s"' % watch_path)
                        watcher.add_watch(watch_path)
        except KeyboardInterrupt:
            print("\nbye!!!")
        finally:
            for path in files:
                watcher.remove_watch(path)

    def handle(
        self,
        relpath="",
        jsout="outfile.min.js",
        cssout="outfile.min.js",
        uglify=None,
        watch=False,
        list_libraries=False,
        *args,
        **kargs
    ):
        self.load_library()

        if list_libraries:
            print(" ".join(Application.js_libraries()))

        if uglify == "all":
            if not watch:
                for name in [
                    lname for lname in Application.js_libraries() if lname != "remote"
                ]:
                    print("uglify %s" % name)
                    self.uglify(name, jsout % name)
            else:
                self.uglify_with_watch(uglify, jsout)
        elif uglify and not watch:
            self.uglify(uglify, jsout % uglify)
        elif uglify and watch:
            self.uglify_with_watch(uglify, jsout)

        cssout is not None and self.minify_css(relpath, cssout)

    def minify_css(self, relpath="", outcss="outfile.min.css"):
        from django.conf import settings

        context = getattr(settings, "CONTEXT")
        relpath = os.path.abspath(relpath)

        filesbuffer = []

        log.info("Loading buffer...")
        for cssfile in Application.collections.get("css", []):
            try:
                cssfile = self.get_css_filename(relpath, context, cssfile)
            except Exception as e:
                log.exception(e)
            else:
                filesbuffer.append(self.get_buffer(cssfile))

        tmpfile = os.path.abspath("tmpmin")
        with open(tmpfile, "wb") as fd:
            fd.write("\n/* --- solder --- */\n".join(filesbuffer))

        self._css_minify_file(tmpfile, os.path.abspath(outcss))
        os.unlink(tmpfile)

    def load_library(self):
        from django.conf import settings

        router_conf = getattr(settings, "ROUTER", {})
        controller_conf = router_conf.get("controllers", [])

        log.info("Carregando modulo de controllers ...")
        for module in controller_conf:
            try:
                import_module(module)
            except ImportError:
                log.warn('Controller module "%s" not found', module)
            except Exception as e:
                log.exception(e)
            else:
                log.info('Module "%s" loaded', module)

    def _read_over_http(self, url):
        if hasattr(ssl, "_create_unverified_context"):
            return urllib.request.urlopen(
                url, context=getattr(ssl, "_create_unverified_context")()
            )
        else:
            return urllib.request.urlopen(url)

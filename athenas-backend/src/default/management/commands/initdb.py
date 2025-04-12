# -*- coding: utf-8 -*-
import fnmatch
import os
import re
import shutil
from subprocess import PIPE, Popen

from django.core.management.base import BaseCommand
from django.db import connections

from contrib.utils import getLogger

log = getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "-d",
            "--drop-db",
            dest="dropdb",
            action="store_true",
            help="Apagar o banco caso ele exista!",
        )
        parser.add_argument(
            "-r",
            "--rename-migrations",
            dest="rename",
            action="store_true",
            help="Renomeia os diretorios de migrations para que possa rodar o migrate direto.!",
        )
        parser.add_argument(
            "-z",
            "--restore-migrations",
            dest="restore",
            action="store_true",
            help="Renomeia os diretorios de migrations para o original!",
        )
        parser.add_argument(
            "-m",
            "--migrate",
            dest="migrate",
            action="store_true",
            help="Executa os migrations!",
        )
        parser.add_argument(
            "-n",
            "--no-sync",
            dest="nosync",
            action="store_true",
            help="Executa os migrations em modo no-sync. Criar todas as tabelas para os apps sem migrations!",
        )
        parser.add_argument(
            "-f",
            "--fake-migrations",
            dest="fake",
            action="store_true",
            help="Executa os migrations em fake mode!",
        )
        parser.add_argument(
            "-a",
            "--apply-fixures",
            dest="fixtures",
            action="store_true",
            help="Carrega as fixtures iniciais!",
        )
        parser.add_argument(
            "-u",
            "--create-user",
            dest="user",
            action="store_true",
            help="Cria o usuario inicial do sistema - athenas como super-usuario!",
        )
        parser.add_argument(
            "-l",
            "--list-summary",
            dest="summary",
            action="store_true",
            help="Mostra informações do banco no estado atual!",
        )
        parser.add_argument(
            "-C",
            "--complete-init",
            dest="complete",
            action="store_true",
            help="Executa todo o processo de geração da base do Athenas!",
        )

    def handle(self, *args, **options):

        config = self.config_db()
        db_exists = self.db_exists()
        exit = False
        if db_exists:
            print("")
            print(f'DATABASE: {self.style.WARNING(config.get("NAME", "athenas"))}')
            print(f'DATABASE EXIST: {"Y" if db_exists else "N"}')
            print(f'DATABASE DROP?: {"Y" if options["dropdb"] else "N"}')
            # msg = 'O banco %s já existe. Para apagar o banco use a opção --drop-db!' % (config.get('NAME', 'athenas'))
            # self._print(self.style.WARNING(msg))
            input_e = ""
            while input_e.upper() not in ("N", "Y"):
                input_e = input("Deseja continuar: [yN]") or "N"
            exit = input_e.upper() == "N"

        if not exit:
            if db_exists:
                self._print("CLOSING CONNECTIONS FOR %s" % config.get("NAME"), nl=False)
                res = self.close_connections()
                self._printr(res)

            cmd_base = "{} -U %s -h %s {}%s" % (
                config.get("USER", "postgres"),
                config.get("HOST", "db"),
                config.get("NAME", "athenas"),
            )
            if options["dropdb"]:
                if db_exists:
                    self._print("DROPPING DB IF EXISTS...", nl=False)
                    res = self.run_cmd(cmd_base.format("dropdb", "--if-exists "))
                    self._printr(res)
            if not self.db_exists():
                self._print(
                    "CREATING DB... %s" % cmd_base.format("createdb", ""), nl=False
                )
                res = self.run_cmd(cmd_base.format("createdb", ""))
                self._printr(res)

            if self.db_exists():
                if options["rename"] or options["complete"]:
                    self._print("RENAMING MIGRATIONS FOR SYNCDB ....", nl=False)
                    res = self.rename_migrations_to_sync()
                    self._printr(res)
                if options["migrate"] or options["complete"]:
                    self._print("MIGRATING DJANGO MODELS...", nl=False)
                    res = self.run_cmd("./manage.py migrate")
                    self._printr(res)
                if options["nosync"] or options["complete"]:
                    self._print("MIGRATE ATHENAS MODELS...", nl=False)
                    res = self.run_cmd("./manage.py migrate --run-syncdb")
                    self._printr(res)
                    self._print("TRUNCATE TABLE django.migrations...", nl=False)
                    res = self._execute(
                        "TRUNCATE TABLE public.django_migrations RESTART IDENTITY CASCADE;"
                    )
                    self._printr(res)
                if options["user"] or options["complete"]:
                    self._print("CREATE A USER athenas ...", nl=False)
                    res = self.run_cmd(
                        "./manage.py loaddata engine/fixtures/initialdb_default_user.json"
                    )
                    self._printr(res)
                if options["fixtures"] or options["complete"]:
                    self._print("APPLING FIXTURES...")
                    self.load_fixtures(["standard"])
                    self.load_fixtures(["engine"])
                    self.load_fixtures(["rh"])
                if options["restore"] or options["complete"]:
                    self._print("REVERT MIGRATIONS DIRECTORY...", nl=False)
                    res = self.revert_migrations_after_sync()
                    self._printr(res)
                if options["fake"] or options["complete"]:
                    self._print("APPLING ALL MIGRATIONS IN FAKE MODE...", nl=False)
                    res = self.run_cmd("./manage.py migrate --fake")
                    self._printr(res)
                if options["summary"] or options["complete"]:
                    self.stdout.write("---------------------------------")
                    regs = self.list_tables_regs()
                    for r in regs:
                        self._print("%s? %s" % (r, regs[r]))
                    self.stdout.write("---------------------------------")

    def _print(self, text, nl=True, style=None):
        text = text if not style else style(text)
        print(text, end="" if not nl else "\n", flush=True)

    def _printr(self, res, nl=True):
        if res and res[0] == 0:
            self._print(self.style.SUCCESS(" OK"))
        else:
            self._print(self.style.ERROR(" ERROR"))
            self._print(res[2])

    def config_db(self, db_link=""):
        from django.conf import settings

        db_settings = getattr(settings, "DATABASES")
        db_link = db_settings.get("default", "")
        return db_link

    def db_exists(self, db_alias="default"):
        c = connections[db_alias]
        try:
            if not c.connection:
                c.connect()
            return True
        except Exception as e:
            log.exception(str(e))
        return False

    def _execute(self, cmd, db_alias="default", single=False, close=True):
        stdout = []
        stderr = None
        result = 0
        if self.db_exists():
            # self._print(cmd)
            try:
                con = connections[db_alias]
                with con.cursor() as c:
                    c.execute(cmd)
                    if c.description:
                        stdout = c.fetchall()  # if not single else c.fetchone()
                con.close()
            except Exception as e:
                result = 1
                stderr = str(e)

        return result, stdout, stderr

    def close_connections(self):
        config = self.config_db()
        sql = """SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '%s'
    AND pid <> pg_backend_pid();""" % config.get(
            "NAME"
        )
        # self.stdout.write(sql)
        return self._execute(sql)

    def copy_with_stats(self, source, target):
        # copy content, stat-info (mode too), timestamps...
        shutil.copy2(source, target)
        # copy owner and group
        st = os.stat(source)
        # os.chown(target, st[stat.ST_UID], st[stat.ST_GID])

    def rename_migrations_to_sync(self, create=False):
        result = 0
        stderr = None
        stdout = []
        try:
            for root, dirs, files in os.walk("."):
                for basename in dirs:
                    if basename in [".hg", ".git"]:
                        pass
                    elif basename == "migrations" and not fnmatch.fnmatch(
                        root, "*/.hg/*"
                    ):
                        msg = self.style.SUCCESS("OK")
                        d1 = os.path.join(root, basename)
                        d2 = "%s_old" % os.path.join(root, basename)
                        if os.path.isdir(d2):
                            msg = self.style.WARNING("%s exists!" % d2, YELLOW)
                        else:
                            f_init1 = os.path.join(d1, "__init__.py")
                            f_init2 = os.path.join(d2, "__init__.py")
                            # st = os.stat(d1)
                            shutil.move(d1, d2)
                            if create:
                                os.mkdir(d1)
                                self.copy_with_stats(f_init2, f_init1)
                        stdout.append(
                            "%s %s > %s: %s" % ("C" if create else "N", d1, d2, msg)
                        )
        except Exception as e:
            result = -1
            stderr = str(e)

        return result, stdout, stderr

    def revert_migrations_after_sync(self):
        result = 0
        stderr = None
        stdout = []
        try:
            for root, dirs, files in os.walk("."):
                for basename in dirs:
                    if basename in [".hg", ".git"]:
                        pass
                    elif basename == "migrations_old" and not fnmatch.fnmatch(
                        root, "*/.hg/*"
                    ):
                        d1 = os.path.join(root, basename)
                        d2 = os.path.join(root, basename).replace("_old", "")
                        if os.path.isdir(d2):
                            shutil.rmtree(d2)
                        shutil.move(d1, d2)

                        stdout.append(
                            "%s > %s: %s" % (d1, d2, self.style.SUCCESS("OK"))
                        )
        except Exception as e:
            result = -1
            stderr = str(e)

        return result, stdout, stderr

    def run_cmd(self, cmd, **params):
        process = Popen(cmd.split(" "), stderr=PIPE, stdout=PIPE)
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def list_tables_regs(self, config={}):
        self._execute("ANALYZE")
        cmd = """SELECT
        n.nspname AS schema_name,
        c.relname AS table_name,
        c.reltuples::int AS num_reg
    FROM pg_class c
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_tablespace t ON t.oid = c.reltablespace
    WHERE c.relkind = 'r'::char
    AND nspname NOT IN('information_schema','pg_catalog','pg_toast')
    AND c.reltuples::int > 0
    ORDER BY n.nspname, c.reltuples::int DESC, c.relname;"""
        result, lines, err = self._execute(cmd)
        regs = {}
        if result == 0:
            for l in lines:
                if len(l) == 3:
                    # print table
                    table_name = "{}.{}".format(l[0], l[1])
                    regs[table_name] = int(l[2])
        else:
            self.stdout.write(self.style.ERROR(err))
        return regs

    def load_fixtures(self, app_labels=[]):
        apps_regex = "|".join(app_labels) if app_labels else ".*"
        prog = re.compile(".*/(%s)/fixtures" % apps_regex)
        fprog = re.compile("initialdb_[0-9]{4}_.*.json")
        for root, dirs, files in os.walk("."):
            if prog.match(root) and not fnmatch.fnmatch(root, "*/.hg/*"):
                self.stdout.write(self.style.MIGRATE_LABEL(">>> %s" % root))
                for f in sorted(files):  # fnmatch.filter(sorted(files), 'initialdb_*'):
                    if fprog.match(f):
                        self._print(self.style.MIGRATE_LABEL("> %s" % f), nl=False)
                        f1 = os.path.join(root, f)
                        res = self.run_cmd("./manage.py loaddata %s" % f1)
                        self._printr(res)

    def clear_pyc_pyo(self):
        cmd1 = r'find . -type f -name "*.pyc" -exec rm -f {} \;'
        cmd2 = r'find . -type f -name "*.pyo" -exec rm -f {} \;'
        p1 = Popen(cmd1.split(" "))
        stdout1, stderr1 = p1.communicate()
        p1.wait()

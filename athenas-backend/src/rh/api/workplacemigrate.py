# -*- coding: utf-8 -*-
from django.db import transaction

from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from rh.models import WorkplaceMigrate, TargetWorkplaceMigrate, ChoiceWorkplaceMigrate

log = getLogger(__name__)
json = get_json_engine()


class RHWorkplaceMigrate(RestfulDRY):

    _model = WorkplaceMigrate

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplacemigrate.Manage")')

    def perform_migration(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}

        self._read_special_verb()
        try:
            for inst in self.get_query().filter(
                pk__in=self.request.PUT.getlist("pkset", [])
            ):
                inst.perform_migration()
        except Exception as e:
            log.exception(e)
            response.update(message="{}".format(e.args[0]))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.renderer(response)


class RHWorkplaceMigrateManager(RHWorkplaceMigrate):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplacemigrate.specialized.Manage")')


class RHTargetWorkplaceMigrate(RestfulDRY):

    _model = TargetWorkplaceMigrate

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplacemigrate.target.Manage")')


class RHChoiceWorkplaceMigrate(RestfulDRY):

    _model = ChoiceWorkplaceMigrate

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplacemigrate.choice.Manage")')

    def get_query(self):
        return (
            super(RHChoiceWorkplaceMigrate, self)
            .get_query()
            .filter(app_label="rh", name="APP_TO_MIGRATE")
        )

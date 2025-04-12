# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, get_json_engine
from rh.cadastralquality.models import RegistrationQuery
from contrib.decorator import login_required, validate
from engine.mq.models import Task
from contrib.middleware import get_current_user
from rh.queryregistration.tasks import report_xls_full


log = getLogger(__name__)
json = get_json_engine()


class QRegistration(RestfulDRY):

    _model = RegistrationQuery

    full_text_index = ("title__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.cadastralquality.Manage")')

    def get_icons(self, instance):
        description = instance.description if instance.description else " - "
        return (
            {"iconCls": "icon-diarias icon-information", "title": f"{description}"},
        )

    def model_to_dict(self, instance):
        _dict_ = super(QRegistration, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": self.get_icons(instance),
            }
        )

        _dict_.pop("sql")

        return _dict_

    @login_required("JSON")
    def full_report(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:

            Task.start(
                report_xls_full,
                f"Gerando Relatório",
                success=f"""<p>Qualidade Cadastral - <a href="/athenas/CQualityReport/download_file/?uuid=%(uuid)s">Download</a>.</p>""",
                user=get_current_user().pk,
                title="Qualidade Cadastral",
                params=[],
                instance="RegistrationQuery",
                download=False,
                filename=f"query-qualidade cadastral-{get_current_user().pk}.xls",
                mimetype="application/vnd.ms-excel",
                extension="xls",
                identifier="cadastralquality",
                save_log=False,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=False,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

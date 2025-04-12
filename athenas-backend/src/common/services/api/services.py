import codecs
import os
import uuid
import random

from datetime import datetime
from django.conf import settings
from django.utils import timezone
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.decorator import login_required

from django.contrib.auth.models import User
from common.services.models import ScheduledServices, StatusLog
from engine.models import TaskSession
from ged.models import Arquivo as FileGED

from common.services.utils import (
    atualiza_info_execucao_servico,
    tmp_dir,
    gerar_historico_servico,
    atualizar_historico_servico,
)
from contrib.utils import getLogger

logg = getLogger("db")
# log = logging.getLogger('db')


class SvcScheduledServicesRestful(RestfulDRY):

    full_text_index = (
        "name__icontains",
        "command__icontains",
        "description__icontains",
    )

    _model = ScheduledServices
    force_upper = False

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.services.scheduled_services.Manage")')

    def model_to_dict(self, instance):
        rst = super(SvcScheduledServicesRestful, self).model_to_dict(instance)

        return rst

    def tmp_dir(self):
        self.uuid = uuid.uuid1().hex
        return os.path.join(settings.UPLOAD_STORE_DIR, "service")

    def execute_job(self, params):
        rst = {
            "success": False,
            "message": "Nada feito ainda!",
            "code": 200,
        }

        task_ = TaskSession(user=get_current_user()).start_execution()
        filename = f"logs-{random.randint(100000, 999999)}.txt"
        start_time = timezone.now()

        try:
            if params and params["api"]:
                service = ScheduledServices.objects.get(pk=self.id)
                if not os.path.exists(tmp_dir()):
                    os.makedirs(tmp_dir())
                file_path = os.path.join(tmp_dir(), filename)
            else:
                service = ScheduledServices.objects.get(pk=self.request.POST.get("id"))
                if not os.path.exists(self.tmp_dir()):
                    os.makedirs(self.tmp_dir())
                file_path = os.path.join(self.tmp_dir(), filename)

            task_.message(f"Iniciando o Job {service.name} em {datetime.today()}")

            historico_servico = gerar_historico_servico(
                service,
                datetime.now(),
            )
            ScheduledServices.objects.filter(id=service.id).update(em_execucao=True)
            service.run_job()

            logs = StatusLog.objects.filter(create_datetime__gt=start_time)

            with codecs.open(file_path, "w", "utf-8") as fd:
                for log in logs:
                    text = str(log.path) + " " + str(log.msg) + "\n"
                    fd.write(text)

            gedfile = FileGED.from_filepath(
                file_path, get_current_user(), "application/txt", ignore_cache=True
            )
            atualizar_historico_servico(historico_servico, True, datetime.now())
            task_.message(f"Finalizado o Job {service.name} em {datetime.today()}")
            task_.add_file(gedfile)

        except Exception as e:
            task_.message(
                f"Erro ao solicitar o Job {service.name} em {datetime.today()}"
            )
            task_.message(f"Erro: {e}")
            rst.update(
                success=False,
                showMessage=True,
                message="Erro ao solicitar o job. {}".format(e),
                code=400,
            )
            atualiza_info_execucao_servico(service, False)
            task_.finish_execution(status="ERROR", msg="ERRO AO SOLICITAR O JOB")
        else:
            rst.update(
                success=True,
                showMessage=True,
                message="Job executado com sucesso.",
                code=200,
            )
            atualiza_info_execucao_servico(service, True)
            task_.finish_execution(msg="Finalizado")

        if params and params["api"]:
            return rst
        else:
            self.renderer(rst)

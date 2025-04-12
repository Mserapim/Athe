# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from engine.mq.models import Task, TaskMessages
from contrib.nil import nil_pk, nil_unicode
from contrib.middleware import get_current_user
from django.db import transaction


log = getLogger(__name__)


class MQTask(RestfulDRY):

    _model = Task

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "owner__username__icontains",
        "description__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("engine.mq.TaskManage")')


class MQTaskCustom(MQTask):

    _model = Task

    def mark_finished(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda."}

        try:
            with transaction.atomic():
                for task in self.get_query().filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    task.mark_finished()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="tarefas marcadas como concluida.")

        self.renderer(rst)

    def get_query(self):
        return super(MQTask, self).get_query().filter(owner=get_current_user())

    def hook(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        uuid = args[0]
        task = self.Model.objects.get(uuid=uuid)

        try:
            data = json.loads(self.request.POST.get("data"))
            log.info("atualizando o estado da task %s para %s", task, data.get("state"))

            task.state = data.get("state")
            task.message = data.get("message") if "message" in data else ""
            task.data = json.dumps(data.get("data") if "data" in data else {})
            task.save()
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="task atualizada com sucesso.")

        self.response["Content-Type"] = "text/json"
        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = super(MQTask, self).model_to_dict(instance)
        progress = float(instance.progress) if instance.progress else None
        if progress:
            rst.update(
                progress_message=(
                    instance.progress_message
                    if instance.progress_message
                    else "%0.1f%%" % instance.progress
                ),
                progress=progress,
            )

        return rst


class MQTaskMessages(RestfulDRY):

    _model = TaskMessages

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "tasker__uuid__iexact",
        "message__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def model_to_dict(self, instance):
        params = super(MQTaskMessages, self).model_to_dict(instance)

        params.update(
            status=[
                {
                    "iconCls": "icon-core icon-core-%s"
                    % instance.get_type_of_display().lower(),
                    "title": instance.get_type_of_display(),
                },
            ],
            file_ged_permalink=(
                instance.file_ged.permalink() if instance.file_ged else ""
            ),
        )

        return params


MQTaskRestful = MQTask

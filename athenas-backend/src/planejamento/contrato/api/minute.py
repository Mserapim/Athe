# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from planejamento.contrato.models import Minute
from standard.models import Configuration
from rh.models import OrgaoGeral
from django.db.models import Q
import json
import locale
from datetime import date


log = getLogger(__name__)


class PHMMinute(RestfulDRY):

    _model = Minute

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()
    full_text_index = (
        "number__icontains",
        "process_number__icontains",
        "minute_object__icontains",
        "parent_process__icontains",
        "provider__nome__icontains",
        "provider__pessoajuridica__razao_social__icontains",
        "provider__pessoajuridica__cnpj__icontains",
        "provider__pessoafisica__social_name__icontains",
        "provider__pessoafisica__cpf__icontains",
        "minuteitems__description__icontains",
        "minutesupervisors__employee__pessoa_fisica__nome__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

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

    def total_amount_display(self, *args):
        obj = {"success": False, "total_amount_display": "0,00"}
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        try:
            minute = self._model.objects.get(pk=self.request.POST.get("pk"))
            _total_amount_display = minute.total_amount or 0
            obj.update(
                total_amount_display=str(
                    locale.currency(_total_amount_display, grouping=True, symbol=None)
                ),
                success=True,
            )

        except Minute.DoesNotExist:
            obj.update(
                total_amount_display=str(locale.currency(0, grouping=True, symbol=None))
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_query(self):

        query = super(PHMMinute, self).get_query().distinct().order_by("end_validity")

        dic = self.request.GET  # dicionário com parametros da request
        keys = [
            *dic
        ]  # chave do dicionário. o nome da chave é filter para ações checkbox

        """ condição 1: ação filtro?
            condição 2: todas as atas?
            condição 3: paginação? """
        if keys[0] == "filter" and "-1" in dic["filter"] or keys[0] == "start":
            query = query.filter()  # traz todas as atas
        else:

            user = get_current_user()

            # Se for gestor geral ou financeiro, visualiza todos
            if user.groups.filter(
                Q(name="hiring-minute-financial")
                | Q(name="hiring-minute-manager")
                | Q(name="hiring-minute-view-all")
            ).exists():
                query = query.filter()

            # Se for fiscal, visualiza os que ele é gestor ou responsável
            elif user.groups.filter(name="hiring-minute-supervisor").exists():
                subordinates = user.servidor.subordinados.filter()
                query = query.filter(
                    Q(minutesupervisors__employee__user=user)
                    | Q(minutesupervisors__employee__in=subordinates),
                    Q(minutesupervisors__end=None),
                )

            else:
                query = query.none()

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.minute.MinuteManage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            display_process_number=instance.process_number,
            display_parent_process=instance.parent_process,
            main_minutesupervisors=instance.main_minutesupervisors_list(),
        )

        return rst

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:

            minute = self.get_query().get(pk=args[0])

            rst.update(
                success=True, document={"content": minute.rendered, "appends": []}
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_management_organ(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            cfg = Configuration.get_or_create("hiring")
            management_organ_id = OrgaoGeral.objects.get(
                pk=cfg.get("management_organ")
            ).pk
        except Exception:
            management_organ_id = 0
        else:
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                management_organ_id=management_organ_id or " ",
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def verify_minute_validity(self, *args):
        obj = {"success": False, "message": ""}
        minute_id = self.request.POST.get("minute")

        try:
            minute = self._model.objects.get(id=minute_id)

            if date.today() < minute.begin_validity:
                obj.update(
                    before_begin_validity=True,
                    message="Ainda não começou a vigência da ata. Gostaria de continuar?",
                )

            if date.today() > minute.end_validity:
                obj.update(
                    after_end_validity=True,
                    message="Esta ata já expirou a data de vigência. Gostaria de continuar?",
                )

            if minute.end_validity >= date.today():
                num_days = minute.end_validity - date.today()
                if num_days.days <= 30:
                    obj.update(
                        days_for_validity=True,
                        message="Ata próxima ao vencimento, a contratação deve acontecer antes do dia "
                        + str(minute.end_validity.strftime("%d/%m/%Y")),
                    )

            obj.update(success=True)

        except Minute.DoesNotExist:
            obj.update(message="Não foi possível encontrar a ata.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

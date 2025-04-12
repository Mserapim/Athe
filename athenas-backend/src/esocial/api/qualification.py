# -*- coding: utf-8 -*-
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from engine.mq.models import Task
from esocial.models import RegistrationQualification
from esocial.tasks.qualification import discouver_persons, qualificate_batch

# from rh import models as rh_models


log = getLogger(__name__)


class ESCRegistrationQualification(RestfulDRY):

    _model = RegistrationQualification

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "natural_person__nome__icontains",
        "nome__icontains",
        "employee__matricula__iexact",
        "employee__pessoa_fisica__nome__icontains",
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

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("esocial.qualification.RegistrationQualificationManage")'
        )

    def get_icons(self, instance):
        """Summary.

        Args:
            instance (TYPE): Description

        Returns:
            TYPE: Description
        """
        map_type_person = {
            1: "icon-fopag icon-user-active",
            2: "icon-fopag icon-user-inactive",
            3: "icon-esocial icon-users",
            4: "icon-fopag icon-user-detective",
            5: "icon-fopag icon-user-silhouette",
            6: "icon-fopag icon-cookies",
            7: "icon-fopag icon-exclamation-circle",
        }

        type_of_person = {
            "iconCls": map_type_person[instance.type_of_person],
            "title": instance.get_type_of_person_display(),
        }

        map_status = {
            1: "icon-esocial icon-waiting",
            2: "icon-esocial icon-error",
            3: "icon-esocial icon-run-with-error",
            4: "icon-esocial icon-error",
            10: "icon-esocial icon-run-ok",
        }

        status = {
            "iconCls": map_status[instance.status],
            "title": instance.get_status_display(),
        }

        map_type_qualif = {
            1: "icon-esocial icon-blank",
            2: "icon-esocial icon-select",
            3: "icon-esocial icon-document-arrow",
        }

        info = {
            "iconCls": (
                "icon-esocial icon-blank"
                if not instance.info
                else "icon-esocial icon-info"
            ),
            "title": instance.info,
        }

        type_qualif = {
            "iconCls": map_type_qualif[instance.type_of_last_qualification],
            "title": instance.get_type_of_last_qualification_display(),
        }

        return [type_of_person, status, type_qualif, info]

    def model_to_dict(self, instance):
        """Summary.

        Args:
            instance (TYPE): Description

        Returns:
            TYPE: Description
        """
        # log.debug(instance)
        _dict = super(ESCRegistrationQualification, self).model_to_dict(instance)
        _dict.update(
            {
                "icons": self.get_icons(instance),
                "errors": [],
            }
        )
        return _dict

    # @login_required(type='JSON')
    # def discouver(self, args=[]):
    #     query_employees = rh_models.Servidor.objects.order_by('pessoa_fisica__nome')

    #     base_pct = query_employees.count()
    #     passo_pct = 0

    #     self.observer.set('total', base_pct)
    #     self.observer.set('pct', passo_pct)

    #     for s in query_employees:
    #         valid_trainee = s.is_trainee() and s.tipo == 'E' and s.ativo
    #         if valid_trainee or s.paychecks.filter(folha__periodo__ano=dt_now.year, folha__periodo__mes=dt_now.month).exists():
    #             pf = s.pessoa_fisica
    #             cpf = pf.cpf.replace('.', '').replace('-', '')
    #             dn = pf.data_nascimento.strftime('%d%m%Y') if pf.data_nascimento else ''
    #             nis = pf.documento.filter(tipo_documento__in=[5, 6]).first().numero
    #                   if pf.documento.filter(tipo_documento__in=[5, 6]) else ''
    #             nis = nis.replace('.', '').replace('-', '')

    #             if not nis and valid_trainee:
    #                 nis = default_nis

    #             group_records.add(
    #                 'persons',
    #                 cpf=cpf,
    #                 nome=tira_acentos(pf.nome),
    #                 nis=nis,
    #                 dn=dn,
    #             )
    #             passo_pct += 1
    #             self.observer.set('pct', passo_pct)

    @login_required(type="JSON")
    def discouver(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            Task.start(discouver_persons, user=get_current_user().pk)
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Avaliação em andamento, você será avisado quando o mesmo for concluído.",
            )
        self.renderer(rst)

    @login_required(type="JSON")
    def qualificate(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        log.info(self.request.POST)
        ged_file_id = self.request.POST["file"]
        try:
            Task.start(
                qualificate_batch, ged_file_id=ged_file_id, user=get_current_user().pk
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(
                success=True,
                message="Qualificação em andamento, você será avisado quando o mesmo for concluído.",
            )
        self.renderer(rst)

# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import Count
from django.db.models.query_utils import Q

from contrib.decorator import is_public, login_required
from contrib.helpers import capitalize_words
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from engine.mq.models import Task
from rh.api.generalorgan import RHGeneralOrganRestful
from rh.models import Lotacao, Publicacao, WorkplaceConfigTag, Atribuicao
from rh.task.workplace import create_new_employeeworkplace

log = getLogger(__name__)
json = get_json_engine()


class RHWorkplaceRestful(RHGeneralOrganRestful):

    _model = Lotacao

    exclude_fields = ["orgaogeral_ptr"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplace.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(RHWorkplaceRestful, self).model_to_dict(instance)

        job_position_responsible = ""

        for job_position in instance.cargo_responsavel.filter():
            if not job_position_responsible:
                job_position_responsible = job_position
            else:
                job_position_responsible = "{} | {}".format(
                    job_position_responsible, job_position
                )

        _dict_.update({"job_position_responsible": str(job_position_responsible)})
        _dict_.update(
            {
                "owner_unicode": (
                    str(instance.owner.first()) if instance.owner.exists() else ""
                )
            }
        )
        return _dict_

    def migrate_workplace(self, args=[]):
        # new, old = instance.new_and_old()
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                obj.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                workplace = Lotacao.objects.get(pk=self.request.POST.get("workplace"))
                publication = Publicacao.objects.get(
                    pk=self.request.POST.get("publication")
                )
        except Lotacao.DoesNotExist:
            obj.update(message="Não foi possível encontrar a lotação.")
        except Publicacao.DoesNotExist:
            obj.update(message="Não foi possível encontrar a publicação.")
        else:
            Task.start(
                create_new_employeeworkplace,
                new=workplace.pk,
                old=workplace.old.pk,
                old_reference=workplace.old.pk if workplace.old else None,
                publication=publication.pk,
                user=get_current_user().pk,
            )

            obj.update(
                success=True, message="Solicitação de migração executada com sucesso!"
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def get_substitutes(self, args=[]):
        rst = {"success": False, "message": "Sem resposta.", "result": []}
        try:
            params = self.get_params(self.request.POST, check_case=True)
            registry = []
            pk = params.get("workplace_substituted", None)
            if pk:
                for employee in Lotacao.objects.get(pk=pk).my_substitute_employee():
                    registry.append(employee.matricula)
            rst.update({"result": registry})

            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = "%s" % err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def toggle_allow_lawsuit(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}

        self._read_special_verb()
        try:
            with transaction.atomic():
                for l in self.get_query().filter(
                    pk__in=self.request.PUT.getlist("pkset", [])
                ):
                    l.toggle_allow_lawsuit()
        except Exception as e:
            log.exception(e)
            response.update(message="{}".format(e.args[0]))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.renderer(response)

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:

            job_position_responsible = ""

            for job_position in record.cargo_responsavel.filter():
                if not job_position_responsible:
                    job_position_responsible = job_position
                else:
                    job_position_responsible = "{} | {}".format(
                        job_position_responsible, job_position
                    )

            rst.append(
                {
                    "Ativo": "SIM" if record.ativo else "Não",
                    "Descrição": record.descricao or "",
                    "Habilita Protocolo": "SIM" if record.habilita_protocolo else "Não",
                    "Sigla": record.sigla or "",
                    "Código CNMP": record.code_cnmp or "",
                    "Responsável em exercício": (
                        record.responsavel.pessoa_fisica.social_name
                        if record.responsavel
                        else ""
                    ),
                    "Responsável substituído ": (
                        record.responsible_substituted.pessoa_fisica.social_name
                        if record.responsible_substituted
                        else ""
                    ),
                    "Organograma": "SIM" if record.organograma else "Não",
                    "Lotacionograama": "SIM" if record.lotacionograma else "Não",
                    "Cargo responsável pela Lotação": job_position_responsible,
                    "Classificação do Organograma": record.get_organizational_classification_display()
                    or "",
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class RHEmployeeWorkplaceByWorkplaceManage(RHWorkplaceRestful):

    def json(self, args=[]):
        departament = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            departament = "expediente"
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.managerbyworkplace.Manage", {departament: "%s"})'
            % departament
        )


class RHPendingExercisesByWorkplaceManage(RHWorkplaceRestful):

    def json(self, args=[]):
        departament = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            departament = "expediente"
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.managerbyworkplace.pendingexercises.Manage", {departament: "%s"})'
            % departament
        )

    def get_query(self):
        return (
            super(RHPendingExercisesByWorkplaceManage, self)
            .get_query()
            .filter(~Q(executionorgan=None))
            .exclude(pk__in=Lotacao.workplace_with_exercises())
        )


class RHEmployeeWorkplaceByWorkplaceManageLimited(RHWorkplaceRestful):

    def json(self, args=[]):
        departament = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            departament = "expediente"
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.workassignmentsubstitution.ManageLimited", {departament: "%s"})'
            % departament
        )


class RHWorkplaceMoreThanOne(RHWorkplaceRestful):

    def get_query(self):
        query = super(RHWorkplaceMoreThanOne, self).get_query()
        return (
            query.filter(
                servidores_lotacao__ativo=True,
                servidores_lotacao__designacao=True,
                servidores_lotacao__servidor__tipo="M",
            )
            .annotate(Count("servidores_lotacao"))
            .filter(servidores_lotacao__count__gt=1)
        )


class RHWorkplaceConfigTag(RestfulDRY):

    _model = WorkplaceConfigTag

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

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
        self.response.write('Ext._create("rh.workplace.WorkplaceConfigTagManage")')


class RHWorkplaceAtribuicao(RestfulDRY):

    _model = Atribuicao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workplace.atribuicao.Manage")')


class RHWorkplaceContacts(RHWorkplaceRestful):
    SEDE_E_PROMOTORIA = 6

    full_text_index = RHGeneralOrganRestful.full_text_index + (
        "address__municipio__nome__icontains",
        "address__logradouro__icontains",
    )

    def model_to_dict(self, instance):
        __dict__ = super().model_to_dict(instance)

        phones = [
            phone.get_number_formated() for phone in instance.phone.filter(publico=True)
        ]
        address = instance.address.first()
        __dict__.update(
            {
                "name": capitalize_words(instance.nome),
                "phones": phones,
                "address": (
                    f"{address.get_tipo_logradouro_display()} {address}"
                    if address
                    else "Não informado"
                ),
                "building_kind": str(instance.characteristic or "Não informado"),
            }
        )

        return __dict__

    def get_query(self):
        query = super().get_query()
        query = query.filter(ativo=True, is_contact_displayed=True)

        params = self.get_params(self.request.GET)
        unit_type = params.get("unit_type")

        query = self.do_filter(query)

        if unit_type:
            if unit_type == "1":
                query = query.filter(Q(nome__icontains="Procuradoria"))
            elif unit_type == "2":
                query = query.filter(
                    Q(localidade__nome="PALMAS")
                    & Q(nome__icontains="Promotoria")
                    & Q(organizational_classification=self.SEDE_E_PROMOTORIA)
                )
            elif unit_type == "3":
                query = query.filter(
                    ~Q(localidade__nome="PALMAS") & Q(nome__icontains="Promotoria")
                )
            elif unit_type == "4":
                query = query.filter(
                    Q(localidade__nome="PALMAS")
                    & ~Q(nome__icontains="Promotoria")
                    & ~Q(nome__icontains="Procuradoria")
                )
            else:
                query = query.none()

        return query

    @is_public()
    def fetch_unit_type(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda.", "collection": None}

        unit_type_choices = [
            (1, "Procuradorias de Justiça"),
            (2, "Promotorias de Justiça da Capital"),
            (3, "Promotorias de Justiça do Interior"),
            (4, "Órgãos da Administração superior e órgãos auxiliares"),
        ]

        rst.update(
            success=True,
            message="Processado com sucesso!",
            collection=[("", "Selecione um tipo")] + unit_type_choices,
        )

        self.renderer(rst)

from datetime import datetime
from functools import reduce
from operator import or_
from rest_framework import serializers
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELADO, CANCELED, ENCERRADO, TIPO_FOLHA_ID
from rh.gfp.models import Folha
from rh.models import Servidor, ServidorLotacao
from rh.pvf.const import (
    GROUPS_PVF,
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_EFFECTIVE,
    STS_REJECTED,
    TYPE_OF_LICENSE,
)
from contrib.base_converter import image_to_base64
from rh.models import Servidor, ServidorLotacao
from rh.pvf.const import GROUPS_PVF
from functools import reduce
from operator import or_
from django.db.models.query_utils import Q
from rh.pvf.models import PortalRequestAbsence
from standard.models import Choice
from contrib.utils import getLogger
from rh.pvf.utils.validacoes import validar_substituto_afastamento


log = getLogger(__name__)


class EmployeeCurrentSerializer(serializers.ModelSerializer):
    """
    Serializer do servidor logado
    """

    workplace = serializers.SerializerMethodField()
    jobposition = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    sexo = serializers.SerializerMethodField()
    is_substitutable = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    manager_permission = serializers.SerializerMethodField()
    group_details = serializers.SerializerMethodField()
    group_ids = serializers.SerializerMethodField()
    comp_contracheque = serializers.SerializerMethodField()
    email_pessoal = serializers.SerializerMethodField()
    email_pessoal_verificado = serializers.SerializerMethodField()
    afastamento_ativo = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = [
            "id",
            "name",
            "matricula",
            "workplace",
            "jobposition",
            "user",
            "type_by_possession",
            "sexo",
            "is_substitutable",
            "photo",
            "manager_permission",
            "group_details",
            "group_ids",
            "comp_contracheque",
            "email_pessoal",
            "email_pessoal_verificado",
            "afastamento_ativo",
        ]

    def get_is_substitutable(self, obj):
        if self.replaceable_position(obj) and self.check_optional_substitute(obj):
            return "OPTIONAL"
        elif self.replaceable_position(obj) and not self.check_optional_substitute(obj):
            return "REQUIRED"
        elif validar_substituto_afastamento(obj):
            return "REQUIRED"
        return "NO_REQUIRED"

    def get_workplace(self, obj):
        return obj.workplace_current.nome if obj.workplace_current else None

    def get_jobposition(self, obj):
        return obj.job_position().cargo.nome if obj.job_position() else None

    def get_user(self, obj):
        return obj.user.username if obj.user else None

    def get_sexo(self, obj):
        return obj.pessoa_fisica.sexo

    def get_photo(self, obj):
        if obj.pessoa_fisica.foto:
            return image_to_base64(obj.pessoa_fisica.foto.absolute_path)
        return None

    def get_manager_permission(self, obj):
        return (
            obj.user.controllerpermission_set.filter(manager_permission=True).exists()
            or obj.user.is_superuser
        )

    def get_group_details(self, obj):
        groups = obj.user.groups.all()
        return [{"id": group.id, "name": group.name} for group in groups]

    def get_group_ids(self, obj):
        groups = obj.user.groups.all()
        return [group.id for group in groups]

    def get_comp_contracheque(self, obj):
        tipo_folha = TIPO_FOLHA_ID.get(obj.type_by_possession, 1)
        folha = Folha.objects.filter(
            tipo_folha__pk=tipo_folha, available_pvf=True
        ).first()
        if folha:
            return f"{folha.periodo.mes}/{folha.periodo.ano}"
        return f"{datetime.today().month}/{datetime.today().year}"

    def check_group_adm_superior(self, employee):
        """
        Verifica se o servidor pertence adm superior.
        Args:
            employee (object):instancia do servidor.
        Returns:
            bool: True se o servidor pertence adm superior.
        """
        for group in employee.user.groups.all():
            if group.name == GROUPS_PVF["AS"]:
                return True
        return False

    def check_optional_substitute_local(self, employee):
        """
        Verifica se a lotação do servidor permite substituição opcional.
        Args:
            employee (object):instancia do servidor.
        Returns:
            bool: True se lotação com substiuição opcional.
        """
        try:
            lotacoes_exclude_names = ServidorLotacao.objects.filter(
                servidor=employee, ativo=True, designacao=True
            ).values_list("lotacao__pk")
            labels_lotacoes = [x[0] for x in lotacoes_exclude_names]
            q_object = reduce(or_, (Q(label=int(x)) for x in labels_lotacoes))
            optional_locals = Choice.objects.filter(
                q_object, name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
            )
            if optional_locals:
                if optional_locals.count() == len(labels_lotacoes):
                    return True
        except Exception as e:
            log.error(e)

        return False

    def check_type_optional(self, employee):
        """
        Verifica se o tipo de servidor permite substituição opcional
        Args:
            employee (object):instancia do servidor.
        Returns:
            bool: True se tipo permite substiuição opcional.
        """
        if employee.type_by_possession in [
            "EFE",
            "CMS",
            "ECM",
            "RCM",
            "RFC",
            "EFC",
            "REQ",
            "VOL",
            "EXT",
            "EST",
        ]:
            return True
        return False

    def check_optional_substitute(self, employee):
        if (
            self.check_group_adm_superior(employee)
            or self.check_optional_substitute_local(employee)
            or self.check_type_optional(employee)
        ):
            return True
        return False

    def replaceable_position(self, employee):
        """
        Verifica se o servidor possui cargo de substituível "
        Args:
            employee (object):instancia do servidor.
        Returns:
            object(exercise) | None.
        """
        exercise = None
        if employee.tipo == "M":
            choices = Choice.objects.filter(
                name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
            ).values_list("label")

            exercise = ServidorLotacao.objects.filter(
                servidor=employee,
                ativo=True,
                designacao=True,
                responsible=True,
                owner=True,
            ).exclude(lotacao__pk__in=[int(x[0]) for x in choices])
        else:
            exercise = ServidorLotacao.objects.filter(
                ativo=True,
                designacao=True,
                servidor=employee,
                movimentacao_posse__quadro__cargo__chefia=True,
            )
        return exercise

    def get_email_pessoal_verificado(self, obj):
        return obj.pessoa_fisica.email_pessoal_verificado

    def get_email_pessoal(self, obj):
        return obj.pessoa_fisica.email_pessoal

    def get_afastamento_ativo(self, obj):
        hoje = datetime.now().date()
        base_afastamento = (
            BaseLicencaAfastamento.objects.filter(
                data_inicio__lte=hoje, data_fim__gte=hoje, servidor=obj
            )
            .exclude(estado__in=[CANCELADO, ENCERRADO])
            .first()
        )
        if base_afastamento:
            data_inicio = base_afastamento.data_inicio.strftime("%d/%m/%Y")
            data_fim = base_afastamento.data_fim.strftime("%d/%m/%Y")
            return f"{base_afastamento.get_texto()} de {data_inicio} à {data_fim}"

        afastamento_portal = (
            PortalRequestAbsence.objects.filter(
                employee=obj, start_date__lte=hoje, end_date__gte=hoje
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            .first()
        )
        if afastamento_portal:
            nome_afastamento = TYPE_OF_LICENSE.get(afastamento_portal.type)
            data_inicio = afastamento_portal.start_date.strftime("%d/%m/%Y")
            data_fim = afastamento_portal.end_date.strftime("%d/%m/%Y")
            return f"{nome_afastamento} de {data_inicio} à {data_fim}"

        return None

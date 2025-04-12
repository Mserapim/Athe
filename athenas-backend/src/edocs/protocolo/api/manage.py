# -*- coding: utf-8 -*-
import ast
import re
import json

from django.db.models import (
    Q,
    F,
    Case,
    When,
    Value,
    CharField,
    BooleanField,
    Func,
    IntegerField,
)
from django.db import transaction
from django.db.models.functions import Concat
from django.template.defaultfilters import striptags
from django.contrib.postgres.aggregates import StringAgg

from contrib.nil import nil_datetime
from contrib.controller import DefaultController
from contrib.utils import (
    getLogger,
    DateUtils,
    user_from_person,
    employee_from_user,
    person_from_user,
)
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from edocs.protocolo.utils import EDOCBoxQuery
from rh.models import Documento, Pessoa, OrgaoGeral, Lotacao
from edocs.protocolo.models import Movimentacao, TipoDocumento, Protocolo, Attachment


log = getLogger("base-athenas")


class EDOCManage(DefaultController):

    _model = Protocolo

    @property
    def Model(self):
        return self._model

    def _filter_eval_value(self, value):
        date_test = re.compile(r"\d{2}\/\d{2}\/\d{4}")
        datetime_test = re.compile(r"\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}")

        if isinstance(value, str):
            if not value or value == "":
                return None
            elif value in ("false", "off"):
                return False
            elif value in ("true", "on"):
                return True
            elif datetime_test.match(value):
                return DateUtils.str_to_datetime(value)
            elif date_test.match(value):
                return DateUtils.str_to_date(value)

        return value

    def do_filter(self, query, str_filter):
        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = str_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:
            stages = {}
            for f in flist:
                stage = int(f.get("stage", 0) or 0)
                stage_list = stages.get(stage, [])
                stage_list.append(f)
                stages.update({stage: stage_list})

            for key in sorted(stages.keys()):
                stage_list = stages.get(key)
                fquery = None

                for part in stage_list:
                    fquery = Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))

                if fquery is not None and key >= 0:
                    query = query.filter(fquery)
                elif fquery is not None and key < 0:
                    query = query.exclude(fquery)

        return query

    def _get_distinct_movements_by_protocol(self):
        dictionary = {}
        pkset = self.request.POST.getlist("pkset")
        queryset = Movimentacao.outbox_queryset()
        for movement in queryset.filter(pk__in=pkset):
            dictionary.update({movement.protocolo.pk: movement})
        movements = list(dictionary.values())
        return movements

    def _get_custom_message(self, message):
        message = ["- " + i for i in message]
        message.insert(0, "Ocorreram os seguintes erros durante o processamento:<br>")
        message = str("<br>".join(message))
        return message

    def undo_send(self, args=[]):
        result = {"success": False, "message": "Nothing done yet."}

        try:
            message = []
            movements = self._get_distinct_movements_by_protocol()
            for movement in movements:
                if movement.child_of:
                    try:
                        with transaction.atomic():
                            movement.child_of.undo()
                    except Exception as e:
                        message.append(str(e))

            if len(message):
                raise Exception(self._get_custom_message(message))

        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(success=True, message="Envios desfeitos com sucesso.")

        self.renderer(result)

    def undo_send_specific(self, args=[]):
        result = {"success": False, "message": "Nothing done yet."}

        try:
            pkset = self.request.POST.get("pkset")
            queryset = Movimentacao.outbox_queryset()
            movement = queryset.filter(pk=pkset).first()

            if movement:
                with transaction.atomic():
                    movement.undo_specific()
            else:
                raise Exception(
                    "Não foi possível desfazer o envio. " + "Item não localizado."
                )
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(success=True, message="Envios desfeitos com sucesso.")

        self.renderer(result)

    def send(self, args=[]):
        result = {"success": False, "message": "Nothing done yet."}

        try:
            params = self.normalize_params()
            params.pop("movement")
            params.update(use_async=True)

            if "physical" not in params:
                raise Exception(
                    "Informe se o envio do documento será por meio eletrônico e/ou por meio físico"
                )
            else:
                params.update(
                    physical=True if params.get("physical").lower() == "true" else False
                )

            if "opinion" in params:
                params.update(opinion=params.get("opinion", "off").lower() == "on")

            if "urgency" in params:
                params.update(urgency=params.get("urgency", "off").lower() == "on")

            if "close" in params:
                params.update(close=params.get("close", "off").lower() == "on")

            pkset = self.request.POST.getlist("movement")

            query = (
                Movimentacao.inbox_queryset()
                .filter(pk__in=pkset)
                .select_related("protocolo__interessado", "lotacao_destino")
            )

            if query.exists():
                with transaction.atomic():
                    for movement in query:
                        if movement.with_workflow:
                            raise Exception(
                                "Operação não permitida para o protocolo %s."
                                % movement.protocolo.codigo
                            )
                        movement.do_send(**params)
            else:
                raise Exception(
                    "Os protocolos selecionados não estão mais na sua caixa de entrada. Atualize sua caixa."
                )
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(success=True, message="Movimentações realizadas com sucesso.")

        self.renderer(result)

    def read_movement(self, request, args=[]):
        result = {"success": False, "message": "nada foi feito ainda"}

        try:
            movement = Movimentacao.inbox_queryset().get(pk=self.request.POST.get("pk"))
        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Informações localizadas com sucesso.",
                instance=self.model_to_dict(movement),
            )

        self.renderer(result)

    def prepare_params(self, querydict):
        params = querydict.dict()
        employee = employee_from_user(self.request.user)

        if "interested" in params and employee.general_protocol:
            params.update(interested=Pessoa.objects.get(id=params.get("interested")))
        else:
            params.update(interested=employee.pessoa_fisica)

        if not params.get("document_type", False):
            raise Exception("Por favor preencha o campo Tipo.")
        else:
            params.update(
                document_type=TipoDocumento.objects.get(pk=params.get("document_type"))
            )

        if not params.get("home_court", False):
            workplace_active = employee.workplace_only_active
            if employee.work_assignment.exists() or not workplace_active.exists():
                raise Exception("Por favor preencha o campo Origem.")
            elif workplace_active.exists():
                params.update(home_court=workplace_active.first().lotacao)
        elif employee.general_protocol:
            params.update(
                home_court=OrgaoGeral.objects.get(pk=params.get("home_court"))
            )
        else:
            params.update(
                home_court=employee.work_locations_effective_exercise.get(
                    pk=params.get("home_court")
                ).orgaogeral_ptr
            )

        if not params.get("subject", False):
            raise Exception("Por favor preencha o campo Assunto")

        return params

    def undocketing(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
        }

        try:
            with transaction.atomic():
                for protocol in self.Model.objects.filter(
                    movimentacoes__in=self.request.POST.getlist("pkset")
                ).distinct():
                    if protocol.movimentacoes.filter(passo__gt=0).exists():
                        log.debug(self.request.POST.getlist("pkset"))
                        log.debug(protocol.codigo)
                        log.debug(
                            [
                                m.passo
                                for m in protocol.movimentacoes.filter(passo__gt=0)
                            ]
                        )
                        raise Exception(
                            "Não posso remover um protocolo que já foi movimentado."
                        )
                    else:
                        protocol.movimentacoes.all().delete()
                        protocol.delete()  # This will do a cascade deletion on any associated Control instance
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Protocolos removidos com sucesso.")

        self.renderer(rst)

    def docketing(self, args=[]):
        result = {
            "success": False,
            "message": "Nada foi feito ainda",
        }

        try:
            protocol = self.Model.docketing(**self.prepare_params(self.request.POST))
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Protocolizado com sucesso.",
                instance={
                    "code": protocol.codigo,
                    "pk": protocol.movimentacoes.order_by("passo").last().pk,
                    "confidential": protocol.sigiloso,
                    "protocol": protocol.pk,
                },
            )

        self.renderer(result)

    def document_type(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        query = TipoDocumento.objects.filter(habilita=True)
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=query.count(),
            collection=[
                {"pk": document_type.pk, "description": str(document_type)}
                for document_type in query.filter()
            ],
        )

        self.renderer(rst)

    def work_locations(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception("Servidor não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=employee.work_locations_effective_exercise.count(),
                collection=[
                    {"pk": wl.pk, "description": str(wl)}
                    for wl in employee.work_locations_effective_exercise
                ],
            )

        self.renderer(rst)

    def undo_close(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            inbox = Movimentacao.closedbox_queryset().filter(pk__in=pkset)

            if inbox.count() == len(set(pkset)):
                with transaction.atomic():
                    for moviment in inbox:
                        if not moviment.with_workflow:
                            moviment.undo_close()
                        else:
                            raise Exception(
                                "Operação não permitida para o protocolo %s."
                                % moviment.protocolo.codigo
                            )
            else:
                rst.update(
                    message="Um ou mais protocolos não estão em sua caixa de finalizados."
                )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Todas finalizações foram desfeitas.")

        self.renderer(rst)

    def close_protocol(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            inbox = Movimentacao.inbox_queryset().filter(pk__in=pkset)

            if inbox.count() == len(set(pkset)):
                with transaction.atomic():
                    for moviment in inbox:
                        if not moviment.with_workflow:
                            moviment.do_close()
                        else:
                            raise Exception(
                                "Operação não permitida para o protocolo %s."
                                % moviment.protocolo.codigo
                            )
            else:
                rst.update(
                    message="Um ou mais protocolos não estão em sua caixa de entrada."
                )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Todos os protocolos foram finalizados.")

        self.renderer(rst)

    def sign_received(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing done yet",
            "personal": False,
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            log.info(self.request.POST)

            inbox = Movimentacao.inbox_queryset().filter(pk__in=pkset)

            if inbox.count() != len(set(pkset)):
                raise Exception(
                    "Um ou mais protocolos não estão em sua caixa de entrada."
                )

            with transaction.atomic():
                for moviment in inbox:
                    if moviment.with_workflow:
                        raise Exception(
                            f"Operação não permitida para o protocolo {moviment.protocolo.codigo}."
                        )

                    if not moviment.protocolo.can_read:
                        raise Exception(
                            "Não foi possível receber a movimentação, pois o "
                            "interessado ou um dos destinatários classificou "
                            f"o protocolo {moviment.protocolo.codigo} "
                            "restringindo seu acesso."
                        )

                    employee = employee_from_user(self.request.user, True)
                    work_locations = employee.work_locations_effective_exercise

                    if not work_locations.exists() and employee.membro:
                        work_locations = Lotacao.objects.filter(
                            pk__in=employee.owner_locations.values("lotacao")
                        )

                    if not work_locations.exists():
                        raise Exception("Você não possui nenhum exercício ativo.")

                    if moviment.is_personal_sending() and moviment.is_unique_exercise():
                        # SE O SERVIDOR TIVER APENAS UMA LOTACAO, JÁ RECEBE AUTOMATICAMENTE POR ELA
                        moviment.lotacao_destino = work_locations[0]
                        # moviment.destinatario = None
                        moviment.sign_received()
                    elif moviment.is_personal_sending():
                        # MOVIMENTACAO PARA PESSOA
                        result.update(personal=True)
                        if not self.request.POST.get("department"):
                            # SE FOI ENVIADO PARA PESSOA E ELA NAO INFORMOU UM DEPARTAMENTO PARA RECEBER O E-DOC
                            raise Exception(
                                "Informe um local de trabalho para receber o documento."
                            )

                        # É PESSOAL E FOI INFORMADO DEPARTAMENTO PARA RECEBER. RECEBER O E-DOC PELA LOTACAO INFORMADA NA JANELA
                        department = OrgaoGeral.objects.get(
                            pk=self.request.POST.get("department")
                        )
                        if department.lotacao not in work_locations:
                            raise Exception("Informe um local de trabalho válido.")

                        moviment.lotacao_destino = department
                        # moviment.destinatario = None
                        moviment.sign_received()
                    else:
                        # MOVIMENTACAO PARA DEPARTAMENTO
                        moviment.sign_received()
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(success=True, message="Todos os protocolos foram recebidos.")

        self.renderer(result)

    def sign_receive_closed(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            inbox = Movimentacao.closedbox_queryset().filter(pk__in=pkset)

            if inbox.count() == len(set(pkset)):
                for moviment in inbox:
                    moviment.sign_received()
            else:
                rst.update(
                    message="Um ou mais protocolos não estão em sua caixa de finalizado."
                )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Todos os protocolos foram recebidos.")

        self.renderer(rst)

    def sign_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            inbox = Movimentacao.inbox_queryset().filter(pk__in=pkset)

            if inbox.count() == len(set(pkset)):
                with transaction.atomic():
                    for moviment in inbox:
                        moviment.sign_document()
            else:
                rst.update(
                    message="Um ou mais documentos não estão em sua caixa de entrada."
                )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Todos os documentos foram recebidos.")

        self.renderer(rst)

    def status_signature_document(self, args=[]):
        rst = {
            "signature": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = int(self.request.POST.get("pkset") or 0)
            inbox = Movimentacao.inbox_queryset().filter(pk=pkset).first()
            if inbox:
                if inbox.protocolo.valid_signatures.exists():
                    rst.update(
                        signature=True, message="O documento encontra-se assinado."
                    )
                else:
                    rst.update(message="O documento não encontra-se assinado.")

        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def sign_unreceived(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkset = self.request.POST.getlist("pkset")
            inbox = Movimentacao.inbox_queryset().filter(pk__in=pkset)

            if inbox.count() == len(set(pkset)):
                for moviment in inbox:
                    moviment.sign_unreceived()
            else:
                rst.update(
                    message="Um ou mais protocolos não estão em sua caixa de entrada."
                )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Todos os protocolos foram recebidos.")

        self.renderer(rst)

    def renderer(self, params):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.dumps(params))

    def json(self, args=[]):

        cfg = {"generalProtocol": False}

        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.protocolo.Manage", %s)' % json.dumps(cfg)
        )

    def box_to_dict(self, box, start, limit):
        aux = box[start : (start + limit)].values_list("pk", flat=True)

        box = (
            box.filter(pk__in=aux)
            .prefetch_related("protocolo__out_court_lawsuits")
            .annotate(
                step=F("passo"),
                code=F("protocolo__codigo"),
                seal_number=F("protocolo__chancela"),
                media=F("protocolo__midia"),
                external_number=F("protocolo__protocolo_externo"),
                home_court=F("lotacao_origem_id"),
                home_court_unicode=F("lotacao_origem__nome"),
                protocol=F("protocolo_id"),
                interested=F("protocolo__interessado_id"),
                interested_unicode=F("protocolo__interessado__nome"),
                document_type=F("protocolo__tipo_documento_id"),
                document_type_unicode=F("protocolo__tipo_documento__nome"),
                confidentials=F("protocolo__sigiloso"),
                content=F("protocolo__resumo"),
                content_stripedtags=F("protocolo__resumo"),
                from_location=F("lotacao_origem__nome"),
                from_person=F("servidor_origem__pessoa_fisica__nome"),
                special_type=F("protocolo__special_type"),
                user=F("servidor_origem__user_id"),
                reopen_by_unicode=F("reopen_by"),
                processos=StringAgg(
                    "protocolo__out_court_lawsuits__cache_number", delimiter="; "
                ),
                removed_by=F("protocolo__out_court_lawsuits__removed_by"),
                protocol_unicode=Concat(
                    "protocolo__codigo",
                    Value("-"),
                    "protocolo__assunto",
                    output_field=CharField(),
                ),
                reopenat=Func(
                    F("reopen_at"),
                    Value("DD/MM/YYYY HH24:MI"),
                    function="to_char",
                    output_field=CharField(),
                ),
                send_date=Func(
                    F("data_encaminhamento"),
                    Value("DD/MM/YYYY HH24:MI"),
                    function="to_char",
                    output_field=CharField(),
                ),
                is_read=Case(
                    When(data_recebimento__isnull=True, then=False),
                    default=True,
                    output_field=BooleanField(),
                ),
                subject=Case(
                    # quando is_delivery_pending == True e sem assunto
                    When(
                        envelops__delivery_state__in=[1, 2],
                        protocolo__assunto__isnull=True,
                        then=Concat(
                            Value("[ENVIO EM PROCESSAMENTO] "), Value("Sem assunto")
                        ),
                    ),
                    # quando is_delivery_pending == True e com assunto
                    When(
                        envelops__delivery_state__in=[1, 2],
                        protocolo__assunto__isnull=False,
                        then=Concat(
                            Value("[ENVIO EM PROCESSAMENTO] "), "protocolo__assunto"
                        ),
                    ),
                    # quando não possuí assunto e is_delivery_pending == False
                    When(protocolo__assunto__isnull=True, then=Value("Sem assunto")),
                    default="protocolo__assunto",
                    output_field=CharField(),
                ),
                withworkflow=Case(
                    When(with_workflow=True, then=True),
                    When(envelops__delivery_state__in=[1, 2], then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
                control=Case(
                    When(
                        protocolo__protocol_control__pk__isnull=False,
                        then="protocolo__protocol_control__pk",
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
                control_type=Case(
                    When(
                        protocolo__protocol_control__control_type__pk__isnull=False,
                        then="protocolo__protocol_control__control_type__pk",
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
                legal_prerogative=Case(
                    When(
                        protocolo__protocol_control__legal_prerogative_id__isnull=False,
                        then="protocolo__protocol_control__legal_prerogative_id",
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
                is_committed=Case(
                    When(
                        protocolo__protocol_control__control_type__is_secret__isnull=False,
                        then="protocolo__protocol_control__control_type__is_secret",
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                is_secret=Case(
                    When(
                        protocolo__protocol_control__control_type__is_secret__isnull=False,
                        then="protocolo__protocol_control__control_type__is_secret",
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                read_icon=Case(
                    When(
                        data_recebimento__isnull=False,
                        envelops__delivery_state__in=[1, 2],
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-in-delivery', "
                            "'title': 'Em processo de envio'}"
                        ),
                    ),
                    When(
                        data_recebimento__isnull=False,
                        servidor_destino__matricula__isnull=False,
                        then=(
                            Concat(
                                Value(
                                    "{ 'iconCls': 'icon-edocs icon-protocolo-read', 'title': 'Recebido por "
                                ),
                                "servidor_destino__matricula",
                                Value(":"),
                                "servidor_destino__pessoa_fisica__nome",
                                Value("'}"),
                            )
                        ),
                    ),
                    When(
                        data_recebimento__isnull=False,
                        servidor_destino__matricula_origem__isnull=False,
                        then=(
                            Concat(
                                Value(
                                    "{ 'iconCls': 'icon-edocs icon-protocolo-read', 'title': 'Recebido por "
                                ),
                                "servidor_destino__matricula_origem",
                                Value(":"),
                                "servidor_destino__pessoa_fisica__nome",
                                Value("'}"),
                            )
                        ),
                    ),
                    default=Value(
                        "{'iconCls': 'icon-edocs icon-protocolo-unread', "
                        "'title': 'Ainda não foi recebido'}"
                    ),
                    output_field=CharField(),
                ),
                urgente_icon=Case(
                    When(
                        urgente__exact=True,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-urgent', "
                            "'title': 'Este protocolo tem pedido de urgência'}"
                        ),
                    ),
                    default=Value(
                        "{'iconCls': 'icon-edocs icon-protocolo-empty', "
                        "'title': 'Este protocolo não possui pedido de urgência'}"
                    ),
                    output_field=CharField(),
                ),
                attach_icon=Case(
                    When(
                        protocolo__attachments__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-attaches', "
                            "'title': 'Este protocolo possui anexos'}"
                        ),
                    ),
                    default=Value(
                        "{'iconCls': 'icon-edocs icon-protocolo-no-attaches',"
                        "'title': 'Este protocolo não possui anexos'}"
                    ),
                    output_field=CharField(),
                ),
                closed_protocol_icon=Case(
                    When(
                        protocolo__data_finalizado__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-close-protocol', "
                            "'title': 'Protocolo finalizado.'}"
                        ),
                    ),
                    When(
                        passo=0,
                        then=Value(
                            "{'iconCls': 'icon-core icon-core-edit', "
                            "'title': 'Protocolo em processo de construção'}"
                        ),
                    ),
                    default=Value(
                        "{'iconCls': 'icon-edocs icon-protocolo-empty', "
                        "'title': 'Protocolo em andamento.'}"
                    ),
                    output_field=CharField(),
                ),
                confidential_icon=Case(
                    When(
                        protocolo__sigiloso=True,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-confidential', "
                            "'title': 'Este protocolo é sigiloso'}"
                        ),
                    ),
                    default=Value(
                        "{'iconCls': 'icon-edocs icon-protocolo-empty', "
                        "'title': 'Este protocolo não é sigiloso'}"
                    ),
                    output_field=CharField(),
                ),
                workflow_icon=Case(
                    When(
                        with_workflow=True,
                        protocolo__out_court_lawsuits__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-locked', 'title': 'Processos(s):' }"
                        ),
                    ),
                    When(
                        with_workflow=True,
                        protocolo__solicitacao__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-locked', "
                            "'title': 'Solicitação de viagem' }"
                        ),
                    ),
                    When(
                        with_workflow=True,
                        protocolo__processo__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-locked', "
                            "'title': 'Processo Administravito' }"
                        ),
                    ),
                    When(
                        with_workflow=True,
                        protocolo__attendance__isnull=False,
                        then=Value(
                            "{'iconCls': 'icon-edocs icon-protocolo-locked', "
                            "'title': 'Atendimento ao público' }"
                        ),
                    ),
                    default=Value("{'iconCls': 'icon-edocs icon-protocolo-empty'}"),
                    output_field=CharField(),
                ),
                send_to=Case(
                    When(destinatario__isnull=False, then="destinatario_id"),
                    default="lotacao_destino_id",
                    output_field=CharField(),
                ),
                send_to_unicode=Case(
                    When(destinatario__isnull=False, then="destinatario__nome"),
                    default="lotacao_destino__nome",
                    output_field=CharField(),
                ),
            )
            .values(
                "pk",
                "step",
                "read_icon",
                "urgente_icon",
                "attach_icon",
                "workflow_icon",
                "closed_protocol_icon",
                "is_read",
                "confidential_icon",
                "code",
                "seal_number",
                "media",
                "external_number",
                "subject",
                "home_court",
                "home_court_unicode",
                "protocol",
                "protocol_unicode",
                "interested",
                "interested_unicode",
                "document_type",
                "document_type_unicode",
                "confidential",
                "withworkflow",
                "content",
                "content_stripedtags",
                "from_location",
                "from_person",
                "send_to",
                "send_to_unicode",
                "special_type",
                "send_date",
                "reopen_by_unicode",
                "reopenat",
                "user",
                "control",
                "control_type",
                "legal_prerogative",
                "is_committed",
                "is_secret",
                "processos",
                "removed_by",
            )
        )
        lenght = len(box)
        for item in range(0, lenght):
            workflow_icon = ast.literal_eval(box[item]["workflow_icon"].strip())
            processos = box[item]["processos"]
            if processos and not box[item]["removed_by"]:
                workflow_icon["title"] = f"Processo(s): {processos}"
            box[item]["content_stripedtags"] = striptags(
                box[item]["content_stripedtags"] or ""
            )
            box[item]["icons"] = [
                ast.literal_eval(box[item]["read_icon"].strip()),
                ast.literal_eval(box[item]["urgente_icon"].strip()),
                ast.literal_eval(box[item]["attach_icon"].strip()),
                workflow_icon,
                ast.literal_eval(box[item]["closed_protocol_icon"].strip()),
                {"iconCls": "icon-edocs icon-protocolo-empty"},
                ast.literal_eval(box[item]["confidential_icon"].strip()),
            ]

        return list(box)

    def model_to_dict(self, instance):
        send_to = instance.lotacao_destino or instance.destinatario
        send_to_unicode = str(instance.lotacao_destino or instance.destinatario)

        subject = (
            instance.protocolo.assunto if instance.protocolo.assunto else "Sem assunto"
        )
        if instance.is_delivery_pending:
            subject = "[ENVIO EM PROCESSAMENTO] {}".format(subject)

        control = self.control_to_dict(protocol=instance.protocolo)

        data = {
            "pk": instance.pk,
            "step": instance.passo,
            "icons": self.extract_icons(instance),
            "is_read": (instance.data_recebimento is not None),
            "code": instance.protocolo.codigo,
            "seal_number": instance.protocolo.chancela,
            "media": instance.protocolo.midia,
            "external_number": instance.protocolo.protocolo_externo,
            "subject": subject,
            "home_court": instance.lotacao_origem.pk,
            "home_court_unicode": instance.lotacao_origem.nome,
            "protocol": instance.protocolo.pk,
            "protocol_unicode": str(instance.protocolo),
            "interested": instance.protocolo.interessado.pk,
            "interested_unicode": str(instance.protocolo.interessado),
            "document_type": instance.protocolo.tipo_documento.pk,
            "document_type_unicode": instance.protocolo.tipo_documento.nome,
            "confidential": instance.protocolo.sigiloso,
            "with_workflow": instance.with_workflow or instance.is_delivery_pending,
            "content": instance.protocolo.resumo,
            "content_stripedtags": striptags(instance.protocolo.resumo or ""),
            "from_location": str(instance.lotacao_origem.nome),
            "from_person": str(instance.servidor_origem.pessoa_fisica),
            "send_to": send_to.pk,
            "send_to_unicode": send_to_unicode,
            "special_type": instance.protocolo.special_type,
            "send_date": nil_datetime(instance.data_encaminhamento, None),
            "reopen_by_unicode": str(instance.reopen_by) if instance.reopen_by else "",
            "reopen_at": nil_datetime(instance.reopen_at, None),
            "user": (
                instance.servidor_origem.user_id if instance.servidor_origem else None
            ),
            # Controle de Acesso (app document_access)
            "control": control.get("control"),
            "control_type": control.get("control_type"),
            "legal_prerogative": control.get("legal_prerogative"),
            "is_committed": control.get("is_committed"),
            "is_secret": control.get("is_secret"),
        }

        user = user_from_person(instance.protocolo.interessado)
        if user:
            data.update({"user": user.id, "user_unicode": user.username})

        return data

    def __extract_read_icon(self, inst):
        rst = {
            "iconCls": "icon-edocs icon-protocolo-unread",
            "title": "Ainda não foi recebido",
        }

        if inst.data_recebimento:
            if inst.is_delivery_pending:
                rst = {
                    "iconCls": "icon-edocs icon-protocolo-in-delivery",
                    "title": "Em processo de envio",
                }
            else:
                rst = {
                    "iconCls": "icon-edocs icon-protocolo-read",
                    "title": "Recebido por %s" % inst.servidor_destino,
                }

        return rst

    def __extract_attach_icon(self, inst):
        attaches = Attachment.objects.filter(protocol=inst.protocolo).exists()

        if attaches:
            return {
                "iconCls": "icon-edocs icon-protocolo-attaches",
                "title": "Este protocolo possui anexos",
            }
        else:
            return {
                "iconCls": "icon-edocs icon-protocolo-no-attaches",
                "title": "Este protocolo não possui anexos",
            }

    def __extract_confidential_icon(self, inst):
        if inst.protocolo.sigiloso:
            return {
                "iconCls": "icon-edocs icon-protocolo-confidential",
                "title": "Este protocolo é sigiloso",
            }
        else:
            return {
                # 'iconCls': 'icon-edocs icon-protocolo-no-confidential',
                "iconCls": "icon-edocs icon-protocolo-empty",
                "title": "Este protocolo não é sigiloso",
            }

    def __extract_empty_icon(self):
        return {
            "iconCls": "icon-edocs icon-protocolo-empty",
        }

    def __extract_urgent_icon(self, inst):
        if inst.urgente:
            return {
                "iconCls": "icon-edocs icon-protocolo-urgent",
                "title": "Este protocolo tem pedido de urgência",
            }
        else:
            return {
                "iconCls": "icon-edocs icon-protocolo-empty",
                "title": "Este protocolo não possui pedido de urgência",
            }

    def __extract_closed_protocol_icon(self, inst):
        if inst.protocolo.data_finalizado:
            return {
                "iconCls": "icon-edocs icon-protocolo-close-protocol",
                "title": "Protocolo finalizado.",
            }
        else:
            return {
                "iconCls": "icon-edocs icon-protocolo-empty",
                "title": "Protocolo em andamento.",
            }

    def __extract_editing_icon(self, inst):
        if inst.protocolo.movimentacoes.count() == 1:
            return {
                "iconCls": "icon-core icon-core-edit",
                "title": "Protocolo em processo de construção",
            }
        return {}

    def __extract_editing_closed_icon(self, inst):
        icon = self.__extract_editing_icon(inst)
        if not icon:
            icon = self.__extract_closed_protocol_icon(inst)
        return icon

    def __extract_with_workflow_icon(self, inst):
        icon = self.__extract_empty_icon()

        if inst.with_workflow:
            icon = {
                "iconCls": "icon-edocs icon-protocolo-locked",
                "title": "desconhecido",
            }

            if inst.protocolo.out_court_lawsuits.exists():
                icon.update(
                    title="Processo(s): %s"
                    % ", ".join(
                        o.cache_number
                        for o in inst.protocolo.out_court_lawsuits.filter(
                            removed_by=None
                        )
                    )
                )
            elif hasattr(inst.protocolo, "solicitacao"):
                icon.update(title="Solicitação de Viagem")
            elif hasattr(inst.protocolo, "processo"):
                icon.update(title="Processo Administrativo")
            elif hasattr(inst.protocolo, "attendance"):
                icon.update(title="Atendimento ao Público")

        return icon

    def extract_icons(self, inst):
        return [
            self.__extract_read_icon(inst),
            self.__extract_urgent_icon(inst),
            self.__extract_attach_icon(inst),
            self.__extract_with_workflow_icon(inst),
            self.__extract_editing_closed_icon(inst),
            self.__extract_empty_icon(),
            self.__extract_confidential_icon(inst),
        ]

    def page_box(self, box, start, limit):
        return box[start : (start + limit)]

    def extract_box(self, box, start, limit):
        collections = [
            self.model_to_dict(inst) for inst in self.page_box(box, start, limit)
        ]
        # collections = self.box_to_dict(box, start, limit)

        data = {
            "success": True,
            "message": "tudo certo",
            "count": box.count(),
            "unReadCount": box.filter(data_recebimento=None).count(),
            "collection": collections,
        }
        return data

    def do_keyword_filter(self, query, keyword):
        """Performs keyword filter using SearchVector"""
        striped_keyword = keyword.strip()
        if striped_keyword != "":
            raw_search_query = EDOCBoxQuery.raw_search_query(striped_keyword)
            query = query.filter(protocolo__search_vector=raw_search_query)
        return query

    def inbox(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "collection": [],
            "count": 0,
        }

        try:
            inbox = Movimentacao.inbox_queryset()
            str_filter = self.request.GET.get("filter", None)
            if str_filter:
                inbox = self.do_filter(inbox, json.loads(str_filter))
            if "keyword" in list(self.request.GET.keys()):
                inbox = self.do_keyword_filter(inbox, self.request.GET.get("keyword"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            start = int(self.request.GET.get("start") or 0)
            limit = int(self.request.GET.get("limit") or 30)

            rst.update(**self.extract_box(inbox, start, limit))

        self.renderer(rst)

    def inbox_person(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "collection": [],
            "count": 0,
        }

        try:
            inbox = Movimentacao.inbox_queryset().filter(
                destinatario=person_from_user(self.request.user)
            )
            str_filter = self.request.GET.get("filter", None)
            if str_filter:
                inbox = self.do_filter(inbox, json.loads(str_filter))
            if "keyword" in list(self.request.GET.keys()):
                inbox = self.do_keyword_filter(inbox, self.request.GET.get("keyword"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            start = int(self.request.GET.get("start") or 0)
            limit = int(self.request.GET.get("limit") or 30)

            rst.update(**self.extract_box(inbox, start, limit))

        self.renderer(rst)

    def sharebox(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "collection": [],
            "count": 0,
        }

        try:
            sharebox = Movimentacao.inbox_queryset()
            str_filter = self.request.GET.get("filter", None)
            if str_filter:
                sharebox = self.do_filter(sharebox, json.loads(str_filter))
            if "keyword" in list(self.request.GET.keys()):
                sharebox = self.do_keyword_filter(
                    sharebox, self.request.GET.get("keyword")
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            start = int(self.request.GET.get("start") or 0)
            limit = int(self.request.GET.get("limit") or 30)

            rst.update(**self.extract_box(sharebox, start, limit))

        self.renderer(rst)

    def outbox(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "collection": [],
            "count": 0,
        }

        try:
            outbox = Movimentacao.outbox_queryset()
            str_filter = self.request.GET.get("filter", None)
            if str_filter:
                outbox = self.do_filter(outbox, json.loads(str_filter))
            if "keyword" in list(self.request.GET.keys()):
                outbox = self.do_keyword_filter(outbox, self.request.GET.get("keyword"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            start = int(self.request.GET.get("start") or 0)
            limit = int(self.request.GET.get("limit") or 30)

            rst.update(**self.extract_box(outbox, start, limit))

        self.renderer(rst)

    def closedbox(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "collection": [],
            "count": 0,
        }

        try:
            closedbox = Movimentacao.closedbox_queryset()
            str_filter = self.request.GET.get("filter", None)
            if str_filter:
                closedbox = self.do_filter(closedbox, json.loads(str_filter))
            if "keyword" in list(self.request.GET.keys()):
                closedbox = self.do_keyword_filter(
                    closedbox, self.request.GET.get("keyword")
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            start = int(self.request.GET.get("start") or 0)
            limit = int(self.request.GET.get("limit") or 30)

            rst.update(**self.extract_box(closedbox, start, limit))

        self.renderer(rst)

    def control_to_dict(self, protocol):
        result = {
            "control": 0,
            "control_type": 0,
            "legal_prerogative": 0,
            "is_committed": False,
            "is_secret": False,
        }

        control = getattr(protocol, "protocol_control", None)
        if control:
            result.update(
                {
                    "control": control.pk,
                    "control_type": (
                        control.control_type.pk if control.control_type else 0
                    ),
                    "legal_prerogative": (
                        control.legal_prerogative.pk if control.legal_prerogative else 0
                    ),
                    "is_committed": control.is_secret,
                    "is_secret": (
                        control.control_type.is_secret
                        if control.control_type
                        else False
                    ),
                }
            )

        return result

    def normalize_params(self):
        params = {}
        for key in list(self.request.REQUEST.keys()):
            value = self.request.REQUEST.getlist(key)
            if len(value) > 1:
                params.update({key: value})
            else:
                params.update({key: value[0]})
        return params

    def validate_control_params(self, params):
        if not params.get("movement"):
            raise Exception("Não posso classificar um protocolo sem o id do protocolo.")

        if isinstance(params.get("movement"), list):
            raise Exception(
                "Não posso classificar uma informação durante uma movimentação que envolva mais de um protocolo."
            )

        if not params.get("control_type"):
            raise Exception(
                "Não posso classificar uma informação sem um Nível de Acesso."
            )

        if not params.get("legal_prerogative"):
            raise Exception(
                "Não posso classificar uma informação sem uma Hipótese Legal."
            )

        if not params.get("justification"):
            raise Exception(
                "Não posso classificar uma informação sem uma Justificativa."
            )

    def access_control(self, args=[]):
        from edocs.protocolo.signals.custom import access_control_signal

        result = {"success": False, "message": "Nothing done yet!"}

        try:
            params = self.normalize_params()
            self.validate_control_params(params)

            if "is_committed" in params:
                params.update(is_committed=params.get("is_committed").lower() == "on")

            movement = Movimentacao.objects.get(pk=params.get("movement"))

            access_control_signal.send(
                sender=Protocolo,
                protocol=movement.protocolo,
                control_type_id=params.get("control_type"),
                legal_prerogative_id=params.get("legal_prerogative"),
                justification=params.get("justification"),
                is_committed=params.get("is_committed", True),
            )
        except Exception as e:
            result.update(message=str(e))
        else:
            control = self.control_to_dict(movement.protocolo)
            result.update(
                {
                    "success": True,
                    "message": "Controle configurado com sucesso!",
                    "instance": {
                        "movement": movement.pk,
                        "control": control.get("control"),
                        "control_type": control.get("control_type"),
                        "legal_prerogative": control.get("legal_prerogative"),
                        "is_committed": control.get("is_committed"),
                        "is_secret": control.get("is_secret"),
                    },
                }
            )

        self.renderer(result)


class EDOCManageGeneralProtocol(EDOCManage):

    def json(self, args=[]):
        employee = employee_from_user(self.request.user, True)

        cfg = {
            "generalProtocol": self.request.user.has_perm(
                "protocolo.has_general_protocol"
            )
            and (True if employee.general_protocol else False)
        }

        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.protocolo.Manage", %s)' % json.dumps(cfg)
        )


class EDOCAthenasReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.reports.AthenasReport")')


class EDOCReportTermConfidentiality(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.reports.ReportTermConfidentiality")')


class EDOCIncomingMovementReport(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.reports.IncomingMovementReport")')


class EDOCOutcomingMovementReport(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.reports.OutcomingMovementReport")')


class EDOCDocumentTransferGuide(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        employee = employee_from_user(get_current_user())
        work_locations = employee.work_locations.values_list("pk", flat=True)
        work_locations = list(map(int, work_locations))
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.reports.DocumentTransferGuide", {employee: %s, work_locations: %s})'
            % (employee.pk, work_locations)
        )

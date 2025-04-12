# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import locale
import math

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Max, Q, Sum
from django.template import loader
from django.utils.formats import localize
from django.utils.html import strip_tags
from num2words import num2words

from contrib.br import br_money
from contrib.daterange import NewDateRange
from contrib.middleware import get_current_user
from contrib.nil import nil_display
from contrib.utils import DateUtils, getLogger, employee_from_user, person_from_user
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
from engine.notification.models import Notification
from rh.models import Cargo
from rh.models import OrgaoGeral as GeneralOrgan
from rh.models import Pessoa, PessoaFisica, PessoaJuridica, Servidor
from ged.models import Arquivo
from standard.models import Choice, AuditTimestampModel


log = getLogger(__name__)


def number_to_words(number):
    """Essa função é um wrap para num2words e faz algumas correções
    no resultado para ficar de acordo com a norma culta da língua
    portuguesa, muito embora não exista uma regra oficial quanto
    à escrita de números por extenso.

    As correções aqui consistem basicamente em:

    1. Aplicar a conjunção 'e' se a parte inteira do número
    terminar em centena "cheia" (por exemplo: R$ 52.300,0).
    2. Remover vírgulas.
    """
    integer_part = math.modf(number)[1]
    words = num2words(number, lang="pt_BR", to="currency")
    if words.find("mil, ") >= 0 and integer_part % 100 == 0:
        words = words.replace("mil, ", "mil e ")
    words = words.replace(",", "")
    return words


class Document(AuditTimestampModel):
    """
    Este modelo registra todos os arquivos dos contratos e das ata.
    Esta necessidade surgiu por ter o sistema que fornecer os links
    dos arquivos para o portal da transparência de forma automática.
    """

    title = models.CharField(max_length=100)
    file = models.ForeignKey(Arquivo, on_delete=models.CASCADE)

    @property
    def filename(self):
        return self.file.filename

    @property
    def document_type(self):
        return str(type(self))


class Contrato(models.Model):
    """O campo data_vencimento está sendo usando apenas como dado legado em razão de
    mudanças na estrutura do modelo e comportamento do sistema."""

    numero = models.CharField(max_length=60, default="")
    objeto_contrato = models.TextField("Objeto do Contrato")
    numero_processo = models.CharField(max_length=30, default="")
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "STATUS_CONTRATO"), default=100
    )
    data_inicio = models.DateField()
    data_vencimento = models.DateField()
    data_vencimento_original = models.DateField(null=True, blank=True)
    dias_para_aviso = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "DIAS_AVISO"), null=True, blank=True
    )
    prorrogado = models.SmallIntegerField(default=0, blank=True)
    max_mes = models.SmallIntegerField(blank=True, default=60)
    tipo_licitacao = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_LICITACAO"),
        null=True,
        blank=True,
    )
    numero_licitacao = models.CharField(max_length=20, null=True, blank=True)
    valor = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tipo_medicao = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_MEDICAO"),
        null=True,
        blank=True,
    )
    dia_pagamento = models.SmallIntegerField(null=True, blank=True)
    tipo_contrato = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_CONTRATO"),
        null=True,
        blank=True,
    )
    numero_pasta = models.CharField(max_length=150, null=True, blank=True, default="")
    data_publicacao = models.DateField(null=True, blank=True)
    data_publicacao_fiscal = models.DateField(null=True, blank=True)
    data_vencimento_flag = models.DateField(null=True, blank=True)
    numero_processo_mae = models.CharField(max_length=30, null=True, blank=True)
    pessoa = models.ManyToManyField("rh.Pessoa", related_name="contratos")
    order = models.ManyToManyField("MinuteSolicitation", related_name="contratos")
    # Índice de Reajuste
    index = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "INDICE_REAJUSTE"),
        null=True,
        blank=True,
    )
    # Mês de Referência (MM)
    reference_month = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "MES_REAJUSTE"),
        null=True,
        blank=True,
    )
    # Aniversário do Reajuste (DD/MM)
    readjustment_anniversary = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        permissions = (
            ("can_view_all_agreement", "Pode visualizar todos os contratos"),
        )

    def __str__(self):
        return "%s - %s" % (self.numero, self.numero_processo)

    def is_finalized(self):
        if self.data_vencimento == date.today():
            return True
        else:
            return False

    def supervisors(self):
        """
        Retorna todos os supervisores de um contrato independente do tipo.
        """
        supervisors = AgreementSupervisor.objects.filter(agreement=self)
        if supervisors.count() > 0:
            return supervisors
        else:
            None

    def active_supervisors(self):
        """
        Retorna todos os supervisores de um contrato independente do tipo.
        Porém, apenas os ativos.
        """
        supervisors = AgreementSupervisor.objects.filter(
            agreement=self, end__isnull=True
        )
        if supervisors.count() > 0:
            return supervisors
        else:
            None

    @classmethod
    def supervisors_minute_to_contract(cls, minute, agreement):
        for s in minute.minutesupervisors.filter(end__isnull=True):
            fiscal = AgreementSupervisor()
            fiscal.employee = s.employee
            fiscal.kind = s.kind
            fiscal.agreement = agreement
            fiscal.begin = s.begin
            # Modificação solicitada no chamado T-036112
            agreement_type = agreement.tipo_contrato
            if int(agreement_type) == 9:
                fiscal.publication_document = s.publication_document
                fiscal.publication_document_date = s.publication_document_date
            fiscal.save()
            if s.classifications.count() > 1:
                for c in s.classifications.all():
                    fiscal.classifications.add(c)

    @classmethod
    def values_minute_to_contract(cls, minute, agreement, solicitations):
        agreementvalue = ValorContrato()
        agreementvalue.contrato = agreement
        agreementvalue.data_ref_inicio = agreement.data_inicio
        agreementvalue.data_assinatura = agreement.data_inicio
        agreementvalue.data_ref_fim = agreement.data_vencimento
        agreementvalue.ordem = 1
        agreementvalue.tipo_valor_contrato = 1
        # Modificação solicitada no chamado T-036112
        agreement_type = agreement.tipo_contrato
        if int(agreement_type) == 9:
            agreementvalue.data_publicacao = agreement.data_inicio

        valor_total = 0
        for s in solicitations:
            for item in MinuteSolicitationItem.objects.filter(solicitation=s):
                valor_total += round(float(item.quantity), 2) * round(
                    float(item.item.unitary_value), 2
                )

        agreementvalue.valor = valor_total
        agreementvalue.save()

    @classmethod
    def validate_equal_minutes(cls, minute, solicitations):
        for s in solicitations:
            if s.minute != minute:
                raise Exception("Selecione pedidos de uma mesma ata.")

    @classmethod
    def validate_solicitation_approved(cls, solicitations):
        for s in solicitations:
            if s.situation != s.APPROVED:
                raise Exception("Selecione pedidos que já foram aprovados.")

    @classmethod
    def already_exists_contract(cls, solicitations):
        contratos = contrato = Contrato.objects.filter(order__in=solicitations)
        if contrato.count() > 0:
            contrato = contrato.last()
            raise Exception(
                f"Esta solicitação já foi utilizada pelo contrato {contrato.numero}."
            )

    @classmethod
    def create_from_minute(
        cls,
        minute,
        solicitations,
        agreement_number,
        agreement_start,
        agreement_end,
        copy_supervisor,
        agreement_type,
    ):

        # Validando as solicitações para gerar um contrato
        # Verificando se os pedidos são de uma mesma ata
        Contrato.validate_equal_minutes(minute, solicitations)
        # Verificando se os pedidos estão na situação de aprovado
        Contrato.validate_solicitation_approved(solicitations)
        # Verificando se o pedido já foi utilizado em algum contrato
        Contrato.already_exists_contract(solicitations)

        agreement = Contrato()

        with transaction.atomic():
            agreement.numero = agreement_number
            agreement.objeto_contrato = minute.minute_object
            agreement.numero_processo = minute.process_number
            agreement.numero_processo_mae = minute.parent_process
            data_inicio = agreement_start.split("/")
            agreement.data_inicio = date(
                int(data_inicio[2]), int(data_inicio[1]), int(data_inicio[0])
            )
            data_fim = agreement_end.split("/")
            agreement.data_vencimento = date(
                int(data_fim[2]), int(data_fim[1]), int(data_fim[0])
            )
            agreement.tipo_licitacao = minute.bidding_type
            agreement.tipo_contrato = agreement_type
            agreement.dias_para_aviso = 100
            agreement.tipo_medicao = 100
            agreement.numero_licitacao = minute.notice_number
            agreement.index = 1

            agreement.save()

            if copy_supervisor:
                Contrato.supervisors_minute_to_contract(minute, agreement)

            Contrato.values_minute_to_contract(minute, agreement, solicitations)

            # Atualizando situação para contratado
            ENGAGED = 7
            for s in solicitations:
                s.situation = ENGAGED
                s.save()
                agreement.order.add(s)

        # Adicionando o Fornecedor issue #1087
        hired = Hired(
            agreement=agreement,
            person=minute.provider,
            start_date=agreement.data_inicio,
        )
        hired.save()

        return agreement

    @property
    def rendered(self):
        """
        Prepara os dados para serem mostrados no painel de visualização (Tile)

        Returns:
            obj: informações referentes ao contrato
        """

        tpl = loader.get_template("agree.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        _data_inicio = None
        if self.data_inicio:
            _data_inicio = self.data_inicio.strftime("%d/%m/%Y")

        ultimo_valor_contrato = (
            self.valores_contrato.all().order_by("-data_ref_fim").first()
        )
        if ultimo_valor_contrato and ultimo_valor_contrato.data_ref_fim:
            _data_vencimento = ultimo_valor_contrato.data_ref_fim.strftime("%d/%m/%Y")
        else:
            _data_vencimento = self.data_vencimento.strftime("%d/%m/%Y")

        _duracao = None

        # Chamado 4659
        primeiro = self.valores_contrato.first()
        ultimo = self.valores_contrato.last()

        if primeiro and primeiro.data_ref_inicio and ultimo and ultimo.data_ref_fim:
            _duracao = abs((ultimo.data_ref_fim - primeiro.data_ref_inicio).days)
            _duracao = _duracao / 30
        else:
            _duracao = abs((self.data_inicio - self.data_vencimento).days)
            _duracao = _duracao / 30

        valor = []
        for i in ValorContrato.objects.filter(contrato_id=self.pk).order_by(
            "data_ref_fim"
        ):
            unidade = ValorContrato()
            if i.data_ref_inicio:
                unidade.data_ref_inicio = i.data_ref_inicio.strftime("%d/%m/%Y")
            if i.data_ref_fim:
                unidade.data_ref_fim = i.data_ref_fim.strftime("%d/%m/%Y")
            if i.data_publicacao:
                unidade.data_publicacao = i.data_publicacao.strftime("%d/%m/%Y")
            if i.valor:
                unidade.valor = locale.currency(i.valor, grouping=True, symbol=None)
            else:
                unidade.valor = 0.00
            executado_c = 0
            for v in i.ne_ref_valor_contrato.all():
                for m in v.medicoes.all():
                    executado_c = executado_c + m.valor
            if i.valor:
                unidade.saldo = locale.currency(
                    i.valor - executado_c, grouping=True, symbol=None
                )
            unidade.executado = locale.currency(executado_c, grouping=True, symbol=None)
            unidade.tipo_valor_contrato = nil_display(i, "tipo_valor_contrato", None)
            unidade.ordem = nil_display(i, "ordem", None)
            valor.append(unidade)

        return tpl.render(
            {
                "agree": {
                    "pk": self.pk,
                    "status": self.get_status_display(),
                    "numero": self.numero,
                    "tipo_licitacao": Choice.objects.get(
                        app_label="contrato",
                        name="TIPO_CONTRATO",
                        value=self.tipo_contrato,
                    ).label,
                    "numero_processo_mae": self.numero_processo_mae or "-",
                    "numero_processo": self.numero_processo or "-",
                    "fornecedor": Pessoa.objects.filter(pk__in=self.pessoa.all()),
                    "objeto": self.objeto_contrato,
                    "numero_licitacao": self.numero_licitacao or "-",
                    "data_inicio": _data_inicio or "-",
                    "data_vencimento": _data_vencimento or "-",
                    "duracao": str(round(_duracao, 2)).replace(".", ",") or "-",
                    "main": [
                        supervisor
                        for supervisor in self.agreementsupervisors.filter(
                            kind=1, end=None
                        )
                    ],
                    "substitutes": [
                        supervisor
                        for supervisor in self.agreementsupervisors.filter(
                            kind=2, end=None
                        )
                    ],
                    "valor_contrato": valor,
                    "total": locale.currency(
                        self._valor_contrato, grouping=True, symbol=None
                    ),
                },
            }
        )

    @property
    def _valor_contrato(self):
        valor = (
            ValorContrato.objects.filter(contrato__id=self.id)
            .aggregate(models.Sum("valor"))
            .get("valor__sum")
        )
        if valor is None:
            valor = 0

        return round(valor, 2)

    @property
    def _data_vencimento(self):
        if self.valores_contrato.exists():
            last_date = (
                self.valores_contrato.all()
                .aggregate(Max("data_ref_fim"))
                .get("data_ref_fim__max")
            )
            return last_date
        else:
            return None

    @property
    def near_due_date(self):
        now = datetime.now().date()
        days = relativedelta(days=self.dias_para_aviso)
        return (
            (now + days) > self.data_vencimento_flag
            if self.data_vencimento_flag
            else self.data_vencimento
        )

    def validate_agreement_exists(self):
        if Contrato.objects.filter(
            numero=self.numero, tipo_contrato=self.tipo_contrato
        ).exists():
            raise Exception(
                "Este número de contrato já está sendo utilizado para o tipo de contrato selecionado!"
            )

    @property
    def last_day_month(self):
        import calendar

        today = datetime.now()
        last_day_month = calendar.monthrange(today.year, today.month)[1]
        return last_day_month

    def get_date_payday(self):
        today = datetime.now()
        if int(self.dia_pagamento) > int(self.last_day_month):
            return date(today.year, today.month, int(self.last_day_month))
        else:
            return date(today.year, today.month, int(self.dia_pagamento))

    @property
    def icons(self):
        status = []
        if self.pending() == 1:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-warn",
                    "title": "Pendência em pagamentos agendados.",
                }
            )
        elif self.pending() == 2:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-warn",
                    "title": "Pendência em pagamento(s).",
                }
            )

        if self.prorrogado > 0:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-extend-agree",
                    "title": "Contrato prorrogado %s vez(es)" % self.prorrogado,
                }
            )

        if not self.ne.all().count():
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-warn",
                    "title": "Ainda não existe NE cadastrada para este contrato.",
                }
            )

        if self.arrear() == 1:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-red",
                    "title": "Contrato com prazo vencido",
                }
            )
        elif self.arrear() == 2:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-green",
                    "title": "Contrato dentro do prazo",
                }
            )
        elif self.arrear() == 3:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-yellow",
                    "title": "Contrato próximo do vencimento",
                }
            )
        elif self.arrear() == 4:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-green",
                    "title": "Contrato dentro do prazo",
                }
            )

        if self.legalperson():
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-pessoajuridica",
                    "title": "Contrato com pessoa jurídica",
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-pessoafisica",
                    "title": "Contrato com pessoa física",
                }
            )

        if self.status == 1:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-appointment-new",
                    "title": "Solicitado Prorrogação",
                }
            )
        elif self.status == 2:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-application-pdf",
                    "title": "Solicitado Licitação",
                }
            )
        elif self.status == 3:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-emblem-important",
                    "title": "Solicitado Rescisão do Contrato",
                }
            )

        return status

    def legalperson(self):
        response = False
        for p in self.pessoa.all():
            if hasattr(p, "pessoajuridica"):
                response = True
        return response

    def pending(self):
        response = 0
        data_pag_agendado = (
            self.get_date_payday() if self.dia_pagamento is not None else None
        )
        if (
            self.tipo_medicao is not None
            and (self.tipo_medicao or 0) == 2
            and self.dia_pagamento is not None
            and datetime.now().date() > data_pag_agendado
        ):
            for med in self.medicoes.all():
                if med.status != 2 and med.data_pagamento is None:
                    response = 1
        else:
            for med in self.medicoes.all():
                if med.status != 2 and med.data_pagamento is None:
                    response = 2

        return response

    def arrear(self):
        now = datetime.now().date()
        days = relativedelta(days=self.dias_para_aviso or 0)

        if (
            now >= self.data_vencimento_flag
            if self.data_vencimento_flag
            else self.data_vencimento
        ):
            response = 1
        elif self.dias_para_aviso == 100:
            response = 2
        elif (
            (now + days) > self.data_vencimento_flag
            if self.data_vencimento_flag
            else self.data_vencimento
        ):
            response = 3
        else:
            response = 4

        return response

    def main_agreementsupervisors_list(self):
        return "; ".join(
            [
                s.employee.pessoa_fisica.nome
                for s in self.agreementsupervisors.filter(kind=1, end=None)
            ]
        )

    # Validando aniversário de reajuste
    def validate_reference(self):
        if self.readjustment_anniversary:
            value = self.readjustment_anniversary.split("/")
            if len(value) != 2 or len(value[0]) != 2 or len(value[1]) != 2:
                raise Exception(
                    f"A referência deve possuir o formato DD/MM. Ex.: 01/12."
                )

    def save(self, *args, **kwargs):
        if self.index != 1:
            self.validate_reference()

        if int(self.tipo_medicao or 0) != 2:
            self.dia_pagamento = None
        if self.pk is None:
            self.validate_agreement_exists()

            if int(self.tipo_medicao or 0) == 2 and self.dia_pagamento is None:
                raise Exception("Campo dia do pagamento é obrigatório.")

            self.prorrogado = 0
            self.data_vencimento_original = self.data_vencimento
            self.max_mes = 60
        else:
            if self._data_vencimento:
                self.data_vencimento_flag = self._data_vencimento

            if int(self.tipo_medicao or 0) == 2 and self.dia_pagamento is None:
                raise Exception("Campo dia do pagamento é obrigatório.")
            old = Contrato.objects.get(pk=self.pk)
            if old.prorrogado != self.prorrogado:
                max = relativedelta(months=self.max_mes)
                n_vencimento = 0
                if hasattr(self, "_prorroga_mes"):
                    n_vencimento = self.data_vencimento + (
                        relativedelta(months=self._prorroga_mes)
                    )
                else:
                    n_vencimento = self.data_vencimento + (
                        self.data_vencimento_original - self.data_inicio
                    )

                log.info(
                    "Data de vencimento atual %s"
                    % DateUtils.date_to_str(self.data_vencimento)
                )
                log.info("Novo periodo %s" % DateUtils.date_to_str(n_vencimento))
                log.info(
                    "Data Maxima de Prorrogação: %s "
                    % DateUtils.date_to_str(self.data_inicio + max)
                )

                # TODO: Permite que um contrato de locação possa ser prorrogado alem do prazo de 60 meses
                if (
                    n_vencimento > (self.data_inicio + max)
                    and "LOCAÇÃO" not in self.objeto_contrato
                ):
                    # if n_vencimento > (self.data_inicio + max):
                    raise Exception("Este contrato não pode mais ser prorrogado.")
                else:
                    self.data_vencimento = n_vencimento

        if self.data_inicio >= self.data_vencimento:
            raise Exception(
                "Não posso cadastrar um contrato, com data de inicio maior que a data de vencimento."
            )

        creating = False
        if self.pk is None:
            creating = True

        super(Contrato, self).save(*args, **kwargs)

        # Adiciona acao de cadastro de contrato
        if creating:
            acao = AcaoContrato(contrato=self, user=get_current_user(), tipo=0)
            acao.save()


class AgreementDocument(Document):
    """
    Entidade derivada de Document específica para ser utilizada
    com contratos.
    """

    agreement = models.ForeignKey(Contrato, on_delete=models.CASCADE)


class Adtivo(models.Model):
    contrato = models.ForeignKey(
        Contrato, related_name="adtivos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    horario = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    user = models.ForeignKey(
        "auth.User", related_name="meus_adtivos", on_delete=models.CASCADE
    )


class Hired(models.Model):
    agreement = models.ForeignKey(
        Contrato, on_delete=models.CASCADE, null=True, blank=True, related_name="hired"
    )
    person = models.ForeignKey(
        "rh.Pessoa", on_delete=models.CASCADE, null=True, blank=True
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.person.nome} em {self.agreement.numero}"
            if self.person and self.agreement
            else ""
        )

    def save(self, *args, **kwargs):

        # Issue 1108 - É necessário manter o campo pessoa do contrato atualizado para
        # questões de retrocompatibilidade
        self.agreement.pessoa.add(self.person)

        super(Hired, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        self.agreement.pessoa.remove(self.person)

        super(Hired, self).delete(*args, **kwargs)


"""
 Poderia ter extendido de PessoaJurídica e "economizaria" a chave extrangeira "person".
"""


# Empresa
class Enterprise(AuditTimestampModel):
    # Pessoa Correspondente à Empresa
    person = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    # Este cadastro se aplica a esta pessoa?
    # Por solicitação do usuário, True = NÃO SE APLICA e False = SE APLICA
    apply = models.BooleanField(default=True)
    # Motivo para o cadastro não se aplicar à pessoa
    motive = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MOTIVO_ESTRUTURA"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.person.nome

    # Validando se aplica ou não aplica o cadastro à pessoa
    def validate_not_apply(self):
        POSSIBLE_STRUCTURE = 5
        NOT_APPLY_STRUCTURE = self.apply

        if NOT_APPLY_STRUCTURE and self.motive == POSSIBLE_STRUCTURE:
            raise Exception(
                "Caso o cadastro não seja aplicável, é preciso definir o motivo válido."
            )

        if not NOT_APPLY_STRUCTURE and self.motive != POSSIBLE_STRUCTURE:
            raise Exception(
                "Caso seja aplicável uma estrutura, escolha uma opção válida."
            )

    def save(self, *args, **kwargs):
        self.validate_not_apply()
        super(Enterprise, self).save(*args, **kwargs)


# Sócios das Empresas (Quadro Societário)
class CorporateStructure(AuditTimestampModel):
    # Empresa / Pessoa Jurídica
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    # Pessoa Ocupante de um Cargo
    person = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    # Cargo da Pessoa
    office = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "CARGO_EMPRESA"), default=1
    )
    # Início da Ocupação do Quadro Societário
    start_date = models.DateField(null=True, blank=True)
    # Final da Ocupação do Quadro Societário
    end_date = models.DateField(null=True, blank=True)

    # Cada pessoa somente pode constar uma vez no cadastro
    def validate_unique_register(self):
        qtd = CorporateStructure.objects.filter(
            enterprise__id=self.enterprise.id, person__id=self.person.id
        ).count()

        if qtd > 1:
            raise Exception("Sócio já cadastrado.")

    def save(self, *args, **kwargs):
        self.validate_unique_register()
        self.enterprise.apply = False
        self.enterprise.motive = 5
        self.enterprise.save()
        super(CorporateStructure, self).save(*args, **kwargs)


class AcaoContrato(models.Model):
    contrato = models.ForeignKey(
        Contrato, related_name="acoes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_acao = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_ACAO_CONTRATO")
    )
    observacao = models.TextField(null=True, blank=True)

    @staticmethod
    def actions_list():
        return {
            c[0]: c[1] for c in Choice.get_choices_for("contrato", "TIPO_ACAO_CONTRATO")
        }

    def __str__(self):
        return "%s, feito por %s" % (
            self.get_tipo_display(),
            self.user.servidor.pessoa_fisica,
        )

    def save(self, *args, **kwargs):
        self.user = get_current_user()

        if self.tipo == 7:  # Ação FINALIZAR
            flag = False

            if self.contrato == 3:
                flag = True
            elif (
                self.contrato._data_vencimento
                and self.contrato._data_vencimento < datetime.now().date()
            ):
                flag = True

            if flag:
                self.contrato.status = 4  # status FINALIZADO
                self.contrato.save()
            else:
                raise Exception(
                    "O contrato só poderá ser finalizado caso esteja vencido ou rescindido."
                )

        elif self.tipo == 9:  # Ação RESCINDIR (Aceitar Pedido de Rescisão Contratual)

            """Obs: não existe status RESCINDIDO.
            Anteriormente quando requerido o pedido de rescisão o status era alterado para SOLICITADA A RESCISÃO.
            Após aceito o pedido de rescisão o status era alterado para FINALIZADO."""

            self.contrato.status = 4  # status FINALIZADO
            self.contrato.save()
        elif self.tipo == 14:  # Ação REATIVAR
            self.contrato.status = 100  # status EM EXECUÇÃO
            self.contrato.save()
        elif self.tipo == 15:  # Ação CANCELAR
            self.contrato.status = 5  # status CANCELADO
            self.contrato.save()
        elif self.tipo == 16:  # Ação ANULAR
            self.contrato.status = 6  # status ANULADO
            self.contrato.save()

        super(AcaoContrato, self).save(*args, **kwargs)


class ValorContrato(AuditTimestampModel):
    contrato = models.ForeignKey(
        Contrato, related_name="valores_contrato", on_delete=models.CASCADE
    )
    data_assinatura = models.DateField(
        verbose_name="Data da Assinatura", null=True, blank=True
    )
    data_ref_inicio = models.DateField(
        verbose_name="Data Referencia Inicio", null=True, blank=True
    )
    data_ref_fim = models.DateField(
        verbose_name="Data Referencia Fim", null=True, blank=True
    )
    valor = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tipo_valor_contrato = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_VALOR_CONTRATO"),
        null=True,
        blank=True,
        default=100,
    )
    ordem = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_ORDEM_CONTRATO"),
        null=True,
        blank=True,
        default=1,
    )
    data_publicacao = models.DateField(null=True, blank=True)
    objeto = models.TextField(blank=True, null=True, verbose_name="Objeto")
    schedule_annotation = models.BooleanField(
        verbose_name="Gera Anotação?", default=False
    )

    class Meta:
        ordering = ("ordem",)

    def __str__(self):
        return "%s (%s - %s - %s)" % (
            self.get_ordem_display(),
            DateUtils.date_to_str(self.data_ref_inicio),
            DateUtils.date_to_str(self.data_ref_fim),
            self.valor,
        )

    def valida_data(self, data):
        return True if self.data_ref_inicio <= data <= self.data_ref_fim else False

    def get_ordem_display(self):
        if self.ordem == 1:
            return "Principal"
        else:
            return f"{'X' if not self.ordem else self.ordem - 1}º Aditivo"

    def create_annotation(self):
        annotation = AgreementAnnotation()
        annotation.agreement = self.contrato
        annotation.kind = 2  # 2 = Lembrete
        annotation.date = datetime.now()
        annotation.schedule = True  # Agendar edoc
        # Data referência fim do valor contrato vai pra data de agendamento
        annotation.schedule_date = self.data_ref_fim + timedelta(
            days=-self.contrato.dias_para_aviso
        )
        # Conteúdo da anotação
        annotation.note = (
            "Sr (a) Fiscal,"
            "<p>&nbsp;</p>"
            '<p style="text-align: justify;">'
            f"Informo que o contrato número {self.contrato}, com objeto "
            f"{self.contrato.objeto_contrato}, com vencimento "
            f"em {self.data_ref_fim:%d/%m/%Y} esta próxima ao termino da vigência. Cabe ao fiscal "
            "tomar todas providências necessárias para sua renovação ou nova "
            "contratação, caso não seja possível sua renovação.\n\n</p>"
            "<p>&nbsp;</p>"
            "Atenciosamente,"
            "<p>&nbsp;</p>"
            "Encarregado da Área de Contratos"
        )
        annotation.save()

    def save(self, *args, **kwargs):
        # atualizando o vencimento
        if self.data_ref_fim <= self.data_ref_inicio:
            raise Exception("A data de início deve ser menor que a de fim.")

        super(ValorContrato, self).save(*args, **kwargs)

        # Verificando se deve ser criada a anotação
        # tipo_valor_contrato / 1 = PRINCIPAL / 2 = PRAZO
        if (
            self.schedule_annotation
            and self.tipo_valor_contrato in [1, 2]
            and self.contrato.dias_para_aviso != 100
        ):

            sched_date = self.data_ref_fim + timedelta(
                days=-self.contrato.dias_para_aviso
            )
            today = date.today()

            if sched_date < today:
                sched_date = today + timedelta(days=1)

            annotations = AgreementAnnotation.objects.filter(
                agreement=self.contrato, kind=2, schedule_date=sched_date
            ).exists()

            if not annotations:
                self.create_annotation()

        self.contrato.save()

    def delete(self, *args, **kargs):
        if self.ne_ref_valor_contrato.count():
            raise Exception("Não posso apagar esta referência.")
        models.Model.delete(self, *args, **kargs)
        self.contrato.save()


class ValueDocument(Document):
    """
    Entidade derivada de Document específica para ser utilizada
    com os valores dos contratos.
    """

    value = models.ForeignKey(ValorContrato, on_delete=models.CASCADE)


class NotaEmpenho(AuditTimestampModel):
    # Parametro "on_delete" adicionado. (Django 2)
    ne_anterior = models.ForeignKey(
        "NotaEmpenho",
        related_name="ne_principal",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    contrato = models.ForeignKey(
        Contrato, related_name="ne", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    numero_ne = models.CharField(max_length=20, unique=True)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    tipo = models.IntegerField(choices=Choice.get_choices_for("contrato", "TIPO_NE"))
    prazo_entrega = models.SmallIntegerField(
        verbose_name="Prazo de entrega do produto", default=0
    )
    classificacao = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "CLASSIFICACAO_NE"),
        null=True,
        blank=True,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    # Atributo que será inutilizado devido a criação de uma entidade (Hired class) para tratar essa informação
    fornecedor = models.ForeignKey(
        "rh.Pessoa",
        related_name="notas_empenhos",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    reforco_estorno = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "REFORCO_ESTORNO"),
        null=True,
        blank=True,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    ref_valor_contrato = models.ForeignKey(
        ValorContrato,
        null=True,
        blank=False,
        related_name="ne_ref_valor_contrato",
        on_delete=models.CASCADE,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    criado_por = models.ForeignKey(
        "auth.User",
        related_name="minhas_nes",
        null=True,
        blank=True,
        default=845,
        on_delete=models.CASCADE,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-id",)
        permissions = (
            ("can_request_reinforcement", "Pode solicitar reforço"),
            ("can_request_reversal", "Pode solicitar estorno"),
        )

    def __str__(self):
        return "%s - %s" % (self.numero_ne, self.get_saldo())

    class ErroReforcoNE(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Não é possível solicitar reforço para NE Ordinária."
            )

    class ErroValorNE(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Não é possível criar NE com valor superior ao do Contrato."
            )

    class ErroValorContrato(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Não é possível criar NE com valor superior a esta referência de pagamento.",
            )

    class ErroNEExists(Exception):
        def __init__(self):
            Exception.__init__(self, "Existe NE cadastrada com esta numeração.")

    def get_data_entrega(self):
        data = ""
        dias = 0
        dias_previsao_entrega = int(self.prazo_entrega)

        for envio in self.envio_ne_fornecedor.all():
            if envio.dias_prorrogacao is not None:
                dias_previsao_entrega += int(envio.dias_prorrogacao)

        if self.envio_ne_fornecedor.all().count() > 0:
            envio = self.envio_ne_fornecedor.all().order_by("id")[0]

            envio = envio.data_envio + relativedelta(days=+dias_previsao_entrega)
            data = envio.strftime("%d/%m/%Y")
            dias = envio - datetime.now().date()

        return "%s (%s dias)" % (data, dias.days)

    def commitmentnote_total_value(self):
        """Retorna a soma do saldo de todas as NEs cadastradas para o contrato, considerando NEs de reforço e NEs de estorno."""

        value_commitmentnotes = (
            self.contrato.ne.filter(reforco_estorno__isnull=True)
            .aggregate(Sum("valor"))
            .get("valor__sum")
        )
        value_commitmentnotes_reinforcement = (
            self.contrato.ne.filter(reforco_estorno=100)
            .aggregate(Sum("valor"))
            .get("valor__sum")
        )
        value_commitmentnotes_reversal = (
            self.contrato.ne.filter(reforco_estorno=1)
            .aggregate(Sum("valor"))
            .get("valor__sum")
        )

        if not value_commitmentnotes:
            value_commitmentnotes = 0.0
        if not value_commitmentnotes_reinforcement:
            value_commitmentnotes_reinforcement = 0.0
        if not value_commitmentnotes_reversal:
            value_commitmentnotes_reversal = 0.0

        total_value_commitmentnotes = (
            round(float(value_commitmentnotes), 2)
            + round(float(value_commitmentnotes_reinforcement), 2)
            - round(float(value_commitmentnotes_reversal), 2)
        )

        return total_value_commitmentnotes

    def get_valor_ne(self):
        valor = self.valor

        valor_reforco_ne = (
            self.ne_principal.filter(reforco_estorno=100)
            .aggregate(models.Sum("valor"))
            .get("valor__sum")
            or 0
        )
        valor_estorno_ne = (
            self.ne_principal.filter(reforco_estorno=1)
            .aggregate(models.Sum("valor"))
            .get("valor__sum")
            or 0
        )

        if valor_reforco_ne is None:
            valor_reforco_ne = 0
        if valor_estorno_ne is None:
            valor_estorno_ne = 0

        valor += valor_reforco_ne
        valor -= valor_estorno_ne

        return round(float(valor), 2)

    def get_saldo(self):
        valor_ne = self.get_valor_ne()
        valor_usado = (
            round(
                self.medicoes.all().aggregate(models.Sum("valor")).get("valor__sum"), 2
            )
            if self.medicoes.exists()
            else 0.0
        )
        saldo = round(float(valor_ne), 2) - round(float(valor_usado), 2)

        if self.ne_anterior:
            saldo = "-"

        return saldo

    def validate_commitmentnote_value(self):
        """Valida se o valor da NE (Na criação e na edição) é maior que o saldo total disponível."""
        if self.reforco_estorno == 1:
            value_commitmentnote = (
                self.contrato.ne.filter(
                    id=self.ne_anterior.id, reforco_estorno__isnull=True
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            value_commitmentnote_reinforcement = (
                self.contrato.ne.filter(
                    ne_anterior=self.ne_anterior, reforco_estorno=100
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            value_commitmentnote_reversal = (
                self.contrato.ne.filter(ne_anterior=self.ne_anterior, reforco_estorno=1)
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            value_paid = (
                Medicao.objects.filter(nota_empenho=self.ne_anterior.id)
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            if not value_commitmentnote_reinforcement:
                value_commitmentnote_reinforcement = 0.0
            if not value_commitmentnote_reversal:
                value_commitmentnote_reversal = 0.0
            if not value_paid:
                value_paid = 0.0

            total_balance = (
                round(float(value_commitmentnote), 2)
                + round(float(value_commitmentnote_reinforcement), 2)
                - round(float(value_commitmentnote_reversal), 2)
                - round(float(self.valor), 2)
                - round(float(value_paid), 2)
            )

            if self.old_fields.get("valor"):
                new_balance = total_balance + self.old_fields.get("valor")
                if new_balance < 0:
                    raise Exception(
                        "O valor da NE de estorno é maior que o saldo disponível."
                    )
            else:
                if not self.pk:
                    if total_balance < 0:
                        raise Exception(
                            "O valor da NE de estorno é maior que o saldo disponível."
                        )
        else:
            value_commitmentnotes = (
                self.contrato.ne.filter(
                    ref_valor_contrato=self.ref_valor_contrato.id,
                    reforco_estorno__isnull=True,
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            value_commitmentnotes_reinforcement = (
                self.contrato.ne.filter(
                    ref_valor_contrato=self.ref_valor_contrato.id, reforco_estorno=100
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            value_commitmentnotes_reversal = (
                self.contrato.ne.filter(
                    ref_valor_contrato=self.ref_valor_contrato.id, reforco_estorno=1
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            # value_updated = Somando caso haja apostilamento
            value_updated = (
                ValorContrato.objects.filter(
                    contrato=self.ref_valor_contrato.contrato.id,
                    ordem=self.ref_valor_contrato.ordem,
                )
                .aggregate(Sum("valor"))
                .get("valor__sum")
            )

            if not value_commitmentnotes:
                value_commitmentnotes = 0.0
            if not value_commitmentnotes_reinforcement:
                value_commitmentnotes_reinforcement = 0.0
            if not value_commitmentnotes_reversal:
                value_commitmentnotes_reversal = 0.0

            total_value_commitmentnotes = (
                round(float(value_commitmentnotes), 2)
                + round(float(value_commitmentnotes_reinforcement), 2)
                - round(float(value_commitmentnotes_reversal), 2)
            )

            total_balance = (
                round(float(self.ref_valor_contrato.valor), 2)
                - round(float(total_value_commitmentnotes), 2)
                + round(float(value_updated), 2)
            )

            if self.old_fields.get("valor"):

                # se alterou valor de nota de empenho subtrai da soma de empenhos e adiciona valor novo
                total_value_commitmentnotes = (
                    round(float(total_value_commitmentnotes), 2)
                    - round(float(self.old_fields.get("valor")), 2)
                    + round(float(self.valor), 2)
                )

                new_balance = float(total_balance) + float(self.old_fields.get("valor"))

                # valor da referência é menor ou igual ao somatório dos empenhos?
                if round(float(value_updated), 2) <= round(
                    float(total_value_commitmentnotes), 2
                ):
                    raise Exception(
                        "Valor da referência é menor ou igual ao somatório do empenhos"
                    )
                elif round(float(self.valor), 2) > round(float(new_balance), 2):
                    raise Exception(
                        "O valor da NE excede o valor permitido para esta referência."
                    )

            elif not self.pk:
                if round(float(value_updated), 2) <= round(
                    float(total_value_commitmentnotes), 2
                ):
                    raise Exception(
                        "Valor da referência é menor ou igual ao somatório do empenhos"
                    )
                elif round(float(self.valor), 2) > round(float(total_balance), 2):
                    raise Exception(
                        "O valor da NE excede o valor permitido para esta referência."
                    )

    def validate_agreement_type(self):
        if self.contrato.tipo_contrato == 6:  # tipo_contrato = 6 (Fornecimento)
            raise Exception(
                "As notas de empenho desse contrato são gerenciadas pelo Gestor de Atas"
            )

    def get_envio(self):
        status = []
        if self.envio_ne_fornecedor.all().count():
            qtd_prorrog = int(self.envio_ne_fornecedor.count() - 1)
            envio = self.envio_ne_fornecedor.all().order_by("id")[0]
            status.append(
                {
                    "iconCls": "icon-contrato icon-ne-send",
                    "title": "NE enviada em: %s"
                    % envio.data_envio.strftime("%d/%m/%Y"),
                }
            )
            status.append(
                {
                    "iconCls": "icon-contrato icon-ne-entrega",
                    "title": "Previsão de entrega: %s" % self.get_data_entrega(),
                }
            )
            status.append(
                {
                    "iconCls": "icon-contrato icon-prorrogacao_entrega_ne",
                    "title": "Entrega prorrogada: %d vez(es)" % qtd_prorrog,
                }
            )
        else:
            if self.reforco_estorno is None:
                status.append(
                    {
                        "iconCls": "icon-agree icon-agree-not-send",
                        "title": "NE não enviada ao fornecedor...",
                    }
                )

        if self.reforco_estorno == 100:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-ne-reinforcement",
                    "title": "Reforço de NE %s" % self.ne_anterior,
                }
            )
        elif self.reforco_estorno == 1:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-list-remove",
                    "title": "Estorno de NE %s " % self.ne_anterior,
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-folder-tree",
                    "title": "NE Principal",
                }
            )

        return status

    def as_active_supervisor(self):
        return self.contrato.agreementsupervisors.filter(
            employee__user=get_current_user()
        )

    def as_inactive_supervisor(self):
        return self.as_active_supervisor().exclude(end=None)

    def is_agreement_supervisor(self):
        return self.contrato.agreementsupervisors.filter(
            employee__user=get_current_user(), agreement=self.contrato
        )

    def check_user_permissions(self):
        user_ = get_current_user()

        if user_.groups.filter(name__icontains="hiring-agreement-"):
            if not user_.groups.filter(
                Q(name="hiring-agreement-manager")
                | Q(name="hiring-agreement-financial")
            ):
                if user_.groups.filter(name="hiring-agreement-supervisor"):
                    if self.as_active_supervisor:
                        if self.reforco_estorno:
                            if self.reforco_estorno == 100:
                                if not self.is_agreement_supervisor():
                                    raise Exception("Você não é o fiscal do contrato.")

                            elif self.reforco_estorno == 1:
                                raise Exception(
                                    "Você não tem permissão para Solicitar Estorno"
                                )
                            else:
                                raise Exception("Você não pode efetuar esta operação")

                        if user_.has_perm("contrato.add_notaempenho"):
                            if not self.pk:
                                if not self.is_agreement_supervisor():
                                    raise Exception("Você não é o fiscal do contrato.")

                        if user_.has_perm(
                            "contrato.change_notaempenho"
                        ) or user_.has_perm("contrato.delete_notaempenho"):
                            if self.pk:
                                raise Exception("Você não pode efetuar esta operação.")

                    else:
                        raise Exception("Este usuário não é um fiscal ativo.")
                else:
                    raise Exception(
                        "Você não tem permissão para efetuar esta operação."
                    )

            return True
        else:
            raise Exception(
                "Você não tem nenhum grupo de permissão do módulo Gestor de Contratações."
            )

    def save(self, *args, **kwargs):
        if self.check_user_permissions():
            self.validate_commitmentnote_value()
            if float(self.valor) > float(self.ref_valor_contrato.valor):
                raise Exception(str(self.ErroValorContrato()))

            if float(self.valor) > float(self.contrato._valor_contrato):
                raise Exception(str(self.ErroValorNE()))

            # validar ref_valor_contrato
            if not ValorContrato.objects.filter(
                contrato__pk=self.contrato.pk, pk=self.ref_valor_contrato.pk
            ).count():
                raise Exception("Tal referência não consta no contrato.")

            # validar fornecedor e salvar se for o caso
            hired_queryset = Hired.objects.filter(
                agreement=self.contrato.pk, person=self.fornecedor.pk
            )
            if not hired_queryset.count():
                raise Exception("Tal empresa não consta no contrato.")

            if self.pk is None:
                if NotaEmpenho.objects.filter(numero_ne=self.numero_ne).count():
                    raise Exception(
                        "Existe NE cadastrada com esta numeração. Contrato %s "
                        % NotaEmpenho.objects.filter(numero_ne=self.numero_ne)[
                            0
                        ].contrato
                    )

            super(NotaEmpenho, self).save(*args, **kwargs)

        else:
            raise Exception("Você não possui esta permissão no módulo Nota de Empenho.")

    def delete(self, *args, **kargs):
        if self.check_user_permissions():

            if self.medicoes.all().count():
                raise Exception(
                    "Não posso apagar esta NE, ela já esta sendo usada para pagamento."
                )

            models.Model.delete(self, *args, **kargs)
        else:
            raise Exception(
                "Você não possui permissão para excluir uma Nota de Empenho."
            )


class Medicao(AuditTimestampModel):
    # Parametro "on_delete" adicionado. (Django 2)
    contrato = models.ForeignKey(
        Contrato, related_name="medicoes", on_delete=models.CASCADE
    )
    observacao = models.TextField(null=True, blank=True)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    # Parametro "on_delete" adicionado. (Django 2)
    user = models.ForeignKey(
        "auth.User",
        related_name="minhas_medicoes",
        blank=True,
        on_delete=models.CASCADE,
    )
    # Parametro "on_delete" adicionado. (Django 2)
    nota_empenho = models.ForeignKey(
        NotaEmpenho,
        related_name="medicoes",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )
    inicio_periodo_referencia = models.DateField(
        verbose_name="Inicio do periodo referencia", null=True, blank=True
    )
    fim_periodo_referencia = models.DateField(
        verbose_name="Fim do periodo de referencia", null=True, blank=True
    )
    status = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "STATUS_MEDICAO"), default=1
    )
    tempst = models.IntegerField(blank=True, null=True)
    ordem_bancaria = models.CharField(max_length=20, null=True, blank=True)
    data_pagamento = models.DateField(
        verbose_name="Data do pagamento", null=True, blank=True
    )
    nota_fiscal = models.CharField(max_length=100, null=True, blank=True)
    modificado_em = models.DateTimeField(auto_now=True)
    horario = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)
        permissions = (
            ("can_do_payment", "Pode lançar pagamento"),
            ("can_undo_payment", "Pode desfazer pagamento"),
        )

    def __str__(self):
        return "%s - %s" % (self.contrato, self.nota_empenho)

    def as_active_supervisor(self):
        return self.contrato.agreementsupervisors.filter(
            employee__user=get_current_user()
        )

    def as_inactive_supervisor(self):
        return self.as_active_supervisor().exclude(end=None)

    def is_agreement_supervisor(self):
        return self.contrato.agreementsupervisors.filter(
            employee__user=get_current_user(), agreement=self.contrato
        )

    def get_state(self):
        status = []
        if self.ordem_bancaria is None:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-aguardando-execucao-financeira",
                    "title": "Aguardando pagamento",
                }
            )
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-view-calendar",
                    "title": "Data da Solicitação: %s" % self.horario,
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-payment-finish",
                    "title": "Pagamento efetuado",
                }
            )
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-view-calendar",
                    "title": "Data do pagamento: %s" % self.data_pagamento,
                }
            )

        return status

    def check_user_permissions(self):
        user_ = get_current_user()
        if user_.groups.filter(name__icontains="hiring-agreement-"):
            if not user_.groups.filter(name="hiring-agreement-manager"):
                if hasattr(self, "_action"):
                    # verifica se o usuário possui permissão para efetuar Pagamento
                    if self._action.lower() == "pay":
                        if user_.has_perm("contrato.can_do_payment"):
                            if not user_.groups.filter(
                                name="hiring-agreement-financial"
                            ):
                                raise Exception(
                                    "Você não possui permissão para efetuar Pagamento"
                                )
                        else:
                            raise Exception(
                                "Você não possui permissão para efetuar Pagamento"
                            )

                        self.status = 2
                    # verifica se o usuário possui permissão para desfazer Pagamento
                    elif self._action.lower() == "unpay":
                        if user_.has_perm("contrato.can_undo_payment"):
                            if not user_.groups.filter(
                                name="hiring-agreement-financial"
                            ):
                                raise Exception(
                                    "Você não possui permissão para desfazer Pagamento"
                                )
                        else:
                            raise Exception(
                                "Você não possui permissão para desfazer Pagamento"
                            )

                        self.ordem_bancaria = ""
                        self.data_pagamento = None
                        # self.status = 1
                    else:
                        raise Exception("Você não pode efetuar esta operação.")

                else:
                    if user_.has_perm("contrato.change_medicao"):
                        if self.pk:
                            if not self.is_agreement_supervisor():
                                raise Exception("Você não é o fiscal do contrato.")

                    if user_.has_perm("contrato.add_medicao"):
                        if not self.pk:
                            if not self.is_agreement_supervisor():
                                raise Exception("Você não é o fiscal do contrato.")

                    if user_.has_perm("contrato.delete_medicao"):
                        if not self.is_agreement_supervisor():
                            raise Exception("Você não pode excluir um Pagamento.")

                return True

            if hasattr(self, "_action"):
                # verifica se o usuário possui permissão para efetuar Pagamento
                if self._action.lower() == "pay":
                    self.status = 2
                # verifica se o usuário possui permissão para desfazer Pagamento
                elif self._action.lower() == "unpay":
                    if user_.has_perm("contrato.can_undo_payment"):
                        self.ordem_bancaria = ""
                        self.data_pagamento = None
                        self.status = 1
                else:
                    raise Exception("Você não pode efetuar esta operação.")
            return True
        else:
            raise Exception(
                "Você não tem nenhum grupo de permissão do módulo Gestor de Contratações."
            )

    def save(self, *args, **kargs):
        self.user = get_current_user()

        if self.check_user_permissions():
            # self.validate_agreement_type()
            # validar nota_empenho
            if not NotaEmpenho.objects.filter(
                contrato__pk=self.contrato.pk, pk=self.nota_empenho.pk
            ).count():
                raise Exception("Tal nota de empenho não consta no contrato.")

            if self.pk is None:
                saldo = round(float(self.nota_empenho.get_saldo()), 2)

                if round(float(self.valor), 2) > saldo:
                    raise Exception(
                        "O valor desta medição estrapola o saldo da NE. Saldo Disponível: R$ %0.2f"
                        % saldo
                    )

                # Adiciona a ação de solicitação de pagamento
                acao = AcaoContrato(
                    contrato=self.contrato, user=get_current_user(), tipo=12
                )
                acao.save()

                # notifica o dep. financeiro que houve uma solicitacao de pagamento
                financeiro = User.objects.filter(groups__name="agreement-financial")
                pay_requester = get_current_user()

                Notification.notify_all(
                    "contrato-solic-pag",
                    [user.servidor for user in financeiro.all() if financeiro.exists()],
                    types=("SYS",),
                    **{
                        "user": str(
                            pay_requester.servidor.pessoa_fisica.nome
                            if pay_requester.servidor
                            else pay_requester
                        ),
                        "contrato": str(self.contrato.numero),
                    },
                )
            else:
                if self.data_pagamento is None:
                    self.data_pagamento = date.today()
                # Adiciona acao de confirmacao de pagamento
                acao = AcaoContrato(
                    contrato=self.contrato, user=get_current_user(), tipo=13
                )
                acao.save()
                # Notifica o gestor que o pagamento foi confirmado
                for s in self.contrato.agreementsupervisors.all():
                    Notification.notify(
                        "contrato-pag-confirmado",
                        s.employee,
                        types=("SYS",),
                        **{"contrato": str(self.contrato.numero)},
                    )

            if self.ordem_bancaria is not None:
                self.status = 2
            else:
                self.status = 1

            super(Medicao, self).save(*args, **kargs)

        else:
            raise Exception("Você não possui esta permissão no módulo de Pagamento.")

    def delete(self, *args, **kargs):
        if self.check_user_permissions():

            if self.ordem_bancaria:
                raise Exception(
                    "Não posso apagar este Pagamento, já existe Ordem bancária lançada para este."
                )

            models.Model.delete(self, *args, **kargs)

        else:
            raise Exception("Você não possui permissão para excluir um Pagamento.")


class EnvioNEFornecedor(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    nota_empenho = models.ForeignKey(
        NotaEmpenho,
        related_name="envio_ne_fornecedor",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )
    data_envio = models.DateField(
        verbose_name="Data envio fornecedor", null=True, blank=True
    )
    prorrogacao = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "PRORROGACAO"), null=True, blank=True
    )
    dias_prorrogacao = models.SmallIntegerField(null=True, blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    criado_por = models.ForeignKey(
        "auth.User", related_name="+", on_delete=models.CASCADE
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s" % (self.nota_empenho, self.prorrogacao)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.nota_empenho.ne_anterior is not None:
                raise Exception("Não posso enviar NE de reforço para contratado(a).")
            self.criado_por = get_current_user()
            if int(self.prorrogacao) == 1 and self.data_envio is None:
                self.data_envio = date.today()

            if self.prorrogacao == 0 and self.dias_prorrogacao is None:
                raise Exception("Campo Dias de prorrogação preenchimento obrigatório.")

        super(EnvioNEFornecedor, self).save(*args, **kwargs)


class Outsourced(AuditTimestampModel):
    # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Servidor, related_name="employee_outsourced", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    contract = models.ForeignKey(
        Contrato, related_name="contract_outsourced", on_delete=models.CASCADE
    )

    def __str__(self):
        return "%s - %s" % (self.employee, self.contract)

    def validate(self):
        if self.employee.tipo != "T":
            raise Exception(
                "O servidor não é um terceirizado. Por favor, verifique o cadastro."
            )
        return True

    def save(self, *args, **kargs):
        self.validate()
        super(Outsourced, self).save(*args, **kargs)


class Minute(AuditTimestampModel):

    number = models.CharField("Número da Ata", max_length=30)
    notice_number = models.CharField(
        "Número do Edital", max_length=30, blank=True, null=True
    )
    management_organ = models.ForeignKey(
        GeneralOrgan,
        verbose_name="Órgão Gerenciador",
        related_name="minutes",
        on_delete=models.PROTECT,
    )
    provider = models.ForeignKey(
        "rh.Pessoa",
        verbose_name="Fornecedor",
        related_name="minutes",
        null=True,
        on_delete=models.SET_NULL,
    )
    enterprise_provider = models.ForeignKey(
        Enterprise,
        verbose_name="Fornecedor",
        related_name="minutes",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    minute_object = models.TextField("Objeto da Ata")
    adhesions_quantity = models.IntegerField(
        "Quantidade de Adesões",
        choices=Choice.get_choices_for("contrato", "MINUTE_ADHESION_QUANTITY"),
    )
    begin_validity = models.DateField("Início da Vigência")
    end_validity = models.DateField("Término da Vigência")
    signature_date = models.DateField("Data da Assinatura")
    bidding_type = models.SmallIntegerField(
        "Tipo de Licitação",
        choices=Choice.get_choices_for("contrato", "TIPO_LICITACAO"),
    )
    publication_date = models.DateField("Data da Publicação", blank=True, null=True)
    official_diary = models.CharField(
        "Número do Diário Oficial", max_length=50, blank=True, null=True
    )
    total_amount = models.DecimalField(
        "Valor Total", max_digits=18, decimal_places=2, blank=True, null=True
    )
    object_execution = models.TextField("Execução do Objeto")
    days_for_notice = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "DIAS_AVISO"), null=True, blank=True
    )
    status = models.SmallIntegerField(
        "Status", choices=Choice.get_choices_for("contrato", "MINUTE_STATUS"), default=1
    )
    process_number = models.TextField("Número do Processo", blank=True, null=True)
    parent_process = models.TextField("Número do Processo Mãe", blank=True, null=True)

    class Meta:
        permissions = (("view_all_minutes", "Can view all minutes"),)
        db_table = "hiring_minute"

    def __str__(self):
        return self.number

    @property
    def rendered(self):
        """
        Prepara os dados para serem mostrados no painel de visualização (Tile)

        Returns:
            obj: informações referentes a ata e itens da ata.
        """

        tpl = loader.get_template("minute.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        _begin_validity = None
        if self.begin_validity:
            _begin_validity = self.begin_validity.strftime("%d/%m/%Y")

        _end_validity = None
        if self.end_validity:
            _end_validity = self.end_validity.strftime("%d/%m/%Y")

        _publication_date = None
        if self.publication_date:
            _publication_date = self.publication_date.strftime("%d/%m/%Y")

        _total_amount = None
        if self.total_amount:
            _total_amount = locale.currency(
                self.total_amount, grouping=True, symbol=None
            )

        items = []
        for i in self.minuteitems.extra(
            select={"_group": 'CAST("group" AS INTEGER)'}
        ).order_by("_group", "id"):
            if i.quantity and i.unitary_value:
                item = dict()
                if i.line:
                    item["group"] = "{}.{}".format(i.group, i.line)
                else:
                    item["group"] = "{}".format(i.group)
                item["description"] = strip_tags(i.description)
                item["quantity"] = str(i.quantity).rstrip("0").rstrip(".")
                item["unitary_value"] = locale.currency(
                    i.unitary_value, grouping=True, symbol=None
                )
                item["total_value"] = locale.currency(
                    i.unitary_value * i.quantity, grouping=True, symbol=None
                )
                sum_item_solicitation = (
                    i.minutesolicitationitems.all()
                    .exclude(
                        solicitation__situation__in=[
                            MinuteSolicitation.REFUSED,
                            MinuteSolicitation.CANCELED,
                        ]
                    )
                    .aggregate(Sum("quantity"))
                    .get("quantity__sum")
                    or 0.0
                )
                balance = round(float(i.quantity), 2) - round(
                    float(sum_item_solicitation), 2
                )
                item["balance"] = str(balance).rstrip("0").rstrip(".")
                item["status"] = 2 if i.status == 2 else 0
                items.append(item)

        return tpl.render(
            {
                "minute": {
                    "pk": self.pk,
                    "number": self.number,
                    "parent_process": self.parent_process,
                    "process_number": self.process_number,
                    "publication_date": _publication_date or "-",
                    "provider": self.provider or "-",
                    "minute_object": self.minute_object,
                    "begin_validity": _begin_validity or "-",
                    "end_validity": _end_validity or "-",
                    "total_amount": _total_amount or "Não Informado",
                    "main": [
                        supervisor
                        for supervisor in self.minutesupervisors.filter(
                            kind=1, end=None
                        )
                    ],
                    "substitutes": [
                        supervisor
                        for supervisor in self.minutesupervisors.filter(
                            kind=2, end=None
                        )
                    ],
                    "items": items,
                },
            }
        )

    @property
    def icons(self):
        """
        Retorna os ícones para serem mostrados no grid.

        Returns:
            [list]: {iconCls: 'icon-class', 'title': 'Title'}
        """

        status = []

        if self.arrear() == 1:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-red",
                    "title": "Ata com prazo vencido",
                }
            )
        elif self.arrear() == 2:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-yellow",
                    "title": "Ata próximo do vencimento",
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-flag-green",
                    "title": "Ata dentro do prazo",
                }
            )

        if self.legalperson():
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-pessoajuridica",
                    "title": "Ata com pessoa jurídica",
                }
            )
        else:
            status.append(
                {
                    "iconCls": "icon-agree icon-agree-pessoafisica",
                    "title": "Ata com pessoa física",
                }
            )

        return status

    def arrear(self):
        """
        Verifica qual a situação da ata em relação ao vencimento: prazo

        Returns:
            int: 1 (prazo vencido), 2 (próximo ao vencimento) ou 3 (dentro do prazo).
        """

        now = datetime.now().date()
        days = relativedelta(days=self.days_for_notice or 0)

        if now > self.end_validity:
            response = 1
        elif (now + days) > self.end_validity:
            response = 2
        else:
            response = 3

        return response

    def legalperson(self):
        """
        Verifica o fornecedor da ata é pessoa física ou pessoa jurídica.

        Returns:
            bool: True (pessoa juridica), False (pessoa física)
        """

        return True if hasattr(self.provider, "pessoajuridica") else False

    def main_minutesupervisors_list(self):
        """
        Retorna os fiscais principais ativos para a ata.

        Returns:
            str: Fiscal1; Fiscal2; Fiscal3
        """

        return "; ".join(
            [
                s.employee.pessoa_fisica.nome
                for s in self.minutesupervisors.filter(kind=1, end=None)
            ]
        )

    def get_supervisors(self):
        return self.minutesupervisors.all()

    def get_active_supervisor(self):
        # Issue #1027
        return self.minutesupervisors.filter(end__isnull=True)

    def validate_dates_validity(self):
        """
        Esta função valida se a data de inicio de vigência é menor que a data de término da vigência.

        Raises:
            Exception: Data de término da vigência é menor que a data de início da vigência.
        """

        if self.end_validity < self.begin_validity:
            raise Exception(
                "A data de Início da Vigência deve ser maior que a data de Término da Vigência."
            )

    def validate_number_and_management_organ(self):
        """
        Esta função valida se o cadastro da ata será duplicado.

        Raises:
            Exception: Existe uma ata cadastrada para o número e órgão gerenciador informados.
        """

        qtd_minutes = self.__class__.objects.filter(
            number=self.number, management_organ=self.management_organ
        ).count()
        if (self.old_fields.get("number") or not self.pk) and qtd_minutes > 0:
            raise Exception("Já existe uma ata cadastrada com este número.")

    def validate_days_for_notice(self):
        """
        Esta função valida o preenchimento do campo Aviso de Vencimento.

        Raises:
            Exception: O campo Aviso de Vencimento está vazio.
        """

        if self.days_for_notice is None:
            raise Exception("Por favor, preencha o campo Aviso de Vencimento.")

    def validate_on_save(self):
        self.validate_dates_validity()
        self.validate_number_and_management_organ()
        self.validate_days_for_notice()

    def create_annotation(self):
        annotation = MinuteAnnotation()
        annotation.minute = self
        annotation.kind = 2  # 2 = Lembrete
        annotation.date = datetime.now()
        annotation.schedule = True  # Agendar edoc
        # Data referência fim do valor contrato vai pra data de agendamento
        annotation.schedule_date = self.end_validity + timedelta(
            days=-self.days_for_notice
        )
        # Conteúdo da anotação
        annotation.note = (
            "Sr (a) Fiscal,"
            "<p>&nbsp;</p>"
            "<p>&nbsp;</p>"
            f"Informo que a ATA número {self.number}, com vencimento "
            f"em {self.end_validity:%d/%m/%Y} esta próxima ao termino da vigência. Cabe ao fiscal "
            "tomar todas providências necessárias para a abertura de nova "
            "licitação, caso o objeto da ATA ainda seja necessário para a administração.\n\n"
            "<p>&nbsp;</p>"
            "<p>&nbsp;</p>"
            "Atenciosamente,"
            "<p>&nbsp;</p>"
            "Encarregado da Área de Contratos"
        )
        annotation.save()

    def _get_or_create_enterprise(self):
        enterprises = Enterprise.objects.filter(person=self.provider)

        if enterprises.exists():
            return enterprises.first()
        else:
            enterprise = Enterprise.objects.create(person=self.provider)
            return enterprise

    def save(self, *args, **kwargs):
        self.validate_on_save()
        self.enterprise_provider = self._get_or_create_enterprise()

        super(Minute, self).save(*args, **kwargs)

        if self.days_for_notice != 100:
            sched_date = self.end_validity + timedelta(days=-self.days_for_notice)
            today = date.today()

            if sched_date < today:
                sched_date = today + timedelta(days=1)

            annotations = self.annotations.filter(
                kind=2, minute__end_validity=self.end_validity, schedule_date=sched_date
            ).exists()

            if not annotations:
                self.create_annotation()


class MinuteDocument(Document):
    """
    Entidade derivada de Document específica para ser utilizada
    com as atas.
    """

    minute = models.ForeignKey(Minute, on_delete=models.CASCADE)


class MinuteAction(models.Model):
    """
    Registra as ações realizadas na Ata (Minute)
    """

    # Parametro "on_delete" adicionado. (Django 2)
    minute = models.ForeignKey(
        Minute, related_name="minuteactions", on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)
    # Parametro "on_delete" adicionado. (Django 2)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    action = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MINUTE_ACTION")
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hiring_minuteaction"

    @staticmethod
    def actions_list():
        return {c[0]: c[1] for c in Choice.get_choices_for("contrato", "MINUTE_ACTION")}

    def __str__(self):
        return "%s, feito por %s" % (
            self.get_action_display(),
            self.user.servidor.pessoa_fisica,
        )

    def validate_action_and_minute_status(self):
        """
        Esta função valida se a ação pode ser realizada de acordo com o status da Ata (Minute)

        Raises:
            Exception: A ata não está ativa para ser cancelada.
            Exception: A ata não está ativa para ser revogada.
            Exception: A ata não está ativa para ser suspensa.
            Exception: A ata não está ativa para ser finalizada.
            Exception: A ata não está vencida para ser finalizada.
        """

        self.user = get_current_user()

        if self.action == 1 and self.minute.status != 1:
            raise Exception("Só posso solicitar cancelamento de um ata ativa.")
        elif self.action == 2 and self.minute.status != 1:
            raise Exception("Só posso solicitar revogação de uma ata ativa.")
        elif self.action == 3 and self.minute.status != 1:
            raise Exception("Só posso solicitar suspensão de uma ata ativa.")
        elif self.action == 4 and self.minute.status != 1:
            raise Exception("Só posso finalizar uma ata ativa.")

        if self.action == 4:
            if self.minute.end_validity < datetime.now().date():
                self.minute.status = 6
                self.minute.save()
            else:
                raise Exception("A ata só poderá ser finalizado caso esteja vencida.")

    def execute_on_save(self):
        """
        Este método possui funções de validação para serem executadas antes de
        salvar um registro.

        Note:
            self.validate_action_and_minute_status()
        """

        self.validate_action_and_minute_status()

    def save(self, *args, **kwargs):
        self.execute_on_save()
        super(MinuteAction, self).save(*args, **kwargs)


class MinuteItem(AuditTimestampModel):
    """
    Esta classe é responsável pelo gerencimamento dos itens da ata.
    """

    minute = models.ForeignKey(
        Minute, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    description = models.TextField("Descrição")
    parent = models.ForeignKey(
        "self", related_name="subitems", on_delete=models.PROTECT, blank=True, null=True
    )
    unit_measure = models.SmallIntegerField(
        default=61,
        choices=Choice.get_choices_for("contrato", "MINUTE_ITEM_UNIT_MEASURE"),
    )
    quantity = models.DecimalField(
        "Quantidade", max_digits=10, decimal_places=2, blank=True, null=True
    )
    unitary_value = models.DecimalField(
        "Valor Unitário", max_digits=18, decimal_places=2, blank=True, null=True
    )
    total_value = models.DecimalField(
        "Valor Total", max_digits=18, decimal_places=2, blank=True, null=True
    )
    group = models.CharField("Grupo/Item", max_length=10, blank=True, null=True)
    line = models.CharField("Linha", max_length=10, blank=True, null=True)
    item_balance = models.DecimalField(
        "Saldo do item", max_digits=18, decimal_places=2, blank=True, null=True
    )
    brand = models.TextField("Marca/Modelo", blank=True, null=True)
    generate_agreement = models.BooleanField("Gera contrato?", default=False)
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MINUTE_ITEM_STATUS"), default=1
    )

    class Meta:
        db_table = "hiring_minuteitem"

    @property
    def description_without_tags(self):
        """
        Retorna a descrição dos Itens da Ata.

        Returns:
            str: strip_tags(self.description)
        """

        return strip_tags(self.description)

    @property
    def subchildren_count(self):
        """
        Retorna a quantidade de subitens para a instancia informada.

        Returns:
            int: Quantidade de subitens
        """

        return MinuteItem.objects.filter(parent=self).count()

    def generate_group(self):
        """
        Esta função é responsável por inserir o grupo (group) do item a ser cadastrado.
        Se for um item principal, é atribuído o valor da linha (line) ao campo grupo.
        Se for um subitem é atribuído o grupo do item de nível superior (parent)

        Raises:
            Exception: Não foi informado o item de nível superior ou o campo linha (line)
        """

        if self.parent:
            self.group = self.parent.group
        else:
            if self.line:
                self.group = self.line
                self.line = None

        if not self.group:
            raise Exception("Informe o item ou linha.")

    def quantity_greater_than_item_balance(self):
        """
        Esta função verifica se a quantidade informada quando estou editando um
        item, é maior que o saldo disponível, desconsiderando os item com pedidos
        cancelados ou recusados

        Raises:
            Exception: Quantidade informada é menor que o saldo disponível para o item
        """

        if self.pk:
            sum_item_quantity = self.minutesolicitationitems.exclude(
                solicitation__situation__in=[
                    MinuteSolicitation.REFUSED,
                    MinuteSolicitation.CANCELED,
                ]
            ).aggregate(Sum("quantity"))

            if round(float(self.quantity), 2) < round(
                float(sum_item_quantity["quantity__sum"] or 0), 2
            ):
                raise Exception(
                    "A quantidade do item deve ser maior que o saldo disponível."
                )

    def update_self_total_value(self):
        """
        Calcula o novo valor total do item.
        """

        if self.quantity and self.unitary_value:
            self.total_value = self.quantity * self.unitary_value

    @staticmethod
    def update_parent_total_value(item):
        """
        Atualiza o valor total dos item e de seus subitens.

        Args:
            item (obj): O objeto item é passado como argumento para poder ter o valor total atualizado.
        """

        if item.parent:
            children_pks = item.parent.subitems.values_list("pk", flat=True)
            total_value = (
                MinuteItem.objects.filter(pk__in=children_pks)
                .aggregate(sum=Sum("total_value"))
                .get("sum")
            )
            MinuteItem.objects.filter(pk=item.parent.pk).update(total_value=total_value)
            item.update_parent_total_value(item.parent)

    def update_parent_total_value_delete(self, minute_id):
        """
        Atualiza o valor total dos itens e de seus subitens para a ata informada.

        Args:
            minute_id (int): Identificador (pk) da ata.
        """

        minute = Minute.objects.get(id=minute_id)
        for item in minute.minuteitems.all():
            self.update_parent_total_value(item)

    def insert_item_balance(self):
        """
        Preenche o valor do cache item_balance com a quantidade informada ao incluir um novo item.
        """

        if not self.pk:
            if self.quantity:
                self.item_balance = self.quantity

    def update_item_balance(self):
        """
        Atualiza o valor do saldo do item (item_balance) para a instancia que está sendo atualizada.
        """

        if self.pk:
            sum_item_quantity = (
                self.minutesolicitationitems.exclude(
                    solicitation__situation__in=[
                        MinuteSolicitation.REFUSED,
                        MinuteSolicitation.CANCELED,
                    ]
                )
                .aggregate(Sum("quantity"))
                .get("quantity__sum")
            )

            if sum_item_quantity:
                self.item_balance = self.quantity - sum_item_quantity
            else:
                self.item_balance = self.quantity

        self.__class__.objects.filter(id=self.id).update(item_balance=self.item_balance)

    @staticmethod
    def update_total_amount(minute_id):
        """
        Calcula o valor dos itens

        Args:
            minute_id (int): [description]
        """

        minute = Minute.objects.get(id=minute_id)
        minuteitems = minute.minuteitems.all()
        if minuteitems:
            total_amount = 0
            for i in minuteitems:
                total_item = 0
                if i.quantity and i.unitary_value:
                    if i.status in [2, 3]:
                        _quantity = i.minutesolicitationitems.aggregate(
                            Sum("quantity")
                        ).get("quantity__sum")
                        if _quantity:
                            total_item = round(_quantity, 2) * round(i.unitary_value, 2)
                    else:
                        total_item = round(i.quantity, 2) * round(i.unitary_value, 2)
                total_amount = round(total_amount, 2) + round(total_item, 2)
        else:
            total_amount = 0

        minute.total_amount = total_amount
        minute.save()

    def validate_unit_measure_and_quantity(self):
        """
        Esta função valida se a unidade de medida pode conter quantidades fracionadas.

        Raises:
            Exception: Unidade de medida não permite a quantidade fracionada.
        """

        if self.quantity:
            if not float(self.quantity).is_integer() and self.unit_measure not in [
                4,
                26,
                35,
                38,
                39,
                40,
                41,
                42,
                44,
                59,
            ]:
                raise Exception(
                    "Esta unidade de medida não aceita números fracionados. Informe um número inteiro."
                )

    def validate_description(self):
        """
        Esta função valida se o campo descrição foi informado.

        Raises:
            Exception: O campo descrição não foi informado.
        """

        if not self.description:
            raise Exception("Informe uma descrição.")

    def validate_quantity_unitary_value(self):
        """
        Esta função valida se a instancia possui a quantidade e valor unitário
        informados.

        Raises:
            Exception: Não foi informada o valor unitário.
            Exception: Não foi informada a quantidade.
        """

        if self.quantity and not self.unitary_value:
            raise Exception("Informe o valor unitário.")
        elif not self.quantity and self.unitary_value:
            raise Exception("Informe a quantidade.")

    def validate_item_status(self):
        """
        Este método valida o status do item.

        Raises:
            Exception: Itens que não estão em edição ou foram aditivados
        """

        if self.pk and self.status != 5:
            if not self.status == 1 and not self.status == 4:
                if not (self.old_fields.get("status") in [1, 4] and self.status == 2):
                    raise Exception("Este item não pode ser editado.")

    def validate_item_solicitation_exists(self):
        """
        Este método valida se um item já possui pedido.

        Raises:
            Exception: Já possui pedido com ciclo de vida ativo.
        """

        queryset = self.minutesolicitationitems.exclude(
            solicitation__situation__in=[
                MinuteSolicitation.REFUSED,
                MinuteSolicitation.CANCELED,
            ]
        )

        if self.pk and queryset.count() > 0:
            if not self.old_fields.get("item_balance"):
                if not (self.old_fields.get("status") in [1, 4] and self.status == 2):
                    raise Exception(
                        "Não é possível editar ou remover um item que já possui pedido."
                    )

    def validate_on_save(self):
        """
        Este método possui funções de validação para serem executadas antes de
        salvar um registro.

        Note:
            self.validate_unit_measure_and_quantity()
            self.validate_description()
            self.validate_quantity_unitary_value()
            self.validate_item_status()
            self.validate_item_solicitation_exists()
        """

        self.validate_unit_measure_and_quantity()
        self.validate_description()
        self.validate_quantity_unitary_value()
        self.validate_item_status()
        self.validate_item_solicitation_exists()

    def validate_on_delete(self):
        """
        Este método possui funções de validação para serem executadas antes de
        remover um registro.

        Note:
            self.validate_item_solicitation_exists()
        """

        self.validate_item_solicitation_exists()

    def __str__(self):
        if self.line:
            return "%s.%s - %s" % (self.group, self.line, strip_tags(self.description))
        else:
            return "%s - %s" % (self.group, strip_tags(self.description))

    def save(self, *args, **kwargs):
        self.generate_group()
        self.validate_on_save()
        self.quantity_greater_than_item_balance()
        self.update_self_total_value()
        self.insert_item_balance()

        try:
            with transaction.atomic():
                super(MinuteItem, self).save(*args, **kwargs)
                self.update_total_amount(self.minute.id)
                self.update_item_balance()
                self.update_parent_total_value(self)

        except Exception as e:
            raise e

    def delete(self, *args, **kwargs):
        self.validate_on_delete()
        _minute = self.minute.id

        try:
            with transaction.atomic():
                super(MinuteItem, self).delete(*args, **kwargs)
                self.update_total_amount(_minute)
                self.update_parent_total_value_delete(_minute)
        except Exception as e:
            raise e


class MinuteItemAction(models.Model):
    """
    Registra as ações realizadas no Item da Ata (MinuteItem)
    """

    # Parametro "on_delete" adicionado. (Django 2)
    item = models.ForeignKey(
        MinuteItem, related_name="minuteitemactions", on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MINUTE_ITEM_ACTION")
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hiring_minuteitemaction"

    @staticmethod
    def actions_list():
        return {
            c[0]: c[1] for c in Choice.get_choices_for("contrato", "MINUTE_ITEM_ACTION")
        }

    def __str__(self):
        return "%s, feito por %s" % (
            self.get_action_display(),
            self.user.servidor.pessoa_fisica,
        )

    def validate_action_and_item_status(self):
        """
        Esta função valida se a ação pode ser realizada de acordo com o status da Item (MinuteItem)

        Raises:
            Exception: O item já está ativo.
            Exception: Ativar um item revogado.
            Exception: Ativar um item que foi aditivado.
            Exception: Desativar um item desativado.
            Exception: Desativar um item revogado.
            Exception: Revogar um item revogado.
            Exception: Aditivar um item desativado
            Exception: Aditivar um item revogado
            Exception: Finalizar um item com pedido pendente
        """

        self.user = get_current_user()
        # STATUS = [1, 4]
        if self.action == 1 and self.item.status == 1:
            raise Exception("O item já se encontra ativo.")
        elif self.action == 1 and self.item.status == 3:
            raise Exception("Não posso ativar um item que foi revogado.")
        elif self.action == 1 and self.item.status == 4:
            raise Exception("Não posso ativar um item que foi aditivado.")
        elif self.action == 2 and self.item.status == 2:
            raise Exception("O item já está desativado.")
        elif self.action == 2 and self.item.status == 3:
            raise Exception("Não posso desativar um item que foi revogado.")
        elif self.action == 3 and self.item.status == 3:
            raise Exception("O item já está revogado.")
        elif self.action == 4 and self.item.status == 2:
            raise Exception("Não posso aditivar um item que foi desativado.")
        elif self.action == 4 and self.item.status == 3:
            raise Exception("Não posso aditivar um item que foi revogado.")

        if self.action == 2:
            for i in MinuteSolicitationItem.objects.filter(item=self.item.id):
                s = i.solicitation
                if s.situation not in [s.CANCELED, s.REQUESTED]:
                    raise Exception(
                        "Não é possível finalizar um item que tenha pedido pendente."
                    )

            self.item.status = 2
            self.item.save()

    def validade_on_save(self):
        """
        Este método possui funções de validação para serem executadas antes de
        salvar um registro.

        Note:
            self.validate_action_and_item_status()
        """

        self.validate_action_and_item_status()

    def save(self, *args, **kwargs):
        self.validade_on_save()

        super(MinuteItemAction, self).save(*args, **kwargs)


class MinuteItemComplementaryDescription(models.Model):
    """
    Gerencia a descrição complementar do item da ata.
    """

    # Parametro "on_delete" adicionado. (Django 2)
    minuteitem = models.ForeignKey(
        "MinuteItem", related_name="%(class)ss", on_delete=models.CASCADE
    )
    characteristic = models.CharField("Característica", max_length=128)
    description = models.CharField("Descrição", max_length=128)

    class Meta:
        db_table = "hiring_minuteitemcomplementarydescription"

    def __str__(self):
        return "%s: %s" % (self.characteristic, self.description)

    def validate_minuteitem_status_and_solicitation_exists(self):
        """
        Este método valida o status do item.

        Raises:
            Exception: Itens que não estão em edição ou foram aditivados
        """

        self.minuteitem.validate_item_status()

    def save(self, *args, **kwargs):
        self.validate_minuteitem_status_and_solicitation_exists()
        super(MinuteItemComplementaryDescription, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.validate_minuteitem_status_and_solicitation_exists()
        super(MinuteItemComplementaryDescription, self).delete(*args, **kwargs)


class MinuteSolicitation(AuditTimestampModel):
    """
    Gerencia os pedidos de itens para aquisição.
    """

    minute = models.ForeignKey(
        Minute,
        related_name="minutesolicitations",
        verbose_name="Minuta",
        on_delete=models.CASCADE,
    )
    number = models.CharField("Número do Pedido", max_length=30, blank=True, null=True)
    justification = models.TextField("Justificativa")

    # Situations
    EDITING, SOLICITED, APPROVED, REFUSED, CANCELED, REQUESTED, ENGAGED, REBALANCED = (
        range(1, 9)
    )
    situation = models.PositiveSmallIntegerField(
        "Situação",
        choices=Choice.get_choices_for("contrato", "MINUTE_SOLICITATION_SITUATION"),
        blank=True,
        null=True,
    )

    # O campo edoc não é mais utilizado (deprecated). Com a implantação
    # do SEI, a feature de geração de edoc foi encerrada.
    edoc = models.OneToOneField(
        Protocolo,
        related_name="minutesolicitation",
        verbose_name="Edoc",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-id",)
        db_table = "hiring_minutesolicitation"
        permissions = (
            ("change_minutesolicitation_situation", "Can change situation."),
        )

    def __str__(self):
        return "%s - %s" % (self.number, strip_tags(self.justification))

    @property
    def rendered(self):
        """
        Prepara os dados para serem mostrados no painel de visualização (Tile)

        Returns:
            obj: informações referentes ao Pedido.
        """

        tpl = loader.get_template("solicitation.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        _minute_begin_validity = None
        if self.minute.begin_validity:
            _minute_begin_validity = self.minute.begin_validity.strftime("%d/%m/%Y")

        _minute_end_validity = None
        if self.minute.end_validity:
            _minute_end_validity = self.minute.end_validity.strftime("%d/%m/%Y")

        _minute_total_amount = None
        if self.minute.total_amount:
            _minute_total_amount = locale.currency(
                self.minute.total_amount, grouping=True, symbol=None
            )

        _total_solicitation = []  # lista com totais de cada item do pedido
        for solicitation_item in self.minutesolicitationitems.all():

            # item reequilibrado do pedido
            balanced_item = BalancedSolicitationItem.objects.filter(
                solicitation_item__id=solicitation_item.id
            )

            if balanced_item.count() > 0:
                _total_solicitation.append(
                    solicitation_item.quantity * balanced_item[0].unit_value
                )
            else:
                _total_solicitation.append(
                    solicitation_item.quantity * solicitation_item.item.unitary_value
                )

        items = []
        for i in self.minutesolicitationitems.all().order_by("item__id"):

            balanced = BalancedSolicitationItem.objects.filter(
                solicitation_item__id=i.id
            )

            item = dict()
            if i.item.line:
                item["group"] = "{}.{}".format(i.item.group, i.item.line)
            else:
                item["group"] = "{}".format(i.item.group)

            item["description"] = strip_tags(i.item.description)
            item["quantity"] = str(i.quantity).rstrip("0").rstrip(".")
            item["unitary_value"] = locale.currency(
                i.item.unitary_value, grouping=True, symbol=None
            )
            item["total_value"] = locale.currency(
                i.item.unitary_value * i.quantity, grouping=True, symbol=None
            )
            if balanced.count():
                item["strip"] = True
            else:
                item["strip"] = False
            items.append(item)

            if balanced.count():
                balanced = balanced.last()
                balanced_item = dict()
                balanced_item["group"] = item["group"]
                balanced_item["description"] = strip_tags(balanced.description)
                balanced_item["quantity"] = item["quantity"]
                balanced_item["unitary_value"] = locale.currency(
                    balanced.unit_value, grouping=True, symbol=None
                )
                balanced_item["total_value"] = locale.currency(
                    balanced.unit_value * i.quantity, grouping=True, symbol=None
                )
                items.append(balanced_item)

        return tpl.render(
            {
                "solicitation": {
                    "pk": self.pk,
                    "number": self.number,
                    "requisition": self.minutesolicitationrequisitions.last(),
                    "minute_number": self.minute.number or "-",
                    "minute_parent_process": self.minute.parent_process,
                    "minute_process_number": self.minute.process_number,
                    "minute_provider": self.minute.provider.nome or "-",
                    "minute_object": self.minute.minute_object,
                    "minute_begin_validity": _minute_begin_validity or "-",
                    "minute_end_validity": _minute_end_validity or "-",
                    "minute_total_amount": _minute_total_amount or "Não Informado",
                    "minute_main": [
                        s.employee.pessoa_fisica.nome
                        for s in self.minute.minutesupervisors.filter(kind=1, end=None)
                    ],
                    "minute_substitutes": [
                        s.employee.pessoa_fisica.nome
                        for s in self.minute.minutesupervisors.filter(kind=2, end=None)
                    ],
                    "justification": strip_tags(self.justification) or "-",
                    "total_solicitation": locale.currency(
                        sum(_total_solicitation), grouping=True, symbol=None
                    )
                    or "-",
                    "created_at": self.created_at.date().strftime("%d/%m/%Y"),
                    "items": items,
                },
            }
        )

    @property
    def content_edoc(self):
        """
        Retorna os dados do conteúdo do Edoc.
        """

        tpl = loader.get_template("edoc_content.html")
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        _provider_title = "None"
        _provider_name = "None"
        _provider_document_title = "None"
        _provider_document = "None"

        try:
            provider = PessoaJuridica.objects.get(pessoa_ptr_id=self.minute.provider.id)
            _provider_title = "NOME DA EMPRESA: "
            _provider_name = provider.razao_social
            _provider_document_title = "CNPJ:"
            cnpj = provider.cnpj
            _provider_document = "{}.{}.{}/{}-{}".format(
                cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:]
            )

        except PessoaJuridica.DoesNotExist:
            try:
                provider = PessoaFisica.objects.get(
                    pessoa_ptr_id=self.minute.provider.id
                )
                _provider_title = "NOME: "
                _provider_name = provider.nome
                _provider_document_title = "CPF"
                _provider_document = provider.cpf

            except Exception as e:
                log.debug(e)

        column_line = False
        column_brand = False
        total_solicitation = 0
        table_group_flag = False
        table_item_flag = False

        for solicitation_item in self.minutesolicitationitems.all():
            if solicitation_item.item.parent:
                if solicitation_item.item.parent.description.upper() == "GRUPO":
                    table_group_flag = True

                if solicitation_item.item.parent.description.upper() == "ITEM":
                    table_item_flag = True
            else:
                table_item_flag = True

            if solicitation_item.item.brand:
                column_brand = True

            if solicitation_item.item.line:
                column_line = True

            total_solicitation = (
                total_solicitation
                + solicitation_item.quantity * solicitation_item.item.unitary_value
            )

        _total_solicitation = (
            str(locale.currency(total_solicitation, grouping=True, symbol=None))
            + " ("
            + number_to_words(total_solicitation)
            + ")"
        )

        items_group = []
        for i in self.minutesolicitationitems.filter(
            Q(item__parent__isnull=False)
            & Q(item__parent__description__in=["Grupo", "grupo", "GRUPO"])
        ).order_by("id"):
            item_group = dict()
            item_group["group"] = i.item.group
            if column_line:
                if i.item.line is not None:
                    item_group["line"] = i.item.line

            item_group["description"] = strip_tags(i.item.description)

            for d in i.solicitationitemdescriptions.all():
                item_group["item_description"] = "{}: {}".format(
                    strip_tags(d.item_description.characteristic),
                    strip_tags(d.item_description.description),
                )

            if column_brand:
                if i.item.brand:
                    item_group["brand"] = i.item.brand

            try:
                measure = Choice.objects.get(
                    name="MINUTE_ITEM_UNIT_MEASURE", value=i.item.unit_measure
                ).label
                item_group["unit_measure"] = measure

            except Choice.DoesNotExist:
                item_group["unit_measure"] = ""

            item_group["quantity"] = "{}".format(i.quantity).rstrip("0").rstrip(".")
            item_group["unitary_value"] = str(
                locale.currency(i.item.unitary_value, grouping=True, symbol=None)
            )
            item_group["total_item"] = str(
                locale.currency(
                    i.quantity * i.item.unitary_value, grouping=True, symbol=None
                )
            )
            items_group.append(item_group)

        items_line = []
        for i in self.minutesolicitationitems.filter(
            Q(item__parent__isnull=True) | Q(item__parent__description="Item")
        ).order_by("id"):
            item_line = dict()
            item_line["group"] = i.item.group
            if column_line:
                if i.item.line is not None:
                    item_line["line"] = i.item.line

            item_line["description"] = strip_tags(i.item.description)

            for d in i.solicitationitemdescriptions.all():
                item_line["item_description"] = "{}: {}".format(
                    strip_tags(d.item_description.characteristic),
                    strip_tags(d.item_description.description),
                )

            if column_brand:
                if i.item.brand:
                    item_line["brand"] = i.item.brand

            try:
                measure = Choice.objects.get(
                    name="MINUTE_ITEM_UNIT_MEASURE", value=i.item.unit_measure
                ).label
                item_line["unit_measure"] = measure

            except Choice.DoesNotExist:
                item_line["unit_measure"] = ""

            item_line["quantity"] = "{}".format(i.quantity).rstrip("0").rstrip(".")
            item_line["unitary_value"] = str(
                locale.currency(i.item.unitary_value, grouping=True, symbol=None)
            )
            item_line["total_item"] = str(
                locale.currency(
                    i.quantity * i.item.unitary_value, grouping=True, symbol=None
                )
            )
            items_line.append(item_line)

        return tpl.render(
            {
                "solicitation": {
                    "minute_justification": strip_tags(self.justification),
                    "number": self.number,
                    "minute_number": self.minute.number,
                    "minute_end_validity": self.minute.end_validity.strftime(
                        "%d/%m/%Y"
                    ),
                    "minute_process_number": self.minute.process_number,
                    "minute_provider_title": _provider_title,
                    "minute_provider_name": _provider_name,
                    "minute_provider_document_title": _provider_document_title,
                    "minute_provider_document": _provider_document,
                    "total_solicitation": _total_solicitation,
                    "table_group_flag": table_group_flag,
                    "column_line": column_line,
                    "column_brand": column_brand,
                    "items_group": items_group,
                    "table_item_flag": table_item_flag,
                    "items_line": items_line,
                }
            }
        )

    @property
    def edoc_display(self):
        """
        Retorna o codigo do Edoc quando existe.
        """

        if self.edoc:
            return self.edoc.codigo

    @property
    def minute_process_number_display(self):
        """
        Retorna o número do processo da ata.
        """

        return self.minute.process_number

    def main_supervisors_display(self):
        """
        Retorna uma lista com os fiscais principais da ata.
        """

        return self.minute.main_minutesupervisors_list()

    def generate_number_and_set_situation(self):
        """
        Gera a numeração automática para o pedido e atribui a numeração e a situação inicial para o pedido.
        """

        if not self.pk:
            self.situation = self.EDITING

            year = str(date.today().year)

            last_solicitation = MinuteSolicitation.objects.first()
            if last_solicitation:
                last_solicitation = str(last_solicitation.number)
                number = last_solicitation.split("/")[0]
                number_year = last_solicitation.split("/")[1]
                if number_year == year:
                    number = str(int(number) + 1)
                    length = len(number)
                    i = 1
                    zero = ""
                    while i <= (4 - length):
                        zero = zero + "0"
                        i = i + 1
                    number = zero + number + "/" + year
                else:
                    number = "0001" + "/" + year
            else:
                number = "0001" + "/" + year

            self.number = number

    def generate_and_validate_situation(self):
        is_changing_situation = self.old_fields.get("situation", None)

        if self.situation != self.EDITING and not is_changing_situation:
            if self.situation != self.REBALANCED:
                raise Exception(
                    f'Você só pode editar um pedido com situação de "Em Edição".'
                )

        user = get_current_user()
        perm = "contrato.change_minutesolicitation_situation"
        situations = [
            self.APPROVED,
            self.REFUSED,
            self.CANCELED,
            self.REQUESTED,
            self.ENGAGED,
            self.REBALANCED,
        ]  # Não permitido aos fiscais.

        if (
            is_changing_situation
            and self.situation in situations
            and not user.has_perm(perm)
        ):
            raise Exception(
                "Você não possui permissão para alterar a situação do pedido."
            )

    @staticmethod
    def update_item_balance(minute_id):
        """
        Atualiza o saldo do item

        Args:
            minute_id (int): Identificação (pk) da ata.
        """

        for item in MinuteItem.objects.filter(minute=minute_id):
            sum_item_quantity = (
                item.minutesolicitationitems.exclude(
                    solicitation__situation__in=[
                        MinuteSolicitation.REFUSED,
                        MinuteSolicitation.CANCELED,
                    ]
                )
                .aggregate(Sum("quantity"))
                .get("quantity__sum")
            )

            if sum_item_quantity:
                item.item_balance = item.quantity - sum_item_quantity
            else:
                item.item_balance = item.quantity

            MinuteItem.objects.filter(id=item.id).update(item_balance=item.item_balance)

    def update_item_balance_on_change_situation(self):
        """
        Atualiza o saldo do item ao alterar a situação do pedido para cancelado ou recusado.
        """
        old_situation = self.old_fields.get("situation")
        if (old_situation in [self.EDITING, self.SOLICITED, self.APPROVED]) and (
            self.situation in [self.REFUSED, self.CANCELED]
        ):  # se situation mudar de 1,2 ou 3 para 4 ou 5
            self.update_item_balance(self)

    def update_status_minute_solicitation(self, action):

        # é um dígito?
        if action.isdigit():
            self.situation = int(action)  # situation requer um int
            self.save()
        else:
            raise Exception("Ocorreu um erro")

    def execute_on_save(self):
        self.generate_number_and_set_situation()
        self.generate_and_validate_situation()

    def validate_supervisor(self):
        """
        Valida se o fiscal possui permissão para alterar um pedido.

        Raises:
            Exception: não possui permissão
        """

        _user = get_current_user()
        if not self.minute.minutesupervisors.filter(
            employee__user=get_current_user(), minute=self.minute
        ):
            if not _user.groups.filter(name="hiring-minute-manager"):
                raise Exception("Você não tem permissão para alterar um pedido.")

    @property
    def check_minute_out_of_validity(self):
        """
        Verifica se a ata esta fora da vigência

        Returns:
            bool: True fora da vigência, False dentro da vigência
        """

        return True if self.minute.end_validity < date.today() else False

    def validate_minute_validity(self):
        """
        Valida se a ata está fora da vigência ao criar um novo pedido.

        Raises:
            Exception: ata fora do período de vigência.
        """

        if not self.old_fields.get("situation"):
            if self.minute.end_validity < date.today():
                raise Exception("Você não pode adicionar pedidos para uma ata vencida.")

    def validate_minute(self):
        """
        Valida se a ata foi alterada para o pedido.

        Raises:
            Exception: A ata foi alterada
        """

        if self.pk:
            if self.old_fields.get("minute"):
                raise Exception("Não é possível alterar a ata.")

    def validate_on_save(self):
        self.validate_supervisor()
        self.validate_minute_validity()

    def validate_on_delete(self):
        self.validate_supervisor()

    def save(self, *args, **kwargs):
        created = False
        if self.pk is None:
            created = True

        self.validate_on_save()
        self.execute_on_save()

        try:
            with transaction.atomic():
                super(MinuteSolicitation, self).save(*args, **kwargs)
                self.update_item_balance(self.minute.id)

                # Cria o registro de ação ao criar e solicitar um pedido
                if created:
                    solicitation_action = MinuteSolicitationAction(
                        solicitation_id=self.pk,
                        user=get_current_user(),
                        action=self.EDITING,
                    )
                    solicitation_action.save()
                else:
                    if (
                        self.old_fields.get("situation") == self.EDITING
                        and self.situation == self.SOLICITED
                    ):
                        solicitation_action = MinuteSolicitationAction(
                            solicitation_id=self.pk,
                            user=get_current_user(),
                            action=self.SOLICITED,
                        )
                        solicitation_action.save()
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs):
        if self.situation == self.EDITING:
            self.validate_on_delete()
            _minute_id = self.minute.id

            try:
                with transaction.atomic():
                    super(MinuteSolicitation, self).delete(*args, **kwargs)
                    self.update_item_balance(_minute_id)
            except Exception as e:
                raise e
        else:
            raise Exception(
                "O pedido só pode ser excluído quando ainda estiver em edição."
            )


class MinuteSolicitationAction(models.Model):
    """
    Gerencia as ações realizadas nos Pedidos (MinuteSolicitation)
    """

    solicitation = models.ForeignKey(
        MinuteSolicitation,
        related_name="minutesolicitationactions",
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MINUTE_SOLICITATION_ACTION")
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hiring_minutesolicitationaction"

    @staticmethod
    def actions_list():
        return {
            c[0]: c[1]
            for c in Choice.get_choices_for("contrato", "MINUTE_SOLICITATION_SITUATION")
        }

    def __str__(self):
        return "%s, feito por %s" % (
            self.get_action_display(),
            self.user.servidor.pessoa_fisica,
        )

    def validate_action_and_solicitation_situation(self):
        """
        Esta função valida se a ação pode ser realizada de acordo com a situação do Pedido (MinuteSolicitation)

        Raises:
            Exception: pedido já existe
            Exception: não é possivel alterar a situação do pedido manualmente.
            Exception: O pedido não esta com situação 1 (em edição) para ser solicitado.
            Exception: O pedido não foi solicitado para poder aprovar.
            Exception: O pedido não foi solicitado para poder recusar.
            Exception: O pedido já esta cancelado.
            Exception: O pedido nao foi aprovado para ser contratado
            Exception: Ação não permitida
        """

        self.user = get_current_user()

        s = self.solicitation

        if self.action == s.EDITING and s.situation != s.EDITING:
            raise Exception("Não posso adicionar um pedido que já existe.")
        elif (
            self.action in [s.SOLICITED, s.APPROVED, s.REFUSED, s.CANCELED, s.REQUESTED]
            and s.situation == s.EDITING
        ):
            raise Exception(
                'Não é possível alterar o status de um pedido "Em Edição". '
            )
        elif self.action == s.SOLICITED and s.situation not in [s.EDITING, s.SOLICITED]:
            raise Exception("Só posso solicitar um pedido que está em edição.")
        elif self.action == s.APPROVED and s.situation != s.SOLICITED:
            raise Exception(
                "Só posso aprovar um pedido que está com a situação de solicitado."
            )
        elif self.action == s.REFUSED and s.situation != s.SOLICITED:
            raise Exception("Só posso recusar um pedido que foi solicitado.")
        elif self.action == s.CANCELED and s.situation == s.CANCELED:
            raise Exception("Este pedido já está cancelado.")
        elif self.action == s.ENGAGED and s.situation != s.APPROVED:
            raise Exception("Só posso contratar um pedido que foi aprovado.")

        if self.action == s.EDITING:
            pass
        elif self.action == s.SOLICITED:
            pass
        elif self.action == s.APPROVED:
            s.situation = s.APPROVED
            s.save()
        elif self.action == s.REFUSED:
            s.situation = s.REFUSED
            s.save()
        elif self.action == s.CANCELED:
            s.situation = s.CANCELED
            s.save()
        elif self.action == s.ENGAGED:
            s.situation = s.ENGAGED
            s.save()
        else:
            raise Exception("Esta ação não é permitida para este pedido.")

    def validate_on_save(self):
        self.validate_action_and_solicitation_situation()

    def save(self, *args, **kwargs):
        self.validate_on_save()
        super(MinuteSolicitationAction, self).save(*args, **kwargs)


class MinuteSolicitationItem(AuditTimestampModel):
    """
    Gerencia os itens do pedido.
    """

    solicitation = models.ForeignKey(
        MinuteSolicitation,
        related_name="minutesolicitationitems",
        verbose_name="Solicitação",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        MinuteItem,
        related_name="minutesolicitationitems",
        verbose_name="Item",
        on_delete=models.PROTECT,
    )
    quantity = models.DecimalField("Quantidade", max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("-id",)
        db_table = "hiring_minutesolicitationitem"

    @property
    def normalized_quantity(self):
        """
        Retorna a quantidade sem as casas decimais se for possível
        retornar um número inteiro.
        """
        return (
            self.quantity
            if self.quantity > round(self.quantity)
            else round(self.quantity)
        )

    @property
    def total_value(self):
        return round(float(self.quantity) * float(self.item.unitary_value), 2)

    def __str__(self):
        if not self.item.line:
            return "%s - %s" % (self.item.group, strip_tags(self.item.description))
        else:
            return "%s.%s - %s" % (
                self.item.group,
                self.item.line,
                strip_tags(self.item.description),
            )

    @property
    def normalized_quantity(self):
        """
        Retorna a quantidade sem as casas decimais se for possível
        retornar um número inteiro.
        Somente funciona no Python 3 devido ao round possuir um comportamento diferente
        entre as versão de Python.
        """
        return (
            self.quantity
            if self.quantity > round(self.quantity)
            else round(self.quantity)
        )

    @property
    def get_item_balance(self):
        """
        Retorna um float com o saldo do item
        """

        return self.item.item_balance

    def validate_unit_measure_and_quantity(self):
        """
        Valida se a unidade de medida pode ter quantidades fracionadas.

        Raises:
            Exception: Esta unidade de medida não pode ter quantidade fracionada.
        """

        if self.quantity:
            if not float(self.quantity).is_integer() and self.item.unit_measure not in [
                4,
                26,
                35,
                38,
                39,
                40,
                41,
                42,
                44,
                59,
            ]:
                raise Exception(
                    "Este item não permite quantidades fracionadas. Informe um número inteiro."
                )

    def validate_item_balance(self):
        """
        Valida se a o item ainda possui saldo para realizar o pedido.

        Raises:
            Exception: não possui saldo.
        """

        sum_item_quantity = (
            self.__class__.objects.filter(item=self.item)
            .exclude(
                solicitation__situation__in=[
                    MinuteSolicitation.REFUSED,
                    MinuteSolicitation.CANCELED,
                ]
            )
            .aggregate(Sum("quantity"))
        )

        if sum_item_quantity["quantity__sum"]:
            sum_item_quantity = round(sum_item_quantity["quantity__sum"], 2)
        else:
            sum_item_quantity = 0

        if self.pk:
            if self.old_fields.get("quantity"):
                quantity_balance = (
                    round(sum_item_quantity, 2)
                    + round(self.quantity, 2)
                    - round(self.old_fields.get("quantity"), 2)
                )
            else:
                quantity_balance = sum_item_quantity
        else:
            quantity_balance = round(sum_item_quantity, 2) + round(self.quantity, 2)

        if self.item.quantity < quantity_balance:
            raise Exception("Informe uma quantidade menor ou igual ao saldo disponível")

    def validate_quantity(self):
        """
        Valida se a quantidade informada para o item do pedido é maior que zero.

        Raises:
            Exception: quantidade 0 ou negativa.
        """

        if self.quantity < 0.01:
            raise Exception("Informe uma quantidade maior do que 0 (zero).")

    def update_item_balance(self):
        """
        Atualiza o saldo do item (item_balance) e depende da função validade_item_balance().
        """

        sum_item_quantity = (
            self.__class__.objects.filter(item=self.item)
            .exclude(
                solicitation__situation__in=[
                    MinuteSolicitation.REFUSED,
                    MinuteSolicitation.CANCELED,
                ]
            )
            .aggregate(Sum("quantity"))
            .get("quantity__sum")
        )

        if sum_item_quantity:
            self.item.item_balance = self.item.quantity - sum_item_quantity
        else:
            self.item.item_balance = self.item.quantity

        self.item.save()

    def validate_status(self):
        """
        Valida a situação do pedido para poder realizar a edição.

        Raises:
            Exception: situação é diferente de 1 (em edição)
        """

        if self.solicitation.situation != self.solicitation.EDITING:
            raise Exception(
                'Só é possível editar uma solicitação com status "Em Edição".'
            )

    def validate_on_save(self):
        self.validate_unit_measure_and_quantity()
        self.validate_quantity()
        self.validate_item_balance()
        self.validate_status()

    def validate_on_delete(self):
        self.validate_status()

    def save(self, *args, **kwargs):
        self.validate_on_save()

        try:
            with transaction.atomic():
                super(MinuteSolicitationItem, self).save(*args, **kwargs)
                self.update_item_balance()
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs):
        self.validate_on_delete()
        try:
            with transaction.atomic():
                super(MinuteSolicitationItem, self).delete(*args, **kwargs)
                self.update_item_balance()
        except Exception as e:
            raise e

    @property
    def balanced_oid(self):
        """
        Propriedade criada para fornecer o id para carregar
        as informações na tela BalancedSolicitationWindow.
        """
        try:
            obj = BalancedSolicitationItem.objects.get(solicitation_item__id=self.id)
            return obj.id
        except:
            return None

    @property
    def is_rebalanced(self):
        if self.balanced_oid is None:
            return False
        else:
            return True


class BalancedSolicitationItem(AuditTimestampModel):
    """
    Esta classe registra os reequilíbrios dos itens dos pedidos.
    Reequilíbrios são todas as modificações dos itens, que não
    podem ser feitas nos itens das atas, sendo registradas aqui.
    """

    solicitation_item = models.ForeignKey(
        MinuteSolicitationItem, on_delete=models.CASCADE
    )
    description = models.TextField(null=True, blank=True)
    brand = models.CharField(null=True, blank=True, max_length=100)
    unit_value = models.DecimalField(
        null=True, blank=True, max_digits=20, decimal_places=2
    )

    def save(self, *args, **kwargs):
        solicitation = self.solicitation_item.solicitation
        if solicitation.situation in [solicitation.ENGAGED, solicitation.REBALANCED]:
            super(BalancedSolicitationItem, self).save(*args, **kwargs)
            solicitation.situation = solicitation.REBALANCED
            solicitation.save()
        else:
            raise Exception(
                "A solicitação precisa estar contratada para ser reequilibrado."
            )


class MinuteSolicitationItemDescription(models.Model):
    """
    Gerencia a descrição dos itens dos pedidos.
    """

    solicitation_item = models.ForeignKey(
        MinuteSolicitationItem,
        related_name="solicitationitemdescriptions",
        on_delete=models.CASCADE,
    )
    item_description = models.ForeignKey(
        MinuteItemComplementaryDescription,
        related_name="solicitationitemdescriptions",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-id",)
        unique_together = ("solicitation_item", "item_description")
        db_table = "hiring_minutesolicitationitemdescription"

    def __str__(self):
        return str(self.item_description)


class MinuteSolicitationCommitmentNote(AuditTimestampModel):
    """
    Gerencia as notas de empenho relacionadas aos pedidos das atas.
    """

    # Parametro "on_delete" adicionado. (Django 2)
    parent = models.ForeignKey(
        "MinuteSolicitationCommitmentNote",
        related_name="minutesolicitationcommitmentnotes",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    solicitation = models.ForeignKey(
        MinuteSolicitation,
        related_name="minutesolicitationcommitmentnotes",
        on_delete=models.PROTECT,
        verbose_name="Pedido",
    )
    number = models.CharField(max_length=20, verbose_name="Número")
    value = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Valor")
    kind = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "TIPO_NE"), verbose_name="Tipo de NE"
    )
    classification = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "CLASSIFICACAO_NE"),
        null=True,
        blank=True,
        verbose_name="Classificação",
    )
    reinforcement_reversal = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "REFORCO_ESTORNO"),
        null=True,
        blank=True,
        verbose_name="Reforço/Estorno",
    )
    origin = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "MINUTE_COMMITMENT_ORIGIN"),
        verbose_name="Origem do Empenho",
    )

    class Meta:
        db_table = "hiring_minutesolicitationcommitmentnote"
        verbose_name = "Nota de Empenho da Ata"
        ordering = ("-id",)
        unique_together = ("number", "origin")
        permissions = (
            (
                "request_minutesolicitationcommitmentnote_reinforcement",
                "Can request a commitmentnote reinforcement of the solicitation.",
            ),
            (
                "request_minutesolicitationcommitmentnote_reversal",
                "Can request a commitmentnote reversal of the solicitation",
            ),
        )

    def __str__(self):
        return self.number

    @property
    def get_provider(self):
        """
        Retorna o contratado da ata.

        Returns:
            str: nome do contratado
        """

        return self.solicitation.minute.provider.nome

    def commitmentnote_total_value(self):
        """Retorna a soma do saldo de todas as NEs cadastradas para o pedido, considerando NEs de reforço e NEs de estorno."""
        """
        [summary]

        Returns:
            float: valor total das NEs
        """

        value_commitmentnotes = (
            self.solicitation.minutesolicitationcommitmentnotes.filter(
                reinforcement_reversal__isnull=True
            )
            .aggregate(Sum("value"))
            .get("value__sum")
        )
        value_commitmentnotes_reinforcement = (
            self.solicitation.minutesolicitationcommitmentnotes.filter(
                reinforcement_reversal=100
            )
            .aggregate(Sum("value"))
            .get("value__sum")
        )
        value_commitmentnotes_reversal = (
            self.solicitation.minutesolicitationcommitmentnotes.filter(
                reinforcement_reversal=1
            )
            .aggregate(Sum("value"))
            .get("value__sum")
        )

        if not value_commitmentnotes:
            value_commitmentnotes = 0.0
        if not value_commitmentnotes_reinforcement:
            value_commitmentnotes_reinforcement = 0.0
        if not value_commitmentnotes_reversal:
            value_commitmentnotes_reversal = 0.0

        total_value_commitmentnotes = (
            round(float(value_commitmentnotes), 2)
            + round(float(value_commitmentnotes_reinforcement), 2)
            - round(float(value_commitmentnotes_reversal), 2)
        )

        return round(float(total_value_commitmentnotes), 2)

    def commitmentnote_value(self):
        """Retorna o saldo da NE atual, considerando NEs de reforço e NEs de estorno.

        Returns:
            float: saldo da NE atual
        """

        value_commitmentnote_reinforcement = (
            self.minutesolicitationcommitmentnotes.filter(reinforcement_reversal=100)
            .aggregate(Sum("value"))
            .get("value__sum")
        )
        value_commitmentnote_reversal = (
            self.minutesolicitationcommitmentnotes.filter(reinforcement_reversal=1)
            .aggregate(Sum("value"))
            .get("value__sum")
        )

        if not value_commitmentnote_reinforcement:
            value_commitmentnote_reinforcement = 0.0
        if not value_commitmentnote_reversal:
            value_commitmentnote_reversal = 0.0

        total_value_commitmentnote = (
            round(float(self.value), 2)
            + round(float(value_commitmentnote_reinforcement), 2)
            - round(float(value_commitmentnote_reversal), 2)
        )

        return round(float(total_value_commitmentnote), 2)

    def get_balance(self):
        """Retorna o saldo da NE para pagamento.

        Returns:
            float: saldo da nota de empenho
        """

        commitmentnote_total_value = self.commitmentnote_value()
        value_paid = (
            round(
                float(
                    self.minutesolicitationpayments.all()
                    .aggregate(Sum("value"))
                    .get("value__sum")
                ),
                2,
            )
            if self.minutesolicitationpayments.exists()
            else 0.0
        )
        balance = round(float(commitmentnote_total_value), 2) - round(
            float(value_paid), 2
        )

        return round(balance, 2) if not self.parent else "-"

    def total_solicitation_value(self):
        """Retorna a soma de todos os itens do pedido.

        Returns:
            float: valor total dos itens
        """

        total_value = 0.0
        for i in self.solicitation.minutesolicitationitems.all():
            total_value += round(float(i.item.unitary_value) * float(i.quantity), 2)

        return round(float(total_value), 2)

    def validate_value_zero(self):
        """
        Valida se o valor da NE é igual a zero.

        Raises:
            Exception: valor da NE é zero
        """

        if self.value == 0.0:
            raise Exception("Não é possível cadastrar uma NE com valor zero.")

    def validate_commitmentnote_value(self):
        """
        Valida se o valor da NE (criação e na edição) é maior que o saldo total disponível.

        Raises:
            Exception: valor da NE(estorno) maior que o saldo.
            Exception: valor NE excede o valor permitido.
        """

        if self.reinforcement_reversal == 1:
            value_commitmentnote = (
                self.solicitation.minutesolicitationcommitmentnotes.filter(
                    id=self.parent.id, reinforcement_reversal__isnull=True
                )
                .aggregate(Sum("value"))
                .get("value__sum")
            )

            value_commitmentnote_reinforcement = (
                self.solicitation.minutesolicitationcommitmentnotes.filter(
                    parent=self.parent, reinforcement_reversal=100
                )
                .aggregate(Sum("value"))
                .get("value__sum")
            )

            value_commitmentnote_reversal = (
                self.solicitation.minutesolicitationcommitmentnotes.filter(
                    parent=self.parent, reinforcement_reversal=1
                )
                .aggregate(Sum("value"))
                .get("value__sum")
            )

            value_paid = (
                MinuteSolicitationPayment.objects.filter(commitmentnote=self.parent.id)
                .aggregate(Sum("value"))
                .get("value__sum")
            )

            value_update = 0

            if not value_commitmentnote_reinforcement:
                value_commitmentnote_reinforcement = 0.0
            if not value_commitmentnote_reversal:
                value_commitmentnote_reversal = 0.0
            if not value_paid:
                value_paid = 0.0

            total_balance = (
                round(float(value_commitmentnote), 2)
                + round(float(value_commitmentnote_reinforcement), 2)
                - round(float(value_commitmentnote_reversal), 2)
                - round(float(self.value), 2)
                - round(float(value_paid), 2)
                + round(float(value_update), 2)
            )

            if self.old_fields.get("value"):
                new_balance = total_balance + self.old_fields.get("value")
                if new_balance < 0:
                    raise Exception(
                        "O valor da NE de estorno é maior que o saldo disponível."
                    )
            else:
                if not self.pk:
                    if total_balance < 0:
                        raise Exception(
                            "O valor da NE de estorno é maior que o saldo disponível."
                        )
        else:
            total_balance = (
                self.total_solicitation_value() - self.commitmentnote_total_value()
            )

            if self.old_fields.get("value"):
                new_balance = total_balance + self.old_fields.get("value")
                if round(float(self.value), 2) > round(float(new_balance), 2):
                    raise Exception(
                        "O valor da NE excede o valor permitido para este pedido."
                    )
            else:
                if not self.pk:
                    if round(float(self.value), 2) > round(float(total_balance), 2):
                        raise Exception(
                            "O valor da NE excede o valor permitido para este pedido."
                        )

    def validate_payment_exists(self):
        """
        Valida se a Nota de Empenho já possui pagamento

        Raises:
            Exception: NE possui pagamento
        """

        if self.pk:
            if self.minutesolicitationpayments.count() > 0:
                raise Exception("Não é possível editar uma NE que já possui pagamento.")

    def validate_commitmentnote_payments(self):
        """Valida se a NE já possui pagamento.

        Raises:
            Exception: não é possível remover a NE.
        """

        if self.minutesolicitationpayments.count() > 0:
            raise Exception(
                "Esta Nota de Empenho já possui pagamento e não pode ser apagada. "
            )

    def validate_on_save(self):
        self.validate_value_zero()
        self.validate_commitmentnote_value()
        self.validate_payment_exists()

    def validate_on_delete(self):
        self.validate_commitmentnote_payments()

    def as_active_supervisor(self):
        return self.solicitation.minute.minutesupervisors.filter(
            employee__user=get_current_user()
        )

    def as_inactive_supervisor(self):
        return self.as_active_supervisor().exclude(end=None)

    def is_minute_supervisor(self):
        return self.solicitation.minute.minutesupervisors.filter(
            employee__user=get_current_user(), minute=self.solicitation.minute
        )

    def check_user_permissions(self):
        """
        Verifica as permissões do usuário para efetuar operações nas notas de empenho.
        """

        _user = get_current_user()

        if _user.groups.filter(name__icontains="hiring-minute-"):
            if not _user.groups.filter(
                Q(name="hiring-minute-manager") | Q(name="hiring-minute-financial")
            ):
                if _user.groups.filter(name="hiring-minute-supervisor"):
                    if self.as_active_supervisor:
                        if self.reinforcement_reversal:
                            if self.reinforcement_reversal == 100:
                                if not self.is_minute_supervisor():
                                    raise Exception("Você não é o fiscal da ata.")

                            elif self.reinforcement_reversal == 1:
                                raise Exception(
                                    "Você não tem permissão para Solicitar Estorno"
                                )
                            else:
                                raise Exception("Você não pode efetuar esta operação")

                        if _user.has_perm(
                            "contrato.add_minutesolicitationcommitmentnote"
                        ):
                            if not self.pk:
                                if not self.is_minute_supervisor():
                                    raise Exception("Você não é o fiscal da ata.")

                        if _user.has_perm(
                            "contrato.change_minutesolicitationcommitmentnote"
                        ) or _user.has_perm(
                            "contrato.delete_minutesolicitationcommitmentnote"
                        ):
                            if self.pk:
                                raise Exception("Você não pode efetuar esta operação.")

                    else:
                        raise Exception("Este usuário não é um fiscal ativo.")
                else:
                    raise Exception(
                        "Você não tem permissão para efetuar esta operação."
                    )

            return True
        else:
            raise Exception(
                "Você não tem nenhum grupo de permissão do módulo Gestor de Atas."
            )

    def save(self, *args, **kwargs):
        if self.check_user_permissions():
            self.validate_on_save()
            super(MinuteSolicitationCommitmentNote, self).save(*args, **kwargs)
        else:
            raise Exception(
                "Você não possui permissão para excluir uma Nota de Empenho."
            )

    def delete(self, *args, **kwargs):
        if self.check_user_permissions():
            self.validate_on_delete()

            super(MinuteSolicitationCommitmentNote, self).delete(*args, **kwargs)
        else:
            raise Exception(
                "Você não possui permissão para excluir uma Nota de Empenho."
            )


class MinuteSolicitationPayment(AuditTimestampModel):
    """
    Gerencia os pagamentos dos pedidos das atas
    """

    observation = models.TextField(null=True, blank=True)
    value = models.DecimalField(max_digits=18, decimal_places=2)
    # Parametro "on_delete" adicionado. (Django 2)
    user = models.ForeignKey(
        "auth.User",
        related_name="minutesolicitationpayments",
        blank=True,
        on_delete=models.CASCADE,
    )
    commitmentnote = models.ForeignKey(
        MinuteSolicitationCommitmentNote,
        related_name="minutesolicitationpayments",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )
    start_reference_period = models.DateField(
        "Inicio do periodo referencia", null=True, blank=True
    )
    end_reference_period = models.DateField(
        "Fim do periodo de referencia", null=True, blank=True
    )
    status = models.IntegerField(
        choices=Choice.get_choices_for("contrato", "STATUS_MEDICAO"), default=1
    )
    bank_order = models.CharField(max_length=20, null=True, blank=True)
    payment_date = models.DateField("Data do pagamento", null=True, blank=True)
    invoice = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "hiring_minutesolicitationpayment"
        ordering = ("-id",)
        permissions = (
            ("do_minutesolicitationpayment", "Can do payment of solicitation."),
            ("undo_minutesolicitationpayment", "Can undo payment of solicitation."),
        )

    def __str__(self):
        return "%s - %s" % (self.commitmentnote.solicitation, self.commitmentnote)

    def as_active_supervisor(self):
        """
        Retorna uma query verificando se o usuário logado é um fiscal da ata
        """

        return self.commitmentnote.solicitation.minute.minutesupervisors.filter(
            employee__user=get_current_user()
        )

    def as_inactive_supervisor(self):
        """
        Retorna uma query verificando se o usuário logado é um fiscal inativo da ata
        """

        return self.as_active_supervisor().exclude(end=None)

    def is_minute_supervisor(self):
        return self.commitmentnote.solicitation.minute.minutesupervisors.filter(
            employee__user=get_current_user(),
            minute=self.commitmentnote.solicitation.minute,
        )

    def add_minute_action(self):
        """
        Adiciona uma ação na minuta ao criar ou alterar os pagamentos.
        """

        if self.pk:
            if self.bank_order:
                minuteaction = MinuteAction(
                    minute=self.commitmentnote.solicitation.minute,
                    user=get_current_user(),
                    action=6,
                )
                minuteaction.save()
            else:
                minuteaction = MinuteAction(
                    minute=self.commitmentnote.solicitation.minute,
                    user=get_current_user(),
                    action=7,
                )
                minuteaction.save()
        else:
            minuteaction = MinuteAction(
                minute=self.commitmentnote.solicitation.minute,
                user=get_current_user(),
                action=5,
            )
            minuteaction.save()

    def validate_balance_payment(self):
        """
        Valida se o valor informado para pagamento é menor ou igual ao saldo da NE.

        Raises:
            Exception: saldo menor que o valor
        """

        balance = self.commitmentnote.get_balance()
        if not self.pk:
            if round(float(self.value), 2) > round(float(balance), 2):
                raise Exception("O valor informado deve ser menor que o saldo da NE.")
        else:
            if self.old_fields.get("value"):
                new_balance = round(float(balance), 2) + round(
                    float(self.old_fields.get("value")), 2
                )
                if round(float(self.value), 2) > round(float(new_balance), 2):
                    raise Exception(
                        "O valor informado deve ser menor que o saldo da NE."
                    )

    def validate_on_save(self):
        self.validate_balance_payment()

    def validate_bank_order(self):
        """
        Valida se já foi realizado o pagamento.

        Raises:
            Exception: pagamento já foi realizado
        """

        if self.bank_order:
            raise Exception("Não é possível remover um pagamento que já foi executado.")

    def validate_on_delete(self):
        self.validate_bank_order()

    def check_user_permissions(self):
        """
        Verifica as permissões do usuário para efetuar operações com os pagamentos.
        """

        _user = get_current_user()
        if _user.groups.filter(name__icontains="hiring-minute-"):
            if not _user.groups.filter(name="hiring-minute-manager"):
                if hasattr(self, "_action"):
                    # verifica se o usuário possui permissão para efetuar Pagamento
                    if self._action.lower() == "pay":
                        if _user.has_perm("contrato.do_minutesolicitationpayment"):
                            if not _user.groups.filter(name="hiring-minute-financial"):
                                raise Exception(
                                    "Você não possui permissão para efetuar Pagamento"
                                )
                        else:
                            raise Exception(
                                "Você não possui permissão para efetuar Pagamento"
                            )

                        self.status = 2
                    # verifica se o usuário possui permissão para desfazer Pagamento
                    elif self._action.lower() == "unpay":

                        if _user.has_perm("contrato.undo_minutesolicitationpayment"):
                            if not _user.groups.filter(name="hiring-minute-financial"):
                                raise Exception(
                                    "Você não possui permissão para desfazer Pagamento"
                                )
                        else:
                            raise Exception(
                                "Você não possui permissão para desfazer Pagamento"
                            )

                        self.bank_order = ""
                        self.payment_date = None
                        self.status = 1
                    else:
                        raise Exception("Você não pode efetuar esta operação.")

                else:
                    if _user.has_perm("contrato.change_minutesolicitationpayment"):
                        if self.pk:
                            if not self.is_minute_supervisor():
                                raise Exception("Você não é o fiscal da ata.")

                    if _user.has_perm("contrato.add_minutesolicitationpayment"):
                        if not self.pk:
                            if not self.is_minute_supervisor():
                                raise Exception("Você não é o fiscal da ata.")

                    if _user.has_perm("contrato.delete_minutesolicitationpayment"):
                        if not self.is_minute_supervisor():
                            raise Exception("Você não pode excluir um Pagamento.")

                return True

            if hasattr(self, "_action"):
                # verifica se o usuário possui permissão para efetuar Pagamento
                if self._action.lower() == "pay":
                    self.status = 2
                # verifica se o usuário possui permissão para desfazer Pagamento
                elif self._action.lower() == "unpay":
                    if _user.has_perm("contrato.undo_minutesolicitationpayment"):
                        self.bank_order = ""
                        self.payment_date = None
                        self.status = 1
                else:
                    raise Exception("Você não pode efetuar esta operação.")
            return True
        else:
            raise Exception(
                "Você não tem nenhum grupo de permissão do módulo Gestor de Contratações."
            )

    def save(self, *args, **kwargs):
        self.user = get_current_user()

        if self.check_user_permissions():
            self.validate_on_save()
            super(MinuteSolicitationPayment, self).save(*args, **kwargs)
            self.add_minute_action()

        else:
            raise Exception("Você não possui esta permissão no módulo de Pagamento.")

    def delete(self, *args, **kwargs):

        if self.check_user_permissions():

            self.validate_on_delete()

            super(MinuteSolicitationPayment, self).delete(*args, **kwargs)

        else:
            raise Exception("Você não possui permissão para excluir um Pagamento.")


class MinuteSolicitationRequisition(AuditTimestampModel):
    """
    Gerencia as requisições de pedidos.
    """

    solicitation = models.ForeignKey(
        "MinuteSolicitation", on_delete=models.PROTECT, related_name="%(class)ss"
    )
    number = models.CharField(
        "Número da Requisição", max_length=10, blank=True, null=True
    )
    object_execution = models.TextField("Execução do Objeto")
    expense_approver = models.ForeignKey(
        Cargo, on_delete=models.PROTECT, related_name="%(class)ss"
    )
    requester = models.ForeignKey(
        Servidor, on_delete=models.PROTECT, related_name="%(class)ss"
    )
    signature_date = models.DateField("Data da Assinatura", null=True, blank=True)

    class Meta:
        ordering = ("-id",)
        db_table = "hiring_minutesolicitationrequisition"

    def __str__(self):
        return "{}".format(self.number)

    def update_solicitation_status(self):
        """
        Atualiza o status do pedido para requisitado quando a requisição está sendo criada.
        """

        if not self.pk:
            action = MinuteSolicitationAction(
                solicitation=self.solicitation,
                user=get_current_user(),
                action=self.solicitation.REQUESTED,
            )
            action.save()
            self.solicitation.situation = self.solicitation.REQUESTED
            self.solicitation.save()

    def validate_number_exists(self):
        """Valida se a requisição já foi cadastrada.

        Raises:
            Exception: A requisição já existe.
        """

        if not self.pk or self.old_fields.get("number"):
            number = self.number.split("/")[0]
            number_year = self.number.split("/")[1]
            number = str(int(number))
            length = len(number)
            i = 1
            zero = ""
            while i <= (4 - length):
                zero = zero + "0"
                i = i + 1
            number = zero + number + "/" + number_year

            if MinuteSolicitationRequisition.objects.filter(
                solicitation__minute=self.solicitation.minute, number=number
            ).exists():
                raise Exception(
                    "Já existe uma requisição cadastrada com esta numeração."
                )
            else:
                self.number = number

    def validate_expense_approver(self):
        """
        Valida se foi informado o ordenador de despesa

        Raises:
            Exception: Ordenador de despesa não informado.
        """

        if not self.expense_approver:
            raise Exception("Informe o ordenador de despesa.")

    def validate_minute_validity_period(self):
        """
        Valida se a ata está dentro do período de validade.

        Raises:
            Exception: Ata não esta no período de validade.
        """

        _date_validity = date.today()
        if (
            _date_validity < self.solicitation.minute.begin_validity
            or _date_validity > self.solicitation.minute.end_validity
        ):
            raise Exception(
                "Não posso requisitar um pedido de uma ata fora do período de vigência"
            )

    def validate_on_save(self):
        self.validate_number_exists()
        self.validate_expense_approver()
        self.validate_minute_validity_period()

    def save(self, *args, **kwargs):
        self.validate_on_save()
        # se for mudar pra 6 e a ata estiver vencida, avisar o usuário
        self.update_solicitation_status()

        super(MinuteSolicitationRequisition, self).save(*args, **kwargs)


class SupervisorClassification(AuditTimestampModel):
    """
    A classificação do fiscal consiste em como o supervisor agirá no contrato.
    """

    # SUPERVISOR_CLASSIFICATION = (
    #     (1, u'Administrativo'),
    #     (2, u'Tecnico'),
    #     (3, u'Requisitante')
    # )

    kind = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("contrato", "SUPERVISOR_CLASSIFICATION")
    )
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("kind", "active")
        db_table = "hiring_supervisorclassification"

    def __str__(self):
        return "%s" % self.get_kind_display()

    def delete(self, *args, **kwargs):
        if self.agreementsupervisors.exists():
            raise Exception(
                "Não é possível excluir classificação que já se aplique a algum fiscal"
            )
        super(SupervisorClassification, self).delete(*args, **kwargs)


class Supervisor(AuditTimestampModel):
    """
    Esta classe é responsável por gerenciar os fiscais que supervisionam o contrato ou ata entre as partes interessadas.
    """

    # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Servidor,
        related_name="%(class)ss",
        verbose_name="Servidor",
        on_delete=models.CASCADE,
    )
    kind = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("contrato", "SUPERVISOR_KIND"),
        verbose_name="Tipo",
    )
    classifications = models.ManyToManyField(
        SupervisorClassification,
        related_name="%(class)ss",
        verbose_name="Classificações",
    )
    publication_document = models.CharField(
        "Portaria", max_length=250, null=True, blank=True
    )
    publication_document_date = models.DateField(null=True, blank=True)
    begin = models.DateField(null=True, blank=True, verbose_name="Início")
    end = models.DateField(null=True, blank=True, verbose_name="Fim")
    observation = models.TextField(blank=True, null=True, verbose_name="Observação")

    class Meta:
        abstract = True

    AUDITABLE = {
        "fields": ["employee_id", "kind", "publication_document_id", "begin", "end"]
    }

    def get_existing_employee_in_same_hiring(self):
        """
        Sobrescrever nas classes especializadas
        """
        pass

    @classmethod
    def get_employee_substitutes(cls, registry, begin_date, end_date):
        """
        Retorna todos os contratos e atas dentro do período de vigência para as datas informadas
        com os respectivos fiscais ativos(matricula), exluindo o fiscal informado.

        Returns:
            dict: {'kind': 'Ata ou Contrato', 'number': 'nnn/yyyy', 'registry': []}
        """

        employee_substitutes = []
        employee_substitutes_agreement = []
        employee_substitutes_minute = []

        employee_agreements = AgreementSupervisor.objects.filter(
            Q(employee__matricula=registry)
            & (
                Q(agreement__data_inicio__lte=begin_date)
                & (
                    Q(agreement__data_vencimento__gte=end_date)
                    | Q(agreement__data_vencimento=None)
                )
            )
        ).order_by("agreement__numero")

        for ea in employee_agreements:
            substitutes_agreement = dict()
            substitutes_agreement["number"] = ea.agreement.numero
            substitutes_agreement["kind"] = "Contrato"
            substitutes_agreement["registry"] = []
            for substitute_agreement in ea.agreement.agreementsupervisors.filter(
                end__isnull=True
            ).exclude(employee__matricula=registry):
                substitutes_agreement["registry"].append(
                    substitute_agreement.employee.matricula
                )

            employee_substitutes_agreement.append(substitutes_agreement)

        employee_minutes = MinuteSupervisor.objects.filter(
            Q(employee__matricula=registry)
            & (
                Q(minute__begin_validity__lte=begin_date)
                & (Q(minute__end_validity__gte=end_date) | Q(minute__end_validity=None))
            )
        ).order_by("minute__number")

        for em in employee_minutes:
            substitutes_minute = dict()
            substitutes_minute["number"] = em.minute.number
            substitutes_minute["kind"] = "Ata"
            substitutes_minute["registry"] = []

            for substitute_minute in em.minute.minutesupervisors.filter(
                end__isnull=True
            ).exclude(employee__matricula=registry):
                substitutes_minute["registry"].append(
                    substitute_minute.employee.matricula
                )

            employee_substitutes_minute.append(substitutes_minute)

        employee_substitutes = (
            employee_substitutes_agreement + employee_substitutes_minute
        )

        return employee_substitutes

    def _validate_close_supervisor(self):
        """
        Valida se o usuário tem permissão para encerrar o fiscal e se o fiscal já está encerrado.

        Raises:
            Exception: Não possui permissão.
            Exception: Fiscal já está encerrado.
        """

        user = get_current_user()
        if not user.has_perm("contrato.can_close_supervisor"):
            raise Exception("Você não possui permissão para realizar essa ação")
        if self.end:
            raise Exception("A atuação do fiscal já está encerrada")

    def _validate_changes(self):
        """
        Valida a alteração no cadastro do fiscal.

        Raises:
            Exception: Não é possível alterar o servidor, tipo e classificação do fiscal
        """

        if self.pk and (
            self.old_fields.get("employee_id") or self.old_fields.get("kind")
        ):
            raise Exception(
                "Uma vez cadastrado o fiscal, não é mais possível realizar alterações nos campos servidor, tipo e classificação"
            )

    def _validate_employe_is_active_and_kind(self):
        """
        Valida se o servidor informado é Servidor ou Membro e se está ativo.

        Raises:
            Exception: O servidor não está ativo.
            Exception: O servidor informado não é Servidor nem Membro.
        """

        if (
            not self.employee.ativo
            and self.pk
            and not hasattr(self, "_close_supervisor")
        ):
            raise Exception(
                "O servidor %s não está ativo." % self.employee.pessoa_fisica.nome
            )
        if self.employee.tipo not in ["S", "M"]:
            raise Exception(
                "%s não é nem Servidor nem Membro." % self.employee.pessoa_fisica.nome
            )

    def _validate_action(self):
        """
        Valida a ação de encerramento do fiscal

        Raises:
            Exception: Fiscal já está encerrado.
        """

        if hasattr(self, "_close_supervisor"):
            self._validate_close_supervisor()
            self.end = getattr(self, "_end") or date.today()
        elif self.end:
            raise Exception("Não é mais possível alterar este registro")

    def _validate_dates(self):
        if (self.begin and self.end) and (self.begin > self.end):
            raise Exception("A data de início não pode ser maior que a de fim")

    def _validate_twice_supervisor_at_same_time(self):
        """
        Valida se o fiscal possui atuação vigente e se o fiscal já esta cadastrado no o período informado.

        Raises:
            Exception: Possui atuação vigente
            Exception: O período informado de inicio e/ou fim conflita com algum anteriormente cadastrado.
        """

        same_employee = self.get_existing_employee_in_same_hiring()
        if same_employee.exists():
            if not self.pk:
                if same_employee.filter(end=None).exists():
                    raise Exception(
                        "Ainda há atuação vigente para %s. Encerre-o antes de criar nova atuação"
                        % self.employee.pessoa_fisica.nome
                    )
            else:
                same_employee = same_employee.exclude(pk=self.pk)
            if self.begin or self.end:
                this = NewDateRange((self.begin or self.end), (self.end or self.begin))
                for se in same_employee.all():
                    existing = NewDateRange(se.begin, se.end)
                    if existing.intersect(this).days:
                        raise Exception(
                            "O período de atuação conflita com algum anteriormente designado"
                        )

    def validate(self):
        self._validate_changes()
        self._validate_employe_is_active_and_kind()
        self._validate_action()
        self._validate_twice_supervisor_at_same_time()
        self._validate_dates()

    def __str__(self):
        return self.employee.pessoa_fisica.nome

    def save(self, *args, **kwargs):
        self.validate()
        super(Supervisor, self).save(*args, **kwargs)


class AgreementSupervisor(Supervisor):
    """
    Esta classe é responsável por gerenciar os fiscais que supervisionam o contrato entre as partes interessadas.
    """

    # Parametro "on_delete" adicionado. (Django 2)
    agreement = models.ForeignKey(
        Contrato,
        related_name="%(class)ss",
        verbose_name="Contrato",
        on_delete=models.CASCADE,
    )

    class Meta:
        permissions = (("can_close_supervisor", "Pode encerrar atuação de fiscal"),)
        db_table = "hiring_agreementsupervisor"
        verbose_name = "Fiscal de Contrato"

    def get_existing_employee_in_same_hiring(self):
        """
        Retorna uma query com as ocorrências do fiscal, para um mesmo contrato e servidor.
        """

        return self.__class__.objects.filter(
            agreement=self.agreement, employee=self.employee
        )


class MinuteSupervisor(Supervisor):
    """
    Esta classe é responsável por gerenciar os fiscais que supervisionam a ata entre as partes interessadas.
    """

    # Parametro "on_delete" adicionado. (Django 2)
    minute = models.ForeignKey(
        Minute,
        related_name="minutesupervisors",
        verbose_name="Ata",
        on_delete=models.CASCADE,
    )

    class Meta:
        permissions = (
            ("close_minutesupervisor", "Can close the supervisor of minutes"),
        )
        db_table = "hiring_minutesupervisor"

    def get_existing_employee_in_same_hiring(self):
        """
        Retorna uma query com as ocorrências do fiscal, para uma mesma ata e servidor.
        """

        return self.__class__.objects.filter(minute=self.minute, employee=self.employee)

    def validate_begin_date_with_minute_begin_validity(self):
        """
        Valida se a data de início da atuação do fiscal é posterior a data de assinatura da ata.

        Raises:
            Exception: Data de início de atuação é menor que a data da assinatura
        """

        if self.begin < self.minute.signature_date:
            raise Exception(
                "A data de início do fiscal não pode ser menor do que a data de assinatura da ata."
            )

    def save(self, *args, **kwargs):
        self.validate_begin_date_with_minute_begin_validity()
        super(MinuteSupervisor, self).save(*args, **kwargs)


class AgreementAnnotation(AuditTimestampModel):
    """
    Esta classe é responsável por gerenciar as anotaçoes referentes a um contrato.
    """

    kind = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "ANNOTATION_TYPE"),
        verbose_name="Tipo",
    )
    note = models.TextField(null=True, blank=True, verbose_name="Nota")
    date = models.DateField(null=True, blank=True, verbose_name="Data da anotação")
    schedule = models.BooleanField(verbose_name="Agendar Data?", default=False)
    schedule_date = models.DateField(
        null=True, blank=True, verbose_name="Data agendamento"
    )
    agreement = models.ForeignKey(
        "Contrato",
        related_name="annotations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    protocol = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        verbose_name="Protocolo de notificação",
        related_name="annotation",
        null=True,
        blank=True,
    )
    protocol_movement = models.ForeignKey(
        Movimentacao,
        on_delete=models.CASCADE,
        related_name="annotation",
        null=True,
        blank=True,
    )

    def get_annotation_type(self):
        """
        Retorna o rótulo do tipo de anotação.
        """
        annotation_type = Choice.objects.get(
            app_label__icontains="contrato",
            name__icontains="ANNOTATION_TYPE",
            value=self.kind,
        )
        return annotation_type.label

    def creating_notification_edoc(self):
        """
        Criando o protocolo de notificação.
        """
        self.protocol = Protocolo.docketing(
            subject=f"Comunicar {self.get_annotation_type()} - Contrato {self.agreement.numero}",
            document_type=TipoDocumento.objects.get(nome="MEMORANDO"),
            interested=person_from_user(self.created_by),
            home_court=employee_from_user(self.created_by).workplace_by_date(),
            content=self.note,
        )

    def dispatching_edoc(self):
        """
        Despachando edoc.
        """
        movement_zero = Movimentacao.objects.filter(
            protocolo=self.protocol, passo=0
        ).first()

        # Enviar apenas para fiscais ativos T-035425
        supervisors = self.agreement.active_supervisors()

        movement_zero.do_send(
            person_destination=[e.employee.pessoa_fisica.pk for e in supervisors],
            employee_origin=employee_from_user(self.created_by),
            physical=False,
            opinion=True,
        )

        movement_one = movement_zero.derivative_for.get(passo=1)
        self.protocol_movement = movement_one

    def edoc_creating(self):
        """
        Este método cria um protocolo eletrônico para notificação
        """
        try:
            with transaction.atomic():
                # Criando o documento eletrônico
                self.creating_notification_edoc()

                # Despachando o documento eletrônico
                self.dispatching_edoc()
        except:
            raise Exception("Problema com a criação do edoc de notificação.")

    def validate_surpevisor_annotation(self):
        pass

    def validate_on_save(self):
        self.validate_surpevisor_annotation()

    def save(self, *args, **kwargs):
        self.validate_on_save()

        if self.schedule:

            tomorrow = date.today() + timedelta(days=1)

            if self.schedule_date < tomorrow:
                self.schedule_date = tomorrow

        super(AgreementAnnotation, self).save(*args, **kwargs)


class MinuteAnnotation(AgreementAnnotation):
    """
        Já existe uma classe chamada AgreementAnnotation que é para anotações
    dos contratos. Agora - T-035534, surgiu a necessidade de se ter anotações
    também nas atas.
        A semelhança entre tais estruturas de dados é notável. No entanto, não há
    uma classe mais abstrata tipo "Annotation", mas sim "AgreementAnnotation".
    Optei por herdar de tal classe, ferindo o Príncipio da Segregação de
    Interfaces por estar de acordo com o príncípio do Não Repita a si Mesmo (DRY)
    , evitando uma enorma duplicação de códigos.
        Foi obedecido, também, até certo ponto, o Princípio Aberto/Fechado que diz
    que uma classe deve estar aberta para herança, mas fechada para modificação, uma
    vez a tabela já está funcionando e uma modificação em suas estruturas poderia
    trazer novos bugs.
        Refatorar não é viável devido à tabela já possuir inúmeros registros.
        Dessa forma, com confiança, podemos decidir de várias maneiras, no que optei
    por herdar e sobrescrever algo quando for necessário.
        Outra implicação é que as chaves estrangeiras devem permitir valores nulos,
    uma vez que a anotação pode ser do contrato ou da ata, mas nunca dos dois.
    """

    minute = models.ForeignKey(
        Minute,
        related_name="annotations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def creating_notification_edoc(self):
        """
        Criando o protocolo de notificação.
        """
        self.protocol = Protocolo.docketing(
            subject=f"Comunicar {self.get_annotation_type()} - Ata {self.minute.numero}",
            document_type=TipoDocumento.objects.get(nome="MEMORANDO"),
            interested=person_from_user(self.created_by),
            home_court=employee_from_user(self.created_by).workplace_by_date(),
            content=self.note,
        )

    def validate_surpevisor_annotation(self):
        """Valida se fiscal pode inserir/editar anotação"""

        user = get_current_user()

        # usuário não está no grupo de gestores?
        if not user.groups.filter(name="hiring-minute-manager"):

            # fiscais ativos da ata
            supervisors = self.minute.minutesupervisors.filter(
                end__isnull=True
            ).values_list("employee_id", flat=True)

            # servidor não está na lista de fiscais?
            if employee_from_user(user, False).id not in list(supervisors):
                raise Exception(
                    "Você não tem permissão para inserir/editar anotação nesta ata"
                )

            # está na lista de fiscais: anotação existe (editando) e usuario é diferente do usuario que a criou?
            elif self.pk and user.id != self.created_by_id:
                raise Exception("Você não tem permissão para editar esta anotação")


class Ride(AuditTimestampModel):
    """
    Esta classe é responsável pelo gerenciamento das caronas/adesões das atas.
    """

    # Número da Carona
    number = models.CharField(
        max_length=100, verbose_name="Número da Carona", blank=True, null=True
    )
    # Número do Ata
    minute = models.ForeignKey(
        Minute, related_name="rides", on_delete=models.CASCADE, default=1
    )
    # Órgão ou Instituição que aderiu
    person = models.ForeignKey(
        PessoaJuridica,
        verbose_name="Instituição/Órgão",
        on_delete=models.CASCADE,
        default=5526,
    )
    # Ofício / Solicitação
    asking = models.CharField(max_length=100, verbose_name="Documento de Solicitação")
    # Data da Solicitação
    asking_date = models.DateField(null=True, blank=True, verbose_name="Data do Pedido")
    # Data da anuência da empresa
    agreement_date = models.DateField(
        null=True, blank=True, verbose_name="Data da Anuência"
    )
    # Data de Autorização
    authorization_date = models.DateField(
        null=True, blank=True, verbose_name="Data de Autorização"
    )
    # Número do Dispacho
    dispatch_number = models.CharField(
        max_length=100, verbose_name="Número do Dispacho", null=True, blank=True
    )

    def __str__(self):
        return f"Carona {self.number}"

    def save(self, *args, **kwargs):
        # Verificando se há CNPJ cadastrado.
        if len(self.person.cnpj) > 0:
            super(Ride, self).save(*args, **kwargs)
            year = str(datetime.now().year)
            ride = Ride.objects.filter(pk=self.pk)
            ride.update(number=f"{self.pk}/{year}")
        else:
            raise Exception(
                "O Órgão selecionado não possui CNPJ cadastrado, cadastre para seguir."
            )


class RideItem(AuditTimestampModel):
    """
    Esta classe é responsável por gerenciar os itens que estão na carona,
    suas quantidades e valores totais.
    """

    # Carona
    ride = models.ForeignKey(Ride, verbose_name="Carona", on_delete=models.PROTECT)
    # Item adicionado à carona
    item = models.ForeignKey(MinuteItem, verbose_name="Item", on_delete=models.CASCADE)
    # Quantidade solicitada do item
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    # status do item (optei por choices devido possibilidades futuras de surgirem mais de 2 tipos de status)
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("contrato", "STATUS_RIDE_ITEM"), default=1
    )
    # justificativa
    justification = models.TextField(null=True, blank=True)

    # Função mágica que retorna o nome de registro em um dataset
    def __str__(self):
        return f"{self.amount} de {self.item.description}"

    # Valida se é um item válido
    def valid_item(self):
        # Valida se não é um registro de grupo ou linha que, infelizmente, é registrado como um item também.
        if self.item.unitary_value is None or self.item.quantity is 0:
            raise Exception(
                "Selecione um item com valor unitário ou quantidade maiores que 0."
            )
        # A solicitação deve ser maior que 0
        if self.amount <= 0:
            raise Exception("A quantidade deve ser maior que zero.")

    @property
    def net_maximum_amount(self):
        """
        Total possível de produtos constantes na ata líquido de solicitações anteriores.
        """

        # Total já utilizado deste produto
        minute = self.ride.minute
        item = self.item
        items = RideItem.objects.filter(ride__minute=minute, item=item)
        amount = items.aggregate(Sum("amount"))

        amount_sum = 0
        if amount["amount__sum"] is not None:
            amount_sum = amount["amount__sum"]

        # Máximo permitido para este produto
        adhesions_quantity = int(self.item.minute.adhesions_quantity)
        maximum_amount = adhesions_quantity * self.item.quantity

        return float(maximum_amount) - float(amount_sum)

    # Valida se não excede a quantidade máxima de adesões por item
    def item_exce_maximum_amount(self):
        """
        Cada produto somente pode ser comprado a quantidade máxima
        de adesões (adhesions_quantity) multiplicada pela quantidade
        registrada (quantity) por instituição.
        """

        # Verificando se é um tipo válido
        self.valid_item()

        if self.amount > self.net_maximum_amount:
            raise Exception(
                f"Quantidade solicitada({self.amount}) excede o saldo restante ({self.net_maximum_amount}) para adesões para essa Ata."
            )

    # Valida se não excede a quantidade máxima de compras (50%) por um caroneiro
    def rider_exce_maximum_registered(self):
        """
        Cada caroneiro não poderá adquirir mais do que o que foi
        registrado na ata para aquele item.
        """

        # Verificando se é um tipo válido
        self.valid_item()

        registered_quantity = self.item.quantity

        half_registered_quantity = 0
        if registered_quantity > 1:
            half_registered_quantity = float(registered_quantity) * 0.5
        elif registered_quantity == 1:
            raise Exception(
                "Este produto possui apenas 1 unidade registrada e não permite carona."
            )

        # Recuperando Demandas Anteriores
        recovered_amount = (
            RideItem.objects.filter(
                ride__minute=self.ride.minute,
                item=self.item,
                ride__person__cnpj=self.ride.person.cnpj,
            )
            .exclude(pk=self.pk)
            .aggregate(Sum("amount"))
        )

        total_amount = 0
        if recovered_amount["amount__sum"] is not None:
            recovered_amount = recovered_amount["amount__sum"]
            total_amount = float(recovered_amount) + float(self.amount)
        else:
            total_amount = self.amount

        if total_amount > half_registered_quantity and half_registered_quantity > 0:
            raise Exception(
                f"A quantidade solicitada({total_amount}) não pode ser superior à 50% à registrada({half_registered_quantity}) por órgão solicitante."
            )

    def save(self, *args, **kwargs):

        # Validando quantidade a ser adquirida
        self.rider_exce_maximum_registered()
        self.item_exce_maximum_amount()

        super(RideItem, self).save(*args, **kwargs)

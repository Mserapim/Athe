from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField

from contrib.utils import getLogger
from datetime import datetime, timedelta
from django.db import transaction

from standard.models import AuditTimestampModel, Choice, Assinatura
from ged.models import Arquivo
from rh.models import Servidor, DadoBancarioPessoa, Estado, Localidade, Banco

from diarias.utils.distancia_itinerario import (
    buscar_gravar_distancia_destino,
    DAADistanciaItinerario,
)
from diarias.utils.utils import (
    buscar_tipo_solicitante_viagem,
    buscar_proximo_cod_os_beneficiario,
    criar_historico,
)
from diarias.const import TURNOS
from django.db.models import Sum

log = getLogger(__name__)


class Viagem(AuditTimestampModel):
    """
    Modelo para armazenar informações sobre Viagens
    """

    TIPO_VIAGEM = (
        ("ESTADUAL", "Estadual"),
        ("NACIONAL", "Nacional"),
        ("INTERNACIONAL", "Internacional"),
    )

    tipo_viagem = models.CharField(
        "Tipo de viagem",
        max_length=50,
        choices=TIPO_VIAGEM,
        default="ESTADUAL",
        db_index=True,
    )
    hospedagem_anfitriao = models.BooleanField(
        "Hospedagem pelo anfitrião", default=False
    )
    motivo_viagem = models.IntegerField(
        "Motivo da viagem",
        choices=Choice.get_choices_for("diarias", "MOTIVO_VIAGEM"),
        null=True,
    )
    finalidade_viagem = models.IntegerField(
        "Finalidade da viagem",
        choices=Choice.get_choices_for("diarias", "FINALIDADE_VIAGEM"),
        null=True,
    )
    data_inicio_viagem = models.DateField(
        "Data início da viagem", null=True, blank=True
    )
    data_fim_viagem = models.DateField("Data fim da viagem", null=True, blank=True)
    resumo = models.TextField("Resumo sobre a viagem", null=True, blank=True)
    justificativa = models.TextField("Justificativa", null=True, blank=True)
    tipo_solicitante = models.IntegerField(
        "Tipo de solicitante",
        choices=Choice.get_choices_for("diarias", "TIPO_SOLICITANTE"),
        null=True,
    )
    fluxo = models.ForeignKey(
        "FluxoViagem",
        on_delete=models.PROTECT,
        related_name="viagens",
        null=True,
        blank=True,
    )
    excedente = models.BooleanField("Viagem Excedente", default=False)
    viagem_origem = models.ForeignKey(
        "Viagem",
        on_delete=models.PROTECT,
        related_name="viagens_excedentes",
        null=True,
        blank=True,
    )
    motorista = models.BooleanField("Motorista", default=False)

    importada = models.BooleanField(default=False)
    gedoc_unico = models.CharField(
        "Numero Gedoc Unico", max_length=50, null=True, blank=True
    )
    gedoc_antigo = models.CharField(
        "Numero Gedoc Antigo", max_length=50, null=True, blank=True
    )

    class Meta:
        verbose_name = "Viagem"
        verbose_name_plural = "Viagens"
        ordering = ("-data_inicio_viagem",)

    def __str__(self):
        dt_inicio = self.data_inicio_viagem.strftime("%d/%m/%Y")
        dt_fim = self.data_fim_viagem.strftime("%d/%m/%Y")
        return f"{self.get_tipo_viagem_display()} - {dt_inicio}-{dt_fim}"

    @property
    def solicitante_servidor(self):
        return self.created_by.servidor

    @property
    def solicitante(self):
        return f"{ self.solicitante_servidor.pessoa_fisica.social_name }"

    @property
    def data_solicitacao(self):
        return self.created_at

    @property
    def fluxo_atual(self):
        """
        Método que retorna o fluxo atual da viagem, com base nos beneficiários.

        Caso ainda não tenha beneficiários cadastrados à viagem, será retornado em relação ao primeiro fluxo.
        Quando houver somente um beneficiário, será retornado o fluxo em relação ao beneficiário.
        Quando houver mais de um beneficiário, será retornado o fluxo ordenado pelo campo 'ordem' com menor valor.
        """

        from diarias.models import FluxoViagem

        q_fluxo = FluxoViagem.objects.order_by("ordem")

        if self.pk is None or self.beneficiarios.count() == 0:
            fluxo = q_fluxo.first()
        else:
            fluxos_ids = [
                b.fluxo.pk for b in self.beneficiarios.all() if b.fluxo is not None
            ]
            fluxo = q_fluxo.filter(id__in=fluxos_ids).first()

        return fluxo

    @property
    def situacao_etapa_atual(self):
        """
        Método que retorna um texto do fluxo atual da viagem, que é a concatenação da 'situação' e 'etapa' com base nos beneficiários.
        """

        fluxo = self.fluxo_atual

        return f"{fluxo.get_situacao_display()} - {fluxo.get_etapa_display()}"

    @property
    def qtd_beneficiarios(self):
        return self.beneficiarios.count()

    def definir_fluxo_atual(self):
        self.fluxo = self.fluxo_atual

    def validacoes_criacao(self):
        self.validar_data_limite()

    def validar_data_limite(self):
        hoje = datetime.now()
        # Data daqui a 5 dias
        data_limite = hoje + timedelta(days=5)

        if self.data_inicio_viagem < data_limite.date():
            raise ValueError(
                "Não é possível criar viagens com menos de 5 dias de antecedência em relação à data de início."
            )

    def save(self, *args, **kwargs):
        ignorar_validacao = kwargs.pop("ignorar_validacao", False)
        criar_hist = True
        tipo_save = "update"

        if self.importada:
            ignorar_validacao = True

        if self.pk is None:
            tipo_save = "create"
            if not ignorar_validacao:
                self.validacoes_criacao()

            if self.importada is False:
                self.definir_fluxo_atual()

        if tipo_save == "create" and not ignorar_validacao:
            self.validacoes_criacao()

        super(Viagem, self).save(*args, **kwargs)

        if tipo_save == "create":
            criar_hist = False
            if not self.importada:
                self.tipo_solicitante = buscar_tipo_solicitante_viagem(
                    self.solicitante_servidor
                )
            self.save()

        if criar_hist and not self.importada:
            criar_historico(self)

    @property
    def possui_excedente(self):
        return self.viagens_excedentes.exclude(motorista=True).exists()

    @property
    def numero_os_importacao(self):
        if not self.importada:
            return None
        return self.beneficiarios.first().codigo_os


class ViagemAnexo(AuditTimestampModel):
    """
    Modelo responsável por armazenar os anexos sobre uma Viagem
    """

    arquivo = models.ForeignKey(
        Arquivo, on_delete=models.PROTECT, related_name="anexos_viagem"
    )
    viagem = models.ForeignKey(
        Viagem, on_delete=models.PROTECT, related_name="anexos_viagem"
    )

    class Meta:
        verbose_name = "Anexo de Viagem"
        verbose_name_plural = "Anexos de Viagem"

    def __str__(self):
        return f"{self.viagem} - {self.arquivo.filename}"


class Beneficiario(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre beneficiários de uma Viagem
    """

    TIPO_LOCOMOCAO = (
        ("veiculo_proprio", "Veículo próprio"),
        ("veiculo_mpmt", "Veículo oficial do MPMT"),
        ("solic_passagem_aerea", "Solicitação de passagem aérea"),
    )

    servidor = models.ForeignKey(
        Servidor, on_delete=models.PROTECT, related_name="diarias_viagens"
    )
    viagem = models.ForeignKey(
        Viagem, on_delete=models.PROTECT, related_name="beneficiarios"
    )
    conta_bancaria_pgto = models.ForeignKey(
        DadoBancarioPessoa,
        on_delete=models.PROTECT,
        related_name="diarias_beneficiario",
        null=True,
    )
    acomp_autoridade_deferimento = models.BooleanField(
        "Deferimento do acompanhamento de autoridade", default=False
    )
    autoridade = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="beneficiario_autoridade",
    )
    fluxo = models.ForeignKey(
        "FluxoViagem",
        on_delete=models.PROTECT,
        related_name="beneficiarios",
        null=True,
        blank=True,
    )
    cargo = models.ForeignKey(
        "CargoDiarias",
        on_delete=models.PROTECT,
        related_name="beneficiarios",
        null=True,
        blank=True,
    )
    codigo = models.IntegerField("Código", null=True, blank=True, db_index=True)
    datas_evento = ArrayField(models.CharField(max_length=250), null=True, blank=True)
    titulo_evento = models.CharField(
        "Título do evento", max_length=250, null=True, blank=True
    )
    tipo_locomocao = models.CharField(
        "Tipo de locomoção",
        max_length=50,
        choices=TIPO_LOCOMOCAO,
        null=True,
        blank=True,
        db_index=True,
    )
    numero_empenho = models.CharField(
        "Número de Empenho", max_length=50, null=True, blank=True
    )
    numero_nota_liquidacao = models.CharField(
        "Número da Nota de Liquidação", max_length=50, null=True, blank=True
    )
    numero_ordem_bancaria = models.CharField(
        "Número da Ordem Bancária", max_length=50, null=True, blank=True
    )
    chefe_imediato = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        related_name="chefe_imediato_diarias",
        null=True,
        blank=True,
    )
    gedoc_numero = models.TextField(
        "Número GEDOC", max_length=50, null=True, blank=True
    )

    class Meta:
        verbose_name = "Beneficiário"
        verbose_name_plural = "Beneficiários"

    def __str__(self):
        return f"{self.servidor} - {self.viagem}"

    @property
    def codigo_os(self):
        codigo = "" if self.codigo is None else self.codigo
        codigo = str(codigo).rjust(6, "0")
        return f"{codigo}/{self.created_at.year}"

    def definir_codigo(self):
        if not self.viagem.importada:
            self.codigo = buscar_proximo_cod_os_beneficiario()

    @property
    def total_distancia_destinos(self):
        """
        Método que retorna a diastancia total entre os trechos de viagem do Beneficiário.
        """
        return self.destinos.aggregate(distancia=Sum("distancia_km"))["distancia"]

    @property
    def pode_editar_valor_deferido(self):
        """
        Método que retorna se pode editar o valor deferido do Beneficiário.
        Para tando, a solicitação do Beneficiário deve estar após o fluxo do DAA e antes do fluxo
        DEFIN - Aguardando pagamento, ou após o fluxo do DAA e antes do fluxo do DAA - Ciência de cancelamento.
        """
        fluxos_daa = [8, 46]
        fluxos_defin = [27]
        fluxos_deplan = [10]
        fluxo_ciencia_cancelamento_daa = 34
        fluxo_ciencia_cancelamento_deplan = 35
        fluxo_defin_pagamento = 15

        historico_fluxo = self.historico_fluxos.filter(
            fluxo__id__in=(fluxos_daa + fluxos_defin + fluxos_deplan)
        ).exists()
        historico_fluxo_ciencia_cancelamento = self.historico_fluxos.filter(
            fluxo__id__in=[
                fluxo_ciencia_cancelamento_daa,
                fluxo_ciencia_cancelamento_deplan,
            ]
        ).exists()
        historico_fluxo_defin = self.historico_fluxos.filter(
            fluxo__id=fluxo_defin_pagamento
        ).exists()

        if historico_fluxo and not (
            historico_fluxo_defin or historico_fluxo_ciencia_cancelamento
        ):
            return True
        return False

    @property
    def codigo_os_viagem_original(self):
        if self.viagem.viagem_origem:
            beneficiario_origem = Beneficiario.objects.filter(
                viagem=self.viagem.viagem_origem, servidor=self.servidor
            ).first()

            if beneficiario_origem:
                return beneficiario_origem.codigo_os
        return None

    @property
    def codigo_os_excedente(self):
        if self.viagem.possui_excedente:
            viagem_excedente = Viagem.objects.filter(
                viagem_origem=self.viagem, beneficiarios__servidor=self.servidor
            ).first()

            beneficiario_excedente = Beneficiario.objects.filter(
                viagem=viagem_excedente, servidor=self.servidor
            ).first()

            if beneficiario_excedente:
                return beneficiario_excedente.codigo_os
        return None

    def validacoes_criacao(self):
        self.validar_beneficiario_existente()
        self.validar_afastamentos_conflitantes()
        self.validar_viagens_conflitantes()

    def validar_beneficiario_existente(self):
        beneficiarios = Beneficiario.objects.filter(
            viagem=self.viagem, servidor=self.servidor
        )

        if beneficiarios.exists():
            raise ValueError("O beneficiário já participa da viagem.")

    def validar_afastamentos_conflitantes(self):

        if self.viagem.excedente:
            return None

        from rh.afastamento.models import BaseLicencaAfastamento
        from rh.pvf.const import (
            STS_CANCELED_APPLICANT,
            STS_CANCELED_DGP,
            STS_EFFECTIVE,
            STS_REJECTED,
        )
        from rh.pvf.models import PortalRequest, SendingTimeSheet

        requests_q = PortalRequest.objects.filter(employee=self.servidor)

        data_inicio = self.viagem.data_inicio_viagem
        data_fim = self.viagem.data_fim_viagem

        requests_q = requests_q.filter(
            Q(
                Q(portalrequestusufruct__isnull=False)
                & (
                    Q(
                        portalrequestusufruct__activity__usufructs__start_date__range=[
                            data_inicio,
                            data_fim,
                        ],
                    )
                    | Q(
                        portalrequestusufruct__activity__usufructs__end_date__range=[
                            data_inicio,
                            data_fim,
                        ],
                    )
                )
            )
            | Q(
                Q(portalrequestabsence__isnull=False)
                & (
                    Q(
                        portalrequestabsence__start_date__range=[data_inicio, data_fim],
                    )
                    | Q(
                        portalrequestabsence__end_date__range=[data_inicio, data_fim],
                    )
                )
            )
        ).exclude(status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT])

        if len(requests_q) > 0:
            raise ValueError(
                "Este beneficiário possui alguma solicitação de afastamento ou licença no período, solicite que o mesmo regularize o afastamento para que consiga solicitar diárias."
            )

        afastamentos = BaseLicencaAfastamento.verifica_interseccao_periodo(
            servidor=self.servidor,
            data_inicio=self.viagem.data_inicio_viagem,
            data_fim=self.viagem.data_fim_viagem,
        )

        if len(afastamentos) > 0:
            raise ValueError(
                "Este beneficiário possui afastamento ou licença no período, solicite que o mesmo regularize o afastamento para que consiga solicitar diárias."
            )

    def validar_viagens_conflitantes(self):
        """
        Método para validar se o beneficiário possui outras viagens no mesmo período.
        Verifica se há qualquer interseção de datas entre a viagem atual e outras viagens do mesmo beneficiário.
        """

        if self.viagem.excedente:
            return None

        viagens_canceladas = self.servidor.diarias_viagens.filter(
            fluxo__in=[21, 32]
        ).values("id")

        viagens_conflitantes = (
            Viagem.objects.filter(
                beneficiarios__servidor=self.servidor,
                data_inicio_viagem__lt=self.viagem.data_fim_viagem,
                data_fim_viagem__gt=self.viagem.data_inicio_viagem,
            )
            .exclude(pk=self.viagem.pk)
            .exclude(id__in=viagens_canceladas)
        )

        if viagens_conflitantes.exists():
            raise ValueError("Este beneficiário já possui viagem no período.")

    def save(self, *args, **kwargs):
        criar_hist = False

        if self.pk is None and not self.viagem.importada:
            criar_hist = True
            self.fluxo_id = 2  # ID do Fluxo de 'Solicitante - Rascunho'
            self.definir_codigo()
            self.validacoes_criacao()

        super(Beneficiario, self).save(*args, **kwargs)

        if criar_hist and not self.viagem.importada:
            criar_historico(self)

    def delete(self, *args, **kwargs):

        validate = kwargs.pop("validate", True)

        if validate:
            situacao_rascunho = Choice.objects.get(
                app_label="diarias",
                name="SITUACAO_SOLICITACAO_VIAGEM",
                label="Rascunho",
            )

            if self.fluxo.situacao != situacao_rascunho.value:
                raise Exception(
                    "Não é possível excluir o beneficiário após o envio da solicitação"
                )

        with transaction.atomic():

            CalculoConsolidado.objects.filter(beneficiario=self).delete()
            Destino.objects.filter(beneficiario=self).delete()
            HistoricoFluxoViagemBeneficiario.objects.filter(beneficiario=self).delete()

            super(Beneficiario, self).delete(*args, **kwargs)


class CalculoConsolidado(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações consolidadas dos cálculos de um Beneficiário
    """

    beneficiario = models.OneToOneField(
        Beneficiario,
        on_delete=models.PROTECT,
        related_name="calculos_diarias_consolidados",
    )
    qtd_total_diarias_calculadas = models.DecimalField(
        verbose_name="Qtd total de diárias calculadas",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qtd_total_diarias = models.DecimalField(
        verbose_name="Qtd total de diárias",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qtd_total_excedente = models.DecimalField(
        verbose_name="Qtd total de diárias excedentes",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qtd_total_diarias_deferido = models.DecimalField(
        verbose_name="Qtd total de diárias deferido",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qtd_total_diarias_dentro_uf = models.DecimalField(
        verbose_name="Qtd total de diárias dentro do Estado MT",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qtd_total_diarias_fora_uf = models.DecimalField(
        verbose_name="Qtd total de diárias fora do Estado MT",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_base_diaria = models.DecimalField(
        verbose_name="Valor base da diária",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_base_subsidio = models.DecimalField(
        verbose_name="Valor base do subsídio",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_base_desc_transporte = models.DecimalField(
        verbose_name="Valor base de desconto em transporte",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_desc_transporte = models.DecimalField(
        verbose_name="Valor de desconto em transporte",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_base_desc_alimentacao = models.DecimalField(
        verbose_name="Valor base de desconto em alimentação",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_desc_alimentacao = models.DecimalField(
        verbose_name="Valor de desconto em alimentação",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_diarias_dentro_estado = models.DecimalField(
        verbose_name="Valor total dentro do Estado MT",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_diarias_fora_estado = models.DecimalField(
        verbose_name="Valor total fora do Estado MT",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_veiculo_mp = models.DecimalField(
        verbose_name="Valor total com veículo do MPMT",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_desconto = models.DecimalField(
        verbose_name="Valor total de desconto",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_bruto = models.DecimalField(
        verbose_name="Valor total bruto",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_liquido = models.DecimalField(
        verbose_name="Valor total líquido",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_total_liquido_deferido = models.DecimalField(
        verbose_name="Valor total líquido deferido",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    reanalise = models.BooleanField("Reanalise devido alterações do DAA", default=False)

    class Meta:
        verbose_name = "Cálculo consolidado"
        verbose_name_plural = "Cálculos consolidado"

    def __str__(self):
        total_desc = (
            "0" if self.valor_total_desconto is None else self.valor_total_desconto
        )
        total_bruto = "0" if self.valor_total_bruto is None else self.valor_total_bruto
        total_liq = (
            "0" if self.valor_total_liquido is None else self.valor_total_liquido
        )
        total_def = (
            "0"
            if self.valor_total_liquido_deferido is None
            else self.valor_total_liquido_deferido
        )

        return f"{self.beneficiario} - Total desc:{total_desc} - Total bruto: {total_bruto} - Total líquido: {total_liq} - Total líquido deferido: {total_def}"

    def qtd_diarias(self):
        return (
            self.qtd_total_diarias_deferido
            if self.qtd_total_diarias_deferido
            else self.qtd_total_diarias
        )

    @property
    def valor_unit_desc_transporte(self):
        return round(self.valor_base_desc_transporte / 30, 2)

    @property
    def valor_unit_desc_alimentacao(self):
        return round(self.valor_base_desc_alimentacao / 30, 2)


class Destino(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre destinos de um beneficiário em uma viagem
    """

    TIPO_DESLOCAMENTO = (
        ("0", "Veículo próprio"),
        ("1", "Avião"),
        ("2", "Veículo institucional"),
        ("3", "Ônibus"),
        ("4", "Van"),
        ("5", "Veículo Oficial MP"),
        ("6", "Veículo Locado"),
        ("7", "Aeronave Fretada"),
        ("8", "Outros"),
        ("9", "Veículo Externo"),
        ("10", "Veiculo Acautelado"),
        ("", "Não Informado"),
        (None, "Não Informado"),
    )

    beneficiario = models.ForeignKey(
        Beneficiario, on_delete=models.PROTECT, related_name="destinos"
    )
    municipio_origem = models.ForeignKey(
        Localidade, on_delete=models.PROTECT, related_name="diarias_destinos_mun_origem"
    )
    municipio_destino = models.ForeignKey(
        Localidade,
        on_delete=models.PROTECT,
        related_name="diarias_destinos_mun_destino",
    )
    forma_deslocamento = models.CharField(
        "Forma de deslocamento",
        max_length=10,
        choices=TIPO_DESLOCAMENTO,
        default="2",
        db_index=True,
        blank=True,
        null=True,
    )
    pref_turno_ida = models.CharField(
        "Preferência de turno da ida",
        max_length=50,
        choices=TURNOS,
        default="MANHA",
        db_index=True,
    )
    data = models.DateTimeField("Data", null=True, blank=True)
    distancia_m = models.PositiveIntegerField("Distância (m)", null=True, blank=True)
    distancia_km = models.PositiveIntegerField("Distância (km)", null=True, blank=True)
    com_motorista = models.BooleanField("Com Motorista", default=False)
    veiculo_daa = models.BooleanField("Veículo do DAA", default=True)
    data_daa = models.DateTimeField(
        "Data segundo análise do DAA", null=True, blank=True
    )

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"

    def __str__(self):
        origem = f"{self.municipio_origem.estado.sigla}/{self.municipio_origem.nome}"
        destino = f"{self.municipio_destino.estado.sigla}/{self.municipio_destino.nome}"
        data = self.data.strftime("%d/%m/%Y")
        return f"{self.beneficiario.servidor} - origem:{origem} - destino: {destino} - data: {data}"

    @property
    def unicode(self):
        origem = f"{self.municipio_origem.estado.sigla}/{self.municipio_origem.nome}"
        destino = f"{self.municipio_destino.estado.sigla}/{self.municipio_destino.nome}"
        data = self.data.strftime("%d/%m/%Y")
        return f"origem:{origem} - destino: {destino} - data: {data}"

    def buscar_gravar_distancia(self):
        if (
            self.municipio_origem
            and self.municipio_destino
            and self.distancia_m is None
            and self.distancia_km is None
        ):
            res = DAADistanciaItinerario().buscar_distancia_cidades(
                self.municipio_origem.ibge, self.municipio_destino.ibge
            )
            self.distancia_m = res[0]["distancia"]
            self.distancia_km = res[0]["distancia_km"]
            self.save()

    def validacoes(self):
        self.validar_comarca()
        self.validar_datas_periodo_viagem()
        self.validar_destino_duplicado()
        self.validar_destino_data_duplicado()

    def validar_destino_data_duplicado(self):

        destinos = Destino.objects.filter(
            beneficiario=self.beneficiario,
            data=self.data,
        )

        if self.pk:
            destinos = destinos.exclude(pk=self.pk)

        if destinos.exists():
            lista_destinos = [d for d in destinos]
            raise ValueError(f"Trecho de destino com data duplicada - {lista_destinos}")

    def validar_destino_duplicado(self):

        destinos = Destino.objects.filter(
            beneficiario=self.beneficiario,
            municipio_origem=self.municipio_origem,
            municipio_destino=self.municipio_destino,
            data=self.data,
        )

        if self.pk:
            destinos = destinos.exclude(pk=self.pk)

        if destinos.exists():
            lista_destinos = [d for d in destinos]
            raise ValueError(f"Trecho de destino Duplicado - {lista_destinos}")

    def validar_datas_periodo_viagem(self):
        """
        Valida se as datas de ida e saída estão dentro do período da viagem do beneficiário.

        Raises:
            ValueError: Se as datas de ida e/ou saída estiverem fora do período da viagem.
        """
        viagem = self.beneficiario.viagem
        data_inicio_viagem = viagem.data_inicio_viagem
        data_fim_viagem = viagem.data_fim_viagem
        data = self.data

        if isinstance(data, datetime):
            data = data.date()

        if data < data_inicio_viagem or data > data_fim_viagem:
            raise ValueError(
                "A data do destino deve estar dentro do período da viagem."
            )

    def validar_comarca(self):
        """
        Valida se a comarca da origem e do destino são a mesma

        Raises:
            ValueError: Se as comarcas de origem e destino são a mesma.
        """
        origem = self.municipio_origem.comarca
        destino = self.municipio_destino.comarca

        if origem is not None and origem == destino:
            raise ValueError(
                "Não é permitido cadastrar municipios de origem e destino da mesma comarca"
            )

    def save(self, *args, **kwargs):
        if not self.beneficiario.viagem.importada:
            self.validacoes()
        super(Destino, self).save(*args, **kwargs)
        buscar_gravar_distancia_destino(self)

    def delete(self, *args, **kwargs):

        situacao_rascunho = Choice.objects.get(
            app_label="diarias", name="SITUACAO_SOLICITACAO_VIAGEM", label="Rascunho"
        )

        if self.beneficiario.fluxo.situacao != situacao_rascunho.value:
            raise Exception(
                "Não é possível excluir o destino após o envio da solicitação"
            )

        with transaction.atomic():
            PassagemAeriaViagem.objects.filter(destino=self).delete()
            VeiculoViagem.objects.filter(destino=self).delete()

            super(Destino, self).delete(*args, **kwargs)

    @property
    def evento(self):
        return self.eventos.first() if self.eventos.exists() else None

    @property
    def analise_daa(self):
        """
        Verifica se existe PassagemAeriaViagem ou VeiculoPassageiro para o Destino.
        """
        passagem_existente = hasattr(self, "passagem")
        veiculo_passageiro_existente = self.veiculo_passageiros.exists()

        return passagem_existente or veiculo_passageiro_existente


class EventoBeneficiario(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações dos eventos do beneficiário
    """

    titulo = models.CharField("Título do evento", max_length=250, null=True, blank=True)
    beneficiario = models.ForeignKey(
        Beneficiario, on_delete=models.PROTECT, related_name="eventos"
    )
    data_inicio = models.DateField("Data Início")
    data_fim = models.DateField("Data Fim", null=True, blank=True)
    destinos = models.ManyToManyField(
        Destino, verbose_name="Destinos", related_name="eventos"
    )

    class Meta:
        verbose_name = "Evento do Beneficiário"
        verbose_name_plural = "Eventos do Beneficiário"

    def __str__(self):
        dt_inicio = self.data_inicio.strftime("%d/%m/%Y")
        dt_fim = f" até {self.data_fim.strftime('%d/%m/%Y')}" if self.data_fim else ""
        txt_data = (
            f" {self.titulo or ''} de {dt_inicio}{dt_fim}"
            if dt_fim
            else f"data: {dt_inicio}"
        )

        return f"{self.beneficiario} - {txt_data}"

    def delete(self, *args, **kwargs):
        if self.destinos.exists():
            raise ValueError(
                "Este evento contém trechos de destinos associados a ele. Por favor, remova essas associações."
            )
        return super(self.__class__, self).delete(*args, **kwargs)

    def validacoes(self):
        self.validar_datas_periodo_viagem()
        self.validar_datas()

    def validar_datas(self):
        """
        Valida se a data inicio é menos que a data fim.

        Raises:
            ValueError: Se a data inicio é maior que a data fim.
        """

        if self.data_fim and (self.data_inicio > self.data_fim):
            raise ValueError("A data de início do evento deve ser menor que data fim.")

    def validar_datas_periodo_viagem(self):
        """
        Valida se as datas esta dentro do período da viagem do beneficiário.

        Raises:
            ValueError: Se a datas do evento estão fora do período da viagem.
        """
        viagem = self.beneficiario.viagem
        data_inicio_viagem = viagem.data_inicio_viagem
        data_fim_viagem = viagem.data_fim_viagem
        data_inicio = self.data_inicio
        data_fim = self.data_fim

        if not (data_inicio_viagem <= data_inicio <= data_fim_viagem):
            raise ValueError(
                "A data de início do evento deve estar dentro do período da viagem."
            )

        if data_fim and not (data_inicio_viagem <= data_fim <= data_fim_viagem):
            raise ValueError(
                "A data de fim do evento deve estar dentro do período da viagem."
            )

    def save(self, *args, **kwargs):
        self.validacoes()
        super(EventoBeneficiario, self).save(*args, **kwargs)


class PassagemAeriaViagem(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre passagem aéria de um Destino
    """

    destino = models.OneToOneField(
        Destino, on_delete=models.PROTECT, related_name="passagem"
    )
    data_hora_bilhete = models.DateTimeField(
        "Data e hora de ida do bilhete para o destino", null=True, blank=True
    )
    nome_companhia = models.CharField(
        "Nome da companhia", max_length=100, null=True, blank=True
    )
    aeroporto = models.CharField(
        "Nome do aeroporto", max_length=100, null=True, blank=True
    )
    numero_bilhete = models.CharField(
        "Número do bilhete", max_length=100, null=True, blank=True
    )

    class Meta:
        verbose_name = "Passagem aéria"
        verbose_name_plural = "Passagens aéria"

    def __str__(self):
        return f"{self.destino} - numero do bilhete:{self.numero_bilhete}"


class PassagemAereaAnexo(AuditTimestampModel):
    """
    Modelo responsável por armazenar os anexos de Passagem Aérea
    """

    passagem = models.ForeignKey(
        PassagemAeriaViagem, on_delete=models.PROTECT, related_name="anexos"
    )
    arquivo = models.ForeignKey(
        Arquivo, on_delete=models.PROTECT, related_name="passagem_aerea_arquivos"
    )

    class Meta:
        verbose_name = "Anexo de Passagem Aérea Viagem"
        verbose_name_plural = "Anexos de Passagem Aérea Viagem"

    def __str__(self):
        dt_criado = self.created_at.strftime("%d/%m/%Y %H:%M")

        try:
            criado_por = str(self.created_by.servidor.pessoa_fisica.social_name)
        except:
            criado_por = str(self.created_by.username)

        return f"Anexo de passagem criado em: {dt_criado} - criado por: {criado_por}"


class VeiculoViagem(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre passagem aéria de um Destino
    """

    placa = models.CharField("Placa", max_length=100)
    kilometragem = models.CharField(
        "Kilometragem", max_length=100, null=True, blank=True
    )
    marca = models.CharField("Marca", max_length=100, null=True, blank=True)
    modelo = models.CharField("Modelo", max_length=100, null=True, blank=True)
    renavam = models.CharField("Renavam", max_length=100, null=True, blank=True)
    capacidade_passageiros = models.IntegerField(
        "Capacidade de Passageiros", null=True, blank=True
    )

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"

    def __str__(self):
        return f"{self.destino} - placa do veículo:{self.placa}"


class VeiculoPassageiro(AuditTimestampModel):
    """
    Modelo responsável por relacionar veículos e passageiros, e definir quem é o motorista
    """

    veiculo = models.ForeignKey(
        VeiculoViagem, on_delete=models.PROTECT, related_name="veiculo"
    )
    passageiro = models.ForeignKey(
        Destino, on_delete=models.PROTECT, related_name="veiculo_passageiros"
    )
    motorista = models.BooleanField("Motorista", default=False)

    class Meta:
        verbose_name = "Veículo Passageiro"
        verbose_name_plural = "Veículo Passageiros"

    def __str__(self):
        return f"Veículo: {self.veiculo.placa} - Passageiro: {self.passageiro} - Motorista: {'Sim' if self.motorista else 'Não'}"

    @property
    def motorista_veiculo(self):
        motorista = VeiculoPassageiro.objects.filter(
            veiculo=self.veiculo, motorista=True
        ).first()
        return motorista.passageiro.beneficiario


class CargoDiarias(AuditTimestampModel):
    nome = models.CharField("Nome", max_length=150)

    def save(self, *args, **kargs):
        self.validate()
        super(CargoDiarias, self).save(*args, **kargs)

    def validate(self):
        self.validar_nome_duplicado()

    def validar_nome_duplicado(self):
        q = CargoDiarias.objects.filter(nome=self.nome)
        if self.pk:
            q = q.exclude(pk=self.pk)
        if q.exists():
            raise Exception("Já existe um Cargo cadastrado com o Nome informado!")


class FluxoViagem(AuditTimestampModel):
    """
    Modelo responsável por armazenar as configurações dos fluxos de Viagem
    """

    ordem = models.SmallIntegerField("Ordem", db_index=True, null=True)
    situacao = models.IntegerField(
        "Situação",
        choices=Choice.get_choices_for("diarias", "SITUACAO_SOLICITACAO_VIAGEM"),
        null=True,
    )
    etapa = models.IntegerField(
        "Etapa",
        choices=Choice.get_choices_for("diarias", "ETAPA_SOLICITACAO_VIAGEM"),
        null=True,
    )
    notificar_solicitante = models.BooleanField("Notificar Solicitante?", default=False)
    notificar_emails = ArrayField(
        models.CharField(max_length=250), null=True, blank=True
    )
    calcular = models.BooleanField("Calcular", default=False)
    deferir_todos_beneficiarios = models.BooleanField(
        "Deferir Todos os Beneficiários", default=False
    )
    link_informacao = models.CharField(max_length=350, null=True, blank=True)

    class Meta:
        verbose_name = "Fluxo de viagem"
        verbose_name_plural = "Fluxos de viagem"

    def __str__(self):
        return (
            f"{self.ordem} - {self.get_situacao_display()} - {self.get_etapa_display()}"
        )

    def save(self, *args, **kwargs):
        self.validar_ordem_duplicada()
        super(FluxoViagem, self).save(*args, **kwargs)

    def validar_ordem_duplicada(self):
        if self.ordem is not None:
            fluxos_com_mesma_ordem = FluxoViagem.objects.filter(ordem=self.ordem)
            if self.pk:
                fluxos_com_mesma_ordem = fluxos_com_mesma_ordem.exclude(pk=self.pk)
            if fluxos_com_mesma_ordem.exists():
                raise Exception(
                    "Já existe um Fluxo de Viagem cadastrado com a Ordem informada!"
                )


class CondicionalFluxoViagem(AuditTimestampModel):
    """
    Modelo responsável por armazenar as condicionais de configurações dos fluxos de Viagem

    O campo condicionais é um CharField que deve ter os valores de IDs do parâmetro de sistema CONDICIONAIS_FLUXO_DIARIAS.

    As regras para definição dos operadores lógicos são:
    - quando itens separados por 'vírgula' seja o operador 'OU'.
    - quando itens separados por 'ponto e vírgula' seja o operador 'E'.
    - quando houver mais de um registro para definição das condicionais, a partir do segundo registro é obrigatório
    a deinição do campo 'tipo_operador'.

    Exs.:

    ## 1 - Fluxo A tem que ter a regra de condicionais sendo: 1
    Então teremos uma linha de registros para o Fluxo A.

    pk: 1, fluxo: 'Fluxo A', tipo_operador: 'None', condicionais: '1'

    ## 2 - Fluxo B tem que ter a regra de condicionais sendo: 1 E 2
    Então teremos uma linha de registros para o Fluxo B, separando os IDs utilizando 'ponto e vírgula'.

    pk: 2, fluxo: 'Fluxo B', tipo_operador: 'None', condicionais: '1;2'

    ## 3 - Fluxo C tem que ter a regra de condicionais sendo: 2 OU 3
    Então teremos uma linha de registros para o Fluxo C, separando os IDs utilizando 'vírgula'.

    pk: 3, fluxo: 'Fluxo C', tipo_operador: 'None', condicionais: '2,3'

    ## 4 - Fluxo D tem que ter a regra de condicionais sendo: 1 E (2 OU 3)
    Então teremos duas linhas de registros para o Fluxo B:
    - a primeira com com o ID 1
    - e a segunda com o IDs 2 e 3 separados por 'vírgula'.

    pk: 5, fluxo: 'Fluxo D', tipo_operador: 'None', condicionais: '1'
    pk: 6, fluxo: 'Fluxo D', tipo_operador: 'E', condicionais: '2,3'

    ## 5 - Fluxo D tem que ter a regra de condicionais sendo: (1 E 2) OU (3 E 4)
    Então teremos duas linhas de registros para o Fluxo B:
    - a primeira com os ID 1 e 2 separados por 'ponto e vírgula'
    - e a segunda com o tipo de operador com o valor 'OU', e com o IDs 3 e 4 separados por 'ponto e vírgula'.

    pk: 5, fluxo: 'Fluxo D', tipo_operador: 'None', condicionais: '1;2'
    pk: 6, fluxo: 'Fluxo D', tipo_operador: 'OU', condicionais: '3;4'
    """

    OPERADORES = (
        ("E", "E"),
        ("OU", "OU"),
    )

    fluxo = models.ForeignKey(
        FluxoViagem, on_delete=models.PROTECT, related_name="condicionais"
    )
    tipo_operador = models.CharField(
        "Tipo de Operador",
        max_length=5,
        choices=OPERADORES,
        null=True,
        blank=True,
        db_index=True,
    )
    condicionais = models.CharField(
        "Condicionais", max_length=250, null=True, blank=True, db_index=True
    )

    class Meta:
        verbose_name = "Condicional do Fluxo de viagem"
        verbose_name_plural = "Condicionais do Fluxo de viagem"

    def __str__(self):
        operador = f"{self.tipo_operador} " if self.tipo_operador is not None else ""
        return f"{self.fluxo} - {operador}{self.condicionais}"


class ValorDiarias(AuditTimestampModel):
    valor_estado = models.DecimalField(
        verbose_name="Valor estado",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_fora_estado = models.DecimalField(
        verbose_name="Valor fora estado",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_exterior = models.DecimalField(
        verbose_name="Valor exterior",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    dt_inicio_vigencia = models.DateField(
        "Data início da vigência", null=True, blank=True
    )
    dt_fim_vigencia = models.DateField("Data início da vigência", null=True, blank=True)

    def __str__(self):
        dt_fim_vigencia = "-" if self.dt_fim_vigencia is None else self.dt_fim_vigencia
        return f"Data vigência início: {self.dt_inicio_vigencia} - Data vigência fim: {dt_fim_vigencia}"

    def save(self, *args, **kargs):
        self.validar()
        super(ValorDiarias, self).save(*args, **kargs)

    def validar(self):
        self.validar_dt_inicio_vigencia()
        self.validar_inicio_maior_fim()
        self.validar_datas()

    def validar_dt_inicio_vigencia(self):
        if not self.dt_inicio_vigencia:
            raise Exception("Favor informar o Início da vigência")

    def validar_inicio_maior_fim(self):
        if self.dt_fim_vigencia and self.dt_fim_vigencia < self.dt_inicio_vigencia:
            raise Exception("Data de início deve ser menor que data fim vigência")

    def validar_datas(self):
        if self.dt_fim_vigencia:
            query = ValorDiarias.objects.filter(
                Q(
                    dt_inicio_vigencia__lte=self.dt_inicio_vigencia,
                    dt_fim_vigencia__isnull=True,
                )
                | Q(
                    dt_inicio_vigencia__lte=self.dt_inicio_vigencia,
                    dt_fim_vigencia__gte=self.dt_inicio_vigencia,
                )
                | Q(
                    dt_inicio_vigencia__gte=self.dt_inicio_vigencia,
                    dt_inicio_vigencia__lte=self.dt_fim_vigencia,
                )
                | Q(
                    dt_fim_vigencia__gte=self.dt_inicio_vigencia,
                    dt_fim_vigencia__lte=self.dt_fim_vigencia,
                )
            )
        else:
            query = ValorDiarias.objects.filter(
                Q(
                    dt_inicio_vigencia__lte=self.dt_inicio_vigencia,
                    dt_fim_vigencia__isnull=True,
                )
                | Q(
                    dt_inicio_vigencia__lte=self.dt_inicio_vigencia,
                    dt_fim_vigencia__gte=self.dt_inicio_vigencia,
                )
                | Q(dt_inicio_vigencia__gte=self.dt_inicio_vigencia)
            )

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise Exception(
                "Já existe um Valor cadastrado para a data/período informado!"
            )

    def buscar_valor_vigente(self, data_referencia=None):
        data_referencia = (
            datetime.today().date() if data_referencia is None else data_referencia
        )

        q_valor = ValorDiarias.objects.filter(
            Q(
                dt_inicio_vigencia__lte=data_referencia,
                dt_fim_vigencia__gte=data_referencia,
            )
            | Q(dt_inicio_vigencia__lte=data_referencia, dt_fim_vigencia__isnull=True)
        )

        return q_valor.first() if q_valor.exists() else None


class GrupoAprovador(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre grupos de aprovadores

    O campo grupos é um ArrayField que deve ter os valores de IDs do parâmetro de sistema ETAPA_SOLICITACAO_VIAGEM.
    """

    nome = models.CharField("Nome do grupo", max_length=150)
    grupos = ArrayField(models.SmallIntegerField(), null=True, blank=True)
    servidores = models.ManyToManyField(
        Servidor,
        verbose_name="Servidores",
        related_name="grupos_aprovadores_viagens",
        blank=True,
    )

    class Meta:
        verbose_name = "Grupo de Aprovadores de Viagens"
        verbose_name_plural = "Grupos de Aprovadores de Viagens"

    def __str__(self):
        return f"{self.nome}"

    def delete(self, *args, **kwargs):
        if self.servidores.exists():
            raise Exception(
                "Não é possível excluir este grupo pois existem servidores associados a ele."
            )
        super().delete(*args, **kwargs)


class HistoricoFluxoViagemBeneficiario(AuditTimestampModel):
    """
    Modelo para armazenar informações sobre o Histórico de Fluxos para uma Viagem e seus Beneficiários
    """

    TIPO_HISTORICO = (
        ("viagem", "Viagem"),
        ("beneficiario", "Beneficiário"),
    )

    DECISAO_CHOICES = (
        ("deferido", "Deferido"),
        ("indeferido", "Indeferido"),
        ("encaminhado", "Encaminhado"),
        ("ciente", "Ciente do cancelamento"),
        ("valor_alterado", "Valor deferido alterado"),
        ("importacao", "Importação"),
        ("recebido", "Recebido"),
        ("liberado", "Liberado"),
    )

    FEEDBACK_CHOICES = (
        ("positivo", "Negativo"),
        ("negativo", "Positivo"),
        ("alerta", "Alerta"),
    )

    viagem = models.ForeignKey(
        Viagem, on_delete=models.PROTECT, related_name="historico_fluxos"
    )
    beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.PROTECT,
        related_name="historico_fluxos",
        null=True,
        blank=True,
    )
    fluxo = models.ForeignKey(
        FluxoViagem, on_delete=models.PROTECT, related_name="historico_fluxos"
    )
    tipo = models.CharField(
        "Tipo de histórico",
        max_length=50,
        choices=TIPO_HISTORICO,
        default="VIAGEM",
        db_index=True,
    )
    obs = models.TextField("Observações - Avaliação", null=True, blank=True)
    decisao = models.CharField(
        "Decisão", max_length=30, choices=DECISAO_CHOICES, null=True, blank=True
    )
    feedback = models.CharField(
        "Feedback", max_length=15, choices=FEEDBACK_CHOICES, null=True, blank=True
    )

    class Meta:
        verbose_name = "Histórico de Fluxos para uma Viagem e seus Beneficiários"
        verbose_name_plural = "Histórico de Fluxos para uma Viagem e seus Beneficiários"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fluxo} - Acão por: {self.acao_por}"

    @property
    def acao_por(self):
        try:
            return str(self.created_by.servidor.pessoa_fisica.social_name)
        except:
            return str(self.created_by.username)

    @property
    def tem_anexo(self):
        """Retorna True se houver anexos associados a este histórico, caso contrário False."""
        return self.anexos.exists()

    @property
    def tem_informacao(self):
        """Retorna True se houver observações, ou se os campos de número de empenho, número de nota de liquidação,
        número de ordem bancária ou qtd_total_diarias_deferido estiverem preenchidos, considerando a situação e etapa específicas.
        """

        if self.obs:
            return True

        elif (
            self.fluxo.situacao == 1
            and self.fluxo.etapa == 3
            and self.decisao == "deferido"
        ):  # Aguardando empenho - DEPLAN- Executor
            if self.beneficiario and self.beneficiario.numero_empenho:
                return True

        elif (
            self.fluxo.situacao == 5
            and self.fluxo.etapa == 11
            and self.decisao == "deferido"
        ):  # Aguardando Nota Liquidação - DEFIN- Gerencia Financeira
            if self.beneficiario and self.beneficiario.numero_nota_liquidacao:
                return True

        elif (
            self.fluxo.situacao == 6
            and self.fluxo.etapa == 11
            and self.decisao == "deferido"
        ):  # Aguardando Ordem Bancária - DEFIN- Gerencia Financeira
            if self.beneficiario and self.beneficiario.numero_ordem_bancaria:
                return True

        elif (
            self.fluxo.id == 27
            and self.beneficiario.gedoc_numero
            and self.decisao in ["deferido", "indeferido"]
        ):  # Fluxo: "DEFIN - Excedente"
            return True

        elif (
            self.fluxo.id in [6, 24, 27, 28, 30, 31, 33]
            and self.decisao  # Fluxos: "Assessoria da DG - Aguardando análise" ou "Aguardando análise - Assessoria do SUB JUR" ou "Aguardando análise - Assessoria do PGJ" ou "DEFIN - Excedente"
            in ["deferido", "encaminhado"]
            and self.beneficiario
            and self.beneficiario.calculos_diarias_consolidados
            and self.beneficiario.calculos_diarias_consolidados.qtd_total_diarias_deferido
        ):
            return True

        elif self.feedback:
            return True


class HistoricoAnexo(AuditTimestampModel):
    """
    Modelo responsável por armazenar os anexos de Prestação de Contas
    """

    historico = models.ForeignKey(
        HistoricoFluxoViagemBeneficiario,
        on_delete=models.PROTECT,
        related_name="anexos",
    )
    arquivo = models.ForeignKey(
        Arquivo,
        on_delete=models.PROTECT,
        related_name="historico_fluxo_viagem_benef_arquivos",
    )

    class Meta:
        verbose_name = "Anexo de Histórico do Fluxo de Viagem/Beneficiário"
        verbose_name_plural = "Anexos de Histórico do Fluxo de Viagem/Beneficiário"

    def __str__(self):
        dt_criado = self.created_at.strftime("%d/%m/%Y %H:%M")

        try:
            criado_por = str(self.created_by.servidor.pessoa_fisica.social_name)
        except:
            criado_por = str(self.created_by.username)

        return f"Anexo de histórico criado em: {dt_criado} - criado por: {criado_por}"


class LimiteDiarias(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre limite de diárias de servidores e membros

    O campo motivo_viagem é um ArrayField que deve ter os valores de IDs do parâmetro de sistema MOTIVO_VIAGEM.
    """

    TIPO_CHOICES = (
        ("servidor", "Servidor"),
        ("membro", "Membro"),
    )
    REFERENCIA_CHOICES = (
        ("anual", "Anual"),
        ("mensal", "Mensal"),
    )

    tipo = models.CharField("Tipo posse", max_length=10, choices=TIPO_CHOICES)
    referencia = models.CharField(
        "Referência de período", max_length=10, choices=REFERENCIA_CHOICES
    )
    motivos_viagem = ArrayField(models.SmallIntegerField(), null=True, blank=True)
    limite = models.IntegerField("Limite de dias", null=True, blank=True, db_index=True)
    dt_inicio_vigencia = models.DateField(
        "Data início da vigência", null=True, blank=True
    )

    class Meta:
        verbose_name = "Limite de Diárias para Servidores e Membros"
        verbose_name_plural = "Limites de Diárias para Servidores e Membros"

    def __str__(self):
        data_inicio = self.dt_inicio_vigencia.strftime("%d/%m/%Y")
        return f"{self.tipo} - {self.referencia} - Motivos: {self.motivos_viagem} - Início: {data_inicio}"

    def delete(self, *args, **kwargs):
        if LimiteDiarias.objects.filter(tipo=self.tipo).count() <= 1:
            raise ValueError(
                f"Não foi possível excluir porque deve existir no mínimo um limite para {self.tipo}. "
                "Cadastre novo limite antes de efetuar a exclusão deste."
            )
        super().delete(*args, **kwargs)


class CnabPagamento(AuditTimestampModel):
    """
    Modelo responsável por armazenar os arquivos CNAB de pagamentos
    """

    cnab = models.ForeignKey(Arquivo, on_delete=models.PROTECT, related_name="cnabs")

    class Meta:
        verbose_name = "CNAB Pagamento"
        verbose_name_plural = "CNABs Pagamentos"

    def __str__(self):
        dt_criado = self.created_at.strftime("%d/%m/%Y %H:%M")

        try:
            criado_por = str(self.created_by.servidor.pessoa_fisica.social_name)
        except:
            criado_por = str(self.created_by.username)

        return f"CNAB criado em: {dt_criado} - criado por: {criado_por}"


class Pagamento(Assinatura):
    """
    Modelo responsável por armazenar informações sobre os pagamentos de diárias
    """

    STATUS_PGTO = (
        ("aguardando", "Aguardando - ordem pendente"),
        ("cnab_criado", "Cnab Criado - Aguardando pagamento"),
        ("pago", "Pago"),
    )

    beneficiario = models.ForeignKey(
        Beneficiario, related_name="pagamentos", on_delete=models.PROTECT
    )
    data_pgto = models.DateField("Data de Pagamento", null=True, blank=True)
    status = models.CharField(
        "Status do Pagamento", max_length=15, choices=STATUS_PGTO, default="aguardando"
    )
    cnab = models.ForeignKey(
        CnabPagamento,
        related_name="pagamentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        dt_pgto = f" - Data Pgto: {self.data_pgto}" if self.data_pgto else ""
        pgto_para = f"{self.beneficiario.servidor.matricula}:{self.beneficiario.servidor.pessoa_fisica.social_name}"
        return f"Pagamento para: {pgto_para} - Status: {self.get_status_display()}{dt_pgto}"

    @property
    def info_conta_bancaria(self):
        if self.beneficiario.viagem.importada:
            return str(self.beneficiario.dados_bancarios_importacao)

        num_banco = self.beneficiario.conta_bancaria_pgto.banco.numero

        if (
            self.beneficiario.conta_bancaria_pgto.agencia_numero
            and self.beneficiario.conta_bancaria_pgto.conta_numero
        ):
            agencia_dv = self.beneficiario.conta_bancaria_pgto.agencia_dv

            if agencia_dv and agencia_dv != "" and agencia_dv != "None":
                ag = f"{self.beneficiario.conta_bancaria_pgto.agencia_numero}{self.beneficiario.conta_bancaria_pgto.agencia_dv}"
            else:
                ag = f"{self.beneficiario.conta_bancaria_pgto.agencia_numero}"

            conta_dv = self.beneficiario.conta_bancaria_pgto.conta_dv
            if conta_dv and conta_dv != "" and conta_dv != "None":
                num_conta = f"{self.beneficiario.conta_bancaria_pgto.conta_numero}{self.beneficiario.conta_bancaria_pgto.conta_dv}"
            else:
                num_conta = f"{self.beneficiario.conta_bancaria_pgto.conta_numero}"

        else:
            ag = self.beneficiario.conta_bancaria_pgto.agencia
            num_conta = self.beneficiario.conta_bancaria_pgto.conta_corrente_completa

        return f"{num_banco} - {ag} - {num_conta}"

    @property
    def servidor(self):
        return f"{self.beneficiario.servidor.matricula} - {self.beneficiario.servidor.pessoa_fisica.social_name}"

    @property
    def valor_liquido_viagem(self):
        return self.beneficiario.calculos_diarias_consolidados.valor_total_liquido

    @property
    def valor_liquido_deferido_viagem(self):
        return (
            self.beneficiario.calculos_diarias_consolidados.valor_total_liquido_deferido
        )

    @property
    def criado_por(self):
        return self.created_by.username if self.created_by else None

    @property
    def modificado_por(self):
        return self.modified_by.username if self.modified_by else None


class PrestacaoContas(Assinatura):
    """
    Modelo responsável por armazenar as informações de Prestação de Contas
    """

    STATUS_PREST_CONTAS = (
        ("aguardando", "Aguardando"),
        ("entregue", "Entregue"),
        ("em_analise", "Em Análise"),
        ("atrasado", "Atrasado"),
        ("com_pendencias", "Com Pendencias"),
        ("aprovado", "Aprovado"),
    )

    beneficiario = models.ForeignKey(
        Beneficiario, related_name="prestacoes_contas", on_delete=models.PROTECT
    )
    avaliador = models.ForeignKey(
        Servidor,
        related_name="avaliacoes_prestacoes_contas_diarias",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    viagem_realizada = models.BooleanField("Viagem Realizada?", default=True)
    viagem_total = models.BooleanField(
        "Viagem foi finalizada na totalidade?", default=True
    )
    data_limite = models.DateField(
        "Data limite de entrega da prestação de contas", null=True, blank=True
    )
    data_entrega = models.DateField(
        "Data de entrega da prestação de contas", null=True, blank=True
    )
    status = models.CharField(
        "Status da Prestação de Contas",
        max_length=15,
        choices=STATUS_PREST_CONTAS,
        default="aguardando",
    )
    obs_servicos_executados = models.TextField(
        "Serviços executados", null=True, blank=True
    )
    obs_resultado = models.TextField("Resultados alcançados", null=True, blank=True)
    obs = models.TextField("Obs. do beneficiário", null=True, blank=True)
    obs_anlaise = models.TextField("Obs. da análise", null=True, blank=True)
    data_validacao = models.DateField(
        "Data da Validação da prestação de contas ", null=True, blank=True
    )
    valor_devolvido = models.DecimalField(
        verbose_name="Valor devolvido",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    doc_encerramento = models.ForeignKey(
        Arquivo,
        on_delete=models.PROTECT,
        related_name="prestacao_contas_doc_encerramento",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Prestação de Contas"
        verbose_name_plural = "Prestações de Contas"

    def __str__(self):
        prestacao_de = f"{self.beneficiario.servidor.matricula}:{self.beneficiario.servidor.pessoa_fisica.social_name}"
        # Verifica se data_limite não é None
        if self.data_limite:
            dt_limite = self.data_limite.strftime("%d/%m/%Y %H:%M")
            data_limite_str = f" - Data limite de entrega: {dt_limite}"
        else:
            data_limite_str = ""  # String vazia se data_limite for None

        return f"Prestação de contas de: {prestacao_de}{data_limite_str} - Status: {self.get_status_display()}"

    @property
    def beneficiario_lotacao(self):
        from rh.models import ServidorLotacao

        lotacoes = ServidorLotacao.objects.filter(
            servidor=self.beneficiario.servidor, designacao=False, ativo=True
        )
        if lotacoes.exists():
            return lotacoes.last().lotacao.nome
        return ""

    @property
    def beneficiario_categoria_funcional(self):
        return self.beneficiario.servidor.get_type_by_possession_display()


class PrestacaoContasAnexo(AuditTimestampModel):
    """
    Modelo responsável por armazenar os anexos de Prestação de Contas
    """

    prestacao = models.ForeignKey(
        PrestacaoContas, on_delete=models.PROTECT, related_name="anexos"
    )
    arquivo = models.ForeignKey(
        Arquivo, on_delete=models.PROTECT, related_name="prestacao_contas_arquivos"
    )

    class Meta:
        verbose_name = "Anexo de Prestação de Contas"
        verbose_name_plural = "Anexos de Prestação de Contas"

    def __str__(self):
        dt_criado = self.created_at.strftime("%d/%m/%Y %H:%M")

        try:
            criado_por = str(self.created_by.servidor.pessoa_fisica.social_name)
        except:
            criado_por = str(self.created_by.username)

        return f"Anexo criado em: {dt_criado} - criado por: {criado_por}"


class DadosBancariosImportacao(AuditTimestampModel):
    beneficiario = models.OneToOneField(
        Beneficiario,
        related_name="dados_bancarios_importacao",
        on_delete=models.PROTECT,
    )
    banco = models.CharField(
        max_length=15, verbose_name="Banco", default="", blank=True
    )
    agencia = models.CharField(
        max_length=15, verbose_name="Agência", default="", blank=True
    )
    conta = models.CharField(
        max_length=15, verbose_name="Conta", default="", blank=True
    )

    def __str__(self):
        return f'{self.banco or ""} - {self.agencia or ""} - {self.conta or ""}'

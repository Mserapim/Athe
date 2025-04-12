from django.db import models


class GeraHistoricoeventosoManager(models.Manager):
    def get_queryset(self):
        return super(GeraHistoricoeventosoManager, self).get_queryset().using("mdc4web")


class GeraHistoricoeventos(models.Model):
    data = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    unidade = models.CharField(max_length=2, blank=True, null=True)
    concentrador = models.CharField(max_length=2, blank=True, null=True)
    grupo = models.CharField(max_length=2, blank=True, null=True)
    evento = models.TextField(blank=True, null=True)  # This field type is a guess.
    nome = models.TextField(blank=True, null=True)  # This field type is a guess.
    cracha = models.TextField(blank=True, null=True)  # This field type is a guess.
    ocorrencia = models.CharField(max_length=3, blank=True, null=True)
    id_empresa = models.BigIntegerField(blank=True, null=True)
    empresa = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_gera_niveis = models.BigIntegerField(blank=True, null=True)
    nivel = models.TextField(blank=True, null=True)  # This field type is a guess.
    descricaounidades = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    visivel = models.IntegerField(blank=True, null=True)
    placa = models.CharField(max_length=7, blank=True, null=True)
    hora = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_usuarios = models.BigIntegerField(blank=True, null=True)
    matricula = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_centrosderesponsabilidade = models.BigIntegerField(blank=True, null=True)
    centroderesponsabilidade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    id_classificacao = models.BigIntegerField(blank=True, null=True)
    classificacao = models.CharField(max_length=3, blank=True, null=True)
    porta = models.CharField(max_length=2, blank=True, null=True)
    atualizador = models.TextField(blank=True, null=True)  # This field type is a guess.
    d_h_atualizacao = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    id_historico_evento = models.BigIntegerField(primary_key=True)
    marcacaoonline = models.BooleanField(blank=True, null=True)
    liberacaocomfluxo = models.BooleanField(blank=True, null=True)
    codref = models.TextField(blank=True, null=True)  # This field type is a guess.
    tp_refe = models.BigIntegerField(blank=True, null=True)
    cod_local = models.TextField(blank=True, null=True)  # This field type is a guess.
    restaurante_idrestaurante = models.IntegerField(blank=True, null=True)
    id_refeicoes = models.BigIntegerField(blank=True, null=True)
    idcatrefe = models.IntegerField(blank=True, null=True)
    tipoinfosap = models.IntegerField(blank=True, null=True)
    qtd_servicos = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=1, blank=True, null=True)
    desctipovis = models.TextField(blank=True, null=True)  # This field type is a guess.
    empresadesc = models.TextField(blank=True, null=True)  # This field type is a guess.
    sodata = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_hist = models.BooleanField(blank=True, null=True)
    id_unidadesremotas = models.BigIntegerField(blank=True, null=True)
    documento = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_autorizacao = models.BigIntegerField(blank=True, null=True)
    valorcomplref = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    id_site = models.IntegerField(blank=True, null=True)
    subtipo = models.TextField(blank=True, null=True)  # This field type is a guess.
    ehbrigadista = models.BooleanField(blank=True, null=True)
    id_alarme = models.IntegerField(blank=True, null=True)
    reconhecidopor = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    ocr_timestamp = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    ocr_pista = models.TextField(blank=True, null=True)  # This field type is a guess.
    acao_tomada = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_visitante = models.BigIntegerField(blank=True, null=True)
    empresavisitante = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    nomevisitado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    datacadastramento = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    observacao2 = models.TextField(blank=True, null=True)  # This field type is a guess.
    sexo = models.TextField(blank=True, null=True)  # This field type is a guess.
    idade = models.IntegerField(blank=True, null=True)
    permanenciamin = models.IntegerField(blank=True, null=True)
    dataacesso = models.TextField(blank=True, null=True)  # This field type is a guess.
    mp_ignorar = models.CharField(max_length=1, blank=True, null=True)
    dtenviogenesys = models.DateTimeField(blank=True, null=True)
    motivo = models.TextField(blank=True, null=True)  # This field type is a guess.
    pista = models.TextField(blank=True, null=True)  # This field type is a guess.
    sentido = models.TextField(blank=True, null=True)  # This field type is a guess.
    tipo_veiculo = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    score = models.TextField(blank=True, null=True)  # This field type is a guess.
    dt_envio_hcor = models.DateTimeField(blank=True, null=True)
    id_lote_refe = models.BigIntegerField(blank=True, null=True)

    objects = GeraHistoricoeventosoManager()

    class Meta:
        managed = False
        db_table = "gera_historicoeventos"


class MpFpjustificativaManager(models.Manager):
    def get_queryset(self):
        return super(MpFpjustificativaManager, self).get_queryset().using("mdc4web")


class MpFpjustificativa(models.Model):
    codigo = models.FloatField(primary_key=True)
    data = models.DateTimeField()  # This field type is a guess.
    justificativa = models.TextField()  # This field type is a guess.
    matricula = models.TextField()  # This field type is a guess.
    marcacao1 = models.CharField(max_length=1, blank=True, null=True)
    marcacao2 = models.CharField(max_length=1, blank=True, null=True)
    marcacao3 = models.CharField(max_length=1, blank=True, null=True)
    marcacao4 = models.CharField(max_length=1, blank=True, null=True)

    objects = MpFpjustificativaManager()

    class Meta:
        managed = False
        db_table = "mp_fpjustificativa"

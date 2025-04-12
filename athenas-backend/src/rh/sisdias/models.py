# Create your models here.
# snowpenguin.django.recaptcha2 => There is no default AppConfig for snowpenguin.django.recaptcha2
# rh.sisdias => There is no default AppConfig for rh.sisdias
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DrSdia01NomeServIxI(models.Model):
    token_text = models.TextField()  # This field type is a guess.
    token_type = models.IntegerField()
    token_first = models.IntegerField()
    token_last = models.IntegerField()
    token_count = models.IntegerField()
    token_info = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dr$sdia01_nome_serv_ix$i"


class DrSdia01NomeServIxK(models.Model):
    docid = models.BigIntegerField(blank=True, null=True)
    textkey = models.TextField(primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "dr$sdia01_nome_serv_ix$k"


class DrSdia01NomeServIxN(models.Model):
    nlt_docid = models.BigIntegerField(primary_key=True)
    nlt_mark = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "dr$sdia01_nome_serv_ix$n"


class DrSdia01NomeServIxR(models.Model):
    row_no = models.IntegerField(primary_key=True)
    data = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dr$sdia01_nome_serv_ix$r"


class DrSdia08NomeIxI(models.Model):
    token_text = models.TextField()  # This field type is a guess.
    token_type = models.IntegerField()
    token_first = models.IntegerField()
    token_last = models.IntegerField()
    token_count = models.IntegerField()
    token_info = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dr$sdia08_nome_ix$i"


class DrSdia08NomeIxK(models.Model):
    docid = models.BigIntegerField(blank=True, null=True)
    textkey = models.TextField(primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "dr$sdia08_nome_ix$k"


class DrSdia08NomeIxN(models.Model):
    nlt_docid = models.BigIntegerField(primary_key=True)
    nlt_mark = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "dr$sdia08_nome_ix$n"


class DrSdia08NomeIxR(models.Model):
    row_no = models.IntegerField(primary_key=True)
    data = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dr$sdia08_nome_ix$r"


class Sdia00Configuracoes(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nome = models.TextField()  # This field type is a guess.
    valor = models.TextField()  # This field type is a guess.
    tipo = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "sdia00_configuracoes"


class Sdia01OrdemServico(models.Model):
    numero = models.IntegerField(primary_key=True)
    data = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    local = models.TextField()  # This field type is a guess.
    chapa_servidor = models.TextField()  # This field type is a guess.
    nome_servidor = models.TextField()  # This field type is a guess.
    cargo_servidor = models.TextField()  # This field type is a guess.
    carteira_identidade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    finalidade = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_designante = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_estado = models.FloatField(blank=True, null=True)
    valor_unit_estado = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_pais = models.FloatField(blank=True, null=True)
    valor_unit_pais = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_exterior = models.FloatField(blank=True, null=True)
    valor_unit_exterior = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_ordenador = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_importancia = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_setor_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_empenho = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_empenho = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    num_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_cheque = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_financeiro = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    situacao = models.ForeignKey(
        "Sdia06SituacaoOs",
        models.DO_NOTHING,
        db_column="situacao",
        blank=True,
        null=True,
    )
    sdia07_cdgmotivo_cancel = models.ForeignKey(
        "Sdia07MotivoCancelamento",
        models.DO_NOTHING,
        db_column="sdia07_cdgmotivo_cancel",
        blank=True,
        null=True,
    )
    sdia02_cdglocalidade_origem = models.ForeignKey(
        "Sdia02Localidade",
        models.DO_NOTHING,
        db_column="sdia02_cdglocalidade_origem",
        blank=True,
        null=True,
    )
    valor_total_estado_old = models.FloatField(blank=True, null=True)
    valor_total_pais_old = models.FloatField(blank=True, null=True)
    valor_total_exterior_old = models.FloatField(blank=True, null=True)
    valor_dolar = models.FloatField(blank=True, null=True)
    sdia12_cdgtipo_finalidade = models.ForeignKey(
        "Sdia12TipoFinalidade",
        models.DO_NOTHING,
        db_column="sdia12_cdgtipo_finalidade",
        blank=True,
        null=True,
    )
    sacs01_usuario_cadastro = models.FloatField(blank=True, null=True)
    sdia08_cdgpessoa_externa = models.ForeignKey(
        "Sdia08PessoaExterna",
        models.DO_NOTHING,
        db_column="sdia08_cdgpessoa_externa",
        blank=True,
        null=True,
    )
    sdia13_cdgconvenio = models.ForeignKey(
        "Sdia13Convenio",
        models.DO_NOTHING,
        db_column="sdia13_cdgconvenio",
        blank=True,
        null=True,
    )
    data_setor_financeiro = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    sacs01_usuario_empenho = models.FloatField(blank=True, null=True)
    sacs01_usuario_cancelamento = models.FloatField(blank=True, null=True)
    data_cancelamento = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    banco = models.FloatField(blank=True, null=True)
    agencia = models.TextField(blank=True, null=True)  # This field type is a guess.
    conta = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_protocolo_banco = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    relatorio_entregue = models.IntegerField(blank=True, null=True)
    meio = models.FloatField(blank=True, null=True)
    km = models.FloatField(blank=True, null=True)
    num_bilhete = models.TextField(blank=True, null=True)  # This field type is a guess.
    empresa_transporte = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    placa_veiculo_mp = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    descricao_resultado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    observacoes = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_relatorio = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    protocolo = models.TextField(blank=True, null=True)  # This field type is a guess.
    meiadiaria = models.BooleanField(blank=True, null=True)
    tipo = models.FloatField(blank=True, null=True)
    relatorioonline = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    emissaobilhete = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    viagemefetivada = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_recebido = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    informacoes_adicionais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_pass = models.FloatField(blank=True, null=True)
    autoridade_sol = models.FloatField(blank=True, null=True)
    autoridade_con = models.FloatField(blank=True, null=True)
    pass_custeada = models.FloatField(blank=True, null=True)
    pass_custeada_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    locomocao_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    auxilios_devolvidos = models.FloatField(blank=True, null=True)
    valor_devolucao = models.FloatField(blank=True, null=True)
    tipo_origem = models.FloatField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)  # This field type is a guess.
    transportes_devolvidos = models.FloatField(blank=True, null=True)
    valor_transportes = models.FloatField(blank=True, null=True)
    numerounicocnmp = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    totaldescontos = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    totalareceber = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_total_estado = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_total_pais = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_total_exterior = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    email_enviado = models.BooleanField(blank=True, null=True)
    qtd_auxilios = models.IntegerField(blank=True, null=True)
    qtd_transportes = models.IntegerField(blank=True, null=True)
    valor_total_bruto = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_total_liquido = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_uni_auxilios = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_uni_transportes = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    comprovante_arquivo = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    relatorio_viagem_arquivo = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_pagamento = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    empenho = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_valor_devolvido = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_devolvido = models.FloatField(
        blank=True, null=True
    )  # This field type is a guess.
    subsidio = models.FloatField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia01_ordem_servico"


class Sdia01OrdemServico20170322(models.Model):
    numero = models.IntegerField()
    data = models.DateTimeField(blank=True, null=True)  # This field type is a guess.
    local = models.TextField()  # This field type is a guess.
    chapa_servidor = models.TextField()  # This field type is a guess.
    nome_servidor = models.TextField()  # This field type is a guess.
    cargo_servidor = models.TextField()  # This field type is a guess.
    carteira_identidade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    finalidade = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_designante = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_estado = models.FloatField(blank=True, null=True)
    valor_unit_estado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_pais = models.FloatField(blank=True, null=True)
    valor_unit_pais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_exterior = models.FloatField(blank=True, null=True)
    valor_unit_exterior = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_ordenador = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_importancia = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_setor_pessoal = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_empenho = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_empenho = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    num_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_cheque = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_financeiro = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    situacao = models.IntegerField(blank=True, null=True)
    sdia07_cdgmotivo_cancel = models.FloatField(blank=True, null=True)
    sdia02_cdglocalidade_origem = models.IntegerField(blank=True, null=True)
    valor_total_estado = models.FloatField(blank=True, null=True)
    valor_total_pais = models.FloatField(blank=True, null=True)
    valor_total_exterior = models.FloatField(blank=True, null=True)
    valor_dolar = models.FloatField(blank=True, null=True)
    sdia12_cdgtipo_finalidade = models.FloatField(blank=True, null=True)
    sacs01_usuario_cadastro = models.FloatField(blank=True, null=True)
    sdia08_cdgpessoa_externa = models.FloatField(blank=True, null=True)
    sdia13_cdgconvenio = models.FloatField(blank=True, null=True)
    data_setor_financeiro = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    sacs01_usuario_empenho = models.FloatField(blank=True, null=True)
    sacs01_usuario_cancelamento = models.FloatField(blank=True, null=True)
    data_cancelamento = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    banco = models.FloatField(blank=True, null=True)
    agencia = models.TextField(blank=True, null=True)  # This field type is a guess.
    conta = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_protocolo_banco = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    relatorio_entregue = models.BooleanField(blank=True, null=True)
    meio = models.FloatField(blank=True, null=True)
    km = models.FloatField(blank=True, null=True)
    num_bilhete = models.TextField(blank=True, null=True)  # This field type is a guess.
    empresa_transporte = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    placa_veiculo_mp = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    descricao_resultado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    observacoes = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_relatorio = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    protocolo = models.TextField(blank=True, null=True)  # This field type is a guess.
    meiadiaria = models.BooleanField(blank=True, null=True)
    tipo = models.FloatField(blank=True, null=True)
    relatorioonline = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    emissaobilhete = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    viagemefetivada = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_recebido = models.DateTimeField(
        blank=True, null=True
    )  # This field type is a guess.
    informacoes_adicionais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_pass = models.FloatField(blank=True, null=True)
    autoridade_sol = models.FloatField(blank=True, null=True)
    autoridade_con = models.FloatField(blank=True, null=True)
    pass_custeada = models.FloatField(blank=True, null=True)
    pass_custeada_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    locomocao_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    auxilios_devolvidos = models.FloatField(blank=True, null=True)
    valor_devolucao = models.FloatField(blank=True, null=True)
    tipo_origem = models.FloatField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia01_ordem_servico_20170322"


class Sdia02Localidade(models.Model):
    cdglocalidade = models.IntegerField(primary_key=True)
    localidade = models.TextField()  # This field type is a guess.
    uf = models.CharField(max_length=2, blank=True, null=True)
    sdia03_cdgpais = models.ForeignKey(
        "Sdia03Pais", models.DO_NOTHING, db_column="sdia03_cdgpais"
    )
    flg = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia02_localidade"


class Sdia03Pais(models.Model):
    cdgpais = models.IntegerField(primary_key=True)
    nome_pais = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia03_pais"


class Sdia04OsLocalidade(models.Model):
    sdia02_cdglocalidade = models.ForeignKey(
        Sdia02Localidade, models.DO_NOTHING, db_column="sdia02_cdglocalidade"
    )
    sdia01_numero_os = models.ForeignKey(
        Sdia01OrdemServico, models.DO_NOTHING, db_column="sdia01_numero_os"
    )
    ordem = models.IntegerField(blank=True, null=True)
    data = models.TextField()  # This field type is a guess.
    peso = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia04_os_localidade"
        unique_together = (("sdia02_cdglocalidade", "sdia01_numero_os", "data"),)


class Sdia05ValorDiaria(models.Model):
    valor_estado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_pais = models.TextField(blank=True, null=True)  # This field type is a guess.
    valor_exterior = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    pfuncao_cdg_funcao = models.TextField(
        primary_key=True
    )  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia05_valor_diaria"


class Sdia06SituacaoOs(models.Model):
    codigo = models.IntegerField(primary_key=True)
    situacao = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia06_situacao_os"


class Sdia07MotivoCancelamento(models.Model):
    cdgmotivo = models.FloatField(primary_key=True)
    motivo = models.TextField()  # This field type is a guess.
    flg = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia07_motivo_cancelamento"


class Sdia08PessoaExterna(models.Model):
    cdgpessoa = models.FloatField(primary_key=True)
    nome = models.TextField()  # This field type is a guess.
    rg = models.TextField(blank=True, null=True)  # This field type is a guess.
    sdia09_cdgcargopessext = models.ForeignKey(
        "Sdia09CargoPessExt", models.DO_NOTHING, db_column="sdia09_cdgcargopessext"
    )
    numbanco = models.TextField(blank=True, null=True)  # This field type is a guess.
    numagencia = models.TextField(blank=True, null=True)  # This field type is a guess.
    numcontacorrente = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    flg = models.BooleanField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)  # This field type is a guess.
    telefone = models.TextField(blank=True, null=True)  # This field type is a guess.
    telefone2 = models.TextField(blank=True, null=True)  # This field type is a guess.
    cpf = models.TextField(blank=True, null=True)  # This field type is a guess.
    nome_ci_ai = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia08_pessoa_externa"


class Sdia09CargoPessExt(models.Model):
    cdgcargopessext = models.FloatField(primary_key=True)
    nomecargo = models.TextField()  # This field type is a guess.
    valor_intermunicipal = models.TextField()  # This field type is a guess.
    valor_interestadual = models.TextField()  # This field type is a guess.
    valor_internacional = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia09_cargo_pess_ext"


class Sdia10HistOrdemServico(models.Model):
    cdghist_ordem_servico = models.FloatField(primary_key=True)
    sacs01_hist_cdgusuario = models.FloatField()
    datahora_alteracao = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    numero = models.IntegerField()
    data = models.TextField(blank=True, null=True)  # This field type is a guess.
    local = models.TextField()  # This field type is a guess.
    chapa_servidor = models.TextField()  # This field type is a guess.
    nome_servidor = models.TextField()  # This field type is a guess.
    cargo_servidor = models.TextField()  # This field type is a guess.
    carteira_identidade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    remuneracao_mensal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    finalidade = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_designante = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_estado = models.FloatField(blank=True, null=True)
    valor_unit_estado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_pais = models.FloatField(blank=True, null=True)
    valor_unit_pais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_exterior = models.FloatField(blank=True, null=True)
    valor_unit_exterior = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_ordenador = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_importancia = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_setor_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_empenho = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_empenho = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_resp_financeiro = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    situacao = models.IntegerField(blank=True, null=True)
    sdia07_cdgmotivo_cancel = models.FloatField(blank=True, null=True)
    sdia02_cdglocalidade_origem = models.IntegerField(blank=True, null=True)
    valor_total_estado = models.FloatField(blank=True, null=True)
    valor_total_pais = models.FloatField(blank=True, null=True)
    valor_total_exterior = models.FloatField(blank=True, null=True)
    valor_dolar = models.FloatField(blank=True, null=True)
    sdia12_cdgtipo_finalidade = models.FloatField(blank=True, null=True)
    sacs01_usuario_cadastro = models.FloatField(blank=True, null=True)
    sdia08_cdgpessoa_externa = models.FloatField(blank=True, null=True)
    sdia13_cdgconvenio = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia10_hist_ordem_servico"


class Sdia11HistOsLocalidade(models.Model):
    sdia10_cdghist_ordem_servico = models.ForeignKey(
        Sdia10HistOrdemServico,
        models.DO_NOTHING,
        db_column="sdia10_cdghist_ordem_servico",
    )
    sdia02_cdglocalidade = models.IntegerField()
    sdia01_numero_os = models.IntegerField()
    ordem = models.IntegerField(blank=True, null=True)
    data = models.TextField()  # This field type is a guess.
    peso = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia11_hist_os_localidade"


class Sdia12TipoFinalidade(models.Model):
    cdgtipo_finalidade = models.FloatField(primary_key=True)
    tipo_finalidade = models.TextField()  # This field type is a guess.
    flg = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia12_tipo_finalidade"


class Sdia13Convenio(models.Model):
    cdgconvenio = models.FloatField(primary_key=True)
    nome_convenio = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_validade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    orgao = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia13_convenio"


class Sdia14Sistema(models.Model):
    flg_bloq = models.FloatField(blank=True, null=True)
    qtd_bloq = models.FloatField(blank=True, null=True)
    flg = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia14_sistema"


class Sdia15Solicitante(models.Model):
    cdgsolicitante = models.FloatField(primary_key=True)
    descricao = models.TextField(blank=True, null=True)  # This field type is a guess.
    flg = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia15_solicitante"


class Sdia16Concedente(models.Model):
    cdgconcedente = models.FloatField(primary_key=True)
    descricao = models.TextField(blank=True, null=True)  # This field type is a guess.
    flg = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia16_concedente"


class Sdia17Locomocao(models.Model):
    cdgloco = models.FloatField(primary_key=True)
    descricao = models.TextField(blank=True, null=True)  # This field type is a guess.
    flg = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "sdia17_locomocao"


class Sdia18PassagemCusteada(models.Model):
    codigo = models.FloatField(blank=True, null=True)
    nome = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia18_passagem_custeada"


class Sdia19SituacaoRelatorio(models.Model):
    codigo = models.IntegerField(primary_key=True)
    situacao = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia19_situacao_relatorio"


class Sdia20BancosPais(models.Model):
    codigo = models.CharField(primary_key=True, max_length=3)
    nome_banco = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia20_bancos_pais"


class Sdia21TipoOrigem(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nome_tipo = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia21_tipo_origem"


class SdiaOrdemServico20180125(models.Model):
    numero = models.IntegerField(primary_key=True)
    data = models.TextField(blank=True, null=True)  # This field type is a guess.
    local = models.TextField()  # This field type is a guess.
    chapa_servidor = models.TextField()  # This field type is a guess.
    nome_servidor = models.TextField()  # This field type is a guess.
    cargo_servidor = models.TextField()  # This field type is a guess.
    carteira_identidade = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    finalidade = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_designante = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_estado = models.FloatField(blank=True, null=True)
    valor_unit_estado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_pais = models.FloatField(blank=True, null=True)
    valor_unit_pais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_diaria_exterior = models.FloatField(blank=True, null=True)
    valor_unit_exterior = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_ordenador = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_importancia = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_setor_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    chapa_resp_pessoal = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_empenho = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_empenho = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    num_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_cheque = models.TextField(blank=True, null=True)  # This field type is a guess.
    chapa_resp_financeiro = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    situacao = models.ForeignKey(
        Sdia06SituacaoOs, models.DO_NOTHING, db_column="situacao", blank=True, null=True
    )
    sdia07_cdgmotivo_cancel = models.ForeignKey(
        Sdia07MotivoCancelamento,
        models.DO_NOTHING,
        db_column="sdia07_cdgmotivo_cancel",
        blank=True,
        null=True,
    )
    sdia02_cdglocalidade_origem = models.ForeignKey(
        Sdia02Localidade,
        models.DO_NOTHING,
        db_column="sdia02_cdglocalidade_origem",
        blank=True,
        null=True,
    )
    valor_total_estado = models.FloatField(blank=True, null=True)
    valor_total_pais = models.FloatField(blank=True, null=True)
    valor_total_exterior = models.FloatField(blank=True, null=True)
    valor_dolar = models.FloatField(blank=True, null=True)
    sdia12_cdgtipo_finalidade = models.ForeignKey(
        Sdia12TipoFinalidade,
        models.DO_NOTHING,
        db_column="sdia12_cdgtipo_finalidade",
        blank=True,
        null=True,
    )
    sacs01_usuario_cadastro = models.FloatField(blank=True, null=True)
    sdia08_cdgpessoa_externa = models.ForeignKey(
        Sdia08PessoaExterna,
        models.DO_NOTHING,
        db_column="sdia08_cdgpessoa_externa",
        blank=True,
        null=True,
    )
    sdia13_cdgconvenio = models.ForeignKey(
        Sdia13Convenio,
        models.DO_NOTHING,
        db_column="sdia13_cdgconvenio",
        blank=True,
        null=True,
    )
    data_setor_financeiro = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    sacs01_usuario_empenho = models.FloatField(blank=True, null=True)
    sacs01_usuario_cancelamento = models.FloatField(blank=True, null=True)
    data_cancelamento = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    banco = models.FloatField(blank=True, null=True)
    agencia = models.TextField(blank=True, null=True)  # This field type is a guess.
    conta = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_protocolo_banco = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    relatorio_entregue = models.BooleanField(blank=True, null=True)
    meio = models.FloatField(blank=True, null=True)
    km = models.FloatField(blank=True, null=True)
    num_bilhete = models.TextField(blank=True, null=True)  # This field type is a guess.
    empresa_transporte = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    placa_veiculo_mp = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    descricao_resultado = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    observacoes = models.TextField(blank=True, null=True)  # This field type is a guess.
    data_relatorio = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    protocolo = models.TextField(blank=True, null=True)  # This field type is a guess.
    meiadiaria = models.BooleanField(blank=True, null=True)
    tipo = models.FloatField(blank=True, null=True)
    relatorioonline = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    emissaobilhete = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    viagemefetivada = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    data_recebido = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    informacoes_adicionais = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    valor_pass = models.FloatField(blank=True, null=True)
    autoridade_sol = models.FloatField(blank=True, null=True)
    autoridade_con = models.FloatField(blank=True, null=True)
    pass_custeada = models.FloatField(blank=True, null=True)
    pass_custeada_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    locomocao_outros = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    auxilios_devolvidos = models.FloatField(blank=True, null=True)
    valor_devolucao = models.FloatField(blank=True, null=True)
    tipo_origem = models.FloatField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "sdia_ordem_servico_20180125"


class VwBiSdia(models.Model):
    ano = models.TextField(blank=True, null=True)  # This field type is a guess.
    anomes = models.TextField(blank=True, null=True)  # This field type is a guess.
    sk_id_ordem_servico = models.IntegerField()
    sk_chapa = models.TextField()  # This field type is a guess.
    cargo_servidor = models.TextField()  # This field type is a guess.
    num_diaria_estado = models.FloatField(blank=True, null=True)
    num_diaria_exterior = models.FloatField(blank=True, null=True)
    num_diaria_pais = models.FloatField(blank=True, null=True)
    valor_unit_estado = models.FloatField(blank=True, null=True)
    valor_unit_exterior = models.FloatField(blank=True, null=True)
    valor_unit_pais = models.FloatField(blank=True, null=True)
    valor_total_estado = models.FloatField(blank=True, null=True)
    valor_total_exterior = models.FloatField(blank=True, null=True)
    valor_total_pais = models.FloatField(blank=True, null=True)
    valor_devolucao = models.FloatField(blank=True, null=True)
    valor_dolar = models.FloatField(blank=True, null=True)
    valor_importancia = models.FloatField(blank=True, null=True)
    valor_pass = models.FloatField(blank=True, null=True)
    sk_concedente = models.FloatField(blank=True, null=True)
    sk_solicitante = models.FloatField(blank=True, null=True)
    sk_loc_origem = models.FloatField(blank=True, null=True)
    sk_locomocao = models.FloatField(blank=True, null=True)
    sk_cdgmotivo_cancel = models.FloatField(blank=True, null=True)
    sk_cdgpessoa_externa = models.FloatField(blank=True, null=True)
    sk_cdgtipo_finalidade = models.FloatField(blank=True, null=True)
    sk_cdgconvenio = models.FloatField(blank=True, null=True)
    sk_situacao_os = models.FloatField(blank=True, null=True)
    sk_loc_dest = models.FloatField(blank=True, null=True)
    qtdd = models.FloatField(blank=True, null=True)
    lista_destinos = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "vw_bi_sdia"

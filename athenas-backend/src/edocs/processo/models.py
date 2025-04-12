# -.- coding: utf-8 -.-
"""
Módulo que contém a definição dos modelos.

:Classes:
  :class:`Processo`,
  :class:`Assunto`,
  :class:`Situacao`,
  :class:`Referencia`,
  :class:`Justificativa`,
  :class:`MovimentacaoProcesso`,

"""
from datetime import datetime

from contrib.middleware import get_current_user
from contrib.utils import getLogger
from django.contrib.auth.models import User
from django.db import models
from django.template import loader
from edocs.processo.verifying_digit import calc_check_digits
from edocs.protocolo.models import Movimentacao, Protocolo, ProtocoloManager
from engine.models import ControllerPermission
from judicial.models import LegalMatter
from rh.models import OrgaoGeral, Pessoa, Servidor
from standard.models import AuditTimestampModel, Choice, Configuration

log = getLogger()


class Processo(Protocolo):
    """
    **Classe** que define o Processo Administrativo.
    """

    class Meta:
        db_table = "epad_processo"
        permissions = (("admin", "Visão administrativa"),)

    codigo_processo = models.CharField(max_length=50, unique=True, blank=True)
    numero = models.IntegerField(blank=True)
    ano = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("epadm", "ANO_EPADM"),
        verbose_name="Ano",
        blank=True,
    )
    paginas = models.SmallIntegerField(null=True, blank=True)
    interessados = models.ManyToManyField(Pessoa, related_name="processo_interessado")
    # Parametro "on_delete" adicionado. (Django 2)
    assunto_processo = models.ForeignKey(
        "Assunto", blank=True, null=True, on_delete=models.CASCADE
    )
    volume = models.SmallIntegerField(null=True, blank=True)
    motivo_excluido = models.TextField(null=True, blank=True)
    manual = models.BooleanField(default=False)
    caixa = models.CharField(max_length=200, null=True, blank=True)

    classe_procedimento = models.IntegerField(null=True, blank=True)
    unidade_mp = models.IntegerField(null=True, blank=True)
    unidade_interna = models.IntegerField(null=True, blank=True)
    digito_verificador = models.IntegerField(null=True, blank=True)

    CLASSE_PROCEDIMENTO = 19
    UNIDADE_MP = 30

    @classmethod
    def int_to_roman(cls, entrada):
        """Converte número inteiro para número romano

        :param entrada: Número inteiro a ser convertido
        :type entrada: Integer

        :returns: Strings com número romano
        """
        if not isinstance(entrada, type(1)):
            raise TypeError("expected integer, got %s" % type(entrada))
        if not 0 < entrada < 4000:
            log.debug("entrada: ")
            log.debug(entrada)
            log.debug(type(entrada))
            raise ValueError("Argument must be between 1 and 3999")
        ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
        nums = ("M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I")
        result = []

        for i in range(len(ints)):
            count = int(entrada / ints[i])
            result.append(nums[i] * count)
            entrada -= ints[i] * count
        return "".join(result)

    @classmethod
    def roman_to_int(cls, entrada):
        """Converte número romano para número inteiro

        :param entrada: Número romano a ser convertido
        :type entrada: String

        :returns: Integer
        """
        if not isinstance(entrada, type("")):
            raise TypeError("expected string, got %s" % type(entrada))
        entrada = entrada.upper()
        nums = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
        soma = 0
        for i in range(len(entrada)):
            try:
                value = nums[entrada[i]]
                if i + 1 < len(entrada) and nums[entrada[i + 1]] > value:
                    soma -= value
                else:
                    soma += value
            except KeyError:
                raise ValueError("Entrada não é um numero Romano válido: %s" % entrada)

        if Processo.int_to_roman(soma) == entrada:
            return soma
        else:
            raise ValueError("Entrada não é um numero Romano válido: %s" % entrada)

    @classmethod
    def Movimentacao(cls):
        return MovimentacaoProcesso

    @classmethod
    def next_numero(cls):
        now = datetime.now()
        query = (
            Processo.objects.filter(ano=now.year)
            .order_by("numero")
            .aggregate(maximo=models.Max("numero"))
        )
        numero = int(query.get("maximo") or 0)

        return numero + 1, now.year

    def __str__(self):
        return "{0} - {1}".format(self.codigo_processo, self.process_matter_subject)

    def create_first_movement(self):
        """
        Este método é responsável por criar a primeira movimentação do protocolo.
        Na primeira movimentação o destinatário será o próprio servidor de origem.
        """
        cfg = Configuration.get_or_create("epad")
        try:
            MovimentacaoProcesso.criar_movimentacao(
                {
                    "protocolo": self,
                    "orgao_geral_origem": (
                        self.orgao_geral_origem.pk if self.orgao_geral_origem else None
                    ),
                    "orgao_geral_destino": (
                        self.orgao_geral_origem.pk if self.orgao_geral_origem else None
                    ),
                    "servidor_origem": (
                        self.servidor_origem.pk if self.servidor_origem else None
                    ),
                    "servidor_destino": (
                        self.servidor_origem.pk if self.servidor_origem else None
                    ),
                    "lotacao_criacao": (
                        self.lotacao_criacao.pk if self.lotacao_criacao else None
                    ),
                    "data_recebimento": self.data_criacao,
                    "data_encaminhamento": self.data_criacao,
                    "parecer": self.resumo,
                    "passo": 0,
                    "paginas": self.paginas,
                    "volume": self.volume,
                    "situacao": Situacao.objects.get(
                        pk=int(cfg.get("situacao_novo_processo"))
                    ),
                    "with_workflow": True,
                }
            )
        except Exception as e:
            log.exception(e)
            raise Exception("Não foi possível gravar as informações!\nTente novamente!")

    @property
    def process_matter_subject(self):
        subject = "Não definido"

        if self.process_matter.filter():
            principal = self.process_matter.filter(principal=True).first()
            if principal:
                subject = principal.legal_matter.path

            return subject
        else:
            return str(self.assunto_processo.nome) if self.assunto_processo else subject

    def get_verify_digit(self):
        number_process = "%s%s%s%07d%4d" % (
            self.classe_procedimento,
            self.unidade_mp,
            self.orgao_geral_origem.lotacao.code_cnmp,
            self.numero,
            self.ano,
        )
        digit = calc_check_digits(number_process)
        return int(digit)

    def get_formated_code_process(self):
        return "%s%s%04d%07d%4d%02d" % (
            self.classe_procedimento,
            self.unidade_mp,
            self.unidade_interna,
            self.numero,
            self.ano,
            self.digito_verificador,
        )

    def save(self, *args, **kwargs):
        self.special_type = self.__class__._meta.model_name

        if not self.pk:
            raise Exception(
                "Esta funcionalidade foi desativada, novos processos devem ser instaurados no SEI."
            )

        user = get_current_user()
        cpermission = ControllerPermission.objects.get(name="epad-admin")
        import datetime

        if not self.pk and not cpermission.users.filter(pk=user.id):
            raise Exception("Você não tem permissão para cadastrar processos!")

        if self.excluido and self.movimentacoes.count() > 1:
            raise Exception(
                "Não é possível excluir este processo pois ele já foi movimentado!"
            )

        if not self.pk:
            cfg = Configuration.get_or_create("epad")
            if cfg.get("situacao_novo_processo") is None:
                raise Exception("Erro: Falta configurar situação de novo processo")
            if self.manual is True:
                self.ano = int(self.ano)
                if not self.ano:
                    raise Exception("É necessário informar o ano do processo.")

                self.numero = int(self.numero)
                log.debug(type(self.ano))
                # if self.ano > 2015:
                if self.ano >= datetime.date.today().year:
                    raise Exception(
                        "Permitido o cadastro manual apenas de processos de %s e anos anteriores"
                        % (datetime.date.today().year - 1)
                    )
                if self.ano < 1900:
                    raise Exception(
                        "Permitido o cadastro manual apenas de processos a partir de 1900"
                    )
                if Processo.objects.filter(ano=self.ano, numero=self.numero).exists():
                    raise Exception("Já existe um processo com este código")
                prox_num, ano_atual = self.next_numero()

                self.classe_procedimento = self.CLASSE_PROCEDIMENTO
                self.unidade_mp = self.UNIDADE_MP
                self.unidade_interna = self.orgao_geral_origem.lotacao.code_cnmp
                self.digito_verificador = self.get_verify_digit()

                cod_unidade = self.codigo_processo.split(".")
                if (
                    self.ano == ano_atual
                    and self.numero >= prox_num
                    and cod_unidade[1] == "0701"
                ):
                    raise Exception(
                        "Não é permitido cadastro manual de processos posteriores"
                    )
            else:

                self.numero, self.ano = self.next_numero()
                # self.codigo_processo = '%4d.0701.%05d' % (self.ano, self.numero)

                self.classe_procedimento = self.CLASSE_PROCEDIMENTO
                self.unidade_mp = self.UNIDADE_MP
                self.unidade_interna = self.orgao_geral_origem.lotacao.code_cnmp

                if not self.unidade_interna:
                    raise Exception(
                        "Não há código de unidade interna cadastrada para essa lotação!"
                    )

                self.digito_verificador = self.get_verify_digit()

                self.codigo_processo = "%s.%s.%s.%07d/%4d-%02d" % (
                    self.classe_procedimento,
                    self.unidade_mp,
                    self.orgao_geral_origem.lotacao.code_cnmp,
                    self.numero,
                    self.ano,
                    self.digito_verificador,
                )
        else:
            old = Processo.objects.get(pk=self.pk)
            user = get_current_user()
            if old.paginas > self.paginas:
                if user.has_perm("processo.admin") is False:
                    raise Exception(
                        "Você não tem permissão para reduzir as páginas do processo"
                    )
                else:
                    if (
                        self.movimentacoes.order_by("-passo")[0]
                        .movimentacaoprocesso.justificativas.filter(
                            tipo=1,
                            valor_antigo=old.paginas,
                            valor_novo=self.paginas,
                            usuario=user,
                        )
                        .count()
                        == 0
                    ):
                        raise Exception(
                            "É necessário informar justificativa, favor utilizar o gerenciador para administradores"
                        )

            if old.volume > self.volume:
                if user.has_perm("processo.admin") is False:
                    raise Exception(
                        "Você não tem permissão para reduzir o volume do processo"
                    )
                else:
                    if (
                        self.movimentacoes.order_by("-passo")[0]
                        .movimentacaoprocesso.justificativas.filter(
                            tipo=2,
                            valor_antigo=old.volume,
                            valor_novo=self.volume,
                            usuario=user,
                        )
                        .count()
                        == 0
                    ):
                        raise Exception(
                            "É necessário informar justificativa, favor utilizar o gerenciador para administradores"
                        )

            if self.excluido:
                mp = self.movimentacoes.latest("passo").movimentacaoprocesso
                mp.situacao = Situacao.objects.get(nome="Excluido")
                mp.save()

        # self.assunto = str(self.assunto_processo) if self.assunto_processo else '----'
        self.assunto = self.process_matter_subject

        super(Processo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        log.warn("Não é permitida a exclusão de um processo")

    @property
    def render_process(self):

        dias_criacao_processo = (
            (datetime.now() - self.protocolo_ptr.data_criacao).days
            if self.protocolo_ptr.data_finalizado is None
            else ""
        )
        dias_criacao_processo = str(dias_criacao_processo) + " dia(s)"

        primeiro_interessado = [
            inte.nome.encode("ascii", "ignore") for inte in self.interessados.filter()
        ]

        tpl = loader.get_template("processo/process.html")
        return tpl.render(
            {
                "process": self,
                "appends": [
                    {
                        "volume": self.int_to_roman(self.volume),
                        "dias_criacao": dias_criacao_processo,
                        "primeiro_interessado": primeiro_interessado,
                    }
                ],
            }
        )

    @property
    def rend_legal_signs(self):
        tpl = loader.get_template("processo/legalSigns.html")
        return tpl.render({"process": self})

    @property
    def rend(self):
        data = self.cache_rendered if self.cache_rendered else self.render_process

        if self.valid_signatures.exists():
            data += self.rend_legal_signs

        return data


class Assunto(models.Model):
    """
    **Classe** que define os assuntos do Processo Administrativo.
    """

    class Meta:
        db_table = "epad_assunto"
        ordering = ("nome",)

    nome = models.CharField(max_length=200)


class Situacao(models.Model):
    """
    **Classe** que define as situações do Processo Administrativo.
    """

    class Meta:
        db_table = "epad_situacao"
        ordering = ("nome",)

    nome = models.CharField(max_length=200)


class Referencia(models.Model):
    """
    **Classe** que define as referencias do Processo Administrativo.
    """

    class Meta:
        db_table = "epad_referencia"
        ordering = ("data",)

    REFERENCIA_CHOICES = (
        (1, "Anexação"),
        (2, "Apensação"),
        (3, "Desapensação"),
    )

    # Parametro "on_delete" adicionado. (Django 2)
    processo = models.ForeignKey(
        Processo, related_name="proc_referencias", on_delete=models.CASCADE
    )
    referenciado = models.ForeignKey(
        Processo, related_name="proc_referenciado_por", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    tipo = models.SmallIntegerField(choices=REFERENCIA_CHOICES, default=1)
    data = models.DateField()
    descricao = models.CharField(max_length=300)

    def save(self, *args, **kwargs):
        ultima_mov = Movimentacao.objects.filter(
            protocolo=self.processo.protocolo_ptr
        ).order_by("-passo")[0]
        ultima_mov_processo = ultima_mov.movimentacaoprocesso
        if ultima_mov_processo.historico_referencias.filter(pk=self.pk):
            raise Exception(
                "Impossível alterar uma referencia após movimentação do processo"
            )
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ultima_mov = Movimentacao.objects.filter(
            protocolo=self.processo.protocolo_ptr
        ).order_by("-passo")[0]
        ultima_mov_processo = ultima_mov.movimentacaoprocesso
        if ultima_mov_processo.historico_referencias.filter(pk=self.pk):
            raise Exception(
                "Impossível excluir uma referencia após movimentação do processo"
            )
        super(self.__class__, self).delete(*args, **kwargs)


class Justificativa(models.Model):
    """
    **Classe** que define as justificativas informadas ao reduzir página ou volume do Processo Administrativo.
    """

    class Meta:
        db_table = "epad_justificativa"

    TIPO_CHOICES = ((1, "Página"), (2, "Volume"))
    # Justificativa será associada à ultima movimentação do processo no momento em que for criada
    # Justificativa terá o usuário que efetuou a justificativa (usuário com permissão de reduzir o numero de pagina ou volume),
    # o destinatário da movimentação associada à justificativa será o responsável pelo pedido de redução de pagina ou volume,
    # informando a justificativa ao administrador que possui permissão para tal
    # Parametro "on_delete" adicionado. (Django 2)
    processo = models.ForeignKey(
        Processo, related_name="justificativas", on_delete=models.CASCADE
    )
    movimentacao = models.ForeignKey(
        "MovimentacaoProcesso", related_name="justificativas", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    usuario = models.ForeignKey(
        User, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    valor_antigo = models.SmallIntegerField(null=True, blank=True)
    valor_novo = models.SmallIntegerField(null=True, blank=True)
    justificativa = models.TextField(null=True, blank=True)
    tipo = models.SmallIntegerField(choices=TIPO_CHOICES, default=1)

    def save(self, *args, **kwargs):
        if self.tipo == 1:
            self.valor_antigo = self.processo.paginas
            self.processo.paginas = self.valor_novo
        if self.tipo == 2:
            self.valor_antigo = self.processo.volume
            self.processo.volume = self.valor_novo
        if self.valor_novo >= self.valor_antigo:
            raise Exception("Justificativa apenas para redução")
        super(self.__class__, self).save(*args, **kwargs)
        self.processo.save()


class MovimentacaoProcesso(Movimentacao):
    """
    **Classe** que define as movimentações do Processo Administrativo.
    """

    class Meta:
        db_table = "epad_movimentacao"

    paginas = models.SmallIntegerField(null=True, default=0)
    situacao = models.ForeignKey(
        Situacao, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    volume = models.SmallIntegerField(null=True, blank=True)
    historico_referencias = models.ManyToManyField(Referencia, related_name="+")

    @classmethod
    def criar_movimentacao(cls, kwargs):
        """
        Este método é responsável por movimentar um Protocolo/Processo.
        OBS: Este método não atualiza a movimentação de origem para o status de encaminhado=True.
        A lotacao_criacao só marcada caso o protocolo seja criado em uma lotação que
        possua propriedade de protocolo geral.
        @param Protocolo - protocolo.
        @param OrgaoGeral - orgao_geral_origem, instância da lotação que está enviando.
        @param OrgaoGeral - orgao_geral_destino, instância da lotação que está recebendo.
        @param Servidor - servidor_origem, servidor que está enviando.
        @param boolean - deferido.
        @param data_encaminhamento - data e hora de encaminhamento.
        @param text - parecer, parecer de envio.
        @param boolean - urgente.
        @param Pessoa - Destinatario.
        @param data_finalizado - data e hora de finalização.
        """
        if "data_recebimento" not in kwargs:
            kwargs.update({"data_recebimento": None})
        protocolo = kwargs.get("protocolo", None)
        lotacao_origem = kwargs.get("orgao_geral_origem", None)
        lotacao_origem = (
            OrgaoGeral.objects.get(pk=lotacao_origem)
            if lotacao_origem is not None
            else lotacao_origem
        )
        lotacao_destino = kwargs.get("orgao_geral_destino", None)
        servidor = kwargs.get("servidor_origem", None)
        servidor_destino = kwargs.get("servidor_destino", None)
        destinatario = kwargs.get("destinatario", None)
        lotacao_criacao = (
            OrgaoGeral.objects.get(pk=int(kwargs.get("lotacao_criacao")))
            if not kwargs.get("lotacao_criacao") is None
            and kwargs.get("lotacao_criacao") != ""
            else None
        )
        if lotacao_criacao is None and lotacao_origem is not None:
            lotacao_criacao = (
                ProtocoloManager.get_lotacao_criacao(servidor)
                if Movimentacao.objects.filter(protocolo=protocolo.pk).exists() == 0
                else None
            )
        try:
            cls.validacao_criar_movimentacao(kwargs)
            log.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            mp = MovimentacaoProcesso(
                protocolo=protocolo,
                lotacao_criacao=lotacao_criacao,
                lotacao_origem=lotacao_origem,
                lotacao_destino=(
                    OrgaoGeral.objects.get(pk=lotacao_destino)
                    if lotacao_destino is not None
                    else lotacao_destino
                ),
                servidor_origem=Servidor.objects.get(pk=servidor),
                servidor_destino=(
                    Servidor.objects.get(pk=servidor_destino)
                    if servidor_destino is not None
                    else servidor_destino
                ),
                destinatario=(
                    destinatario
                    if destinatario is None or destinatario == "None"
                    else Pessoa.objects.get(pk=destinatario)
                ),
                data_encaminhamento=kwargs.get("data_encaminhamento", datetime.now()),
                parecer=kwargs.get("parecer"),
                urgente=kwargs.get("urgente", False),
                data_finalizado=kwargs.get("data_finalizado"),
                passo=kwargs.get("passo", None),
                data_recebimento=kwargs.get("data_recebimento", None),
                paginas=kwargs.get("paginas", 0),
                situacao=kwargs.get("situacao", None),
                volume=kwargs.get("volume", None),
                with_workflow=True,
            )
            mp.save()

            if (
                MovimentacaoProcesso.objects.filter(
                    protocolo=mp.protocolo,
                    lotacao_origem=mp.lotacao_origem,
                    lotacao_destino=mp.lotacao_destino,
                    passo=mp.passo,
                ).count()
                > 1
            ):
                MovimentacaoProcesso.objects.filter(
                    protocolo=mp.protocolo,
                    lotacao_origem=mp.lotacao_origem,
                    lotacao_destino=mp.lotacao_destino,
                    passo=mp.passo,
                )[0].delete()

        except Exception as e:
            log.exception(e)
            raise e


class ProcessMatter(AuditTimestampModel):

    principal = models.BooleanField(default=False)
    legal_matter = models.ForeignKey(
        LegalMatter, related_name="in_process_matter", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    process = models.ForeignKey(
        Processo, related_name="process_matter", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return "%s" % self.legal_matter

    @property
    def state_icon(self):
        rst = {}

        if self.principal:
            rst.update(
                title="Assunto principal",
                iconCls="icon-edocs icon-protocolo-close-protocol",
            )

        return rst

    @property
    def icons(self):
        return [self.state_icon]

    def define_initial_principal(self):
        if not self.process.process_matter.filter():
            self.principal = True

    def save(self, *args, **kargs):
        self.define_initial_principal()
        super(ProcessMatter, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        if self.principal:
            if self.process.process_matter.exclude(pk=self.pk).count() > 0:
                obj = self.process.process_matter.exclude(pk=self.pk).first()
                obj.principal = True
                obj.save()

        super(ProcessMatter, self).delete(*args, **kargs)

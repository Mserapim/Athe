# -.- coding: utf-8 -.-
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields as generic
from django.db import models, transaction
from contrib.utils import getLogger
from contrib import decorator

# import os
# import md5
# import hashlib
import random
import string

SEP = "##"
DIVSEP = "$$"
log = getLogger(__name__)


@decorator.to_search(
    [
        {"name": "enunciado", "type": "text"},
        # {'name':'cpf', 'type':'number'},
    ]
)
class Questao(models.Model):
    """
    Classe de questões, pois toda questão deve herdar dessa classe para poder ser usada corretamente por pela classe Questionario
    """

    class Meta:
        # ordering= ('label',)
        db_table = "qst_questao"

    enunciado = models.TextField(blank=False, null=False)
    mista = models.BooleanField(null=False, default=False)
    # alternativas= models.ManyToManyField(Alternativa, blank=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Child model
    child = generic.GenericForeignKey(fk_field="id")

    def save(self, **kwargs):
        if not self.pk:
            self.content_type = ContentType.objects.get_for_model(self)
        super(Questao, self).save(**kwargs)

    def __str__(self):
        return self.enunciado

    @property
    def label(self):
        return self.enunciado

    @property
    def tipo(self):
        # return content_type
        return "Questão"

    def add_grupo(self, grupo):
        if grupo:
            for alt in Alternativa.objects.filter(grupo=grupo).exclude(
                pk__in=[a.id for a in self.alternativas.all()]
            ):
                self.alternativas.add(alt)
        return self.alternativas.count()

    def to_str(self):
        text = "-#" * 50 + "\nQUESTÃO %d\n%s" % (self.pk, self.enunciado)
        for alt in self.alternativas.all():
            text += "\n%s %s" % (alt.label or "o", alt.texto)
        return text

    def to_json(self):
        dic = {"id": self.id, "enunciado": "%s" % self.enunciado, "alternativas": []}
        for alt in self.alternativas.all().order_by("valor"):
            dic["alternativas"].append(alt.to_json())
        return dic

    def resposta(self, alternativa_id):
        try:
            alt = self.alternativas.get(pk=alternativa_id[0])
        except Exception as e:
            log = getLogger("Questionario:RespostaQuestao:Model")
            log.exception(e)
            raise e
        # TODO otmizar essa formatação
        return "%(valor)s%(SEP)s%(texto)s%(SEP)s%(id)d" % {
            "valor": alt.valor,
            "SEP": SEP,
            "texto": alt.texto,
            "id": alt.id,
        }

    def convert_resp(self, resp, qr):
        valor, texto, id = resp.split(SEP)
        try:
            alt = Alternativa.objects.get(pk=id)
        except Exception as e:
            print("Erro ao carregar alternativa %s" % id)
        if not alt.texto == texto:
            return (
                "Id da alternativa não confere com o texto. ID: %d| Texto: %s -> %s"
                % (alt.id, texto, alt.texto)
            )
        r = Resposta()
        r.alternativa = alt
        r.questao = self
        r.questionario_resposta = qr
        r.save()
        return "%r" % r

    def reorder(self):
        posicao = 1
        for alt in Alternativa.objects.filter(questao=self).order_by("ordem"):
            if alt.ordem != posicao:
                alt.ordem = posicao
                alt.save()
            posicao += 1


@decorator.to_search(
    [
        {"name": "texto", "type": "text"},
        {"name": "valor", "type": "text"},
        {"name": "grupo", "type": "text"},
    ]
)
class Alternativa(models.Model):
    """
    Classe de alternativas, para as questões que possuem alternativas. EX.: Questões de ME(múltipla escolha) ou MS(multiseleção)
    """

    class Meta:
        ordering = ("ordem",)
        db_table = "qst_alternativa"

    label = models.CharField(max_length=100, null=True, default="")
    texto = models.TextField(blank=True, null=False)
    valor = models.CharField(max_length=5, blank=True, null=False)
    grupo = models.CharField(max_length=50, blank=True, null=True)
    ordem = models.PositiveSmallIntegerField(null=True)
    questao = models.ForeignKey(
        Questao, related_name="alternativas", null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s %s" % (self.label, self.texto)

    def to_json(self):
        return {"label": "%s" % self.label, "id": self.id, "texto": "%s" % self.texto}

    def delete(self, *args, **kwargs):
        # q = self.questionario
        super(Alternativa, self).delete(*args, **kwargs)
        self.questao.reorder()

    def move_up(self):
        if self.ordem == 1:
            return False
        else:
            try:
                alt = Alternativa.objects.get(
                    questao=self.questao, ordem=(self.ordem - 1)
                )
            except:
                alt = None
            finally:
                if alt is not None:
                    alt.ordem = self.ordem
                    alt.save()
                self.ordem -= 1
                self.save()
                return True

    def move_down(self):
        try:
            alt = Alternativa.objects.get(questao=self.questao, ordem=(self.ordem + 1))
        except Exception as e:
            alt = None
            log.exception(e)
        finally:
            if alt is not None:
                alt.ordem = self.ordem
                alt.save()
                self.ordem += 1
                self.save()
                return True
            else:
                return False


class QuestaoAberta(Questao):
    class Meta:
        # ordering= ('label',)
        db_table = "qst_questaoaberta"

    def resposta(self, texto):
        log = getLogger("Questionario:RespostaAberta:Model")
        log.debug(texto[0])
        return "%s" % (texto[0])

    def convert_resp(self, resp, qr):
        r = Resposta()
        r.questao = self
        r.questionario_resposta = qr
        r.texto = resp
        r.save()
        return "%r" % r

    @property
    def tipo(self):
        # return content_type
        return "Questão Aberta"


class QuestaoMS(Questao):
    """
    Questão do tipo multipla escolha
    """

    class Meta:
        # ordering= ('label',)
        db_table = "qst_questaoms"

    def resposta(self, alternativas_id):
        log = getLogger("Questionario:RespostaQuestao:Model")
        log.exception("ALTERNATIVAS:")
        log.exception(alternativas_id)
        """
        Retorna a resposta formatada para a questao MS de acordo com o @alternativa_id: FORMATO {[VALOR_alternativa:ENUNCIADO_alternativa:1:ID_alternativa[,VALOR_alternativa:ENUNCIADO_alternativa:1:ID_alternativa]}

        Parametros
        @alternativa_id= IDs das alternativas escolhidas
        """
        resposta = ""
        try:
            for alternativa in alternativas_id:
                log.exception("ALTERNATIVA:")
                log.exception(alternativa)
                alt = self.alternativas.get(pk=alternativa)
                resposta += (
                    "%(valor)s%(SEP)s%(texto)s%(SEP)s1%(SEP)s%(id)d%(divsep)s"
                    % {
                        "valor": alt.valor,
                        "SEP": SEP,
                        "divsep": DIVSEP,
                        "texto": alt.texto,
                        "id": alt.id,
                    }
                )
        except Exception as e:
            log = getLogger("Questionario:RespostaQuestao:Model")
            log.exception(e)

        return resposta

    def convert_resp(self, resp, qr):
        alts = resp.split(DIVSEP)
        for texto_alt in alts:
            if texto_alt:
                valor, texto, peso, id = texto_alt.split(SEP)
                try:
                    alt = Alternativa.objects.get(pk=id)
                except Exception as e:
                    print("Erro ao carregar alternativa %s" % id)
                if not alt.texto == texto:
                    return (
                        "Id da alternativa não confere com o texto. ID: %d| Texto: %s -> %s"
                        % (alt.id, texto, alt.texto)
                    )
                r = Resposta()
                r.alternativa = alt
                r.questao = self
                r.questionario_resposta = qr
                r.peso = peso
                r.save()
                print("%r" % r)

    @property
    def tipo(self):
        # return content_type
        return "Questão MS"


class QuestaoEnum(QuestaoMS):
    """
    Questão do tipo multipla escolha com numeração das alternativas escolhidas

    Atributos
    @valores: armazena os valores possíveis para as alternativas no formato: {valor:label_do_valor;[valor:label_do_valor]}
    """

    class Meta:
        # ordering= ('label',)
        db_table = "qst_questaoenum"

    valores = models.CharField(max_length=100, default="1:1")

    def to_json(self):
        dic = super(QuestaoMS, self).to_json()
        dic["valores"] = []
        for value in self.valores.split("#"):
            a = value.split(":")
            dic["valores"].append(dict(label=a[0], valor=a[1]))
        return dic

    def resposta(self, alternativas_id):
        """
        Retorna a resposta formatada para a questao MS-ENUM de acordo com o @alternativas_id: FORMATO {[ID_alternativa:ENUNCIADO_alternativa:valor[,ID_alternativa:ENUNCIADO_alternativa:valor]}

        Parametros
        @alternativa_id= IDs das alternativas escolhidas
        """
        resposta = ""
        #        print alternativas_id
        if alternativas_id:
            try:
                log = getLogger("Questionario:QuestaoEnum:Model")
                log.debug(alternativas_id)
                for alternativa_resp in alternativas_id:
                    resp = alternativa_resp.split(":")
                    peso = resp[1]
                    alt = self.alternativas.get(pk=resp[0])
                    resposta += (
                        "%(valor)s%(SEP)s%(texto)s%(SEP)s%(peso)s%(SEP)s%(id)d%(divsep)s"
                        % {
                            "valor": alt.valor,
                            "SEP": SEP,
                            "divsep": DIVSEP,
                            "texto": alt.texto,
                            "id": alt.id,
                            "peso": peso,
                        }
                    )
            except Exception as e:
                log = getLogger("Questionario:RespostaQuestao:Model")
                log.exception(e)
                raise e

        return resposta

    @property
    def tipo(self):
        # return content_type
        return "Questão Enum"


class Questionario(models.Model):
    """
    Classe Questionario, que gerencia as questoes e os textos para um questionario em específico. Qualquer questionario deve ser herdado dessa classe.
    @titulo: Título do quetionário
    @descrição: Descrição da finalidade e objetivos do formulário
    @data_inicio, @data_fim: início e fim para utilização do questionário
    @criado_em, @modificado_em: data de criação e modificação do questionário
    @ativo: Se o questionário ainda pode ser utilizado, mesmo que esteja dentro da data de validade
    @unico: Se o questionário so pode ser respondido uma única vez por um mesmo usuário
    """

    class Meta:
        ordering = ["-ativo", "titulo"]
        db_table = "qst_questionario"

    titulo = models.CharField(max_length=50, blank=False)
    descricao = models.TextField(default="")
    data_inicio = models.DateField(blank=False)
    data_fim = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(null=False, default=True)
    unico = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.titulo

    class IsActive(Exception):
        def __init__(self):
            Exception.__init__(self, "Atenção! Este questionário não está ativo.")

    class DelError(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Atenção! Este questionário não pode ser excluido."
            )

    def validate_active(self, id_questionario):
        q = Questionario.objects.filter(pk=id_questionario, ativo=True)

        if not q:
            raise self.IsActive()

    def to_json(self):
        dic = {
            "titulo": "%s" % self.titulo,
            "descricao": "%s" % self.descricao,
            "elementos": [],
        }
        for q in self.elemento_set.order_by("ordem"):
            dic["elementos"].append(q.to_json())
        return dic

    def questao(self, questao_id):
        try:
            q = self.elemento_set.get(pk=questao_id).elemento.child
        except Exception as e:
            log = getLogger("Questionario:RespostaQuestao:Model")
            log.exception(e)
            raise e

        return q

    def reorder(self):
        posicao = 1
        for il in Elemento.objects.filter(questionario=self).order_by("ordem"):
            if il.ordem != posicao:
                il.ordem = posicao
                # il.label = 'Q0'+str(posicao)
                il.save()
            posicao += 1

    def gera_chave(self):
        char_set = string.ascii_uppercase + string.digits
        chave = "".join(random.sample(char_set, 32))
        # chave = '25f9e794323b453885f5181f1b624d0b'
        return chave


class QuestionarioChave(models.Model):
    chave = models.CharField(max_length=100)
    questionario = models.ForeignKey(
        Questionario, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        unique_together = (("chave", "questionario"),)
        # ordering= ('label',)
        db_table = "qst_questionariochave"

    def save_chave(self, questionario, chave):
        qc = QuestionarioChave()
        try:
            obj, created = QuestionarioChave.objects.get_or_create(
                questionario=questionario, chave=chave
            )
            return created
        except Exception as e:
            log.exception(e)


class ReferenciaTextual(models.Model):
    class Meta:
        ordering = ("label",)
        db_table = "qst_referenciatextual"

    label = models.CharField(max_length=100)
    conteudo = models.TextField(default="")

    def __str__(self):
        return self.label

    def to_text(self):
        pass

    def to_json(self):
        return {"label": "%s" % self.label, "conteudo": "%s" % self.conteudo}

    @property
    def tipo(self):
        # return content_type
        return "Ref. Textual"


class Elemento(models.Model):
    class Meta:
        ordering = ("ordem",)
        db_table = "qst_elemento"
        unique_together = ["object_id", "content_type"]

    questionario = models.ForeignKey(
        Questionario, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    object_id = models.PositiveIntegerField()
    elemento = generic.GenericForeignKey("content_type", "object_id")
    ordem = models.PositiveSmallIntegerField(null=True)
    label = models.CharField(max_length=50)
    grupo = models.CharField(max_length=50, null=True)
    elemento_pai = models.ForeignKey(
        "Elemento",
        related_name="pai_elemento",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s - %s" % (self.questionario, self.elemento)

    #    def save(self,*args, **kwargs):
    #        if self.ordem is None:
    #            self.ordem= Elemento.objects.aggregate(Max('ordem'))['ordem__max']+1
    #        super(Elemento, self).save(*args, **kwargs)

    def to_json(self):
        dic = self.elemento.to_json()
        dic["tipo"] = self.content_type.name
        dic["ordem"] = self.ordem
        dic["grupo"] = self.grupo
        dic["label"] = self.label
        dic["id_elemento"] = self.id
        return dic

    def move_up(self):
        if self.ordem == 1:
            return False
        else:
            try:
                q = Elemento.objects.get(
                    questionario=self.questionario, ordem=(self.ordem - 1)
                )
            except:
                q = None
            finally:
                if q is not None:
                    q.ordem = self.ordem
                    # q.label = 'Q0'+str(self.ordem)
                    q.save()
                self.ordem -= 1
                # self.label = 'Q0'+str(self.ordem)

                self.save()
                return True

    def move_down(self):
        try:
            q = Elemento.objects.get(
                questionario=self.questionario, ordem=(self.ordem + 1)
            )
        except Exception as e:
            q = None
            log.exception(e)
        finally:
            if q is not None:
                q.ordem = self.ordem
                # q.label = 'Q0'+str(self.ordem)
                q.save()
                self.ordem += 1
                # self.label = 'Q0'+str(self.ordem)
                self.save()
                return True
            else:
                return False

    def delete(self, *args, **kwargs):
        # q = self.questionario
        super(Elemento, self).delete(*args, **kwargs)
        self.questionario.reorder()


class QuestionarioResposta(models.Model):
    class Meta:
        # ordering= ('label',)
        db_table = "qst_questionarioresposta"

    chave = models.CharField(max_length=64)
    questionario = models.ForeignKey(
        Questionario, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.questionario, self.chave)

    class KeyExists(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Atenção! Esta chave já foi utilizada para responder este questionário.",
            )

    def validate(self, id_questionario, chave):
        # log.debug(id_questionario)
        # log.debug(chave)
        try:
            q = Questionario.objects.get(pk=id_questionario, unico=True)
            qr = QuestionarioResposta.objects.filter(questionario=q, chave=chave)

            if qr:
                return False  # retorna false se já existir um questionarioResposta para a chave
                # raise self.KeyExists()
            else:
                return True  # retorna true se nao existir
        except:
            return True
            # log.exception(e)
        # q = Questionario.objects.get(pk=id_questionario,unico=True)
        # qr = QuestionarioResposta.objects.filter(questionario=q, chave = chave)
        # try:
        #     if qr:
        #         return True
        #     else:
        #         raise self.KeyExists()
        # except:
        #     raise self.KeyExists()


class RespostaQuestao(models.Model):
    """
    questao: Questao para qual foi dada essa resposta
    questionario_resposta: QuestionarioResposta que armazena as informações sobre quem respondeu o questionario
    texto: Armazena as respostas no formato: valor_alternativa:label_alternativa:id_alternativa(esse id é apenas para uma eventual auditoria)
    """

    class Meta:
        unique_together = (("questao", "questionario_resposta"),)
        db_table = "qst_respostaquestao"

    questao = models.ForeignKey(
        Questao, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    questionario_resposta = models.ForeignKey(
        QuestionarioResposta, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    texto = models.TextField(default="")
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Child model
    child = generic.GenericForeignKey(fk_field="id")

    def save(self, **kwargs):
        if not self.pk:
            self.content_type = ContentType.objects.get_for_model(self)

        super(RespostaQuestao, self).save(**kwargs)

    def _get_valor(self):
        return valor

    def _set_resposta(self, id_alternativa):
        try:
            alt = self.questao.alternativas.get(pk=id_alternativa)
        except Exception as e:
            log = getLogger("Questionario:RespostaQuestao:Model")
            log.exception(e)
            raise e
        self.texto = "%s:%s" % (alt.valor, alt)

    def _get_resposta(self):
        return self.texto

    resposta = property(_get_resposta, _set_resposta)


class RespostaQuestaoMS(RespostaQuestao):
    class Meta:
        db_table = "qst_resposta_questao_ms"

    """
    texto: Armazena as respostas no formato: valor_alternativa:label_alternativa:id_alternativa:peso_da_resposta (esse id_alternativa é apenas para uma eventual auditoria)
    """
    pass


class RespostaQuestaoAberta(RespostaQuestao):
    class Meta:
        db_table = "qst_resposta_questao_aberta"

    """
    texto: Armazena as respostas no formato: texto
    """
    pass


class Resposta(models.Model):
    """
    questao: Questao para qual foi dada essa resposta
    questionario_resposta: QuestionarioResposta que armazena as informações sobre quem respondeu o questionario
    texto: Armazena as respostas no formato: valor_alternativa:label_alternativa:id_alternativa(esse id é apenas para uma eventual auditoria)
    """

    class Meta:
        db_table = "qst_resposta"

    questao = models.ForeignKey(
        Questao, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    questionario_resposta = models.ForeignKey(
        QuestionarioResposta, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    alternativa = models.ForeignKey(
        Alternativa, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    texto = models.TextField(default="")
    peso = models.IntegerField(default=0)

    def __str__(self):
        return "%s: %s: %s" % (
            self.questionario_resposta,
            self.questao,
            self.alternativa,
        )

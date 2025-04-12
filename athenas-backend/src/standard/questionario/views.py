# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect
from django import forms

# from django.db import transaction
from django.db import models as models_d
from contrib import extjs
from contrib.utils import getLogger
from django.contrib.contenttypes.models import ContentType
from contrib.decorator import *
from contrib.extjs import ExtWidget
from contrib.decorator import login_required, validate
import contrib.ezjson as json
from standard.questionario import models
from contrib.utils import DateUtils
from datetime import *


from contrib.utils import get_json_engine

json = get_json_engine()
# import json

log = getLogger("Questionario:View")


@tab(
    [
        {
            "title": "Questionário",
            "field": ["titulo", "descricao", "data_inicio", "data_fim", "ativo"],
        },
        {
            "title": "Questões",
            "field": [
                "elementos",
            ],
        },
        {"title": "Referências Textuais", "field": []},
    ]
)
class QQuestionario(extjs.ExtCrud):

    class Form(forms.ModelForm):
        # data_inicio= forms.DateField(label="Data de inicio")

        class Meta:
            model = models.Questionario
            exclude = ("criado_em", "modificado_em")

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Título",
                "sortable": True,
                "dataIndex": "titulo",
                "key": "titulo",
                "width": 500,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "ativo",
                "key": "ativo",
                "width": 80,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questionários",
        "LIST": "Questionários",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }

    def to_json(self, args=[]):
        try:
            obj = self.Form.Meta.model.objects.get(pk=args[0])
            self.response.write(json.encode(obj.to_json()))
        except Exception as e:
            self.log.exception(e)
            self.log.debug(self.Form.Meta.model.objects.filter(pk=args[0])._as_sql())

    # @transaction.commit_manually
    def responder(self, args=[]):
        # TODO Esse método deve ser genérico, pois deve tratar cada questao de tipo diferente
        obj = {"result": []}
        params = dict(self.request.POST)
        if len(params) > 0:
            questionario_id = params.pop("questionario").pop()
            identificador = params.pop("identificador").pop()
            resp = models.Questionario.objects.filter(pk=questionario_id)
            if (
                resp.count() == 1
                and resp[0].unico
                and models.QuestionarioChave.objects.filter(
                    questionario=questionario_id, chave=identificador
                ).count()
                == 0
            ):
                try:
                    qresposta = models.QuestionarioResposta(
                        questionario_id=questionario_id
                    )
                    qresposta.save()
                    qc = models.QuestionarioChave(
                        questionario_id=questionario_id, chave=identificador
                    )
                    qc.save()
                    for elemento_id, alternativa_id in list(params.items()):
                        questao = qresposta.questionario.questao(elemento_id)
                        qresposta.respostaquestao_set.add(
                            models.RespostaQuestao(
                                questao=questao, texto=questao.resposta(alternativa_id)
                            )
                        )

                except Exception as e:
                    # transaction.rollback()
                    obj["success"] = False
                    obj["result"].append({"message": "Erro ao salvar o questionário!"})
                    self.log.exception(e)
                    self.response.write(json.encode(obj))
                else:
                    # transaction.commit()
                    obj["success"] = True
                    obj["result"].append({"message": "Questionário salvo com sucesso!"})
                    self.response.write(json.encode(obj))
            else:
                obj["success"] = False
                obj["result"].append(
                    {
                        "message": "Você não tem permissão para responder esse questionário!"
                    }
                )
                self.response.write(json.encode(obj))
        else:
            obj["success"] = False
            obj["result"].append({"message": "Erro no envio do questionario!"})
            self.response.write(json.encode(obj))

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        query = self.Form.Meta.model.objects.all()
        # query = self.Form.Meta.model.objects.filter(data_fim__gte=datetime.now()) #traz apenas os q nao estao com data_fim > data atual

        for quest in query:
            obj["collection"].append(
                {
                    "pk": quest.id,
                    "titulo": quest.titulo,
                    "data_inicio": DateUtils.datetime_to_str(quest.data_inicio),
                    "data_fim": (
                        DateUtils.datetime_to_str(quest.data_fim)
                        if quest.data_fim
                        else ""
                    ),
                    "ativo": quest.ativo,
                }
            )
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        self.log.info(self.request.POST)

        q = models.Questionario(
            titulo=self.request.REQUEST.get("titulo").upper(),
            descricao=self.request.REQUEST.get("descricao"),
            data_inicio=datetime.strptime(
                self.request.REQUEST.get("data_inicio"),
                getattr(settings, "DATE_INPUT_FORMATS")[0],
            ),
            data_fim=(
                datetime.strptime(
                    self.request.REQUEST.get("data_fim"),
                    getattr(settings, "DATE_INPUT_FORMATS")[0],
                )
                if self.request.REQUEST.get("data_fim")
                else None
            ),
            criado_em=datetime.now(),
            modificado_em=datetime.now(),
            ativo=True if self.request.REQUEST.get("ativo") == "on" else False,
            unico=True if self.request.REQUEST.get("unico") == "on" else False,
        )

        try:
            q.save()
            obj.update(success=True)
        except Exception as e:
            obj.update(message=str(e))
            self.log.error(e)
        else:
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        # self.log.info(self.request.POST)
        try:
            q = self.Form.Meta.model.objects.get(pk=self.request.REQUEST.get("pk"))
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                message="Não consigo encontrar o questionário para atualizar os valores."
            )
        else:
            q.titulo = self.request.REQUEST.get("titulo").upper()
            q.descricao = self.request.REQUEST.get("descricao")
            q.data_inicio = datetime.strptime(
                self.request.REQUEST.get("data_inicio"),
                getattr(settings, "DATE_INPUT_FORMATS")[0],
            )
            q.data_fim = (
                datetime.strptime(
                    self.request.REQUEST.get("data_fim"),
                    getattr(settings, "DATE_INPUT_FORMATS")[0],
                )
                if self.request.REQUEST.get("data_fim")
                else None
            )
            q.modificado_em = (datetime.now(),)
            q.ativo = True if self.request.REQUEST.get("ativo") == "on" else False
            q.unico = True if self.request.REQUEST.get("unico") == "on" else False
            q.save()
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}

        try:
            qst = self.Form.Meta.model.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            element = models.Elemento.objects.filter(questionario=qst)
            if element.exists():
                raise Exception(models.Questionario.DelError())
            for questao in element:
                questao.elemento.delete()  # deleta tmb as questoes e alternativas vinculadas a esse questionario
            for questionario in qst:
                qst.delete()  # deleta o questionario
        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": str(e)})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _get_instance(self, pk):
        obj = {}
        # self.log.info(pk);
        try:
            q = self.Form.Meta.model.objects.get(pk=pk)
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                {
                    "message": "Não consegui encontrar o questionario desejado.",
                    "success": False,
                }
            )
        else:
            obj.update(
                {
                    "instance": {
                        "pk": q.pk,
                        "titulo": str(q.titulo),
                        "descricao": str(q.descricao),
                        "data_inicio": DateUtils.date_to_str(q.data_inicio),
                        "data_fim": (
                            DateUtils.date_to_str(q.data_fim) if q.data_fim else ""
                        ),
                        "ativo": q.ativo,
                        "unico": q.unico,
                    },
                    "success": True,
                }
            )
        return obj

    def get(self, args=[]):
        obj = None if len(args) == 0 else self._get_instance(args[0])

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QQuestao(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            model = models.Questao
            exclude = ("content_type",)

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Enunciado",
                "sortable": True,
                "dataIndex": "enunciado",
                "key": "enunciado",
                "width": 500,
            },
        ]
        self.response["ContextType"] = "text/javascript"
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questões",
        "LIST": "Questões",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def create(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)

        try:
            questao = self.Form.Meta.model(
                enunciado=self.request.POST.get("enunciado"),
                mista=True if self.request.REQUEST.get("mista") == "on" else False,
            )
            questao.save()

            quest = self.request.POST.get("questionario")
            questionario = models.Questionario.objects.get(id=quest)
            content_type = ContentType.objects.get(
                app_label="questionario", model="questao"
            )

            ordem = (
                int(
                    models.Elemento.objects.filter(questionario=quest)
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )

            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=questao.id,
                ordem=ordem,
                label=self.request.POST.get("label"),
                grupo=self.request.POST.get("grupo").upper(),
                elemento_pai=elemento_pai,
            )

            element.save()
            questionario.reorder()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def __addAlternativa(self, tipo):

        tipos = dict(
            CE=("ERRADO", "CERTO"), SN=("NÃO", "SIM"), VF=("FALSO", "VERDADEIRO")
        )
        lb = ["a)", "b)"]

        opts = tipos.get(tipo)
        results = []
        try:

            for label, texto in zip(list(range(len(opts))), opts):
                alternativa = models.Alternativa(
                    label=lb[label], texto=texto, valor="5", grupo=tipo
                )
                alternativa.save()
                results.append(alternativa)
        except Exception as e:
            self.log.error(e)
            # transaction.rollback()
        else:
            # transaction.commit()
            return results

    def create_c_e(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}

        grupo = self.request.POST.get("tipo_alternativa")
        # self.log.info(self.request.POST)

        qs = models.Alternativa.objects.filter(grupo=grupo)
        # a1, a2 = qs if qs.exists() else self.__addAlternativa(grupo)
        alt = self.__addAlternativa(grupo)

        try:
            questao = self.Form.Meta.model(
                enunciado=self.request.POST.get("enunciado"),
                mista=True if self.request.REQUEST.get("mista") == "on" else False,
            )

            ordem = (
                int(
                    models.Alternativa.objects.filter(questao=questao.id)
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            questao.save()
            for a in alt:
                ordem = (
                    int(
                        models.Alternativa.objects.filter(questao=questao.id)
                        .aggregate(ultima_posicao=models_d.Max("ordem"))
                        .get("ultima_posicao")
                        or 0
                    )
                    + 1
                )
                a.ordem = ordem
                a.questao = questao
                a.save()

            # questao.alternativas.add(a1)
            # questao.alternativas.add(a2)

            questionario = models.Questionario.objects.get(
                id=self.request.POST.get("questionario")
            )
            content_type = ContentType.objects.get(
                app_label="questionario", model="questao"
            )

            ordem = (
                int(
                    models.Elemento.objects.filter(
                        questionario=self.request.POST.get("questionario")
                    )
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )
            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=questao.id,
                ordem=ordem,
                label=self.request.POST.get("label"),
                # label = 'Q0'+str(ordem),
                grupo=self.request.POST.get("grupo").upper(),
                elemento_pai=elemento_pai,
            )
            element.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)
        try:
            questao = self.Form.Meta.model.objects.get(pk=self.request.POST.get("pk"))
            element = models.Elemento.objects.get(object_id=self.request.POST.get("pk"))
            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )

        except Exception as e:
            self.log.error(e)
            obj.update(message="Não consegui encontrar a questao desejada.")
        else:

            if "alternativas" in self.request.POST:
                obj.update(success=True)
                questao.alternativas.clear()
                try:
                    for alternativa in self.request.POST.getlist("alternativas"):
                        questao.alternativas.add(
                            models.Alternativa.objects.get(pk=alternativa)
                        )
                    obj.update(message="Sucesso!")

                except Exception as e:
                    self.log.error(e)
                    obj.update(warning=True)
                    obj.update(message="Não consegui preencher as alternativas. %s" % e)
            else:
                questao.enunciado = self.request.REQUEST.get("enunciado")
                questao.mista = (
                    True if self.request.REQUEST.get("mista") == "on" else False
                )
                questao.save()
                element.label = self.request.POST.get("label")
                element.grupo = self.request.POST.get("grupo").upper()
                element.elemento_pai = elemento_pai
                element.save()

                obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _get_instance(self, pk):
        obj = {}
        try:
            q = self.Form.Meta.model.objects.get(pk=pk)
            element = models.Elemento.objects.filter(
                object_id=pk
            )  # pega ordem,label e grupo do elemento referente a questao
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                {
                    "message": "Não consegui encontrar a questao desejada.",
                    "success": False,
                }
            )
        else:
            for el in element:
                elemento_pai = models.Elemento.objects.filter(pk=el.elemento_pai_id)
                obj.update(
                    {
                        "instance": {
                            "pk": q.pk,
                            "enunciado": q.enunciado,
                            "mista": q.mista,
                            "ordem": el.ordem,
                            "label": el.label,
                            "grupo": el.grupo,
                            "alternativas": [
                                [alternativa.pk, str(alternativa)]
                                for alternativa in q.alternativas.filter()
                            ],
                            "elemento_pai": (
                                "%s" % elemento_pai[0].elemento
                                if elemento_pai.count()
                                else ""
                            ),
                            "elemento_pai_id": (
                                "%s" % el.elemento_pai_id if elemento_pai else ""
                            ),
                        },
                        "success": True,
                    }
                )

        return obj

    def get(self, args=[]):
        obj = None if len(args) == 0 else self._get_instance(args[0])

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QQuestaoAberta(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            model = models.QuestaoAberta
            exclude = ("content_type",)

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Enunciado",
                "sortable": True,
                "dataIndex": "enunciado",
                "key": "enunciado",
                "width": 500,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questões Abertas",
        "LIST": "Questões",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def create(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            questao = self.Form.Meta.model(
                enunciado=self.request.POST.get("enunciado"),
                mista=True if self.request.REQUEST.get("mista") == "on" else False,
            )

            questao.save()

            questionario = models.Questionario.objects.get(
                id=self.request.POST.get("questionario")
            )
            content_type = ContentType.objects.get(
                app_label="questionario", model="questaoaberta"
            )

            ordem = (
                int(
                    models.Elemento.objects.filter(
                        questionario=self.request.POST.get("questionario")
                    )
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )

            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=questao.id,
                ordem=ordem,
                label=self.request.POST.get("label"),
                # label = 'Q0'+str(ordem),
                grupo=self.request.POST.get("grupo").upper(),
                elemento_pai=elemento_pai,
            )
            element.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QQuestaoMS(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            model = models.QuestaoMS
            exclude = ("content_type",)

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Enunciado",
                "sortable": True,
                "dataIndex": "enunciado",
                "key": "enunciado",
                "width": 500,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questões de Multipla Seleção",
        "LIST": "Questões",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def create(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            questao = self.Form.Meta.model(
                enunciado=self.request.POST.get("enunciado"),
                mista=True if self.request.REQUEST.get("mista") == "on" else False,
            )

            questao.save()

            questionario = models.Questionario.objects.get(
                id=self.request.POST.get("questionario")
            )
            content_type = ContentType.objects.get(
                app_label="questionario", model="questaoms"
            )
            ordem = (
                int(
                    models.Elemento.objects.filter(
                        questionario=self.request.POST.get("questionario")
                    )
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )

            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=questao.id,
                ordem=ordem,
                label=self.request.POST.get("label"),
                # label = 'Q0'+str(ordem),
                grupo=self.request.POST.get("grupo").upper(),
                elemento_pai=elemento_pai,
            )
            element.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QQuestaoEnum(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            model = models.QuestaoEnum
            exclude = ("content_type",)

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Enunciado",
                "sortable": True,
                "dataIndex": "enunciado",
                "key": "enunciado",
                "width": 500,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questões de Multipla Seleção",
        "LIST": "Questões",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def create(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            questao = self.Form.Meta.model(
                enunciado=self.request.POST.get("enunciado"),
                mista=True if self.request.REQUEST.get("mista") == "on" else False,
                valores=self.request.POST.get("valores"),
            )

            questao.save()

            questionario = models.Questionario.objects.get(
                id=self.request.POST.get("questionario")
            )
            content_type = ContentType.objects.get(
                app_label="questionario", model="questaoenum"
            )
            ordem = (
                int(
                    models.Elemento.objects.filter(
                        questionario=self.request.POST.get("questionario")
                    )
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )
            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=questao.id,
                ordem=ordem,
                label=self.request.POST.get("label"),
                # label = 'Q0'+str(ordem),
                grupo=self.request.POST.get("grupo").upper(),
                elemento_pai=elemento_pai,
            )
            element.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _get_instance(self, pk):
        obj = {}
        try:
            q = self.Form.Meta.model.objects.get(pk=pk)
            element = models.Elemento.objects.filter(
                object_id=pk
            )  # pega ordem,label e grupo do elemento referente a questao

        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                {
                    "message": "Não consegui encontrar a questao desejada.",
                    "success": False,
                }
            )
        else:
            for el in element:
                elemento_pai = models.Elemento.objects.filter(pk=el.elemento_pai_id)
                obj.update(
                    {
                        "instance": {
                            "pk": q.pk,
                            "enunciado": q.enunciado,
                            "mista": q.mista,
                            "ordem": el.ordem,
                            "label": el.label,
                            "grupo": el.grupo,
                            "valores": q.valores,
                            "elemento_pai": (
                                "%s" % elemento_pai[0].elemento
                                if elemento_pai.count()
                                else ""
                            ),
                            "elemento_pai_id": (
                                "%s" % el.elemento_pai_id if elemento_pai else ""
                            ),
                        },
                        "success": True,
                    }
                )

        return obj

    def get(self, args=[]):
        obj = None if len(args) == 0 else self._get_instance(args[0])

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)
        try:
            questao = self.Form.Meta.model.objects.get(pk=self.request.POST.get("pk"))
            element = models.Elemento.objects.get(object_id=self.request.POST.get("pk"))
            elemento_pai = (
                models.Elemento.objects.get(pk=self.request.POST.get("elemento_pai"))
                if self.request.POST.get("elemento_pai")
                else None
            )

        except Exception as e:
            self.log.error(e)
            obj.update(message="Não consegui encontrar a questao desejada.")
        else:

            questao.enunciado = self.request.REQUEST.get("enunciado")
            questao.valores = self.request.REQUEST.get("valores")
            questao.mista = True if self.request.REQUEST.get("mista") == "on" else False
            questao.save()
            element.label = self.request.POST.get("label")
            element.grupo = self.request.POST.get("grupo")
            element.elemento_pai = elemento_pai
            element.save()

            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QAlternativa(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.Alternativa

    titles = {
        "PANEL": "Alternativas",
        "LIST": "Alternativas",
        "NEW": "Nova",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def list(self, args=[]):

        obj = {"collection": [], "count": 0}
        self.log.info(self.request.GET.get("questao"))
        questao = models.Questao.objects.get(pk=self.request.GET.get("questao"))

        for (
            alt
        ) in questao.alternativas.all():  # itera sobre as alternativas das questoes
            # print alt.texto
            obj["collection"].append(
                {
                    "pk_quest": alt.questao.id,
                    "pk": alt.id,
                    "label": alt.label,
                    "texto": alt.texto,
                    "valor": alt.valor,
                    "grupo": alt.grupo,
                }
            )
        obj.update(count=questao.alternativas.all().count())

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _get_instance(self, pk):
        obj = {}

        try:
            alt = self.Form.Meta.model.objects.get(pk=pk)
            # element = models.Elemento.objects.filter(object_id=pk) #pega ordem,label e grupo do elemento referente a questao
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                {
                    "message": "Não consegui encontrar a alternativa desejada.",
                    "success": False,
                }
            )
        else:
            obj.update(
                {
                    "instance": {
                        "pk": alt.pk,
                        "label": alt.label,
                        "texto": alt.texto,
                        "valor": alt.valor,
                        "grupo": alt.grupo,
                    },
                    "success": True,
                }
            )

        return obj

    def get(self, args=[]):
        # obj = self._get_list() if len(args) == 0 else self._get_instance(args[0])
        obj = None if len(args) == 0 else self._get_instance(args[0])

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):

        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)

        try:
            questao = models.Questao.objects.get(pk=self.request.POST.get("questao"))
            quest = self.request.POST.get("questao")

            ordem = (
                int(
                    models.Alternativa.objects.filter(questao=quest)
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            alternativa = self.Form.Meta.model(
                label=self.request.POST.get("label"),
                texto=self.request.POST.get("texto"),
                valor=self.request.POST.get("valor"),
                grupo=self.request.POST.get("grupo").upper(),
                questao=questao,
                ordem=ordem,
            )

            alternativa.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            alt = self.Form.Meta.model.objects.get(pk=self.request.POST.get("pk"))
        except Exception as e:
            self.log.error(e)
            obj.update(message="Não consegui encontrar a alternativa desejada.")
        else:

            alt.label = self.request.REQUEST.get("label")
            alt.texto = self.request.REQUEST.get("texto")
            alt.valor = self.request.REQUEST.get("valor")
            alt.grupo = self.request.REQUEST.get("grupo").upper()
            alt.save()

            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}
        # self.log.info(self.request.POST)
        try:
            alt = self.Form.Meta.model.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for alternativas in alt:
                alternativas.delete()
        except Exception as e:
            obj.update({"success": False, "message": str(e)})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def move_alternativa(self, args=[]):
        obj = self._move_up() if args[0] == "up" else self._move_down()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _move_up(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        # self.log.info(self.request.POST)
        query = models.Alternativa.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = models.Questao.objects.get(
                    pk=query.values("questao")
                    .distinct()
                    .latest("questao")
                    .get("questao")
                )
            except Exception as e:
                obj.update(message="Não consegui encontrar a alternativa.")
            else:
                q.reorder()
                for alt in query.order_by("ordem"):
                    alt.move_up()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj

    def _move_down(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        # self.log.info(self.request.POST)
        query = models.Alternativa.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = models.Questao.objects.get(
                    pk=query.values("questao")
                    .distinct()
                    .latest("questao")
                    .get("questao")
                )

            except Exception as e:
                obj.update(message="Não consegui encontrar a alternativa.")
            else:
                q.reorder()
                for alt in query.order_by("-ordem"):
                    alt.move_down()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj


class QReferenciaTextual(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.ReferenciaTextual

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Label",
                "sortable": True,
                "dataIndex": "label",
                "key": "label",
                "width": 250,
            },
            {
                "header": "Conteudo",
                "sortable": False,
                "dataIndex": "conteudo",
                "key": "conteudo",
                "width": 500,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Refências Textuais",
        "LIST": "Refêrencias",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtro",
    }

    def _get_instance(self, pk):
        obj = {}
        try:
            ref = self.Form.Meta.model.objects.get(pk=pk)
            element = models.Elemento.objects.filter(
                object_id=pk
            )  # pega ordem,label e grupo do elemento referente a REF TEXTUAL
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                {
                    "message": "Não consegui encontrar a referencia textual desejada.",
                    "success": False,
                }
            )
        else:
            # Itera sobre o elemento para setar ordem,label e grupo para uma referencia textual
            for el in element:
                ordem = el.ordem
                label = el.label
                grupo = el.grupo
            obj.update(
                {
                    "instance": {
                        "pk": ref.pk,
                        "label": ref.label,
                        "conteudo": ref.conteudo,
                        "ordem": ordem,
                        "label_elemento": label,
                        "grupo": grupo,
                    },
                    "success": True,
                }
            )

        return obj

    def get(self, args=[]):
        obj = None if len(args) == 0 else self._get_instance(args[0])

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}

        try:
            textual = self.Form.Meta.model(
                label=self.request.POST.get("label"),
                conteudo=self.request.POST.get("conteudo"),
            )

            textual.save()

            quest = self.request.POST.get("questionario")
            questionario = models.Questionario.objects.get(id=quest)
            content_type = ContentType.objects.get(
                app_label="questionario", model="referenciatextual"
            )

            ordem = (
                int(
                    models.Elemento.objects.filter(questionario=quest)
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )

            element = models.Elemento(
                questionario=questionario,
                content_type=content_type,
                object_id=textual.id,
                ordem=ordem,
                label=self.request.POST.get("label_elemento"),
                # label = 'Q0'+str(ordem),
                grupo=self.request.POST.get("grupo").upper(),
            )
            element.save()

        except Exception as e:
            self.log.error(e)
            obj.update(message="Erro! Não consegui concluir a operação.")
        else:
            obj.update(success=True)
            obj.update(message="Salvo com sucesso!.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        # self.log.info(self.request.POST)
        try:
            ref = self.Form.Meta.model.objects.get(pk=self.request.REQUEST.get("pk"))
            element = models.Elemento.objects.get(object_id=self.request.POST.get("pk"))
        except self.Form.Meta.model.DoesNotExist:
            obj.update(
                message="Não consigo encontrar a referencia textual para atualizar os valores."
            )
        else:
            ref.label = self.request.REQUEST.get("label")
            ref.conteudo = self.request.REQUEST.get("conteudo")
            ref.save()

            element.grupo = self.request.POST.get("grupo")
            element.label = self.request.REQUEST.get("label_elemento")
            element.save()

            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class QElemento(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.Elemento

    #            exclude = ('ordem',)

    titles = {
        "PANEL": "Referências do Questionários ",
        "LIST": "Referências",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filtrar",
    }

    def get_elemento_pai(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.POST)
        for el in models.Elemento.objects.filter(
            questionario=self.request.POST["pk_questionario"]
        ):
            if el.content_type.name == "referencia textual":
                obj["collection"].append({"pk": el.id, "descricao": "%s" % el.elemento})
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.GET.get("questionario"))
        query = self.Form.Meta.model.objects.filter(
            questionario=self.request.GET.get("questionario")
        )
        for eleme in query:
            # self.log.info(eleme)
            obj["collection"].append(
                {
                    "pk": eleme.elemento.id,  # pk da referencia textual ou questao
                    "pk_element": eleme.id,
                    "enunciado": eleme.elemento.label,
                    "tipo": eleme.elemento.tipo,
                }
            )
        obj.update(count=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}

        # self.log.info(self.request.POST)
        try:
            qs = self.Form.Meta.model.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for elemento in qs:
                elemento.delete()

            try:
                # Aqui faz a exclusao tambem na tabela questao ou ref textual
                if "Ref. Textual" in self.request.POST.getlist("tipo"):
                    # ref textual
                    refT = models.ReferenciaTextual.objects.filter(
                        pk__in=self.request.POST.getlist("pk2")
                    )
                    for ref in refT:
                        ref.delete()
                else:
                    # exclui alternativas da questao e a propria questao
                    q = models.Questao.objects.filter(
                        pk__in=self.request.POST.getlist("pk2")
                    )
                    alt = models.Alternativa.objects.filter(questao=q)
                    for al in alt:
                        alt.delete()
                    for questao in q:
                        q.delete()
            except Exception as e:
                self.log.error(e)
                obj.update(message="Erro! Não consegui concluir a operação.")

        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": str(e)})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def move_questao(self, args=[]):
        obj = self._move_up() if args[0] == "up" else self._move_down()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _move_up(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        query = models.Elemento.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = models.Questionario.objects.get(
                    pk=query.values("questionario")
                    .distinct()
                    .latest("questionario")
                    .get("questionario")
                )
            except Exception as e:
                self.log.error(e)
                obj.update(message="Não consegui encontrar a questão.")
            else:
                q.reorder()
                for el in query.order_by("ordem"):
                    el.move_up()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj

    def _move_down(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        # self.log.info(self.request.POST)
        query = models.Elemento.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = models.Questionario.objects.get(
                    pk=query.values("questionario")
                    .distinct()
                    .latest("questionario")
                    .get("questionario")
                )

            except Exception as e:
                obj.update(message="Não consegui encontrar a questão.")
            else:
                q.reorder()
                for el in query.order_by("-ordem"):
                    el.move_down()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj


class QQuestionarioResposta:
    class Meta:
        exclude = []
        model = models.QuestionarioResposta

    def responder(self):
        pass


class QMontarQuestionario(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.Questionario

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 40,
            },
            {
                "header": "Titulo",
                "sortable": True,
                "dataIndex": "titulo",
                "key": "titulo",
                "width": 230,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Questionário",
        "LIST": "Questionários",
        "NEW": "Novo Questionário",
        # 'EDIT': 'Editando Configuração',
        # 'DELETE': 'Removendo Configuração',
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.questionario.GerenciaQuestionario()")

    def get_resp(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        self.log.info(args)
        obj = None if len(args) == 0 else self.get_data_resposta(*args)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # def get_data_resposta(self, args=[]):
    def get_data_resposta(self, pk, servidor_pk=None):

        obj = {"collection": [], "count": 0}
        self.log.info(pk)
        self.log.info(servidor_pk)

        try:

            if servidor_pk is None:
                self.log.info("servidor_pk vazio")
                q = self.Form.Meta.model()
            else:
                q = self.Form.Meta.model.objects.get(pk=servidor_pk)

            pk_questionario = pk
            qst = models.Questionario.objects.get(pk=pk_questionario)
            chave = q.gera_chave()
            self.log.info(chave)

            try:
                qr = models.QuestionarioResposta.objects.filter(
                    models_d.Q(questionario=pk_questionario),
                    models_d.Q(
                        models_d.Q(manifestation_apd__subordinate=q)
                        | models_d.Q(evaluation_apd__subordinate=q)
                    ),
                ).order_by("id", "criado_em")
            except:
                qr = models.QuestionarioResposta.objects.filter(
                    questionario=pk_questionario, chave=chave
                ).order_by("id", "criado_em")
            for qrc in qr:
                obj["collection"].append(
                    {
                        "pk": qrc.id,
                        "titulo": qrc.questionario.titulo,
                        "data": DateUtils.date_to_str(qrc.criado_em),
                    }
                )

            obj.update(count=qr.count())
            self.log.info(obj)

        except Exception as e:
            self.log.error(e)
        else:
            return obj

    def ver_resposta(self, args=[]):
        obj = {"collection": []}
        self.log.info(self.request.GET)
        # self.log.info(self.request.POST )
        try:

            pk_quest_resposta = self.request.GET.get("pk_questionario_resposta")
            try:
                qc = models.QuestionarioResposta.objects.get(pk=pk_quest_resposta)
                data = qc.criado_em
                elementos = models.Elemento.objects.filter(
                    questionario=qc.questionario_id
                )
                for el in elementos:
                    alt_list = []
                    resp_texto = []
                    if isinstance(el.elemento, models.Questao):
                        q = models.Questao.objects.get(pk=el.elemento.id)
                        r = models.Resposta.objects.filter(
                            questao=el.elemento.id,
                            questionario_resposta=pk_quest_resposta,
                        )
                        for alt in q.alternativas.all():
                            qs = models.Resposta.objects.filter(
                                questao=el.elemento.id,
                                questionario_resposta=pk_quest_resposta,
                                alternativa=alt,
                            )
                            alt_list.append(
                                {
                                    "flag": 0 if qs.exists() else 1,
                                    "texto": alt.texto.replace("<br>", ""),
                                    "label": alt.label,
                                }
                            )
                        for resp in r:
                            if "Questão MS" in el.elemento.tipo:
                                if el.elemento.mista == True:
                                    resp_texto.append(
                                        {
                                            "texto": (
                                                resp.texto.replace("<br>", "")
                                                if not el.elemento.mista
                                                else resp.texto + "<br>"
                                            ),
                                        }
                                    )
                                    break
                                else:
                                    pass
                            else:
                                resp_texto.append(
                                    {
                                        "texto": (
                                            resp.texto.replace("<br>", "")
                                            if not el.elemento.mista
                                            else resp.texto + "<br>"
                                        ),
                                        "alternativa": (
                                            resp.alternativa.texto.replace("<br>", "")
                                            if resp.alternativa
                                            else ""
                                        ),
                                        "label": (
                                            resp.alternativa.label
                                            if resp.alternativa
                                            else ""
                                        ),
                                    }
                                )

                        obj["collection"].append(
                            {
                                "data": DateUtils.date_to_str(data),
                                "enunciado": el.label + " - " + el.elemento.enunciado,
                                "tipo": el.elemento.tipo,
                                "alternativas": alt_list or [],
                                "respostas": resp_texto or [],
                                "mista": el.elemento.mista,
                            }
                        )

                    elif isinstance(el.elemento, models.ReferenciaTextual):
                        obj["collection"].append(
                            {
                                "data": DateUtils.date_to_str(data),
                                "enunciado": el.label
                                + " - "
                                + el.elemento.label
                                + "<br>"
                                + el.elemento.conteudo,
                                "alternativas": alt_list or [],
                                "respostas": resp_texto or [],
                                "tipo": el.elemento.tipo,
                            }
                        )

            except Exception as e:
                self.log.error(e)
        except Exception as e:
            self.log.error(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_questionario(self, pk, servidor_pk=None, qtype=None):
        obj = {"collection": []}
        try:

            if servidor_pk is None:
                self.log.info("servidor_pk vazio")
                qs = self.Form.Meta.model()
            else:
                qs = self.Form.Meta.model.objects.get(pk=servidor_pk)
            questionario = models.Questionario.objects.get(pk=pk)
            elemento = questionario.elemento_set.all()

            if not questionario.ativo:
                obj["success"] = False
                obj["message"] = "Este questionário não está ativo"
                raise Exception
            chave = qs.gera_chave()
            questionario_resposta = models.QuestionarioResposta()
            log.debug(questionario_resposta)
            validateqr = qs.validate(questionario_resposta, qtype)
            log.debug(validateqr)
            if validateqr:
                obj["success"] = False
                obj["message"] = str(models.QuestionarioResposta.KeyExists())
                raise Exception

            qchave = models.QuestionarioChave()
            qchave.save_chave(questionario, chave)

            for el in elemento:
                alt_list = []
                if isinstance(el.elemento, models.Questao):

                    questao = models.Questao.objects.get(pk=el.elemento.id)
                    for alt in questao.alternativas.all():
                        alt_list.append(
                            {
                                "id": alt.id,
                                "label": alt.label,
                                "texto": alt.texto.replace("<br>", ""),
                                "valor": alt.valor,
                                "grupo": alt.grupo,
                            }
                        )

                    obj["collection"].append(
                        {
                            "id": el.elemento.id,
                            "id_questionario": el.questionario_id,
                            "enunciado": el.elemento.enunciado,
                            "tipo": el.elemento.tipo,
                            "mista": el.elemento.mista or None,
                            "label": el.label,
                            "chave": chave,
                            "alternativas": alt_list or None,
                        }
                    )

                elif isinstance(el.elemento, models.ReferenciaTextual):
                    obj["collection"].append(
                        {
                            "id": el.elemento.id,
                            "id_questionario": el.questionario_id,
                            "label": el.elemento.label,
                            "label_ele": el.label,
                            "conteudo": el.elemento.conteudo,
                            "chave": chave,
                            "tipo": el.elemento.tipo,
                        }
                    )

            if len(obj.get("collection")) == 0:
                obj["success"] = False
                obj["message"] = "Este questionário não possui questões cadastradas"
        except Exception as e:
            log.exception(e)
            obj["success"] = False
            # obj['message'] = 'Ocorreu um erro ao exibir o questionário'
        return obj

    def get(self, args=[]):
        obj = None if len(args) == 0 else self.list_questionario(*args)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def valida_enumerada(self, questao, valor, alts):
        qenum = models.QuestaoEnum.objects.get(pk=questao)
        valores = qenum.valores.split(":")
        resp = "".join(alts)
        if resp.upper() in valores or resp == "":
            return True
        else:
            return False

    def is_valid_format(self, data):
        """Valida o formato da questao multipla selecao
        Ex: se o formato esperado é: 1,2,3 etc, ou I,II,
        """
        for a, b in list(data.items()):
            c = a.split(":")
            questionario = c[2]
            questao = c[3]
            if len(c) == 5:
                aux = self.valida_enumerada(questao, c[-1], b)
                if aux:
                    return True
                else:
                    return False
            else:
                return True

    def is_valid_format_alter(self, data):
        """Valida o formato da questao multipla selecao
        Ex: se o formato esperado é: 1,2,3 etc, ou I,II,
        """
        for a, b in list(data.items()):
            c = a.split(":")
            questionario = c[2]
            questao = c[4]
            if len(c) == 6:
                aux = self.valida_enumerada(questao, c[-1], b)
                if aux:
                    return True
                else:
                    return False
            else:
                return True

    def valid_save(self, data):
        """Valida se o questionario é do tipo único e se já há uma chave salva para tal questionário
        @retorna true se ainda nao tiver a chave
        @retorna false caso o questionario seja tipo unico e a chave já tenha sido utilizada
        """
        for a, b in list(data.items()):
            c = a.split(":")
            chave = c[1]
            questionario = c[2]
            questao = c[3]

        qr = models.QuestionarioResposta()

        if not qr.validate(questionario, chave):
            raise models.QuestionarioResposta.KeyExists()

    def valid_alter(self, data):
        """Valida se o questionario é do tipo único e se já há uma chave salva para tal questionário
        @retorna true se ainda nao tiver a chave
        @retorna false caso o questionario seja tipo unico e a chave já tenha sido utilizada
        """
        for a, b in list(data.items()):
            c = a.split(":")
            chave = c[1]
            questionario = c[2]
            questao = c[4]

        qr = models.QuestionarioResposta()

        if not qr.validate(questionario, chave):
            raise models.QuestionarioResposta.KeyExists()

    def valid_active(self, data):
        for a, b in list(data.items()):
            c = a.split(":")
            questionario = c[2]
        q = models.Questionario()
        q.validate_active(questionario)

    # @transaction.commit_manually
    def create(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        data = dict(self.request.POST)
        obj["success"] = True
        try:
            if len(data) < 1:
                obj["message"] = "Preencha o formulário"
                # transaction.rollback()
                raise Exception
            self.valid_active(data)
            try:
                # self.valid_save(data)
                if self.is_valid_format(data):
                    try:
                        for x, c in list(data.items()):
                            q = x.split(":")
                        chave = q[1]
                        qst = q[2]  # id do questionario

                        quest = models.Questionario.objects.get(pk=qst)
                        # qr = models.QuestionarioResposta(chave = chave, questionario = quest,criado_em = datetime.now())
                        # qr.save()

                        qr, created = models.QuestionarioResposta.objects.get_or_create(
                            chave=chave, questionario=quest, criado_em=datetime.now()
                        )

                        for a, b in list(data.items()):
                            c = a.split(":")
                            questionario = c[2]
                            questao = c[3]

                            questao = models.Questao.objects.get(pk=questao)

                            b = list(b)
                            try:
                                int(
                                    b[-1]
                                )  # se fizer o cast do ultimo elemento pra int então nao é uma questao mista ou aberta
                                if len(b) == 1:
                                    try:
                                        # self.log.info('questao normal multipla escolha')
                                        alternativa = models.Alternativa.objects.get(
                                            pk=b[0]
                                        )
                                        # qresp = models.Resposta(
                                        #     questao = questao,
                                        #     questionario_resposta = qr,
                                        #     alternativa = alternativa,
                                        #     peso = alternativa.valor
                                        # )
                                        # qresp.save()
                                        resposta, created = (
                                            models.Resposta.objects.get_or_create(
                                                questao=questao,
                                                questionario_resposta=qr,
                                                # alternativa = alternativa,
                                                # peso = alternativa.valor
                                            )
                                        )
                                        if created:
                                            # resposta.questao = questao
                                            # resposta.questionario_resposta = qr
                                            resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.save()
                                        else:
                                            resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.save()

                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()
                                if len(b) > 1:
                                    try:
                                        # self.log.info('questao multiselect normal')
                                        for alt in b:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    alternativa=alternativa,
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()
                            except:
                                if len(b) == 2:  # questao mista tipo radio
                                    # self.log.info('radio mista')
                                    alternativa_id, texto = b
                                    try:
                                        alternativa = models.Alternativa.objects.get(
                                            pk=alternativa_id
                                        )
                                        # qresp = models.Resposta(
                                        #     questao = questao,
                                        #     questionario_resposta = qr,
                                        #     alternativa = alternativa,
                                        #     peso = alternativa.valor,
                                        #     texto = texto
                                        # )
                                        # qresp.save()
                                        resposta, created = (
                                            models.Resposta.objects.get_or_create(
                                                questao=questao,
                                                questionario_resposta=qr,
                                                alternativa=alternativa,
                                            )
                                        )
                                        if created:
                                            # resposta.questao = questao
                                            # resposta.questionario_resposta = qr
                                            # resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.texto = texto
                                            resposta.save()
                                        else:
                                            # resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.texto = texto
                                            resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()

                                elif len(b) > 2:  # questao mista tipo selectbox
                                    texto = b[-1]
                                    alts = b[:-1]
                                    # self.log.info('select mista')
                                    try:
                                        for alt in alts:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor,
                                            #     texto = texto
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    alternativa=alternativa,
                                                )
                                            )
                                            if created:
                                                # # resposta.questao = questao
                                                # # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = texto
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = texto
                                                resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()

                                elif len(b) == 1:
                                    # self.log.info('questao aberta')
                                    txt = b[0].upper()
                                    if len(c) == 5:  # se for questao enum
                                        alt = c[-1]
                                        try:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor,
                                            #     texto = txt
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    alternativa=alternativa,
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = txt
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = txt
                                                resposta.save()

                                        except Exception as e:
                                            self.log.info(e)
                                            # transaction.rollback()
                                        # else:
                                        # transaction.commit()

                                    else:
                                        # self.log.info('questão aberta')
                                        try:
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     texto = txt
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    # alternativa = alternativa,
                                                    # peso = alternativa.valor
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                resposta.texto = txt
                                                resposta.save()
                                            else:
                                                resposta.texto = txt
                                                resposta.save()
                                        except Exception as e:
                                            self.log.info(e)
                                            # transaction.rollback()
                                        # else:
                                        # transaction.commit()

                    except Exception as e:
                        self.log.info("Erro ao salvar Questionário!")
                        self.log.error(e)
                        # transaction.rollback()
                        obj.update(message="Ocorreu um erro ao salvar os dados!")
                    else:
                        # transaction.commit()
                        self.log.info("Salvo com sucesso!")
                        obj.update(data=qr.pk)
                        obj.update(message="Salvo com sucesso!.")
                        obj.update(success=True)
                else:
                    # transaction.rollback()
                    obj.update(
                        message="Atenção! Formato de resposta invalido, verifique se a resposta corresponde ao formato solicitado na questão."
                    )
            except models.QuestionarioResposta.KeyExists as e:
                # transaction.rollback()
                obj["message"] = str(e)
                obj["success"] = False
        except models.Questionario.IsActive as e:
            obj["message"] = str(e)
            # transaction.rollback()
        except Exception as e:
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def update(self, args=[]):
        obj = {"success": False, "message": "Nada aconteceu ainda"}
        data = dict(self.request.POST)
        obj["success"] = True
        # self.log.info(data)
        try:
            if len(data) < 1:
                obj["message"] = "Preencha o formulário"
                # transaction.rollback()
                raise Exception
            self.valid_active(data)
            try:
                # self.valid_alter(data)
                if self.is_valid_format_alter(data):
                    try:
                        for x, c in list(data.items()):
                            q = x.split(":")
                        chave = q[1]
                        qst = q[2]  # id do questionario
                        id_questionario_resposta = q[3]  # id_questionario_resposta
                        # self.log.info(data)

                        quest = models.Questionario.objects.get(pk=qst)
                        qr, created = models.QuestionarioResposta.objects.get_or_create(
                            id=id_questionario_resposta,
                            chave=chave,
                            questionario=quest,
                        )

                        for a, b in list(data.items()):
                            c = a.split(":")
                            questionario = c[2]
                            questao = c[4]
                            # questao = c[3]

                            questao = models.Questao.objects.get(pk=questao)

                            b = list(b)
                            try:
                                int(
                                    b[-1]
                                )  # se fizer o cast do ultimo elemento pra int então nao é uma questao mista ou aberta
                                if len(b) == 1:
                                    try:
                                        # self.log.info('questao normal multipla escolha')
                                        alternativa = models.Alternativa.objects.get(
                                            pk=b[0]
                                        )
                                        # qresp = models.Resposta(
                                        #     questao = questao,
                                        #     questionario_resposta = qr,
                                        #     alternativa = alternativa,
                                        #     peso = alternativa.valor
                                        # )
                                        # qresp.save()
                                        resposta, created = (
                                            models.Resposta.objects.get_or_create(
                                                questao=questao,
                                                questionario_resposta=qr,
                                                # alternativa = alternativa,
                                                # peso = alternativa.valor
                                            )
                                        )
                                        if created:
                                            # resposta.questao = questao
                                            # resposta.questionario_resposta = qr
                                            resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.save()
                                        else:
                                            resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.save()

                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()
                                if len(b) > 1:
                                    try:
                                        # self.log.info('questao multiselect normal')
                                        for alt in b:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    alternativa=alternativa,
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()
                            except:
                                if len(b) == 2:  # questao mista tipo radio
                                    # self.log.info('radio mista')
                                    alternativa_id, texto = b
                                    try:
                                        alternativa = models.Alternativa.objects.get(
                                            pk=alternativa_id
                                        )
                                        # qresp = models.Resposta(
                                        #     questao = questao,
                                        #     questionario_resposta = qr,
                                        #     alternativa = alternativa,
                                        #     peso = alternativa.valor,
                                        #     texto = texto
                                        # )
                                        # qresp.save()
                                        resposta, created = (
                                            models.Resposta.objects.get_or_create(
                                                questao=questao,
                                                questionario_resposta=qr,
                                            )
                                        )
                                        if created:
                                            # resposta.questao = questao
                                            # resposta.questionario_resposta = qr
                                            # resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.texto = texto
                                            resposta.alternativa = alternativa
                                            resposta.save()
                                        else:
                                            # resposta.alternativa = alternativa
                                            resposta.peso = alternativa.valor
                                            resposta.texto = texto
                                            resposta.alternativa = alternativa
                                            resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()

                                elif len(b) > 2:  # questao mista tipo selectbox
                                    texto = b[-1]
                                    alts = b[:-1]
                                    # self.log.info('select mista')
                                    try:
                                        for alt in alts:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor,
                                            #     texto = texto
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                )
                                            )
                                            if created:
                                                # # resposta.questao = questao
                                                # # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = texto
                                                resposta.alternativa = alternativa
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = texto
                                                resposta.alternativa = alternativa
                                                resposta.save()
                                    except Exception as e:
                                        self.log.info(e)
                                        # transaction.rollback()
                                    # else:
                                    # transaction.commit()

                                elif len(b) == 1:
                                    # self.log.info('questao aberta')
                                    txt = b[0].upper()
                                    if len(c) == 6:  # se for questao enum
                                        alt = c[-1]
                                        try:
                                            alternativa = (
                                                models.Alternativa.objects.get(pk=alt)
                                            )
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     alternativa = alternativa,
                                            #     peso = alternativa.valor,
                                            #     texto = txt
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    alternativa=alternativa,
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = txt
                                                resposta.save()
                                            else:
                                                # resposta.alternativa = alternativa
                                                resposta.peso = alternativa.valor
                                                resposta.texto = txt
                                                resposta.save()

                                        except Exception as e:
                                            self.log.info(e)
                                            # transaction.rollback()
                                        # else:
                                        # transaction.commit()

                                    else:
                                        # self.log.info('questão aberta')
                                        try:
                                            # qresp = models.Resposta(
                                            #     questao = questao,
                                            #     questionario_resposta = qr,
                                            #     texto = txt
                                            # )
                                            # qresp.save()
                                            resposta, created = (
                                                models.Resposta.objects.get_or_create(
                                                    questao=questao,
                                                    questionario_resposta=qr,
                                                    # alternativa = alternativa,
                                                    # peso = alternativa.valor
                                                )
                                            )
                                            if created:
                                                # resposta.questao = questao
                                                # resposta.questionario_resposta = qr
                                                resposta.texto = txt
                                                resposta.save()
                                            else:
                                                resposta.texto = txt
                                                resposta.save()
                                        except Exception as e:
                                            self.log.info(e)
                                            # transaction.rollback()
                                        # else:
                                        # transaction.commit()

                    except Exception as e:
                        self.log.info("Erro ao salvar Questionário!")
                        self.log.error(e)
                        # transaction.rollback()
                        obj.update(message="Ocorreu um erro ao salvar os dados!")
                    else:
                        # transaction.commit()
                        self.log.info("Questionario alterado com sucesso!")
                        obj.update(data=qr.pk)
                        obj.update(message="Alterado com sucesso!.")
                        obj.update(success=True)
                else:
                    # transaction.rollback()
                    obj.update(
                        message="Atenção! Formato de resposta invalido, verifique se a resposta corresponde ao formato solicitado na questão."
                    )
            except models.QuestionarioResposta.KeyExists as e:
                # transaction.rollback()
                obj["message"] = str(e)
                obj["success"] = False
        except models.Questionario.IsActive as e:
            obj["message"] = str(e)
            # transaction.rollback()
        except Exception as e:
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

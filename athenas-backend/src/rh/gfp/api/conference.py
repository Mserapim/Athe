import json as json_main

from django.db.models import Q
from datetime import datetime

from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger

from rh.gfp.models import ContraCheque as Paycheck, Evento
from rh.models import Servidor as Employee
from rh.gfp.models import FolhaTipo, Folha, FolhaEvento, ConferencePayroll
from django.core.exceptions import FieldDoesNotExist, ValidationError
from rh.gfp.tasks_conference import process_check_payroll, delete_entries_task
from engine.mq.models import Task
from django.db import transaction


log = getLogger(__name__)
json = get_json_engine()


class GFPConferenceLiquidValue(RestfulDRY):

    _model = Paycheck

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.conference.liquidvalue.Manage")')

    def model_to_dict(self, instance):
        params = super(GFPConferenceLiquidValue, self).model_to_dict(instance)

        total_liquido_lancamentos = instance.total_liquido_lancamentos
        params.update({"total_liquido_lancamentos": float(total_liquido_lancamentos)})

        return params

    def get_query(self):
        getting_params = self.get_params().get("filter", "[]")
        params_list = json_main.loads(getting_params)
        folha_id = params_list[0]["value"]

        q = self.Model.objects.filter(pensioner__isnull=True, folha__id=folha_id)
        matriculas = list(
            map(
                lambda obj: obj.servidor.matricula,
                (
                    filter(
                        lambda obj: obj.total_liquido != obj.total_liquido_lancamentos,
                        q,
                    )
                ),
            )
        )

        return q.filter(servidor__matricula__in=matriculas)


class GFPMassManagementFunds(RestfulDRY):

    _model = Evento

    full_text_index = ("titulo__icontains", "numero__icontains")

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.conference.massmanagementfunds.Manage")'
        )

    def get_new_number_display(self, event_number):
        if len(event_number) == 5:
            return "%s-%s" % (event_number[:3], event_number[3:5])
        else:
            return event_number

    def model_to_dict(self, instance):
        params = super(GFPMassManagementFunds, self).model_to_dict(instance)
        hoje = datetime.now().date()
        query = instance.configs.filter(start_validity__lte=hoje).filter(
            Q(end_validity__lte=hoje) | Q(end_validity__isnull=True)
        )
        if query.exists():
            automatico = query.first().automated
        else:
            automatico = False

        params.update(
            numero=instance.numero,
            numero_display=self.get_new_number_display(instance.numero),
            titulo=instance.titulo,
            automatico=automatico,
        )
        return params

    def get_query(self):
        folha_id = None
        getting_params = self.get_params().get("filter", "[]")
        params_list = json_main.loads(getting_params)
        q = Evento.objects.all()

        if params_list != []:
            folha_id = params_list[0]["value"]

            folhas_eventos = (
                FolhaEvento.objects.filter(folha_id=folha_id)
                .values("evento")
                .distinct()
            )
            q = Evento.objects.filter(
                pk__in=folhas_eventos.values_list("evento", flat=True)
            )

        return q

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            # Buscar um item
            try:
                inst = self.get_query().get(pk=pk)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Processo com sucesso!",
                        "instance": self.model_to_dict(inst),
                    }
                )
        else:
            # Trazer a lista de itens
            try:
                query = self.get_query()
                # Lógicas comentadas por não serem usadas nessa funcionalidadde, remover o comentário da
                # funcionalidade desejada quando for necessário modificá-la. (Jira MPMT: ATH-3056)
                # if 'filter' in self.request.GET:
                #     query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)
                rst.update(count=query.count())
                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                rst.update(
                    {
                        "collection": [self.model_to_dict(record) for record in query],
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        return rst

    @login_required("JSON")
    def delete_entries(self, *args):
        obj = {
            "success": True,
            "message": "",
        }
        payroll = Folha.objects.get(pk=self.request.POST.get("payroll_pk"))
        event = Evento.objects.get(pk=self.request.POST.get("event_pk"))

        can = self.check_permission(
            self.request.user,
            "delete",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                message="Você não tem permissão para deletar %s."
                % self.Model._meta.object_name
            )
        else:
            if payroll.status == 3:
                obj["message"] = f"A {payroll} está fechada. Procedimento cancelado."
            else:
                Task.start(
                    delete_entries_task,
                    description=f"Deletar os lançamentos da Verba {event} - Folha {payroll}",
                    user=self.request.user.id,
                    payroll_id=payroll.pk,
                    event_id=event.pk,
                )
                obj["message"] = (
                    f"Iniciando - Deletar os lançamentos: Verba {event} - Folha {payroll}"
                )
        self.response.write(json.encode(obj))


class GFPConferenceFolhaEvento(RestfulDRY):

    _model = FolhaEvento

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.conference.massmanagementfunds.folhaevento.Manage")'
        )

    def get_query(self):
        folha_id = None
        getting_params = self.get_params().get("filter", "[]")
        params_list = json_main.loads(getting_params)
        q = []

        if params_list != []:
            folha_id = params_list[0]["value"]
            try:
                evento_id = params_list[1]["value"]
            except:
                evento_id = None

            if evento_id != None:
                q = FolhaEvento.objects.filter(folha_id=folha_id, evento_id=evento_id)

        return q

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            # Buscar um item
            try:
                inst = self.get_query().get(pk=pk)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Processo com sucesso!",
                        "instance": self.model_to_dict(inst),
                    }
                )
        else:
            # Trazer a lista de itens
            try:
                query = self.get_query()
                # Lógicas comentadas por não serem usadas nessa funcionalidadde, remover o comentário da
                # funcionalidade desejada quando for necessário modificá-la. (Jira MPMT: ATH-3056)
                # if 'filter' in self.request.GET:
                #     query = self.do_filter(query)
                # if 'keyword' in self.request.GET:
                #     query = self.do_full_text_filter(query)
                # if 'sort' in self.request.GET:
                #     query = self.do_sort(query)
                rst.update(count=query.count())
                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                rst.update(
                    {
                        "collection": [self.model_to_dict(record) for record in query],
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        return rst

    def do_filter(self, query, force_filter=None):
        """Aplica o filtro na query.

        :param query: QuerySet a ser aplicada um filtro.

        :returns: QuerySet com filtro aplicado.

        Parâmetros do Request.Method
        filter deve ser uma lista de dicionários com as seguintes chaves
        filter=[{'stage':____,'property':____,'value':____},{...}]
        stage deve ser um inteiro, zero ou positivo para utilizar filter, ou negativo para utilizar exclude
        dicionários com stage iguais serão tratados com "OR",
        dicionários com stage diferentes serão tratados com "AND"
        """

        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = None
            if not force_filter:
                flist = json_main.loads(self.get_params().get("filter", "[]"))
            else:
                flist = force_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:
            # log.debug(flist)

            stages = {}
            for f in flist:
                if f["property"] != "evento":
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
            rst.append(
                {
                    "Folha": record.folha,
                    "Descrição": record.evento,
                    "Matricula": record.servidor.matricula,
                    "Nome": record.servidor.pessoa_fisica.nome,
                    "Valor da Verba": record.correct_valor,
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class GFPConferencePayroll(RestfulDRY):

    _model = ConferencePayroll

    full_text_index = (
        "created_by__matricula__icontains",
        "created_by__pessoa_fisica__nome__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(GFPConferencePayroll, self).model_to_dict(instance)

        _dict_.update(
            {
                "payroll_pendencies": float(instance.payroll_pendencies),
            },
        )
        return _dict_

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                with transaction.atomic():
                    params = self.get_params(self.request.POST, check_case=True)
                    inst = self.factoryModel(**params)

                    if self.use_full_clean:
                        inst.full_clean()

                    inst.save()
                    self.fill_instance_m2m(inst, params)
                    Task.start(
                        process_check_payroll,
                        description="Processando conferência de folha %s"
                        % inst.payroll,
                        payroll_id=inst.payroll.pk,
                        conference_id=inst.pk,
                        user=self.request.user.id,
                    )
            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
                    rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    @login_required("JSON")
    def finish(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            conference_id = self.request.POST.get("pk")
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            elif conference_id:
                conference = self.Model.objects.get(pk=conference_id)
                conference = conference.finish()
                message = "Conferência finalizada com sucesso."
                rst.update(
                    {
                        "success": True,
                        "message": message,
                    }
                )
            else:
                raise Exception("Conferência não informada.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.conference.payroll.ConferenceManage")')

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import getLogger, get_json_engine, DateUtils
from contrib.nil import nil_date
from django.db.models import Q


from rh.models import Servidor, MovimentacaoTeletrabalho
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
from rh.pvf.models import RelatorioSemestralTeletrabalho

import json


from standard.models import Item


from contrib.utils import QuerySetChain


from django.template.loader import render_to_string


from standard.models import EmailTemplate
from common.util.send_email import EmailNotification


log = getLogger(__name__)
json_engine = get_json_engine()


class GestorRelatorioSemestral(RestfulDRY):
    """
    Api para a Tela de gestão do relatorio de teletrabalho semestral.

    obs.: cuidado ao editar os property filter pois eles tambem são usado para buscar os paramentros do filtro dos periodos
    """

    _model = Servidor

    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__iexact",
    )

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """

        situacao = self.request.GET.get("situacao", "todos")
        periodo_pk = self.request.GET.get("periodo_pk", None)

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
                if "filter" in self.request.GET:
                    query = self.do_filter(query)

                periodo = self.get_periodo(periodo_pk)

                q_relatorios_servidor = RelatorioSemestralTeletrabalho.objects.filter(
                    periodo_envio=periodo
                ).values_list("employee")

                q_gestores = Servidor.objects.filter(
                    pk__in=q_relatorios_servidor
                ).exclude(pk__in=query)

                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                    q_gestores = self.do_full_text_filter(q_gestores)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)
                    q_gestores = self.do_sort(q_gestores)

                if situacao != "naoEnviado":
                    query = QuerySetChain(q_gestores, query)

                query = self.remove_projection(query)

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

        situacao = self.request.GET.get("situacao", "todos")
        periodo_pk = self.request.GET.get("periodo_pk", None)

        periodo = self.get_periodo(periodo_pk)

        q_relatorios_servidor = RelatorioSemestralTeletrabalho.objects.filter(
            periodo_envio=periodo
        ).values_list("employee")

        if q_relatorios_servidor.exists():
            q_relatorios_servidor = q_relatorios_servidor
        else:
            q_relatorios_servidor = []

        if situacao != "todos":

            if situacao == "enviado":
                query = query.filter(pk__in=q_relatorios_servidor)
            else:
                query = query.exclude(pk__in=q_relatorios_servidor)

        """ Aplica o filtro na query.

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
                flist = json.loads(self.get_params().get("filter", "[]"))
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
                stage = int(f.get("stage", 0) or 0)
                stage_list = stages.get(stage, [])
                stage_list.append(f)
                stages.update({stage: stage_list})

            query_filter = Q()

            for key in sorted(stages.keys()):
                stage_list = stages.get(key)
                fquery = None

                for part in stage_list:
                    fquery = Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))

                query_filter &= Q(fquery)

            query = query.filter(query_filter)
        return query.distinct()

    def model_to_dict(self, instance):

        rst = super(GestorRelatorioSemestral, self).model_to_dict(instance)

        lotacao_nome = ""
        if instance.get_workplace_only().exists():
            lotacao_nome = instance.get_workplace_only().first().lotacao.nome

        cod_vdf = ""
        if self.get_relatorio(instance=instance).exists():
            cod_vdf = self.get_relatorio(instance=instance).first().pk

        rst.update(
            servidor_pk=instance.pk,
            matricula=instance.matricula,
            nome=instance.pessoa_fisica.social_name,
            lotacao=lotacao_nome,
            enviado=self.get_icon(instance),
            cod_vdf=cod_vdf,
        )

        return rst

    def get_periodo(self, periodo_pk):
        if periodo_pk:
            periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.get(id=periodo_pk)
        else:
            periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()

        return periodo

    def get_relatorio(self, instance):
        periodo_pk = self.request.GET.get("periodo_pk", None)

        return RelatorioSemestralTeletrabalho.objects.filter(
            periodo_envio=periodo_pk,
            employee=instance,
        )

    def get_icon(self, instance):
        q_relatorio = self.get_relatorio(instance=instance)

        if q_relatorio.exists():
            alt = "enviado"
            title = "Enviado"
            icon = "icon-core icon-core-success"
        else:
            alt = "não enviado"
            title = "Não Enviado"
            icon = "icon-core icon-core-delete"

        return {
            "iconCls": icon,
            "title": title,
            "alt": alt,
        }

    def get_email_template(self, template_code):
        try:
            log.info(f"Buscando o Modelo de Email: {template_code}!")

            return EmailTemplate.objects.get(code=template_code)
        except EmailTemplate.DoesNotExist:
            log.error(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
            return None

    def enviar_notificacao_email(self, *args):
        obj = {
            "success": True,
            "message": "Nada Feito",
        }

        try:
            gestor_pk = self.request.POST.get("gestor_pk")
            periodo_pk = self.request.POST.get("periodo_pk")

            gestor = Servidor.objects.get(pk=gestor_pk)
            email_template_code = "RELATORIO_SEMESTRAL_TELETRABALHO_NOTIFICACAO"

            email_template = self.get_email_template(email_template_code)

            periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.get(pk=periodo_pk)
            data_inicio = periodo.data_inicio_periodo_envio.strftime("%d/%m/%Y")
            data_fim = periodo.data_fim_periodo_envio.strftime("%d/%m/%Y")

            email_to = (
                gestor.user.email if gestor.user.email else gestor.pessoa_fisica.email
            )

            config_email_item = Item.objects.get(
                key="notificacao_semestral_teletrabalho"
            )

            lista_email = config_email_item.value.split(",")

            destinatarios = [
                {
                    "email": email_to,
                    "nome": gestor.pessoa_fisica.social_name,
                    "idUsuario": gestor.id_usuario_mastiff,
                }
            ]

            for email in lista_email:
                destinatarios.append(
                    {
                        "email": email,
                        "nome": email.split("@")[0],
                    }
                )

            message = (
                email_template.contents.replace(
                    "@nome_gestor", gestor.pessoa_fisica.social_name
                )
                .replace(
                    "@mes_inicio", periodo.data_inicio_periodo_analisado.split("/")[0]
                )
                .replace("@mes_final", periodo.data_fim_periodo_analisado.split("/")[0])
                .replace("@ano", periodo.data_fim_periodo_analisado.split("/")[1])
                .replace("@dia_inicio", data_inicio)
                .replace("@dia_fim", data_fim)
            )
            html_content = render_to_string(
                "util/template_email.html", {"message": message}
            )

            log.info(
                f">>> Enviando email para: {gestor.pessoa_fisica.social_name}, email: {email_to}"
            )
            EmailNotification().send_email_default(
                destinatarios, email_template.subject, html_content
            )

            obj["message"] = (
                f" Notificação enviada para {gestor.pessoa_fisica.social_name} !"
            )

        except Exception as error:
            log.error(error)
            obj["success"] = False
            obj["message"] = "Erro ao tentar Enviar a Notificação por Email."

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def json(self, args=[]):

        periodos = [
            {
                "id": x.id,
                "label": x.titulo,
                "data_inicio_analisado": nil_date(
                    x.data_inicio_periodo_analisado_completa, None
                ),
                "data_fim_analisado": nil_date(
                    x.data_fim_periodo_analisado_completa, None
                ),
            }
            for x in ConfigPeriodoEnvioRelatoriosSemestrais.objects.all()
        ]

        params = {"lista_periodos": periodos}

        self.response["content-type"] = "text/javascript"
        self.response.write(
            f"Ext._create('rh.teletrabalho.gestor_relatorio_semestral.Manage', {params})"
        )


class ServidorRelatorioSemestral(RestfulDRY):

    _model = MovimentacaoTeletrabalho

    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__iexact",
    )

    def model_to_dict(self, instance):
        rst = super(ServidorRelatorioSemestral, self).model_to_dict(instance)

        servidor = instance.servidor

        lotacao_nome = "Sem titularidade ativa"
        if servidor.get_workplace_only().exists():
            lotacao_nome = servidor.get_workplace_only().first().lotacao.nome

        rst.update(
            servidor_pk=instance.servidor.pk,
            matricula=servidor.matricula,
            nome=servidor.pessoa_fisica.social_name,
            lotacao=lotacao_nome,
            tipo=servidor.get_type_by_possession_display(),
            data_inicio=(
                DateUtils.date_to_str(instance.data_inicio)
                if instance.data_inicio
                else ""
            ),
            data_fim=(
                DateUtils.date_to_str(instance.data_fim) if instance.data_fim else ""
            ),
        )

        return rst

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.teletrabalho.gestor_relatorio_semestral.servidor.Manage")'
        )

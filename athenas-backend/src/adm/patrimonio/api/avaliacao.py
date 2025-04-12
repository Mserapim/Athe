# -*- coding: utf-8 -*-
from adm.patrimonio.models import (
    Avaliacao,
    AvaliacaoItem,
    Especie,
    GrupoEspecie,
    ItemAvaliacao,
    ParametroAvaliacao,
    TabelaAvaliacao,
)
from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk, nil_unicode
from contrib.utils import DateUtils, getLogger
from django.db import transaction
from rh.models import Publicacao

log = getLogger(__name__)


class PATItemAvaliacao(Restful):

    _model = AvaliacaoItem

    full_text_index = ("patrimonio__plaqueta__icontains",)

    def undo(self, args=[]):
        rst = {"message": "nada foi feito até o momento", "success": False}

        with transaction.atomic():
            try:
                for ia in self.Model.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    ia.undo(self.request.POST.get("justify"))
            except Exception as e:
                rst.update(message=str(e))
            else:
                rst.update(message="Desfeito com sucesso.", success=True)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for name in (
            "valor_atual",
            "valor_avaliado",
            "residual",
            "depreciacao",
            "taxa_pro_rata",
        ):
            if name in params and params.get(name) == "":
                params.pop(name)

        for related_name in ("avaliacao", "patrimonio"):
            if related_name in params:
                if params.get(related_name) != "":
                    field = getattr(self.Model, related_name)

                    # mater compatibilidade com django-1.4.x
                    get_queryset = field.get_queryset
                    query = get_queryset()

                    try:
                        params.update(
                            {related_name: query.get(pk=params.get(related_name))}
                        )
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({related_name: None})

        if "discarded_justify" in params:
            params.pop("discarded_justify")

        return params

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            icons=instance.icons,
            patrimonio=nil_pk(instance.patrimonio, None),
            patrimonio_unicode=nil_unicode(instance.patrimonio, None),
            plaqueta=instance.patrimonio.plaqueta,
            especie=nil_pk(instance.patrimonio.item_entrada.especie, None),
            especie_unicode=nil_unicode(instance.patrimonio.item_entrada.especie, None),
            conservacao=instance.conservacao,
            conservacao_display=nil_display(instance, "conservacao", None),
            valor_atual=float(instance.valor_atual or 0),
            valor_avaliado=float(instance.valor_avaliado or 0),
            residual=float(instance.residual or 0),
            depreciacao=float(instance.depreciacao or 0),
            quantidade_dias=int(instance.quantidade_dias or 0),
            vida_util=(
                int(instance.vida_util) if instance.vida_util is not None else None
            ),
            data_tombo=nil_datetime(instance.patrimonio.data_tombo, None),
            custo_aquisicao=float(instance.patrimonio.item_entrada.valor_unitario or 0),
            discarded=instance.discarded,
            discarded_justify=instance.discarded_justify,
            discarded_at=nil_datetime(instance.discarded_at, None),
            discarded_by=nil_pk(instance.discarded_by, None),
            discarded_by_unicode=nil_unicode(instance.discarded_by, None),
        )

        return params


class PATAvaliacao(Restful):

    _model = Avaliacao

    full_text_index = ("itens__patrimonio__plaqueta__icontains",)

    def analize(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            from engine.mq.models import Task
            from adm.patrimonio.tasks import avaliation_analise

            avaliacao = Avaliacao.objects.get(pk=args[0])
        except Avaliacao.DoesNotExist:
            rst.update(message="Avaliação requisitada não foi encontrada.")
        except ImportError:
            rst = self.local_analize()
        else:
            Task.start(avaliation_analise, avaliation=avaliacao.pk)
            rst.update(
                success=True, message="Pedido de analise de avalição solicitado."
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def local_analize(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            avaliacao = Avaliacao.objects.get(pk=args[0])
            avaliacao.analize(execute=False)
        except Avaliacao.DoesNotExist:
            rst.update(message="Não consegui encontrar a avaliação desejada.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Avaliação executada com sucesso.")

        return rst

    def execute(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}

        try:
            from engine.mq.models import Task
            from adm.patrimonio.tasks import avaliation_execute

            avaliacao = Avaliacao.objects.get(pk=args[0])
        except Avaliacao.DoesNotExist:
            rst.update(message="Avaliação requisitada não foi encontrada.")
        except ImportError:
            rst = self.local_execute()
        else:
            Task.start(
                avaliation_execute,
                username=self.request.user.username,
                avaliation=avaliacao.pk,
            )

            rst.update(
                success=True, message="Pedido de execução de avalição solicitado."
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def local_execute(self, args=[]):
        rst = {"success": False, "message": "Não foi executado nada ainda."}

        try:
            inst = self.Model.objects.get(pk=args[0])
            inst.analize(True)
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar o item desejado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        return rst

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.avaliacao.Manage")')

    def get_params(self, querydict=None, **kargs):
        params = super(PATAvaliacao, self).get_params(querydict, **kargs)

        if "de" in params:
            try:
                params.update(de=DateUtils.str_to_datetime(params.get("de")))
            except Exception:
                del params["de"]

        if "ate" in params:
            try:
                params.update(ate=DateUtils.str_to_datetime(params.get("ate")))
            except Exception:
                del params["ate"]

        return params

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            icons=instance.icons,
            tabela=nil_pk(instance.tabela, None),
            tabela_unicode=nil_unicode(instance.tabela, None),
            tipo=instance.tipo,
            tipo_display=instance.get_tipo_display(),
            competencia="{mes:0>2}/{ano}".format(**vars(instance)),
            number_formated="{numero:0>5}/{ano}".format(**vars(instance)),
            numero=instance.numero,
            mes=instance.mes,
            ano=instance.ano,
            executor=nil_pk(instance.executor, None),
            executor_unicode=nil_unicode(instance.executor, None),
            de=nil_datetime(instance.de, None),
            ate=nil_datetime(instance.ate, None),
        )

        return params


class PATItemTabelaAvaliacao(Restful):

    _model = ItemAvaliacao

    full_text_index = ("especie__titulo__icontains",)

    def get_entity_data(self, params, model, field, default=None):
        if field in params:
            try:
                dado = model.objects.get(pk=params.get(field))
            except model.DoesNotExist:
                dado = default
            except Exception as e:
                log.exception(e)
                dado = default
            finally:
                return dado
        else:
            return default

    def get_params(self, querydict=None, **kargs):
        params = super(PATItemTabelaAvaliacao, self).get_params(querydict, **kargs)

        if "especie" in params:
            params.update(especie=self.get_entity_data(params, Especie, "especie"))

        if "tabela" in params:
            params.update(
                tabela=self.get_entity_data(params, TabelaAvaliacao, "tabela")
            )

        if "grupo" in params:
            params.update(grupo=self.get_entity_data(params, GrupoEspecie, "grupo"))

        return params

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        def nil_unicode(x, v):
            return str(x) if x else v

        def nil_pk(x, v):
            return x.pk if x else v

        params.update(
            tabela=nil_pk(instance.tabela, None),
            tabela_unicode=nil_unicode(instance.tabela, None),
            grupo=nil_pk(instance.grupo, None),
            grupo_unicode=nil_unicode(instance.grupo, None),
            especie=nil_pk(instance.especie, None),
            especie_unicode=nil_unicode(instance.especie, None),
            vida_util=int(instance.vida_util or 0),
            depreciacao=float(instance.depreciacao or 0),
            residual=float(instance.residual or 0),
            tipo=(1 if instance.especie is None else 2),
        )

        return params


class PATParametroAvaliacao(Restful):

    _model = ParametroAvaliacao

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            valor=instance.valor,
            variavel=instance.variavel,
            variavel_display=instance.get_variavel_display(),
            tipo=instance.tipo,
        )

        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATParametroAvaliacao, self).get_params(querydict, **kargs)

        if "tabela" in params:
            params.update(tabela=TabelaAvaliacao.objects.get(pk=params.get("tabela")))
        else:
            params.update(tabela=None)

        return params


class PATTabelaAvaliacao(Restful):

    _model = TabelaAvaliacao

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        def nil_unicode(x, v):
            return str(x) if x else v

        def nil_pk(x, v):
            return x.pk if x else v

        def nil_date(x, v):
            return DateUtils.date_to_str(x) if x else v

        params.update(
            numero=instance.numero,
            ano=instance.ano,
            numero_formatado=instance.number_display(),
            publicacao=nil_pk(instance.publicacao, None),
            publicacao_unicode=nil_unicode(instance.publicacao, "Sem publicação ainda"),
            data_vigencia=nil_date(instance.data_vigencia, None),
            data_fim_vigencia=nil_date(instance.data_fim_vigencia, None),
        )

        return params

    def get_params(self, querydict=None, **kargs):
        params = super(PATTabelaAvaliacao, self).get_params(querydict, **kargs)

        if "publicacao" in params:
            try:
                params.update(
                    publicacao=Publicacao.objects.get(pk=params.get("publicacao", None))
                )
            except Exception:
                params.update(publicacao=None)

        if params.get("data_vigencia", "") not in ("", None):
            params.update(
                data_vigencia=DateUtils.str_to_date(params.get("data_vigencia"))
            )
        elif params.get("data_vigencia", None) == "":
            params.update(data_vigencia=None)

        return params

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.avaliacao.TabelaManage")')

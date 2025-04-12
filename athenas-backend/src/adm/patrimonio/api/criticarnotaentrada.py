# -*- coding: utf-8 -*-
from adm.patrimonio.models import CriticarNotaEntrada
from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk, nil_unicode
from contrib.utils import DateUtils, getLogger, person_from_user

log = getLogger(__name__)


class PATCriticarNotaEntrada(Restful):

    _model = CriticarNotaEntrada

    def change_state(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            obj = self.Model.objects.get(pk=self.request.POST.get("pk"))
            obj.change_state(
                int(self.request.POST.get("state") or 0),
                self.request.POST.get("justify"),
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Sucesso!")

        renderer = self.get_renderer("text/json")
        renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "empenho" in params:
            if params.get("empenho") != "":
                field = getattr(self.Model, "empenho")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(empenho=query.get(pk=params.get("empenho")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(empenho=None)

        if "conta" in params:
            if params.get("conta") != "":
                field = getattr(self.Model, "conta")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(conta=query.get(pk=params.get("conta")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(conta=None)

        if "respondido_quando" in params:
            if params.get("respondido_quando") != "":
                params.update(
                    respondido_quando=DateUtils.str_to_date(
                        params.get("respondido_quando")
                    )
                )
            else:
                params.update(respondido_quando=None)

        if "quando" in params:
            if params.get("quando") != "":
                params.update(quando=DateUtils.str_to_date(params.get("quando")))
            else:
                params.update(quando=None)

        if "por" in params:
            if params.get("por") != "":
                field = getattr(self.Model, "por")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(por=query.get(pk=params.get("por")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(por=None)

        if "data_compra" in params:
            if params.get("data_compra") != "":
                params.update(
                    data_compra=DateUtils.str_to_date(params.get("data_compra"))
                )
            else:
                params.update(data_compra=None)

        if "fornecedor" in params:
            if params.get("fornecedor") != "":
                field = getattr(self.Model, "fornecedor")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(fornecedor=query.get(pk=params.get("fornecedor")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(fornecedor=None)

        if "nota" in params:
            if params.get("nota") != "":
                field = getattr(self.Model, "nota")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(nota=query.get(pk=params.get("nota")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(nota=None)

        if "data_nota" in params:
            if params.get("data_nota") != "":
                params.update(data_nota=DateUtils.str_to_date(params.get("data_nota")))
            else:
                params.update(data_nota=None)

        if "respondido_por" in params:
            if params.get("respondido_por") != "":
                field = getattr(self.Model, "respondido_por")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        respondido_por=query.get(pk=params.get("respondido_por"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(respondido_por=None)

        if "execucao_orcamentaria" in params:
            if params.get("execucao_orcamentaria") != "":
                params.update(
                    execucao_orcamentaria=int(params.get("execucao_orcamentaria") or 0)
                )
            else:
                params.update(execucao_orcamentaria=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        def get_pessoa_from_user(user):
            if not user:
                return "Ninguem"
            if person_from_user(user):
                return str(person_from_user(user))
            else:
                return str(user)

        rst.update(
            execucao_orcamentaria=instance.execucao_orcamentaria,
            execucao_orcamentaria_display=nil_display(
                instance, "execucao_orcamentaria", None
            ),
            empenho=nil_pk(instance.empenho, None),
            empenho_unicode=nil_unicode(instance.empenho, None),
            conta=nil_pk(instance.conta, None),
            conta_unicode=nil_unicode(instance.conta, None),
            respondido_quando=nil_datetime(instance.respondido_quando, None),
            quando=nil_datetime(instance.quando, None),
            por=nil_pk(instance.por, None),
            por_unicode=get_pessoa_from_user(instance.por),
            data_compra=nil_datetime(instance.data_compra, None),
            fornecedor=nil_pk(instance.fornecedor, None),
            fornecedor_unicode=nil_unicode(instance.fornecedor, None),
            state=instance.state,
            state_display=nil_display(instance, "state", None),
            nota=nil_pk(instance.nota, None),
            nota_unicode=nil_unicode(instance.nota, None),
            data_nota=nil_datetime(instance.data_nota, None),
            respondido_por=nil_pk(instance.respondido_por, None),
            respondido_por_unicode=get_pessoa_from_user(instance.respondido_por),
            processo=instance.processo,
            descricao=instance.descricao,
        )

        return rst

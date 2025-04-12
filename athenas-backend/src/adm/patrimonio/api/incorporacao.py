# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q
from django.template.defaultfilters import striptags

from adm.patrimonio.models import Patrimonio
from contrib.newrest import Restful
from contrib.utils import DateUtils, employee_from_user
from rh.models import Servidor


class PATPatrimonio(Restful):

    _model = Patrimonio

    full_text_index = (
        "plaqueta__icontains",
        "descricao__icontains",
        "responsavel__matricula__icontains",
        "responsavel__pessoa_fisica__nome__icontains",
        "localizacao__path_cache__icontains",
    )

    can_update_fields_values = ("utilizacao", "utilizado_por")

    def save_observation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        self.get_query().filter(pk=args[0]).update(
            observacao=self.request.POST.get("conteudo")
        )

        rst.update(success=True, message="Observação salva com sucesso.")
        self.renderer(rst)

    def get_params(self, querydict=None, **kargs):
        params = super(PATPatrimonio, self).get_params(querydict, **kargs)

        if params.get("utilizado_por", "") != "":
            params.update(
                utilizado_por=Servidor.objects.get(pk=params.get("utilizado_por"))
            )
        else:
            params.update(utilizado_por=None)

        return params

    def change_consevation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                for pat in self.get_query().filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    pat.change_consevation(self.request.POST.get("conservation"))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Patrimonios alterados com sucesso.")

        self.renderer(rst)

    def model_to_dict(self, instance):
        _dict_ = super(PATPatrimonio, self).model_to_dict(instance)

        def nil_unicode(x, v):
            return str(x) if x is not None else v

        def nil_pk(x, v):
            return x.pk if x is not None else v

        def nil_baixa_pk(x):
            return (
                x.baixas.get(nota__state=2).nota.pk
                if x.baixas.filter(nota__state=2).exists()
                else None
            )

        def nil_baixa_cache_type(x):
            return (
                x.baixas.get(nota__state=2).nota.cache_type
                if x.baixas.filter(nota__state=2).exists()
                else None
            )

        nota_fiscal = getattr(instance.item_entrada.nota, "notafiscal", None)

        _dict_.update(
            {
                "icons": instance.icons,
                "plaqueta_unicode": instance.plaqueta,
                "plaqueta": instance.plaqueta,
                "especie": instance.item_entrada.especie.pk,
                "especie_unicode": str(instance.item_entrada.especie.titulo),
                "especie_codigo": instance.item_entrada.especie.codigo_cache,
                "localizacao": nil_pk(instance.localizacao, None),
                "localizacao_unicode": (
                    instance.localizacao.path
                    if instance.localizacao
                    else "Sem localização"
                ),
                "responsavel": nil_pk(instance.responsavel, None),
                "responsavel_unicode": nil_unicode(
                    instance.responsavel, "Sem responsavel"
                ),
                "utilizado_por": nil_pk(instance.utilizado_por, None),
                "utilizado_por_unicode": nil_unicode(
                    instance.utilizado_por, "Sem utilizador"
                ),
                "conservacao": instance.conservacao,
                "conservacao_display": instance.get_conservacao_display(),
                "utilizacao": instance.utilizacao,
                "utilizacao_display": instance.get_utilizacao_display(),
                "descricao": striptags(instance.descricao),
                "observacao": instance.observacao,
                "prazo_garantia": DateUtils.date_to_str(instance.prazo_garantia),
                "data_baixa": (
                    DateUtils.date_to_str(instance.data_baixa)
                    if instance.data_baixa is not None
                    else None
                ),
                "data_tombo": (
                    DateUtils.date_to_str(instance.data_tombo)
                    if instance.data_tombo is not None
                    else None
                ),
                "valor_atual": float(instance.valor_atual or 0),
                "valor_aquisicao": float(instance.item_entrada.valor_unitario or 0),
                "valor_base": float(instance.valor_base or 0),
                # float(instance.item_entrada.valor_unitario) - float(instance.valor_atual or 0),
                "depreciado": float(instance.get_total_depreciado()),
                "total_reavaliacao": float(instance.get_total_reavaliado()),
                "nota_entrada": instance.item_entrada.nota.pk,
                "nota_entrada_cache_type": instance.item_entrada.nota.cache_type,
                "nota_baixa": nil_baixa_pk(instance),
                "numero_nota_fiscal": nota_fiscal.numero if nota_fiscal else None,
                "fornecedor": instance.item_entrada.nota.provider_name,
                "processo": (
                    instance.item_entrada.nota.processo
                    if instance.item_entrada.nota.processo
                    else None
                ),
                "nota_baixa_cache_type": nil_baixa_cache_type(instance),
                "read_only": instance.is_read_only(self.request.user),
                "status_baixa": nil_unicode(instance.downloaded, ""),
            }
        )

        return _dict_

    def get_query(self):
        query = super(PATPatrimonio, self).get_query()

        if not self.request.user.has_perm(
            "patrimonio.admin"
        ) and not self.request.user.has_perm("patrimonio.control"):
            servidor = employee_from_user(self.request.user)
            query = query.filter(Q(responsavel=servidor))

        return query

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            patrimony = self.get_query().get(pk=args[0])

            rst.update(
                success=True, document={"content": patrimony.rendered, "appends": []}
            )
        except self._model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

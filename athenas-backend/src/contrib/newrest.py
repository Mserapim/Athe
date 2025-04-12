# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes que implementam REST.

:Classes:
  :class:`Restful`,
  :class:`RestfulTree`

"""

import json
import uuid
from decimal import Decimal

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import ForeignKey, OneToOneField, ProtectedError, Q
from django.http import QueryDict
from django.conf import settings

from contrib.extjs import ExtWidget
from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class Restful(ExtWidget):
    """
    **Classe** para implementação da REST (Transferência de Estado Representativo).

    :Métodos:
        :func:`factoryModel`,
        :func:`renderer_as_xml`,
        :func:`renderer_as_yaml`,
        :func:`renderer_as_json`,
        :func:`get_query`,
        :func:`do_filter`,
        :func:`do_full_text_filter`,
        :func:`do_sort`,
        :func:`do_page`,
        :func:`model_to_dict`,
        :func:`do_get`,
        :func:`_force_case`,
        :func:`get_params`,
        :func:`do_post`,
        :func:`do_delete_single`,
        :func:`do_delete_multi`,
        :func:`do_put`,
        :func:`do_put_multi`,
        :func:`fill_instance_values`,
        :func:`fill_instance_m2m`,
        :func:`do_put_single`,
        :func:`get_renderer`,
        :func:`get_method`,
        :func:`v1`.
    """

    """
    Chama o validador de modelo.
    """
    use_full_clean = True

    can_update_fields_values = None

    """ Classe do modelo representado pelo recurso."""
    _model = None

    """ Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas."""
    full_text_index = ()

    """ Força o tratamento de todos os dados vindos do browser em uppercase."""
    force_upper = True

    """ Em caso de delete ou update multi row força utilizar o ORM para realizar as ações."""
    force_orm_single = False

    primary_key = "pk"

    page_size = 30

    def count(self, args=[]):
        rst = {"success": False, "collection": []}

        try:
            rules = json.loads(self.request.GET.get("rules"))
            data = []
            seq = 0

            for name, rule in list(rules.items()):
                query = self.do_filter(self.get_query(), rule)
                seq += 1

                data.append({"id": seq, "name": name, "count": query.count()})

            rst.update(collection=data, success=True)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def get_item_as_list(self, params, item, default=[]):
        if item in params:
            rst = None
            if isinstance(params.get(item), (list, tuple)) is False:
                rst = [params.get(item)]
            else:
                rst = params.get(item)
        else:
            rst = default

        return rst

    @property
    def Model(self):
        if self._model is not None:
            return self._model
        else:
            raise NotImplementedError("The model not specified!")

    def factoryModel(self, *args, **kargs):
        """Cria uma instância de Model.

        :param *args: Argumentos posicionais arbitrários para um Model com construtor.

        :param **kargs: Argumentos nomeados com os atributos do Model.

        :returns: Uma instância de Model.
        """
        fields = [f.name for f in self.Model._meta.fields] + getattr(
            self.Model, "extraFields", []
        )

        for key, value in list(kargs.items()):
            if key not in fields or isinstance(value, (tuple, list, set)):
                del kargs[key]

        return self.Model(*args, **kargs)

    def renderer_as_xml(self, obj):
        pass

    def renderer_as_yaml(self, obj):
        pass

    def _render_as_csv_split_row(self, row):
        rst = []
        for col in list(row.values()):
            try:
                rst.append(('"%s"' % col) if isinstance(col, str) else str(col))
            except Exception:
                rst.append('"ERROR"')
        return rst

    def renderer_as_csv(self, obj):
        if isinstance(obj, (tuple, set, list)) is True:
            self.response["Content-Type"] = "text/csv"

            if len(obj) > 0:
                row = obj[0]
                self.response.write(";".join(list(row.keys())))
                self.response.write("\n")
                for row in obj:
                    try:
                        self.response.write(
                            ";".join(self._render_as_csv_split_row(row))
                        )
                    except Exception:
                        log.error(row)
                    finally:
                        self.response.write("\n")
            else:
                self.response.write("Sem resultado")
        else:
            self.response.status_code = 406
            self.response.write("this format not suported for this method.")

    def renderer_as_json(self, obj):
        indent = None

        if "HTTP_JSINDENT" in self.request.META:
            indent = int(self.request.META.get("HTTP_JSINDENT", 4) or 0)
        else:
            indent = None

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(obj, indent=indent))

    def get_query(self):
        """:returns: QuerySet com todas instâncias de Model."""
        return self.Model.objects.filter()

    def _filter_eval_value(self, value):
        try:
            if isinstance(value, str) and value.lower() in ["off", "false"]:
                value = False
            elif isinstance(value, str) and value.lower() in ["on", "true"]:
                value = True
        except Exception as e:
            log.exception(e)

        return value

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

    def do_full_text_filter(self, query):
        """Realiza pesquisa com valor de keyword do Request nos campos adicionados em full_text_index.

        :param query: QuerySet a ser aplicada o filtro com keyword.

        :returns: QuerySet com filtro aplicado.
        """

        if self.full_text_index:
            qf = None

            for index in self.full_text_index:
                q = Q(**{index: self.request.GET.get("keyword")})
                qf = q if qf is None else Q(qf | q)

            query = query.filter(qf)

        return query

    def _sort_prepere(self, sort_info):
        return "%s%s" % (
            ("-" if sort_info.get("direction", "ASC") == "DESC" else ""),
            (self._sort_prepare_name(sort_info.get("property"))),
        )

    def _sort_prepare_name(self, name):
        return getattr(self, "_sort_map", {}).get(name, name)

    def do_sort(self, query):
        try:
            slist = json.loads(self.get_params().get("sort", "[]"))
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:
            log.debug(slist)
            sort = []
            for s in slist:
                sort.append(self._sort_prepere(s))

        return query.order_by(*sort)

    def do_page(self, query):
        start = int(self.request.GET.get("start", 0))
        end = start + int(self.request.GET.get("limit", self.page_size))
        return query[start:end]

    def model_to_dict(self, instance):
        """Cria um dicionário com atributos de uma instância.

        :param instance: Instância de Model.

        :returns: Dicionário com indices pk e unicode da instância.

        Este método deve ser sobrescrito para adicionar os demais atributos de uma determinada instância.
        Os valores dos atributos devem ser convertidos neste método para um formato serializável se necessário.
        """
        try:
            return {
                "pk": instance.pk,
                "unicode": str(instance),
            }
        except Exception:
            return {
                "pk": instance.pk,
                "unicode": "Instance of %d with error" % instance.pk,
            }

    def export(self, args=[]):
        rst = []

        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = [self.model_to_dict(record) for record in query]

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    def remove_projection(self, query):
        """Este método deve ser sobrescrito para remover valores repetidos no self._model.

        Args:
            query (queryset):

        Returns:
            queryset: default é query
        """
        return query

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
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

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

    def _force_case(self, value):
        """Modifica os dados para uppercase de acordo com atributo 'force_upper'"""
        if isinstance(value, (tuple, list, set)):
            uvalue = [v.upper() for v in value]
            return uvalue
        else:
            return value.upper() if self.force_upper else value

    def get_params(self, querydict=None, check_case=False):
        """Recebe os parâmetros do browser como uma QueryDict e converte para um dicionário.

        :param querydict: QueryDict.

        :param check_case: Define se verifica o atributo 'force_upper' para conversão em uppercase.

        Este método deve ser sobrescrito para converter os parâmetros para um formato serializável se necessário.
        """
        _dict_ = {}

        querydict = (
            querydict
            if querydict is not None
            else getattr(self.request, self.request.method, QueryDict("", False))
        )

        for key in querydict:
            value = querydict.getlist(key)
            if len(value) > 1:
                _dict_.update({key: self._force_case(value) if check_case else value})
            else:
                value = querydict.get(key)
                _dict_.update({key: self._force_case(value) if check_case else value})

        return _dict_

    def check_permission(self, user, action, app_label, object_name):
        perm = "%(app_label)s.%(action)s_%(object_name)s" % vars()
        perm = perm.lower()

        log.info("check %s permission for %s" % (perm, user))
        if user.has_perm(perm) is True:
            log.info("user %s has permission %s" % (user, perm))
            return True
        else:
            log.warn("permission %s dained for %s" % (perm, user))
            return False

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
                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)

                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
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

    def get_instance_model(self, pk):
        """Este método retorna a instância de pk.

        Args:
            pk (int)
        """
        return self.Model.objects.get(pk=pk)

    def do_delete_single(self, pk):
        """Remove uma instância.

        :param pk: Chave primária de uma instância.
        :type pk: Integer
        """
        rst = {"success": False}

        try:
            inst = self.get_instance_model(pk)
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado para remoção.")
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            try:
                inst.delete()
            except ProtectedError:
                rst.update(
                    message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update({"message": "Removido com sucesso!", "success": True})

        return rst

    def do_delete_multi(self):
        """Remove múltiplas instâncias."""
        rst = {"success": False}

        try:
            query = self.do_filter(self.get_query())
            rst.update(count=query.count())

            with transaction.atomic():
                if (
                    self.force_orm_single is False
                    and getattr(self, "force_orm_delete_single", False) is False
                ):
                    query.delete()
                else:
                    [obj.delete() for obj in query]
        except ProtectedError:
            rst.update(
                message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update({"success": True, "message": "Dados removidos com sucesso."})

        return rst

    def do_delete(self, pk=None):
        """Executa uma requisição DELETE."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "delete",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para remover %s."
                % self.Model._meta.object_name
            )
        else:
            rst.update(
                self.do_delete_multi()
                if "filter" in self.request.DELETE
                else self.do_delete_single(pk)
            )

        return rst

    def do_put(self, pk=None):
        """Executa uma requisição PUT.

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

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
        else:
            rst.update(
                self.do_put_multi()
                if "filter" in self.request.PUT
                else self.do_put_single(pk)
            )

        return rst

    def do_put_multi(self):
        """Atualiza múltiplas instâncias."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            query = self.do_filter(self.get_query())
            rst.update(count=query.count())
            params = self.get_params(self.request.PUT, check_case=True)

            if "filter" in params:
                del params["filter"]

            if self.can_update_fields_values is not None:
                params = {
                    k: v
                    for k, v in list(params.items())
                    if k in self.can_update_fields_values
                }

            if not getattr(self, "force_orm_single", False) and not getattr(
                self, "force_orm_update_single", False
            ):
                log.info("restful not in single mode")

                with transaction.atomic():
                    query.update(**params)
            else:
                log.info("restful in single mode")

                with transaction.atomic():
                    for obj in query:
                        self.fill_instance_values(obj, params)
                        if self.use_full_clean:
                            obj.full_clean()
                        obj.save()
                        self.fill_instance_m2m(obj, params)

        except ValidationError as e:
            rst.update(
                errors=[
                    {"field": key, "values": value}
                    for key, value in e.message_dict.items()
                ],
                message="Alguns campos não foram preenchidos corretamente.",
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update({"success": True, "message": "Dados atualizados com sucesso."})

        return rst

    def fill_instance_values(self, instance, values):
        """Preenche os atributos de uma instância.

        :param instance: Instância.

        :param values: Dicionário com nome e valor dos atributos.
        """
        fields = [
            f.name
            for f in instance._meta.get_fields()
            if not f.is_relation or isinstance(f, (ForeignKey, OneToOneField))
        ]
        fields += getattr(self.Model, "extraFields", [])

        for key, value in list(values.items()):
            if key in fields and isinstance(value, (tuple, list, set)) is False:
                log.info([key, "->", value])
                setattr(instance, key, value)

    def _all_fields_many_to_many_rel(self, instance):
        for field in instance._meta.get_fields():
            if (
                field.many_to_many
                and hasattr(field, "related_name")
                and field.related_name
            ):
                yield field

    def fill_instance_m2m(self, instance, values):
        """
        FIXME: Verificar se realmente ainda é necessário o usuo deste tipo de preenchimento
               uma vez que temos um componente de edição inteligente para campos m2m.

               foi inserido na migração django 1.9 -> 1.10
        """
        fields = [f.name for f in instance._meta.many_to_many]
        fields += [f.name for f in self._all_fields_many_to_many_rel(instance)]

        for key, value in list(values.items()):
            field = getattr(instance, key, None)
            if key in fields and isinstance(value, (tuple, list, set)):
                field.clear()
                for item in value:
                    field.add(item)

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            log.debug(
                "COUNT UPDATE FOR %s [%s,]: %s"
                % (self.Model.__name__, pk, self.Model.objects.filter(pk=pk).count())
            )
            params = self.get_params(self.request.PUT, check_case=True)
            log.debug("PUT GETPARAMS....")
            log.debug(json.dumps(params, default=str))
            inst = self.Model.objects.get(pk=pk)
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que deseja atualizar. pk: %s model: %s ctr: %s"
                % (pk, self.Model.__name__, self.__class__.__name__)
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            if self.can_update_fields_values is not None:
                params = {
                    k: v
                    for k, v in list(params.items())
                    if k in self.can_update_fields_values
                }

            self.fill_instance_values(inst, params)
            try:
                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
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

    @property
    def renderer_map(self):
        return {
            "text/javascript": self.renderer_as_json,
            "text/json": self.renderer_as_json,
            "text/yaml": self.renderer_as_yaml,
            "text/yml": self.renderer_as_yaml,
            "text/xml": self.renderer_as_xml,
            "text/csv": self.renderer_as_csv,
            "default": self.renderer_as_json,
        }

    def get_renderer(self, accept):
        return self.renderer_map.get(accept, self.renderer_map.get("default"))

    @property
    def method_map(self):
        return {
            "GET": self.do_get,
            "POST": self.do_post,
            "PUT": self.do_put,
            "DELETE": self.do_delete,
        }

    def do_related_get(self, instance):
        rst = {}

        params = self.get_params()
        query = self.get_query_related(params.get("field"), instance)

        if query is not None:

            if "filter" in self.request.GET:
                query = self.do_filter(query)
            if "keyword" in self.request.GET:
                query = self.do_full_text_filter(query)
            if "sort" in self.request.GET:
                query = self.do_sort(query)

            rst.update(success=True, count=query.count())

            query = self.do_page(query)
            rst.update(
                collection=[{"pk": inst.pk, "unicode": str(inst)} for inst in query]
            )
        else:
            rst.update(success=False, message="Atributo desejado não existe.")

        return rst

    def do_related_post(self, instance):
        rst = {"success": False, "message": "Nada foi realizado ainda."}

        params = self.get_params()
        field_obj = getattr(instance, params.get("field"), None)

        def as_list(x):
            return x if isinstance(x, (tuple, list, set)) else [x]

        if field_obj is None:
            rst.update(
                message="Não existe este campo na entidade %s"
                % (instance._meta.verbose_name)
            )
        else:
            count = 0
            try:
                can = self.check_permission(
                    self.request.user,
                    "change",
                    self.Model._meta.app_label,
                    self.Model._meta.object_name,
                )

                if not can:
                    raise Exception("O usuário não tem permissão para executar a ação.")

                for obj in as_list(params.get(params.get("field"), [])):
                    field_obj.add(obj)
                    count += 1
            except Exception as e:
                log.exception(e)
                rst.update(message=str(e))
            else:
                rst.update(
                    success=True,
                    count=count,
                    message="Foram adicionados %d item%s"
                    % (count, "s" if count > 1 else ""),
                )

        return rst

    def do_related_delete(self, instance):
        rst = {"success": False, "message": "Nada foi realizado ainda."}

        params = self.get_params()
        field_obj = getattr(instance, params.get("field"), None)

        def as_list(x):
            return x if isinstance(x, (tuple, list, set)) else [x]

        if field_obj is None:
            rst.update(
                message="Não existe este campo na entidade %s"
                % instance._meta.verbose_name
            )
        else:
            try:
                can = self.check_permission(
                    self.request.user,
                    "change",
                    self.Model._meta.app_label,
                    self.Model._meta.object_name,
                )

                if not can:
                    raise Exception("O usuário não tem permissão para executar a ação.")

                log.debug(params)
                to_remove = as_list(params.get(params.get("field"), []))
                if to_remove:
                    for obj in to_remove:
                        field_obj.remove(obj)
                else:
                    field_obj.clear()
            except Exception as e:
                log.exception(e)
                rst.update(message=str(e))
            else:
                rst.update(success=True)

        return rst

    def get_query_related(self, field, instance):
        field_obj = getattr(instance, field, None)

        if field_obj is not None:
            return field_obj.filter()
        else:
            return None

    @property
    def method_related_map(self):
        return {
            "GET": self.do_related_get,
            "POST": self.do_related_post,
            "DELETE": self.do_related_delete,
        }

    def get_method(self, method):
        """:returns: Método referente à requisição."""
        return self.method_map.get(method, "GET")

    def get_related_method(self, method):
        """:returns: Método referente à requisição."""
        return self.method_related_map.get(method, "GET")

    @property
    def renderer(self):
        return self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))

    def related(self, args=[]):
        """Restful Router.

        :param args: Lista com 1 elemento, uma chave primária. (Opcional)
        :type args: Array of Integer
        """
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        method = self.get_related_method(self.request.method)

        rst = {}

        try:
            instance = self.get_query().get(pk=args[0])
        except self.Model.DoesNotExist:
            rst = {
                "success": False,
                "message": "Não consegui encontrar a informação base.",
            }
        except Exception as e:
            log.exception(e)
            rst = {"success": False, "message": str(e)}
        else:
            try:
                if self.request.method in ("GET", "PUT", "DELETE"):
                    if self.request.method != "GET":
                        setattr(
                            self.request,
                            self.request.method,
                            QueryDict(self.request.read(), False),
                        )

                rst = method(instance)
            except Exception as e:
                log.exception(e)
                rst = {"success": False, "message": str(e)}

        rendererer(rst)

    def _read_special_verb(self):
        content_type = self.request.META.get(
            "HTTP_CONTENT_TYPE", self.request.META.get("CONTENT_TYPE", None)
        )

        if content_type in ("application/json", "text/json"):
            setattr(self.request, self.request.method, json.loads(self.request.read()))
        else:
            setattr(
                self.request, self.request.method, QueryDict(self.request.read(), False)
            )

    def v1(self, args=[]):
        """Restful Router.

        :param args: Lista com 1 elemento, uma chave primária. (Opcional)
        :type args: Array of Integer
        """
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        method = self.get_method(self.request.method)

        try:
            if self.request.method in ("GET", "PUT", "DELETE"):
                if self.request.method != "GET":
                    self._read_special_verb()
                if len(args) == 0:
                    rendererer(method())
                else:
                    # log.debug(".!. >>> %s" % args)
                    rendererer(method(args[0]))
            else:
                rendererer(method())
        except Exception as e:
            log.exception(e)
            rendererer({"success": False, "message": str(e)})


class RestfulDRY(Restful):

    exclude_fields = []
    """
        Fields que não serão rastreados pelo model_to_dict e pelo get_params
    """
    only_fields = []
    """
        Fields que serão rastreados pelo model_to_dict e pelo get_params
    """

    force_persist_boolean_fields = []
    """ Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
        Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    """

    force_persist_clear_m2m = []
    """ Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados """

    def __init__(self, *args, **kargs):
        super(RestfulDRY, self).__init__(*args, **kargs)
        if not self.only_fields:
            self.only_fields = [f.name for f in self._model._meta.fields]
        self._fields = set(self.only_fields) - set(self.exclude_fields)

    def get_icons(self, instance):
        return []

    def model_to_dict(self, instance):
        """Cria um dicionário com atributos de uma instância.

        :param instance: Instância de Model.

        :returns: Dicionário com indices pk e unicode da instância.

        Este método deve ser sobrescrito para adicionar os demais atributos de uma determinada instância.
        Os valores dos atributos devem ser convertidos neste método para um formato serializável se necessário.
        """
        # Se a instance produzida no getquery for um dicionario
        # Pode acontecer quando o getquery foi sobrescrito para um aggregate
        if isinstance(instance, dict):
            return instance

        params = {
            "pk": instance.pk,
            "unicode": str(instance),
            "icons": self.get_icons(instance),
        }
        meta = instance._meta

        for f in meta.fields:
            if f.name in self._fields:
                _type = f.get_internal_type()
                if _type == "DecimalField":
                    params[f.name] = (
                        float(getattr(instance, f.name))
                        if getattr(instance, f.name) is not None
                        else ""
                    )
                elif _type == "DateTimeField":
                    params[f.name] = (
                        DateUtils.datetime_to_str(getattr(instance, f.name))
                        if getattr(instance, f.name)
                        else ""
                    )
                elif _type == "DateField":
                    params[f.name] = (
                        DateUtils.date_to_str(getattr(instance, f.name))
                        if getattr(instance, f.name)
                        else ""
                    )
                elif _type in ["ForeignKey", "OneToOneField"]:
                    params[f.name] = getattr(instance, f.attname) or ""
                elif _type in (
                    "BigIntegerField",
                    "IntegerField",
                    "PositiveIntegerField",
                    "PositiveSmallIntegerField",
                    "SmallIntegerField",
                ):
                    params[f.name] = (
                        int(getattr(instance, f.attname))
                        if getattr(instance, f.attname) is not None
                        else None
                    )
                elif _type == "UUIDField":
                    params[f.name] = str(getattr(instance, f.name)) or ""
                else:
                    params[f.name] = getattr(instance, f.name)
                if f.choices:
                    params["%s_display" % f.name] = (
                        getattr(instance, "get_%s_display" % f.name)() or ""
                    )
                if f.remote_field:
                    params["%s_unicode" % f.name] = str(getattr(instance, f.name) or "")

        return params

    def get_fields(self, args=[]):
        """Cria um dicionário com fields de @Model.

        :returns: Dicionário com nome do field e tipo.

        Este método pode ser sobrescrito para adicionar outros fields que não sejam de @Model ou alterar o tipo de algum field.
        """
        fields = {
            "pk": {"type": "int", "verbose": "pk"},
            "unicode": {"type": "string", "verbose": "unicode"},
        }

        meta = self._model._meta

        for f in meta.fields:
            if f.name in self._fields:
                if f.name not in fields:
                    fields[f.name] = {}
                _type = f.get_internal_type()
                _ext_type = "string"

                if _type in [
                    "IntegerField",
                    "SmallIntegerField",
                    "PositiveIntegerField",
                    "PositiveSmallIntegerField",
                    "AutoField",
                ]:
                    _ext_type = "int"
                elif _type in [
                    "BooleanField",
                ]:
                    _ext_type = "boolean"
                elif _type in ["DateTimeField", "DateField"]:
                    _ext_type = "float"

                fields[f.name] = {"type": _ext_type, "verbose": f.verbose_name}

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(fields)

    def get_params(self, querydict=None, check_case=False):
        """Recebe os parâmetros do browser como uma QueryDict e converte para um dicionário.

        :param querydict: QueryDict.

        :param check_case: Define se verifica o atributo 'force_upper' para conversão em uppercase.

        Este método deve ser sobrescrito para converter os parâmetros para um formato serializável se necessário.
        """

        # params = super(RestfulDRY, self).get_params(querydict, check_case)

        _dict_ = {}
        opts = self._model._meta

        querydict = (
            querydict
            if querydict is not None
            else getattr(self.request, self.request.method, QueryDict("", False))
        )

        keys = (
            set(querydict.keys())
            .union(self.force_persist_boolean_fields)
            .union(self.force_persist_clear_m2m)
            .difference(self.exclude_fields)
        )

        # log.debug('KEYS: %s' % keys)

        for key in keys:
            value = querydict.getlist(key) if key in querydict else []
            if len(value) <= 1:
                value = querydict.get(key) if key in querydict else None

            value = self._force_case(value) if check_case and value else value

            try:
                field = opts.get_field(key)
                model = getattr(field, "model", None)
                direct = not field.auto_created or field.concrete
                m2m = getattr(field, "many_to_many", None)

                _type = field.get_internal_type() if not m2m else "ManyToManyField"
                # log.debug('1 KEY: %s VALUE: %s TYPE: %s/%s' % (key, value, _type, type(value)))
                if _type in ["ForeignKey", "OneToOneField"]:
                    if not value:
                        value = None
                    else:
                        value = field.remote_field.model.objects.get(pk=value)
                elif _type == "DateTimeField":
                    value = DateUtils.str_to_datetime(value) if value else None
                elif _type == "DateField":
                    value = DateUtils.str_to_date(value) if value else None
                elif _type == "ManyToManyField":
                    value = querydict.getlist(key)
                elif _type in [
                    "IntegerField",
                    "BigIntegerField",
                    "PositiveIntegerField",
                    "PositiveSmallIntegerField",
                    "SmallIntegerField",
                ]:
                    value = int(value) if value not in ("", None) else None
                elif _type == "DecimalField":
                    value = Decimal(value) if value not in ("", None) else None
                elif _type == "BooleanField":
                    if value in ("", "off", "OFF", None, 0, False, "FALSE"):
                        value = False
                    elif value.lower() in ("on", "true"):
                        value = True
                elif _type == "UUIDField":
                    value = uuid.UUID(value) if value else None
                else:
                    log.debug("OTHER KEY: %s VALUE: %s" % (key, value))
                # log.debug('2 KEY: %s VALUE: %s TYPE: %s' % (key, value, type(value)))

            except FieldDoesNotExist:
                log.warn("Field %s do not exist in model %s" % (key, self._model))
            except Exception as e:
                log.exception(str(e))
                raise e

            _dict_.update({key: value})

        if self.force_persist_clear_m2m:
            # Deixando como [] os m2m que não vieram no request
            for field in opts.many_to_many:
                fname = field.name
                if fname in self.force_persist_clear_m2m and fname not in _dict_:
                    _dict_[fname] = []

        return _dict_

    def get_matricula_field_blocked(self):
        """Informa se é ou não para bloquear o campo matríula

        :returns: Boolean
        """
        return "true" if settings.MATRICULA_FIELD_BLOCKED else "false"


class RestfulTreeBase(object):
    """
    **Classe** REST para fornecer dados no formato de árvore.
    O Model deve possuir os atributos 'leaf' para indicar se o objeto é uma folha,
    e 'path' para descrever o caminho até o objeto a partir da raiz.

    :Métodos:
        :func:`folder`.
    """

    folder_index = "root_of"
    """ Campo de Model que possui a referência para o próprio Model. Representa o nó imediatamente superior ao atual na árvore"""

    def model_to_node(self, node):
        return {
            "text": str(node),
            "id": str(node.pk),
            "path": getattr(node, "path", None),
            "leaf": getattr(node, "leaf", False),
            "disableNode": True,
        }

    def folder(self, args=[]):
        """Renderiza a árvore."""
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        nodeId = (
            None
            if self.request.GET.get("node", "0") == "0"
            else int(self.request.GET.get("node"))
        )

        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)

        rendererer(
            [
                self.model_to_node(node)
                for node in query.filter(**{self.folder_index: nodeId})
            ]
        )


class RestfulTree(RestfulTreeBase, Restful):
    pass


class RestfulTreeDRY(RestfulTreeBase, RestfulDRY):
    pass

# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import transaction
from django.template.defaultfilters import slugify

from contrib.extjs import ExtWidget
from contrib.restful import Restful
from contrib.utils import get_json_engine
from rh.gfp.models import Evento, FolhaTipo
from rh.gfp.planoconta.models import Plano, PlanoConta
from rh.models import Banco, PessoaJuridica

json = get_json_engine()


class PCPlanoConta(Restful):

    model = PlanoConta

    def to_dict(self, qdict):
        rdict = Restful.to_dict(self, qdict)

        if "plano" in rdict:
            rdict.update(plano=Plano.objects.get(pk=rdict.get("plano")))

        return rdict


class PCPlano(Restful):

    model = Plano

    def to_dict(self, qdict):
        rdict = Restful.to_dict(self, qdict)

        self.log.debug(rdict)

        if "pessoa_juridica" in rdict:
            rdict.update(
                pessoa_juridica=PessoaJuridica.objects.get(
                    pk=rdict.get("pessoa_juridica")
                )
            )
        if "folha_tipo" in rdict:
            rdict.update(folha_tipo=FolhaTipo.objects.get(pk=rdict.get("folha_tipo")))
        if "banco" in rdict:
            try:
                rdict.update(banco=Banco.objects.get(pk=rdict.get("banco")))
            except:
                rdict.update(banco=None)

        eventos = []
        if not isinstance(rdict.get("eventos", ""), (tuple, list)):
            try:
                e = Evento.objects.get(pk=rdict.get("eventos"))
            except Exception as e:
                self.log.exception(e)
            else:
                eventos.append(e)
        else:
            for evento in rdict.get("eventos", []):
                try:
                    e = Evento.objects.get(pk=evento)
                except:
                    pass
                else:
                    eventos.append(e)

        rdict.update(eventos=eventos)
        return rdict

    def list_from_year(self, args=[]):
        obj = {"root": None}
        root = []

        planos = Plano.objects.filter(
            ano_calendario=self.request.POST.get("ano_calendario")
        )
        planos = (
            planos.filter(tipo=self.request.POST.get("f__tipo"))
            if "f__tipo" in self.request.POST
            else planos
        )
        planos = (
            planos.filter(folha_tipo=self.request.POST.get("f__folha_tipo"))
            if "f__folha_tipo" in self.request.POST
            else planos
        )

        for plano in planos.order_by("folha_tipo", "tipo", "pessoa_juridica"):
            root.append(
                {
                    "pk": plano.pk,
                    "titulo": (
                        plano.titulo if plano.titulo is not None else "Sem titulo"
                    ),
                    "pessoa_juridica": str(plano.pessoa_juridica.razao_social),
                    "pessoa_juridica__pk": plano.pessoa_juridica.pk,
                    "folha_tipo": str(plano.folha_tipo),
                    "folha_tipo__pk": plano.folha_tipo.pk,
                    "tipo_value": plano.tipo,
                    "ano_calendario": plano.ano_calendario,
                    "tipo": [
                        {
                            "icon": "/%s/static/rh/images/planoconta-tipo-%s.png"
                            % (
                                getattr(settings, "CONTEXT"),
                                slugify(plano.get_tipo_display()),
                            ),
                            "title": plano.get_tipo_display(),
                            "alt": plano.get_tipo_display(),
                        }
                    ],
                    "banco_pk": plano.banco.pk if plano.banco is not None else "",
                    "agencia": plano.agencia,
                    "conta": plano.conta,
                    "fonte": plano.fonte,
                    "eventos": [
                        (evento.pk, str(evento)) for evento in plano.eventos.all()
                    ],
                }
            )

        obj.update(root=root)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PCConsignatario(Restful):

    model = Plano

    def list(self, args=[]):
        from django.db.models import Q
        from rh.gfp.models import Folha

        obj = {"totalRows": 0, "root": None}
        root = []

        filter = Q(tipo=1)  # Tipo CONSIGNACAO
        try:
            folha = Folha.objects.get(pk=self.request.GET.get("folha"))
        except Exception as e:
            self.log.exception(e)
        else:
            folha_tipo = folha.tipo_folha
            ano = folha.periodo.ano
            filter = filter & (Q(folha_tipo=folha_tipo) & Q(ano_calendario=ano))

        planos = Plano.objects.filter(filter)

        for plano in planos:
            root.append(
                {
                    "pk": plano.pk,
                    "description": "%s" % plano.titulo,
                }
            )

        obj.update(root=root, totalRows=planos.count())

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PCGestor(ExtWidget):

    def copy_conta_tipo(self, args=[]):
        obj = {"success": False, "message": "Não consegui transportar nenhum plano"}

        try:
            conta = PlanoConta.objects.get(pk=int(self.request.POST.get("src")))
        except Exception as e:
            obj.update(
                message="Não consegui encontrar a conta para ser copiada.\n\n%s"
                % str(e)
            )
        else:
            conta.pk = None
            conta.tipo = int(self.request.POST.get("dst"))
            conta.save()
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def copy_ano_calendario(self, args=[]):
        obj = {"success": False, "message": "Não consegui transportar nenhum plano"}

        for plano in Plano.objects.filter(
            ano_calendario=int(self.request.POST.get("src"))
        ):
            sid = transaction.savepoint()

            novo = Plano(
                pessoa_juridica=plano.pessoa_juridica,
                ano_calendario=int(self.request.POST.get("dst")),
                folha_tipo=plano.folha_tipo,
                tipo=plano.tipo,
                titulo=plano.titulo,
                banco=plano.banco,
                agencia=plano.agencia,
                conta=plano.conta,
            )

            try:
                novo.save()

                for evento in plano.eventos.all():
                    novo.eventos.add(evento)

                for conta in plano.contas.all():
                    conta.pk = None
                    conta.plano = novo
                    conta.save()
            except:
                transaction.savepoint_rollback(sid)
            else:
                obj.update(success=True)
                transaction.savepoint_commit(sid)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def copy_plano_empresa(self, args=[]):
        obj = {"success": False, "message": "Nada ainda foi feito."}

        try:
            plano = Plano.objects.get(pk=int(self.request.POST.get("src")))
        except:
            obj.update(message="Não consegui encontrar o Plano de origem do tranporte.")
        else:
            for pj in PessoaJuridica.objects.filter(
                pk__in=self.request.POST.getlist("dsts")
            ):
                sid = transaction.savepoint()

                novo = Plano(
                    pessoa_juridica=pj,
                    ano_calendario=plano.ano_calendario,
                    folha_tipo=plano.folha_tipo,
                    tipo=plano.tipo,
                    banco=plano.banco,
                    agencia=plano.agencia,
                    conta=plano.conta,
                )

                try:
                    novo.save()

                    for evento in plano.eventos.all():
                        novo.eventos.add(evento)

                    for conta in plano.contas.all():
                        conta.pk = None
                        conta.plano = novo
                        conta.save()
                except:
                    transaction.savepoint_rollback(sid)
                else:
                    obj.update(success=True)
                    transaction.savepoint_commit(sid)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_from_plano(self, args=[]):
        obj = {"root": None}
        root = []

        try:
            plano = Plano.objects.get(pk=self.request.POST.get("plano"))
        except:
            pass
        else:
            for conta in plano.contas.all():
                root.append(
                    {
                        "pk": conta.pk,
                        "finalidade": conta.get_finalidade_display(),
                        "finalidade_id": conta.finalidade,
                        "inscricao_ne": conta.inscricao_ne,
                        "evento_nlc": conta.evento_nlc,
                        "evento_nld": conta.evento_nld,
                        "classificacao_nld": conta.classificacao_nld,
                        "classificacao_nlc": conta.classificacao_nlc,
                        "tipo": [
                            {
                                "icon": "/%s/static/rh/images/%s.png"
                                % (
                                    getattr(settings, "CONTEXT"),
                                    slugify(conta.get_tipo_display()),
                                ),
                                "alt": conta.get_tipo_display(),
                                "title": conta.get_tipo_display(),
                            },
                            {
                                "icon": "/%s/static/rh/images/%s.png"
                                % (
                                    getattr(settings, "CONTEXT"),
                                    slugify(conta.get_finalidade_display()),
                                ),
                                "alt": conta.get_finalidade_display(),
                                "title": conta.get_finalidade_display(),
                            },
                        ],
                        "tipo_id": conta.tipo,
                    }
                )

        obj.update(root=root)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_folha_tipo(self, args=[]):
        obj = {
            "root": [
                {"pk": f.pk, "description": str(f)}
                for f in FolhaTipo.objects.order_by("titulo")
            ]
        }
        obj.get("root").insert(0, {"pk": 0, "description": "TODAS"})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_ano_calendario(self, args=[]):
        obj = {}
        result = []

        for plano in (
            Plano.objects.order_by("-ano_calendario")
            .values("ano_calendario")
            .distinct()
        ):
            result.append(
                {
                    "ano": plano.get("ano_calendario"),
                    "description": "Ano Calendário %d" % plano.get("ano_calendario"),
                }
            )

        obj.update(result=result)
        self.response.write(json.encode(obj))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gfp.planoconta.Gestor()")

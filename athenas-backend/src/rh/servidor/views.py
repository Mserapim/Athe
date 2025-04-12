# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.query_utils import Q

from auditoria.models import LineLog
from contrib import extjs
from contrib.decorator import is_public, login_required
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, get_json_engine, getLogger
from ged.models import Arquivo
from rh.const import (
    CNH,
    CNH_CATEGORIA,
    CNH_FIRST_DATE,
    CTPS,
    CTPS_SERIE,
    ESTADO_CIVIL_CHOICES,
    FATOR_RH,
    GRAU_INSTRUCAO_CHOICES,
    NIS,
    PIS_PASEP,
    PROFESSIONAL_COUNCIL,
    PROFESSIONAL_COUNCIL_ISSUER,
    RACA_COR_CHOICES,
    REGIME_PREVIDENCIARIO,
    RESERVISTA,
    RESERVISTA_CLASSE,
    RIC,
    RIC_ISSUER,
    RNE,
    RNE_ISSUER,
    SANGUE,
    SEXO_CHOICES,
    TIPO_ENDERECO_CHOICES,
    TIPO_LOGRADOURO_ENDERECO_CHOICES,
    TIPO_MOVIMENTACAO_CARREIRA,
    TITULO_ELEITOR,
    TITULO_ELEITOR_MUNICIPIO,
    TITULO_ELEITOR_SECAO,
    TITULO_ELEITOR_ZONA,
)
from rh.gfp.models import ContraCheque, DadoBancarioServidorFolha, Folha, FolhaTipo
from rh.models import (
    Banco,
    Curso,
    DadoBancarioPessoa,
    Dependente,
    DocsDataSpecificSpecialized,
    DocumentSpecialized,
    Estado,
    Localidade,
    Molestia,
    MovimentacaoPosse,
    NaturalPersonSpecializedEmployee,
    PessoaFisica,
    PessoaJuridica,
    Servidor,
    ServidorVinculo,
)
from rh.utils import format_categoria, format_situacao_funcional
from standard.models import Choice

json = get_json_engine()
context = getattr(settings, "CONTEXT", "")

log = getLogger(__name__)


class RHDadoBancarioGerenciador(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.dadobancario.Gerenciador()")

    @login_required(type="JSON")
    def remove(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            if args[0] == "dadobancario":
                # TODO: MODIFICAR ESTE DELETE
                DadoBancarioPessoa.objects.filter(
                    pk__in=self.request.POST.getlist("db")
                ).delete()
            elif args[0] == "servidorfolhatipo":
                DadoBancarioServidorFolha.objects.filter(
                    dado_bancario_pessoa__pk=dado_bancario_pessoa,
                    tipo_folha__pk__in=tipo_folha,
                ).delete()
        except Exception as e:
            obj["message"] = "Não consegui remover o dado!"
            obj["success"] = False
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def vincular(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            for db in self.request.POST.getlist("dadobancario"):
                for tipo_folha in self.request.POST.getlist("folha"):
                    dado_bancario = DadoBancarioServidorFolha(
                        dado_bancario_pessoa=DadoBancarioPessoa.objects.get(pk=int(db)),
                        tipo_folha=FolhaTipo.objects.get(pk=int(tipo_folha)),
                    )
                    dado_bancario.save()
        except Exception as e:
            obj["message"] = "Não consegui vincular Dado Bancário!"
            obj["success"] = False
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        if args[0] == "banco":
            obj = self.get_store_banco(args)
        elif args[0] == "dado_bancario":
            obj = self.get_store_dado_bancario(
                Servidor.objects.get(pk=self.request.POST.get("servidor"))
            )
        elif args[0] == "folhatipo":
            obj = self.get_store_folha_tipo()
        elif args[0] == "servidorfolhatipo":
            obj = self.get_store_servidor_folha_tipo()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_store_dado_bancario_folhas(self, args=[]):
        obj = {"total": 0, "result": []}
        try:
            s = Servidor.objects.get(pk=self.request.POST.get("servidor"))
            for tf in (
                s.entries.values("folha__tipo_folha__titulo", "folha__tipo_folha")
                .distinct("folha__tipo_folha")
                .order_by("folha__tipo_folha__titulo")
            ):
                dbsfs = DadoBancarioServidorFolha.objects.filter(
                    dado_bancario_pessoa__pessoa=s.pessoa_fisica,
                    tipo_folha=tf["folha__tipo_folha"],
                ).order_by("-data_inicio_vigencia")
                if dbsfs:
                    obj["result"].append(
                        {
                            "pk": dbsfs[0].pk,
                            "tipo_folha_id": dbsfs[0].tipo_folha.pk,
                            "tipo_folha": "%s" % dbsfs[0].tipo_folha,
                            "dado_bancario_id": dbsfs[0].dado_bancario_pessoa.pk,
                            "dado_bancario": "%s - Ag.: %s Conta: %s"
                            % (
                                dbsfs[0].dado_bancario_pessoa.banco,
                                dbsfs[0].dado_bancario_pessoa.agencia,
                                dbsfs[0].dado_bancario_pessoa.conta_corrente_completa,
                            ),
                            "data_inicio_vigencia": "%s"
                            % (DateUtils.date_to_str(dbsfs[0].data_inicio_vigencia)),
                        }
                    )
                else:
                    obj["result"].append(
                        {
                            "pk": 0,
                            "tipo_folha_id": tf["folha__tipo_folha"],
                            "tipo_folha": "%s" % tf["folha__tipo_folha__titulo"],
                            "dado_bancario_id": 0,
                            "dado_bancario": "---",
                            "data_inicio_vigencia": "---",
                        }
                    )
            obj["total"] = len(obj["result"])
        except Exception:
            log.warn("erro distinct")
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_store_banco(self, args=[]):
        obj = []
        try:
            for row in Banco.objects.all():
                obj.append([row.id, str(row)])
        except Exception as e:
            self.log.exception(e)
            obj.append(["", ""])
        return obj

    @login_required(type="JSON")
    def get_store_folha_tipo(self, args=[]):
        obj = {"result": []}
        try:
            query = FolhaTipo.objects.all()
            if "query" in self.request.POST:
                months = []
                for month in Choice.get_choices_for("rh", "MONTHS"):
                    try:
                        month[1].lower().index(self.request.POST["query"].lower())
                        months.append(month[0])
                    except Exception:
                        pass
                query = query.filter(
                    Q(
                        Q(periodo__ano__icontains=self.request.POST["query"])
                        | Q(tipo_folha__titulo__icontains=self.request.POST["query"])
                        | Q(periodo__mes__in=months)
                    )
                )
            for row in query:
                obj["result"].append({"codigo": row.id, "descricao": str(row)})
        except Exception as e:
            self.log.exception(e)
            obj.append({})
        return obj

    @login_required(type="JSON")
    def get_store_servidor_folha_tipo(self, args=[]):
        obj = {"result": []}
        try:
            for row in DadoBancarioServidorFolha.objects.filter(
                dado_bancario_pessoa=self.request.POST.get("dado_bancario")
            ):
                obj["result"].append(
                    {"codigo": row.tipo_folha.pk, "descricao": str(row.tipo_folha)}
                )
        except Exception as e:
            self.log.exception(e)
            obj.append({})
        return obj

    @login_required(type="JSON")
    def get_store_dado_bancario(self, servidor):
        obj = {"result": []}
        try:
            if self.request.POST.get("xaction", "") == "read":
                for db_pessoa in DadoBancarioPessoa.objects.filter(
                    pessoa=servidor.pessoa_fisica
                ):
                    folha = []
                    # TODO: MODIFICAR EM db_pessoa.dado_bancario_folhas.all() PARA db_pessoa.dado_bancario_folhas.get()
                    # TODO: MODIFICAR O VINCULAR PARA VINCULAR APENAS UM POR DADO BANCARIO PESSOA
                    [
                        folha.append(str(f.tipo_folha))
                        for f in db_pessoa.dado_bancario_folhas.all()
                    ]
                    obj["result"].append(
                        {
                            "codigo": db_pessoa.pk,
                            "banco": str(db_pessoa.banco),
                            "agencia": db_pessoa.agencia,
                            "conta": db_pessoa.conta_corrente_completa,
                            "tipo_conta": db_pessoa.get_tipo_conta_display(),
                            "principal": "Sim" if db_pessoa.principal else "Não",
                            "folha": folha,
                        }
                    )
            elif self.request.POST.get("xaction", "") == "create":
                import json

                result = json.loads(self.request.POST.get("result"))
                dbp = DadoBancarioPessoa(
                    banco=Banco.objects.get(pk=int(result.get("banco"))),
                    agencia=result.get("agencia"),
                    conta_corrente_completa=result.get("conta"),
                    tipo_conta=result.get("tipo_conta"),
                    principal=result.get("principal"),
                    pessoa=servidor.pessoa_fisica.pessoa_ptr,
                )
                dbp.save()
                obj["result"].append(
                    {
                        "codigo": dbp.pk,
                        "banco": str(dbp.banco),
                        "agencia": dbp.agencia,
                        "conta": dbp.conta_corrente_completa,
                        "tipo_conta": dbp.get_tipo_conta_display(),
                        "principal": "Sim" if dbp.principal else "Não",
                        "folha": [],
                    }
                )
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(["", ""])
        return obj


class RHServidorEspecializado(extjs.ExtWidget):

    @classmethod
    def _concat_obj(cls, obj, obj_par):
        for err in obj_par.get("errors", []):
            obj["success"] = False
            obj["errors"].append(err)
        return obj

    @classmethod
    def _concat_validation_error(cls, obj, validation_error):
        validation_error = dict(validation_error)
        obj["success"] = False
        for key in validation_error:
            obj["errors"].append({key: validation_error.get(key)})
        return obj

    @is_public()
    def constants(self, args=[]):
        if hasattr(RHServidorEspecializado, "__cache_constants") is False:
            obj = {
                "SEXO": SEXO_CHOICES,
                "RACA_COR": RACA_COR_CHOICES,
                "ESTADO_CIVIL": ESTADO_CIVIL_CHOICES,
                "SANGUE": SANGUE,
                "FATOR_RH": FATOR_RH,
                "TIPO_ENDERECO": TIPO_ENDERECO_CHOICES,
                "TIPO_LOGRADOURO": TIPO_LOGRADOURO_ENDERECO_CHOICES,
                "GRAU_INSTRUCAO": [
                    (x[0], x[1])
                    for x in list(GRAU_INSTRUCAO_CHOICES.items())
                    if x[0] != 14
                ],
                "TIPO_CONTA": [x for x in Choice.get_choices_for("rh", "TIPO_CONTA")],
                "REGIME_PREVIDENCIARIO": list(REGIME_PREVIDENCIARIO.items()),
            }

            RHServidorEspecializado.__cache_constants = obj
        else:
            obj = RHServidorEspecializado.__cache_constants

        self.response["content-type"] = "text/javascript"
        self.response.write("toolkit.rh.CHOICES = %s" % json.encode(obj))

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.servidor.Servidor()")

    @staticmethod
    def get_link_arquivo(publicacao):
        """
        Este método retorna o link do arquivo para download.
        @param Publicacao - Objeto rh.Publicacao
        @return text - Link do arquivo para download.
        """
        download = ""
        try:
            download = publicacao.arquivo.permalink()
        except Exception:
            pass
        return download

    @staticmethod
    def get_parametro_download(publicacao):
        """
        Este método constroe o objeto para download de arquivos das publicações.
        @param Movimentacao - Objeto rh.Publicacao.
        @return dict - dict com os atributos necessários para construir o objeto de download.
        """
        download = RHServidorEspecializado.get_link_arquivo(publicacao)
        title = "Arquivo"
        image = "static/images/attachment.png"
        if download == "" or download is None:
            image = "static/engine/images/icons/athenas-0517.png"
            title = "Não possui arquivo"
        return {
            "link": download,
            "icon": "/%s/%s" % (context, image),
            "title": title,
            "alt": title,
        }

    @login_required(type="JSON")
    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        store = {
            "dependente": self.get_store_dependente,
            "servidorvinculo": self.get_store_servidor_vinculo,
        }
        try:
            if args[0] == "estado":
                obj = self.get_store_estado(args)
            elif args[0] == "banco":
                obj = self.get_store_banco(args)
            else:
                servidor = None
                if "servidor" in self.request.POST and self.request.POST.get(
                    "servidor"
                ):
                    servidor = Servidor.objects.get(
                        pk=self.request.POST.get("servidor")
                    )
                obj = store.get(args[0])(servidor)
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def status(self, par=False):
        return {
            "icon": "/%s/static/engine/images/icons/%s"
            % (context, "athenas-0073.png" if par else "athenas-0226.png"),
            "title": "Sim" if par else "Não",
            "alt": "Sim" if par else "Não",
        }

    def get_store_estado(self, args=[]):
        obj = []
        for row in Estado.objects.all():
            obj.append([row.id, row])
        return obj

    def get_store_banco(self, args=[]):
        obj = []
        for row in Banco.objects.all():
            obj.append([row.id, str(row)])
        return obj

    def get_store_dependente(self, servidor):
        obj = []
        for row in Dependente.objects.filter(servidor=servidor):
            obj.append([row.id, row])
        return obj

    def get_store_servidor_vinculo(self, servidor):
        obj = []
        for row in ServidorVinculo.objects.filter(servidor=servidor):
            obj.append([row.id, row])
        return obj

    def get_store_folha(self):
        obj = {"result": []}
        for row in Folha.objects.filter():
            obj["result"].append({"codigo": row.id, "descricao": row})
        return obj

    @login_required(type="JSON")
    def get_data_employee(self, args=[]):
        obj = {
            "pessoa_fisica": {
                "pk": None,
                "nome": "",
                "social_name": "",
                "cpf": "",
                "rg": "",
                "sexo": "",
                "sangue": "",
                "estado_civil": "",
                "municipio_naturalidade": "",
                "raca_cor": "",
                "email_institucional": "",
                "email_pessoal": "",
                "data_nascimento": "",
                "data_obito": "",
                "rg_orgao": "",
                "rg_data_expedicao": "",
                "rg_uf": "",
                "fator_rh": "",
                "doador": "",
                "nome_pai": "",
                "nome_mae": "",
                "nome_conjuge": "",
                "foto": "",
                "foto_link": "",
                "molestia": "",
                "necessidades_especiais": "",
            },
            "servidor": {
                "chefe_imediato": "",
                "organ_social_security": "",
                "regime_previdenciario": "",
                "grau_instrucao": "",
                "matricula": "",
                "matricula_origem": "",
                "numero_cartao_ponto": "",
                "classificacao": "",
                "curso": "",
                "data_referencia_ferias": "",
                "situacao_funcional": "",
                "categoria": "",
                "tipo": "",
                "posicao_concurso": "",
            },
            "documento": {
                "cnh": "",
                "cnh_categoria": "",
                "cnh_expedition_date": "",
                "cnh_validity_date": "",
                "cnh_first_date": "",
                "cnh_state": "",
                "ctps": "",
                "serie_ctps": "",
                "ctps_state": "",
                "pis_pasep": "",
                "reservista": "",
                "classe_reservista": "",
                "professional_council": "",
                "professional_council_state": "",
                "professional_council_expedition_date": "",
                "professional_council_validity_date": "",
                "professional_council_issuer": "",
                "titulo_eleitor": "",
                "zona_titulo": "",
                "secao_titulo": "",
                "municipio_titulo": "",
                "ric": "",
                "ric_expedition_date": "",
                "ric_issuer": "",
                "ric_state": "",
                "rne": "",
                "rne_expedition_date": "",
                "rne_issuer": "",
                "rne_state": "",
                "nis": "",
            },
            "endereco": {
                "tipo_endereco": "",
                "municipio": "",
                "tipo_logradouro": "",
                "logradouro": "",
                "numero": "",
                "cep": "",
                "bairro": "",
                "complemento": "",
            },
            "telefone": {"numero_telefone1": "", "numero_telefone2": ""},
            "dependente": [],
            "dados_estaticos_efetivo": {"cargo": [], "progressao": []},
            "dados_estaticos_cmfc": {
                "cargo": [],
                "referencia": [],
            },
            "dados_estaticos_designacao": {
                "cargo": [],
            },
            "dados_estaticos_eletivo": {
                "cargo": [],
                "referencia": [],
            },
            "dados_estaticos_informacoes": {
                "lotacao": [],
                "estagio_probatorio": [],
                "data_estabilidade": [],
                "categoria": "",
                "situacao_funcional": "",
            },
        }
        pk = self.request.POST.get("servidor", None)
        if pk:
            try:
                servidor = Servidor.objects.get(pk=int(pk))
                necessidades_especiais = []
                for n in servidor.pessoa_fisica.necessidades_especiais.all():
                    necessidades_especiais.append([n.pk, n])
                obj.get("pessoa_fisica").update({"nome": servidor.pessoa_fisica.nome})
                obj.get("pessoa_fisica").update(
                    {"social_name": servidor.pessoa_fisica.social_name}
                )
                obj.get("pessoa_fisica").update({"pk": servidor.pessoa_fisica.pk})
                obj.get("pessoa_fisica").update({"cpf": servidor.pessoa_fisica.cpf})
                obj.get("pessoa_fisica").update({"rg": servidor.pessoa_fisica.rg})
                obj.get("pessoa_fisica").update({"sexo": servidor.pessoa_fisica.sexo})
                obj.get("pessoa_fisica").update(
                    {"sangue": servidor.pessoa_fisica.sangue}
                )
                obj.get("pessoa_fisica").update(
                    {"estado_civil": servidor.pessoa_fisica.estado_civil}
                )
                obj.get("pessoa_fisica").update(
                    {
                        "municipio_naturalidade": (
                            servidor.pessoa_fisica.municipio_naturalidade.pk
                            if servidor.pessoa_fisica.municipio_naturalidade is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {"raca_cor": servidor.pessoa_fisica.raca_cor}
                )
                obj.get("pessoa_fisica").update(
                    {"email_institucional": servidor.pessoa_fisica.email_institucional}
                )
                obj.get("pessoa_fisica").update(
                    {"email_pessoal": servidor.pessoa_fisica.email_pessoal}
                )
                obj.get("pessoa_fisica").update(
                    {
                        "data_nascimento": (
                            DateUtils.date_to_str(
                                servidor.pessoa_fisica.data_nascimento
                            )
                            if servidor.pessoa_fisica.data_nascimento is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {
                        "data_obito": (
                            DateUtils.date_to_str(servidor.pessoa_fisica.data_obito)
                            if servidor.pessoa_fisica.data_obito is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {"rg_orgao": servidor.pessoa_fisica.rg_orgao}
                )
                obj.get("pessoa_fisica").update(
                    {
                        "rg_data_expedicao": (
                            DateUtils.date_to_str(
                                servidor.pessoa_fisica.rg_data_expedicao
                            )
                            if servidor.pessoa_fisica.rg_data_expedicao is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {
                        "rg_uf": (
                            servidor.pessoa_fisica.rg_uf.pk
                            if servidor.pessoa_fisica.rg_uf is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {"fator_rh": servidor.pessoa_fisica.fator_rh}
                )
                obj.get("pessoa_fisica").update(
                    {"doador": True if servidor.pessoa_fisica.doador is True else False}
                )
                obj.get("pessoa_fisica").update(
                    {"nome_pai": servidor.pessoa_fisica.nome_pai}
                )
                obj.get("pessoa_fisica").update(
                    {"nome_mae": servidor.pessoa_fisica.nome_mae}
                )
                obj.get("pessoa_fisica").update(
                    {"nome_conjuge": servidor.pessoa_fisica.nome_conjuge}
                )
                obj.get("pessoa_fisica").update(
                    {
                        "foto": (
                            [
                                servidor.pessoa_fisica.foto,
                                servidor.pessoa_fisica.foto.pk,
                            ]
                            if servidor.pessoa_fisica.foto is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {
                        "foto_link": (
                            servidor.pessoa_fisica.foto.resizelink((85, 113))
                            if servidor.pessoa_fisica.foto
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {
                        "molestia": (
                            servidor.molestia.pk
                            if servidor.molestia is not None
                            else ""
                        )
                    }
                )
                obj.get("pessoa_fisica").update(
                    {"necessidades_especiais": necessidades_especiais}
                )
                curso = []
                for c in servidor.curso.all():
                    curso.append([c.pk, c])

                obj.get("servidor").update(
                    {
                        "chefe_imediato": (
                            servidor.chefe_imediato.pk
                            if servidor.chefe_imediato
                            else ""
                        )
                    }
                )
                obj.get("servidor").update(
                    {
                        "organ_social_security": (
                            servidor.organ_social_security.pk
                            if servidor.organ_social_security
                            else ""
                        )
                    }
                )
                obj.get("servidor").update(
                    {"regime_previdenciario": servidor.regime_previdenciario}
                )
                obj.get("servidor").update(
                    {"grau_instrucao": servidor.pessoa_fisica.grau_instrucao}
                )
                obj.get("servidor").update({"matricula": servidor.matricula})
                obj.get("servidor").update(
                    {"matricula_origem": servidor.matricula_origem}
                )
                obj.get("servidor").update(
                    {"numero_cartao_ponto": servidor.numero_cartao_ponto}
                )
                obj.get("servidor").update({"classificacao": servidor.classificacao})
                obj.get("servidor").update({"curso": curso})
                obj.get("servidor").update(
                    {
                        "data_referencia_ferias": (
                            DateUtils.date_to_str(servidor.data_referencia_ferias)
                            if servidor.data_referencia_ferias is not None
                            else ""
                        )
                    }
                )
                obj.get("servidor").update({"tipo": servidor.tipo})
                obj.get("servidor").update(
                    {"posicao_concurso": servidor.posicao_concurso}
                )

                cnh = self.save_doc_cnh(servidor.pessoa_fisica, False)
                cnh_categoria = self.save_cnh_category(cnh, False)
                cnh_first_date = self.save_cnh_first_date(cnh, False)
                ctps = self.save_doc_ctps(servidor.pessoa_fisica, False)
                serie_ctps = self.save_ctps_series(ctps, False)
                pis_pasep = self.save_doc_pis_pasep(servidor.pessoa_fisica, False)
                reservista = self.save_doc_reservist(servidor.pessoa_fisica, False)
                classe_reservista = self.save_reservist_class(reservista, False)
                professional_council = self.save_doc_professional_council(
                    servidor.pessoa_fisica, False
                )
                professional_concil_issuer = self.save_doc_professional_council_issuer(
                    professional_council, False
                )
                titulo_eleitor = self.save_doc_voter(servidor.pessoa_fisica, False)
                zona_titulo = self.save_voter_zone(titulo_eleitor, False)
                secao_titulo = self.save_voter_section(titulo_eleitor, False)
                municipio_titulo = self.save_voter_city(titulo_eleitor, False)
                ric = self.save_doc_ric(servidor.pessoa_fisica, False)
                ric_issuer = self.save_ric_issuer(ric, False)
                rne = self.save_doc_rne(servidor.pessoa_fisica, False)
                rne_issuer = self.save_rne_issuer(rne, False)
                nis = self.save_doc_nis(servidor.pessoa_fisica, False)
                try:
                    obj.get("documento").update(
                        {
                            "municipio_titulo": Localidade.objects.get(
                                pk=int(municipio_titulo.valor)
                            ).pk
                        }
                    )
                except Exception:
                    pass
                obj.get("documento").update({"cnh": cnh.numero if cnh else ""})
                obj.get("documento").update(
                    {"cnh_categoria": cnh_categoria.valor if cnh_categoria else ""}
                )
                obj.get("documento").update(
                    {
                        "cnh_expedition_date": (
                            DateUtils.date_to_str(cnh.data_expedicao)
                            if cnh and cnh.data_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "cnh_validity_date": (
                            DateUtils.date_to_str(cnh.data_validade)
                            if cnh and cnh.data_validade
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {"cnh_first_date": cnh_first_date.valor if cnh_first_date else ""}
                )
                obj.get("documento").update(
                    {
                        "cnh_state": (
                            cnh.estado_expedicao.pk
                            if cnh and cnh.estado_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update({"ctps": ctps.numero if ctps else ""})
                obj.get("documento").update(
                    {"serie_ctps": serie_ctps.valor if serie_ctps else ""}
                )
                obj.get("documento").update(
                    {
                        "ctps_state": (
                            ctps.estado_expedicao.pk
                            if ctps and ctps.estado_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {"pis_pasep": pis_pasep.numero if pis_pasep else ""}
                )
                obj.get("documento").update(
                    {"reservista": reservista.numero if reservista else ""}
                )
                obj.get("documento").update(
                    {
                        "classe_reservista": (
                            classe_reservista.valor if classe_reservista else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "professional_council": (
                            professional_council.numero if professional_council else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "professional_council_state": (
                            professional_council.estado_expedicao.pk
                            if professional_council
                            and professional_council.estado_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "professional_council_expedition_date": (
                            DateUtils.date_to_str(professional_council.data_expedicao)
                            if professional_council
                            and professional_council.data_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "professional_council_validity_date": (
                            DateUtils.date_to_str(professional_council.data_validade)
                            if professional_council
                            and professional_council.data_validade
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {
                        "professional_council_issuer": (
                            professional_concil_issuer.valor
                            if professional_concil_issuer
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {"titulo_eleitor": titulo_eleitor.numero if titulo_eleitor else ""}
                )
                obj.get("documento").update(
                    {"zona_titulo": zona_titulo.valor if zona_titulo else ""}
                )
                obj.get("documento").update(
                    {"secao_titulo": secao_titulo.valor if secao_titulo else ""}
                )
                obj.get("documento").update({"ric": ric.numero if ric else ""})
                obj.get("documento").update(
                    {
                        "ric_expedition_date": (
                            DateUtils.date_to_str(ric.data_expedicao)
                            if ric and ric.data_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {"ric_issuer": ric_issuer.valor if ric_issuer else ""}
                )
                obj.get("documento").update(
                    {
                        "ric_state": (
                            ric.estado_expedicao.pk
                            if ric and ric.estado_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update({"rne": rne.numero if rne else ""})
                obj.get("documento").update(
                    {
                        "rne_expedition_date": (
                            DateUtils.date_to_str(rne.data_expedicao)
                            if rne and rne.data_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update(
                    {"rne_issuer": rne_issuer.valor if rne_issuer else ""}
                )
                obj.get("documento").update(
                    {
                        "rne_state": (
                            rne.estado_expedicao.pk
                            if rne and rne.estado_expedicao
                            else ""
                        )
                    }
                )
                obj.get("documento").update({"nis": nis.numero if nis else ""})

                endereco = self.get_endereco(servidor.pessoa_fisica, False)[0]
                if endereco:
                    obj.get("endereco").update(
                        {"tipo_endereco": endereco.tipo_endereco}
                    )
                    obj.get("endereco").update(
                        {
                            "municipio": (
                                endereco.municipio.pk
                                if endereco.municipio is not None
                                else ""
                            )
                        }
                    )
                    obj.get("endereco").update(
                        {"tipo_logradouro": endereco.tipo_logradouro}
                    )
                    obj.get("endereco").update({"logradouro": endereco.logradouro})
                    obj.get("endereco").update({"numero": endereco.numero})
                    obj.get("endereco").update({"cep": endereco.cep})
                    obj.get("endereco").update({"bairro": endereco.bairro})
                    obj.get("endereco").update({"complemento": endereco.complemento})
                dependente = Dependente.objects.filter(servidor=servidor)
                for d in dependente:
                    obj["dependente"].append([d.pk, d.pessoa_fisica.nome])
                situacao_funcional = format_situacao_funcional(
                    servidor.situacao_funcional_cache
                )
                if servidor.pessoa_fisica.data_obito:
                    situacao_funcional += " - Falecido"
                categoria = (
                    format_categoria(servidor.categoria)
                    if servidor.categoria
                    else "Em processamento"
                )
                obj["servidor"]["categoria"] = categoria
                obj["servidor"]["situacao_funcional"] = situacao_funcional
                obj.update(self.functional_data(args=args))
            except Exception as e:
                self.log.exception(e)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def functional_data(self, args=[]):
        obj = {
            "dados_estaticos_efetivo": {"cargo": [], "progressao": []},
            "dados_estaticos_cmfc": {
                "cargo": [],
                "referencia": [],
            },
            "dados_estaticos_designacao": {
                "cargo": [],
            },
            "dados_estaticos_eletivo": {
                "cargo": [],
                "referencia": [],
            },
            "dados_estaticos_informacoes": {
                "lotacao": [],
                "estagio_probatorio": [],
                "data_estabilidade": [],
                "categoria": "",
                "situacao_funcional": "",
            },
        }
        pk = self.request.POST.get("servidor", None)
        if pk:
            try:
                servidor = Servidor.objects.get(pk=int(pk))
                situacao_funcional = format_situacao_funcional(
                    servidor.situacao_funcional_cache
                )
                if servidor.pessoa_fisica.data_obito is not None:
                    situacao_funcional += " - Falecido"
                categoria = (
                    format_categoria(servidor.categoria)
                    if servidor.categoria
                    else "Em processamento"
                )

                posse_efetivo = (
                    servidor.posses_ativas.get(
                        quadro__cargo__tipo_lei_cargo__in=("EF", "AC")
                    )
                    if servidor.is_efetivo
                    else None
                )
                referencia_nivel2d = (
                    ContraCheque._get_referencia_from_posse(
                        servidor.posses_ativas.get(quadro__cargo__tipo_lei_cargo="EF")
                    )
                    if servidor.is_efetivo
                    else None
                )
                data_inicio_progressao = None
                try:
                    data_inicio_progressao = (
                        posse_efetivo.progressoes.exclude(
                            data_inicio_vigencia__gt=datetime.datetime.now()
                        )
                        .latest("data_inicio_vigencia")
                        .data_inicio_vigencia
                        if servidor.is_efetivo and not servidor.membro
                        else ""
                    )
                except Exception:
                    log.info("A posse %s não possui progressão!" % posse_efetivo)

                posse_cmfc = None
                if servidor.posses_ativas.filter(
                    quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "ES")
                ).exists():
                    posse_cmfc = servidor.posses_ativas.get(
                        quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL", "ES")
                    )
                posse_el = None
                if servidor.posses_ativas.filter(
                    quadro__cargo__tipo_lei_cargo__in=("EL",)
                ).exists():
                    posse_el = servidor.posses_ativas.get(
                        quadro__cargo__tipo_lei_cargo__in=("EL",)
                    )

                posse = posse_cmfc or posse_efetivo or posse_el
                referencia = ""
                if posse_cmfc or (
                    posse_efetivo and posse_efetivo.quadro.cargo.indicativo == "M"
                ):
                    from rh.gfp.models import EstruturaTabelaSalarial

                    try:
                        rs = EstruturaTabelaSalarial.salarios(posse.quadro.cargo)
                        referencia = rs[0][1] if rs else None
                        if (
                            posse_efetivo
                            and posse_efetivo.quadro.cargo.indicativo == "M"
                        ):
                            # referencia_nivel2d = referencia
                            data_inicio_progressao = posse_efetivo.data_posse
                    except Exception as err:
                        self.log.exception(err)
                lotacoes = []
                try:
                    lotacao = servidor.workplace
                    designacao = servidor.work_assignment
                    lotacoes = ""
                    for sl in lotacao:
                        lotacoes += " " + sl
                    for sl in designacao:
                        lotacoes += " " + sl
                except Exception as err:
                    self.log.exception(err)
                obj["dados_estaticos_efetivo"]["cargo"] = (
                    posse_efetivo.quadro
                    + " - Posse: %s - Exercício: %s"
                    % (
                        DateUtils.date_to_str(posse_efetivo.data_posse),
                        DateUtils.date_to_str(posse_efetivo.data_exercicio),
                    )
                    if posse_efetivo
                    else ""
                )
                obj["dados_estaticos_efetivo"]["progressao"] = (
                    referencia_nivel2d.sigla_cache
                    + " - Início: %s" % (DateUtils.date_to_str(data_inicio_progressao))
                    if referencia_nivel2d and data_inicio_progressao
                    else ""
                )
                obj["dados_estaticos_cmfc"]["cargo"] = (
                    posse_cmfc.quadro
                    + " - Posse: %s - Exercício: %s"
                    % (
                        DateUtils.date_to_str(posse_cmfc.data_posse),
                        DateUtils.date_to_str(posse_cmfc.data_exercicio),
                    )
                    if posse_cmfc
                    else ""
                )
                obj["dados_estaticos_cmfc"]["referencia"] = (
                    referencia
                    + " - Início: %s" % (DateUtils.date_to_str(posse_cmfc.data_posse))
                    if posse_cmfc
                    else ""
                )
                obj["dados_estaticos_designacao"]["cargo"] = ""
                obj["dados_estaticos_eletivo"]["cargo"] = (
                    posse_el.quadro
                    + " - Posse: %s - Exercício: %s"
                    % (
                        DateUtils.date_to_str(posse_el.data_posse),
                        DateUtils.date_to_str(posse_el.data_exercicio),
                    )
                    if posse_el
                    else ""
                )
                obj["dados_estaticos_eletivo"]["referencia"] = (
                    referencia
                    + " - Início: %s" % (DateUtils.date_to_str(posse_el.data_posse))
                    if posse_el
                    else ""
                )
                obj["dados_estaticos_informacoes"]["categoria"] = categoria
                obj["dados_estaticos_informacoes"][
                    "situacao_funcional"
                ] = situacao_funcional
                obj["dados_estaticos_informacoes"]["lotacao"] = (
                    lotacoes if lotacoes else "Lotação não existe ou não está ativa"
                )
                obj["dados_estaticos_informacoes"]["estagio_probatorio"] = (
                    "" if not servidor.is_efetivo else "Em processamento"
                )
                obj["dados_estaticos_informacoes"]["data_estabilidade"] = (
                    "" if not servidor.is_efetivo else "Em processamento"
                )
            except Exception as e:
                self.log.exception(e)
        return obj

    @login_required(type="JSON")
    def search(self, args=[]):
        obj = {"result": []}
        try:
            valor = self.request.POST.get("valor")
            query = (
                Q(pessoa_fisica__nome__icontains=valor)
                | Q(matricula__icontains=valor)
                | Q(pessoa_fisica__cpf__icontains=valor)
            )
            for employee in Servidor.objects.filter(query):
                obj["result"].append(
                    {
                        "id": employee.id,
                        "natural_person_id": employee.pessoa_fisica.pk,
                        "registry": employee.matricula,
                        "description": employee,
                        "status": {
                            "icon": "/%s/static/engine/images/icons/%s"
                            % (
                                context,
                                (
                                    "athenas-0073.png"
                                    if employee.ativo
                                    else "athenas-0226.png"
                                ),
                            ),
                            "title": "Sim" if employee.ativo else "Não",
                            "alt": "Sim" if employee.ativo else "Não",
                        },
                    }
                )
        except Exception as err:
            self.log.exception(err)
            obj["result"].append({"id": "", "description": ""})
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def validate(self, args=[]):
        obj = {"result": True, "errors": []}
        if len(args) > 0 and args[0] == "employee_validate":
            obj = self.employee_validate()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def employee_validate(self, args=[]):
        obj = {"success": True, "errors": []}
        if self.request.POST.get("nome", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"nome": "Nome não informado!"}
            )
        if self.request.POST.get("municipio_naturalidade", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"municipio_naturalidade": "Naturalidade não informado!"}
            )
        if self.request.POST.get("estado_civil", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"estado_civil": "Estado civil não informado!"}
            )
        if self.request.POST.get("raca_cor", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"raca_cor": "Raça/Cor não informado!"}
            )
        if self.request.POST.get("cpf", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"cpf": "CPF não informado!"}
            )
        if self.request.POST.get("titulo_eleitor", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"titulo_eleitor": "Título de eleitor não informado!"}
            )
        if self.request.POST.get("zona_titulo", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"zona_titulo": "Zona do título não informado!"}
            )
        if self.request.POST.get("secao_titulo", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"secao_titulo": "Seção de título não informado!"}
            )
        if self.request.POST.get("municipio_titulo", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"municipio_titulo": "Município de título não informado!"}
            )
        if self.request.POST.get("matricula", "") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"matricula": "Matrícula não informado!"}
            )
        if self.request.POST.get("grau_instrucao") == "":
            RHServidorEspecializado._concat_validation_error(
                obj, {"grau_instrucao": "Grau de instrução não informado!"}
            )
        return obj

    @login_required(type="JSON")
    def commit(self, args=[]):
        obj = {"success": True, "errors": []}
        if len(args) > 0 and args[0] == "employee_commit":
            obj = self.employee_commit()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def do_save_documents(self, natural_person):
        return self.save_document(natural_person)

    @login_required(type="JSON")
    def employee_commit(self, args=[]):
        obj = {
            "success": True,
            "errors": [],
            "servidor": None,
            "pessoa_fisica": None,
            "registry": None,
            "created": (
                False
                if self.search_employee(
                    self.request.POST.get("servidor", None),
                    self.request.POST.get("matricula", None),
                )
                else True
            ),
        }
        # errors_to_show = []
        linelog = LineLog(level=71, status=1)
        linelog.read_request(self.request)
        employee = None
        obj_naturalperson = {"success": False, "errors": []}
        obj_documento = {"success": False, "errors": []}
        obj_employee = {"success": False, "errors": []}

        natural_person = self.search_natural_person(
            employee_pk=self.request.POST.get("servidor", None),
            rg=self.request.POST.get("rg", None),
            cpf=self.request.POST.get("cpf", None),
        )

        did_save_documents = False
        if natural_person:
            obj_documento = self.do_save_documents(natural_person)
            did_save_documents = True

        natural_person, obj_naturalperson = self.save_natural_person_employee(
            natural_person
        )
        if obj_naturalperson["success"] is True:
            employee, obj_employee = self.save_employee(natural_person)
            if obj_employee["success"] is True:
                curso, obj_curso = self.save_curso(employee)

        if natural_person and not did_save_documents:
            obj_documento = self.do_save_documents(natural_person)

        if employee:
            obj["servidor"] = employee.pk
            obj["registry"] = employee.matricula
            obj["is_member"] = employee.is_member
        if natural_person:
            obj["pessoa_fisica"] = natural_person.pk
        RHServidorEspecializado._concat_obj(obj, obj_employee)
        RHServidorEspecializado._concat_obj(obj, obj_naturalperson)
        RHServidorEspecializado._concat_obj(obj, obj_documento)
        if obj["success"] is False:
            linelog.status = 0
            err = ""
            for o in obj["errors"]:
                err += " - " + o
            linelog.json_description["messageException"] = err
        linelog.save()
        return obj

    def search_natural_person(self, employee_pk=None, rg=None, cpf=None):
        # employee = None
        natural_person = None
        if employee_pk:
            natural_person = Servidor.objects.get(pk=int(employee_pk)).pessoa_fisica
            self.log.warn("Utilizando Pessoa Física a partir do Servidor.")
        if not natural_person:
            rst_rg = None
            rst_cpf = None
            if cpf:
                rst_cpf = PessoaFisica.objects.filter(cpf=cpf)
                natural_person = rst_cpf.last()
                self.log.warn("Utilizando Pessoa Física a partir do CPF.")
            elif rg:
                rst_rg = PessoaFisica.objects.filter(rg=rg)
                natural_person = rst_rg.last()
                self.log.warn("Utilizando Pessoa Física a partir do RG.")
        if not natural_person:
            self.log.warn(
                "Pessoa Física não encontrada! A partir de agora um será criado um novo cadastro."
            )
        log.debug(natural_person)
        return natural_person

    def save_natural_person_employee(self, natural_person):
        if natural_person:
            natural_person = NaturalPersonSpecializedEmployee.objects.get(
                pk=natural_person
            )
        obj = {"success": True, "errors": []}
        nome = self.request.POST.get("nome", None)
        social_name = self.request.POST.get("social_name", None)
        cpf = self.request.POST.get("cpf", None)
        rg = self.request.POST.get("rg", None)
        sexo = self.request.POST.get("sexo", None)
        sangue = self.request.POST.get("sangue", None)
        estado_civil = self.request.POST.get("estado_civil", None)
        municipio_naturalidade = None
        try:
            municipio_naturalidade = Localidade.objects.get(
                pk=int(self.request.POST.get("municipio_naturalidade", None))
            )
        except Exception:
            pass
        raca_cor = self.request.POST.get("raca_cor", None)
        email_institucional = self.request.POST.get("email_institucional", None)
        email_pessoal = self.request.POST.get("email_pessoal", None)
        data_nascimento = None
        try:
            if self.request.POST.get("data_nascimento", None):
                data_nascimento = DateUtils.str_to_date(
                    self.request.POST.get("data_nascimento", None)
                )
        except Exception:
            pass
        data_obito = None
        try:
            if self.request.POST.get("data_obito", None):
                data_obito = DateUtils.str_to_date(
                    self.request.POST.get("data_obito", None)
                )
        except Exception:
            pass
        rg_orgao = self.request.POST.get("rg_orgao", None)
        rg_data_expedicao = None
        try:
            if self.request.POST.get("rg_data_expedicao", None):
                rg_data_expedicao = DateUtils.str_to_date(
                    self.request.POST.get("rg_data_expedicao", None)
                )
        except Exception:
            pass
        rg_uf = None
        try:
            rg_uf = Estado.objects.get(pk=int(self.request.POST.get("rg_uf", None)))
        except Exception:
            pass
        fator_rh = None
        try:
            fator_rh = self.request.POST.get("fator_rh", None)
        except Exception:
            pass
        doador = True if self.request.POST.get("doador", "") == "on" else False
        nome_pai = self.request.POST.get("nome_pai", None)
        nome_mae = self.request.POST.get("nome_mae", None)
        nome_conjuge = self.request.POST.get("nome_conjuge", None)
        foto = None
        try:
            foto = Arquivo.objects.get(pk=int(self.request.POST.get("foto", None)))
        except Exception:
            pass
        grau_instrucao = self.request.POST.get("grau_instrucao", None)
        try:
            if not natural_person:
                natural_person = NaturalPersonSpecializedEmployee(
                    nome=nome,
                    social_name=social_name,
                    estado_civil=estado_civil,
                    raca_cor=raca_cor,
                    doador=doador,
                    cpf=cpf,
                    rg=rg,
                    sexo=sexo,
                    sangue=sangue,
                    municipio_naturalidade=municipio_naturalidade,
                    email_institucional=email_institucional,
                    email_pessoal=email_pessoal,
                    data_nascimento=data_nascimento,
                    data_obito=data_obito,
                    rg_orgao=rg_orgao,
                    rg_data_expedicao=rg_data_expedicao,
                    rg_uf=rg_uf,
                    fator_rh=fator_rh,
                    nome_pai=nome_pai,
                    nome_mae=nome_mae,
                    nome_conjuge=nome_conjuge,
                    foto=foto,
                    grau_instrucao=grau_instrucao,
                )
                natural_person.clean_fields()
                natural_person.save()
            else:
                natural_person.nome = nome
                natural_person.social_name = social_name
                natural_person.cpf = cpf
                natural_person.rg = rg
                natural_person.sexo = sexo
                natural_person.sangue = sangue
                natural_person.estado_civil = estado_civil
                natural_person.municipio_naturalidade = municipio_naturalidade
                natural_person.raca_cor = raca_cor
                natural_person.email_institucional = email_institucional
                natural_person.email_pessoal = email_pessoal
                natural_person.data_nascimento = data_nascimento
                natural_person.data_obito = data_obito
                natural_person.rg_orgao = rg_orgao
                natural_person.rg_data_expedicao = rg_data_expedicao
                natural_person.rg_uf = rg_uf
                natural_person.fator_rh = fator_rh
                natural_person.doador = doador
                natural_person.nome_pai = nome_pai
                natural_person.nome_mae = nome_mae
                natural_person.nome_conjuge = nome_conjuge
                natural_person.foto = foto
                natural_person.grau_instrucao = grau_instrucao
                natural_person.clean_fields()
                natural_person.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"message_err": err})
        return natural_person, obj

    def search_employee(self, pk, registry):
        employee = None
        if pk:
            employee = Servidor.objects.filter(pk=int(pk)).last()
        if registry and not employee:
            employee = Servidor.objects.filter(matricula=registry).last()
        return employee

    def save_employee(self, natural_person=None):
        obj = {"success": True, "errors": []}
        permission = False
        employee = None
        pk = self.request.POST.get("servidor", None)
        registry = self.request.POST.get("matricula", None)

        try:
            permission = get_current_user().has_perm(
                "rh.add_servidor"
            ) or get_current_user().has_perm("rh.change_servidor")
            if not permission:
                raise Exception("Você não possui permissão para manipular servidor!")
            if not natural_person:
                raise Exception(
                    "Dados de servidor não persistidos. Pessoa Física não encontrada."
                )
            elif not registry:
                raise Exception(
                    "Dados de servidor não persistidos. Matrícula não informada."
                )

            employee = self.search_employee(pk, registry)
            matricula_origem = self.request.POST.get("matricula_origem", None)
            numero_cartao_ponto = self.request.POST.get("numero_cartao_ponto", None)
            numero_cartao_ponto = (
                None if numero_cartao_ponto == "" else numero_cartao_ponto
            )
            chefe_imediato = None
            try:
                if self.request.POST.get("chefe_imediato", None):
                    chefe_imediato = Servidor.objects.get(
                        pk=int(self.request.POST.get("chefe_imediato"))
                    )
            except Exception:
                pass
            organ_social_security = None
            try:
                if self.request.POST.get("organ_social_security", None):
                    organ_social_security = PessoaJuridica.objects.get(
                        pk=int(self.request.POST.get("organ_social_security"))
                    )
            except Exception:
                pass
            data_referencia_ferias = self.request.POST.get(
                "data_referencia_ferias", None
            )
            if data_referencia_ferias:
                data_referencia_ferias = DateUtils.str_to_date(data_referencia_ferias)
            else:
                data_referencia_ferias = None
            molestia = None
            try:
                if self.request.POST.get("molestia", None):
                    molestia = Molestia.objects.get(
                        pk=int(self.request.POST.get("molestia"))
                    )
            except Exception:
                pass

            classificacao = None

            if not employee:
                self.log.warn("Servidor não possui instância e será persistido.")
                employee = Servidor(
                    pessoa_fisica=natural_person,
                    data_referencia_ferias=data_referencia_ferias,
                    matricula=registry,
                    matricula_origem=matricula_origem,
                    numero_cartao_ponto=numero_cartao_ponto,
                    classificacao=classificacao,
                    molestia=molestia,
                    chefe_imediato=chefe_imediato,
                )
                employee.clean_fields()
                employee.save()
            else:
                self.log.warn("Servidor será ataulizado.")
                employee.data_referencia_ferias = data_referencia_ferias
                employee.matricula = registry
                employee.matricula_origem = matricula_origem
                employee.numero_cartao_ponto = numero_cartao_ponto
                employee.classificacao = classificacao
                employee.molestia = molestia
                employee.chefe_imediato = chefe_imediato
                employee.clean_fields()
                employee.save()
        except ValidationError as err:
            self.log.exception(err)
            # RHServidorEspecializado._concat_validation_error(obj, {'message_err': unicode(err)})
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"message_err": err})
        return employee, obj

    def save_curso(self, servidor):
        obj = {"success": True, "errors": []}
        curso = None
        try:
            curso = servidor.curso.all()
            cursos_list = self.request.POST.getlist("curso")
            for c in cursos_list:
                if c not in curso:
                    servidor.curso.add(Curso.objects.get(pk=int(c)))
            servidor.save()
            curso = servidor.curso.all()
            for c in curso:
                if not str(c.pk) in cursos_list:
                    servidor.curso.remove(c)
            servidor.save()
            curso = servidor.curso.all()
        except Exception as e:
            self.log.exception(e)
            curso = None
            obj["success"] = False
            obj["errors"].append("Cursos não persistidos!")
        return curso, obj

    def save_document(self, natural_person):
        obj_final = {"success": True, "errors": []}
        titulo_eleitor, obj = self.save_doc_voter(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        cnh, obj = self.save_doc_cnh(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        professional_council, obj = self.save_doc_professional_council(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        ctps, obj = self.save_doc_ctps(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        pis_pasep, obj = self.save_doc_pis_pasep(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        nis, obj = self.save_doc_nis(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        reservista, obj = self.save_doc_reservist(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        ric, obj = self.save_doc_ric(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        rne, obj = self.save_doc_rne(natural_person)
        RHServidorEspecializado._concat_obj(obj_final, obj)

        return obj_final

    def save_doc_cnh(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.cnh
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = self.request.POST.get("cnh", None)
        data_validade = None
        if self.request.POST.get("cnh_validity_date", None):
            data_validade = DateUtils.str_to_date(
                self.request.POST.get("cnh_validity_date")
            )
        expedition_date = None
        if self.request.POST.get("cnh_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                self.request.POST.get("cnh_expedition_date")
            )
        state = self.request.POST.get("cnh_state", None)
        state = Estado.objects.get(pk=int(state)) if state else None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=CNH,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=data_validade,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.data_validade = data_validade
                document.estado_expedicao = state
                # document.clean()
                document.save(validate_mandatory=False)

            RHServidorEspecializado._concat_obj(
                obj, self.save_cnh_category(document)[1]
            )
            RHServidorEspecializado._concat_obj(
                obj, self.save_cnh_first_date(document)[1]
            )
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"cnh": err})
        return document, obj

    def save_cnh_category(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.cnh_category
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("cnh_categoria")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CNH_CATEGORIA, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"cnh_categoria": err}
            )
        return data_spec, obj

    def save_cnh_first_date(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.cnh_first_date
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("cnh_first_date")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CNH_FIRST_DATE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"cnh_first_date": err}
            )
        return data_spec, obj

    def save_doc_ctps(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.ctps
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = self.request.POST.get("ctps", None)
        state = self.request.POST.get("ctps_state", None)
        state = Estado.objects.get(pk=int(state)) if state else None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=CTPS,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.estado_expedicao = state
                # document.clean()
                document.save(validate_mandatory=False)

            RHServidorEspecializado._concat_obj(obj, self.save_ctps_series(document)[1])
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"ctps": err})
        return document, obj

    def save_ctps_series(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.ctps_series
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = None
        if "serie_ctps" in self.request.POST:
            value = self.request.POST["serie_ctps"]
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CTPS_SERIE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"serie_ctps": err})
        return data_spec, obj

    def save_doc_pis_pasep(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.pis_pasep
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = None
        if "pis_pasep" in self.request.POST:
            number = self.request.POST["pis_pasep"]
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=PIS_PASEP,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save()
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"pis_pasep": err})
        return document, obj

    def save_doc_nis(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.nis
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = None
        if "nis" in self.request.POST:
            number = self.request.POST["nis"]
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=NIS,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save()
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"nis": err})
        return document, obj

    def save_doc_reservist(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.reservist
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = None
        if "reservista" in self.request.POST:
            number = self.request.POST["reservista"]
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RESERVISTA,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.save()
                    document.clean()
                    natural_person.documento.add(document)
            else:
                document.numero = number
                # document.clean()
                document.save()

            RHServidorEspecializado._concat_obj(
                obj, self.save_reservist_class(document)[1]
            )
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"reservista": err})
        return document, obj

    def save_reservist_class(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.reservist_class
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = None
        if "classe_reservista" in self.request.POST:
            value = self.request.POST["classe_reservista"]
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RESERVISTA_CLASSE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"classe_reservista": err}
            )
        return data_spec, obj

    def save_doc_professional_council(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.professional_council
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        try:
            number = self.request.POST.get("professional_council")
            validity_date = None
            if self.request.POST.get("professional_council_validity_date", None):
                validity_date = DateUtils.str_to_date(
                    self.request.POST.get("professional_council_validity_date")
                )
            expedition_date = None
            if self.request.POST.get("professional_council_expedition_date"):
                expedition_date = DateUtils.str_to_date(
                    self.request.POST.get("professional_council_expedition_date")
                )
            state = self.request.POST.get("professional_council_state", None)
            state = Estado.objects.get(pk=int(state)) if state else None

            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=PROFESSIONAL_COUNCIL,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=validity_date,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.data_validade = validity_date
                document.estado_expedicao = state
                # document.clean()
                document.save(validate_mandatory=False)

            RHServidorEspecializado._concat_obj(
                obj, self.save_doc_professional_council_issuer(document)[1]
            )
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"professional_council": err}
            )
        return document, obj

    def save_doc_professional_council_issuer(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.professional_council_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("professional_council_issuer", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=PROFESSIONAL_COUNCIL_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"professional_council_issuer": err}
            )
        return data_spec, obj

    def save_doc_voter(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.voter
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)
        if not save_update:
            return document

        number = self.request.POST.get("titulo_eleitor", None)
        city = self.request.POST.get("municipio_titulo", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=TITULO_ELEITOR,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=(
                            Localidade.objects.get(pk=int(city)).estado
                            if city
                            else None
                        ),
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                # document.clean()
                document.save(validate_mandatory=False)

            RHServidorEspecializado._concat_obj(obj, self.save_voter_zone(document)[1])
            RHServidorEspecializado._concat_obj(
                obj, self.save_voter_section(document)[1]
            )
            RHServidorEspecializado._concat_obj(obj, self.save_voter_city(document)[1])

            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"titulo_eleitor": "Não foi possível salvar título eleitor!"}
            )
        return document, obj

    def save_voter_zone(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.voter_zone
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("zona_titulo", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_ZONA, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"zona_titulo": err})
        return data_spec, obj

    def save_voter_section(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.voter_section
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("secao_titulo")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_SECAO, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"secao_titulo": err})
        return data_spec, obj

    def save_voter_city(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.voter_city
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = self.request.POST.get("municipio_titulo")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_MUNICIPIO, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(
                obj, {"municipio_titulo": err}
            )
        return data_spec, obj

    def save_doc_ric(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.ric
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = self.request.POST.get("ric", None)
        expedition_date = None
        if self.request.POST.get("ric_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                self.request.POST["ric_expedition_date"]
            )
        state = None
        if self.request.POST["ric_state"]:
            state = Estado.objects.get(pk=self.request.POST["ric_state"])
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RIC,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.estado_expedicao = state
                # document.clean()
                document.save(validate_mandatory=False)
            RHServidorEspecializado._concat_obj(obj, self.save_ric_issuer(document)[1])
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"ric": err})
        return document, obj

    def save_ric_issuer(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.ric_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = None
        if "ric_issuer" in self.request.POST:
            value = self.request.POST["ric_issuer"]
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RIC_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"ric_issuer": err})
        return data_spec, obj

    def save_doc_rne(self, natural_person, save_update=True):
        obj = {"success": True, "errors": []}
        document = natural_person.rne
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        if not save_update:
            return document

        number = self.request.POST.get("rne", None)
        expedition_date = None
        if self.request.POST.get("rne_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                self.request.POST["rne_expedition_date"]
            )
        state = None
        if self.request.POST["rne_state"]:
            state = Estado.objects.get(pk=self.request.POST["rne_state"])
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RNE,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.estado_expedicao = state
                # document.clean()
                document.save(validate_mandatory=False)
            RHServidorEspecializado._concat_obj(obj, self.save_rne_issuer(document)[1])
            if document:
                document.clean()
                document.save()
        except ValidationError as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, err)
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"rne": err})
        return document, obj

    def save_rne_issuer(self, document, save_update=True):
        obj = {"success": True, "errors": []}
        data_spec = None
        if document:
            data_spec = document.rne_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        if not save_update:
            return data_spec

        value = None
        if "rne_issuer" in self.request.POST:
            value = self.request.POST["rne_issuer"]
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RNE_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHServidorEspecializado._concat_validation_error(obj, {"rne_issuer": err})
        return data_spec, obj

    def get_endereco(self, pessoa_fisica, save_update=True):
        obj = {"success": True, "errors": []}
        endereco = pessoa_fisica.address.last()
        if not endereco:
            self.log.warn("Endereço não encontrado!")
        return endereco, obj

    def get_telefone(self, pessoa_fisica, save_update=True):
        obj = {"success": True, "errors": []}
        telefone = pessoa_fisica.phone.all()
        if not telefone.exists():
            self.log.warn("Telefone não encontrado!")
        return telefone, obj


class RHPessoaSemDocumento(extjs.ExtWidget):

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.pessoa.PessoaSemDocumento()")

    @login_required(type="JSON")
    def search(self, args=[]):
        obj = {"result": []}
        for p in PessoaFisica.objects.filter(
            Q(nome__icontains=self.request.POST["valor"])
        ):
            obj["result"].append(
                {
                    "id": p.id,
                    "description": p,
                    "documento": {
                        "icon": (
                            "static/engine/images/icons/athenas-0073.png"
                            if p.cpf != ""
                            else "static/engine/images/icons/athenas-0134.png"
                        ),
                        "title": "Possui CPF" if p.cpf != "" else "Não possui CPF",
                        "alt": "Possui CPF" if p.cpf != "" else "Não possui CPF",
                    },
                }
            )
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_data_pessoa(self, args=[]):
        obj = {"pessoa_fisica": [], "endereco": [], "telefone": []}
        try:
            pessoa_fisica = PessoaFisica.objects.get(pk=self.request.POST["pessoa"])
            obj["pessoa_fisica"].append(
                {
                    "nome": pessoa_fisica.nome if pessoa_fisica.nome else "",
                    "social_name": (
                        pessoa_fisica.social_name if pessoa_fisica.social_name else ""
                    ),
                    "sexo": pessoa_fisica.sexo if pessoa_fisica.sexo else "",
                    "sangue": pessoa_fisica.sangue if pessoa_fisica.sangue else "",
                    "estado_civil": (
                        pessoa_fisica.estado_civil if pessoa_fisica.estado_civil else ""
                    ),
                    "municipio_naturalidade": (
                        pessoa_fisica.municipio_naturalidade.pk
                        if pessoa_fisica.municipio_naturalidade
                        else ""
                    ),
                    "raca_cor": (
                        pessoa_fisica.raca_cor if pessoa_fisica.raca_cor else ""
                    ),
                    "email_institucional": (
                        pessoa_fisica.email_institucional
                        if pessoa_fisica.email_institucional
                        else ""
                    ),
                    "email_pessoal": (
                        pessoa_fisica.email_pessoal
                        if pessoa_fisica.email_pessoal
                        else ""
                    ),
                    "data_nascimento": (
                        DateUtils.date_to_str(pessoa_fisica.data_nascimento)
                        if pessoa_fisica.data_nascimento
                        else ""
                    ),
                    "data_obito": (
                        DateUtils.date_to_str(pessoa_fisica.data_obito)
                        if pessoa_fisica.data_obito
                        else ""
                    ),
                    "fator_rh": (
                        pessoa_fisica.fator_rh if pessoa_fisica.fator_rh else ""
                    ),
                    "doador": pessoa_fisica.doador,
                    "nome_pai": (
                        pessoa_fisica.nome_pai if pessoa_fisica.nome_pai else ""
                    ),
                    "nome_mae": (
                        pessoa_fisica.nome_mae if pessoa_fisica.nome_mae else ""
                    ),
                }
            )
            rhservidor = RHServidorEspecializado(self.request, self.response)
            endereco = rhservidor.get_endereco(pessoa_fisica, False)[0]
            if endereco:
                obj["endereco"].append(
                    {
                        "tipo_endereco": (
                            endereco.tipo_endereco if endereco.tipo_endereco else ""
                        ),
                        "municipio": (
                            endereco.municipio.pk if endereco.municipio else ""
                        ),
                        "tipo_logradouro": (
                            endereco.tipo_logradouro if endereco.municipio else ""
                        ),
                        "logradouro": (
                            endereco.logradouro if endereco.logradouro else ""
                        ),
                        "numero": endereco.numero if endereco.numero else "",
                        "cep": endereco.cep if endereco.cep else "",
                        "bairro": endereco.bairro if endereco.bairro else "",
                        "complemento": (
                            endereco.complemento if endereco.complemento else ""
                        ),
                    }
                )
            telefone = rhservidor.get_telefone(pessoa_fisica, False)
            telefone1 = None
            if len(telefone) > 0:
                telefone1 = telefone[0].numero
            telefone2 = None
            if len(telefone) > 1:
                telefone2 = telefone[1].numero
            if telefone:
                obj["telefone"].append(
                    {
                        "numero_telefone1": telefone1 if telefone1 else "",
                        "numero_telefone2": telefone2 if telefone2 else "",
                    }
                )
            else:
                obj["telefone"].append({"numero_telefone1": "", "numero_telefone2": ""})
        except Exception as e:
            self.log.exception(e)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def validate(self, args=[]):
        obj = {"result": True, "errors": []}
        if len(args) > 0 and args[0] == "pessoa_validate":
            obj = self.pessoa_validate()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def pessoa_validate(self, args=[]):
        obj = {"success": True, "errors": []}
        if self.request.POST["nome"] == "":
            obj["success"] = False
            obj["errors"].append(["nome", "Nome não informado!"])
        return obj

    @login_required(type="JSON")
    def commit(self, args=[]):
        obj = {"success": True, "errors": []}
        if len(args) > 0 and args[0] == "pessoa_commit":
            obj = self.pessoa_commit()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def pessoa_commit(self, args=[]):
        obj = {"success": True, "errors": [], "pessoa": None}
        linelog = LineLog(level=65, status=0)
        linelog.read_request(self.request)
        obj_pessoa = {"success": False, "errors": []}

        # rhservidor = RHServidorEspecializado(self.request, self.response)
        self.log.warn("tentanto salvar pessoa_fisica-------------------------")
        pessoa_fisica = None
        if "pessoa" in self.request.POST and self.request.POST["pessoa"] != "":
            pessoa_fisica = PessoaFisica.objects.get(pk=self.request.POST["pessoa"])
        pessoa_fisica, obj_pessoa = self.save_pessoa_fisica(pessoa_fisica)
        obj["pessoa"] = pessoa_fisica.pk if pessoa_fisica else None
        if obj_pessoa["success"] is False:
            obj["success"] = False
            obj["errors"].append(["nome", "Dados de Pessoa Física não persistidos!"])
        if obj["success"] is False:
            linelog.status = 0
            err = ""
            for o in obj["errors"]:
                err += " - " + o
            linelog.json_description["messageException"] = err
        linelog.save()
        return obj

    def save_pessoa_fisica(self, pessoa_fisica):
        self.log.warn("save_pessoa_fisica 2")
        obj = {"success": True, "errors": []}
        nome = self.request.POST.get("nome")
        cpf = None
        rg = None
        sexo = None
        try:
            if self.request.POST["sexo"] != "":
                sexo = self.request.POST["sexo"]
        except Exception:
            self.log.warn("Campo sexo não está no POST!")
        sangue = None
        try:
            if self.request.POST["sangue"] != "":
                sangue = self.request.POST["sangue"]
        except Exception:
            self.log.warn("Campo sangue não está no POST!")
        estado_civil = None
        try:
            if self.request.POST["estado_civil"] != "":
                estado_civil = self.request.POST["estado_civil"]
        except Exception:
            self.log.warn("Campo estado_civil não está no POST!")
            obj.update({"success": False})
            obj["errors"].append("Estado civil não informado!")
        municipio_naturalidade = None
        try:
            municipio_naturalidade = Localidade.objects.get(
                pk=int(self.request.POST["municipio_naturalidade"])
            )
        except Exception:
            self.log.warn("Campo municipio_naturalidade não está no POST!")
        raca_cor = 0
        try:
            if self.request.POST["raca_cor"] != "":
                raca_cor = self.request.POST["raca_cor"]
        except Exception:
            self.log.warn("Campo raca_cor não está no POST!")
            obj.update({"success": False})
            obj["errors"].append("Raça/cor não informado!")
        email_institucional = None
        try:
            if self.request.POST["email_institucional"] != "":
                email_institucional = self.request.POST["email_institucional"]
        except Exception:
            self.log.warn("Campo email_institucional não está no POST!")
        email_pessoal = None
        try:
            if self.request.POST["email_pessoal"] != "":
                email_pessoal = self.request.POST["email_pessoal"]
        except Exception:
            self.log.warn("Campo email_pessoal não está no POST!")
        data_nascimento = None
        try:
            if self.request.POST["data_nascimento"] != "":
                data_nascimento = DateUtils.str_to_date(
                    self.request.POST["data_nascimento"]
                )
        except Exception:
            self.log.warn("Campo data_nascimento não está no POST!")
        data_obito = None
        try:
            if self.request.POST["data_obito"] != "":
                data_obito = DateUtils.str_to_date(self.request.POST["data_obito"])
        except Exception:
            self.log.warn("Campo data_obito não está no POST!")
        rg_orgao = None
        rg_data_expedicao = None
        rg_uf = None
        fator_rh = None
        try:
            if self.request.POST["fator_rh"] != "":
                fator_rh = self.request.POST["fator_rh"]
        except Exception:
            self.log.warn("Campo fator_rh não está no POST!")
        doador = False
        try:
            if self.request.POST["doador"] == "on":
                doador = True
        except Exception:
            self.log.warn("Campo doador não está no POST!")
        nome_pai = None
        try:
            if self.request.POST["nome_pai"] != "":
                nome_pai = self.request.POST["nome_pai"]
        except Exception:
            self.log.warn("Campo nome_pai não está no POST!")
        nome_mae = None
        try:
            if self.request.POST["nome_mae"] != "":
                nome_mae = self.request.POST["nome_mae"]
        except Exception:
            self.log.warn("Campo nome_mae não está no POST!")
        nome_conjuge = None
        foto = None
        try:
            with transaction.atomic():
                if not pessoa_fisica:
                    pessoa_fisica = PessoaFisica(
                        nome=nome,
                        estado_civil=estado_civil,
                        raca_cor=raca_cor,
                        doador=doador,
                        cpf=cpf,
                        rg=rg,
                        sexo=sexo,
                        sangue=sangue,
                        municipio_naturalidade=municipio_naturalidade,
                        email_institucional=email_institucional,
                        email_pessoal=email_pessoal,
                        data_nascimento=data_nascimento,
                        data_obito=data_obito,
                        rg_orgao=rg_orgao,
                        rg_data_expedicao=rg_data_expedicao,
                        rg_uf=rg_uf,
                        fator_rh=fator_rh,
                        nome_pai=nome_pai,
                        nome_mae=nome_mae,
                        nome_conjuge=nome_conjuge,
                        foto=foto,
                    )
                    pessoa_fisica.save_sem_cpf()
                else:
                    pessoa_fisica.nome = nome
                    pessoa_fisica.sexo = sexo
                    pessoa_fisica.sangue = sangue
                    pessoa_fisica.estado_civil = estado_civil
                    pessoa_fisica.municipio_naturalidade = municipio_naturalidade
                    pessoa_fisica.raca_cor = raca_cor
                    pessoa_fisica.email_institucional = email_institucional
                    pessoa_fisica.email_pessoal = email_pessoal
                    pessoa_fisica.data_nascimento = data_nascimento
                    pessoa_fisica.data_obito = data_obito
                    pessoa_fisica.fator_rh = fator_rh
                    pessoa_fisica.doador = doador
                    pessoa_fisica.nome_pai = nome_pai
                    pessoa_fisica.nome_mae = nome_mae
                    pessoa_fisica.save_sem_cpf()
        except Exception as err:
            pessoa_fisica = None
            obj.update({"success": False})
            obj["errors"].append(
                "Erro salvando dados pessoais! Verifique dados obrigatórios!"
            )
            self.log.exception(err)
        return pessoa_fisica, obj


class RHGestorProvimentos(extjs.ExtWidget):

    @login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        servidor = self.request.POST.get("servidor", None)
        if servidor and not servidor == "":
            # sort = self.request.POST['sort'] if 'sort' in self.request.POST else 'data_exercicio'
            # direction = self.request.POST['dir'] if 'dir' in self.request.POST else 'ASC'

            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            limit = (
                int(self.request.POST["limit"]) if "limit" in self.request.POST else 50
            )
            end = start + limit

            query = MovimentacaoPosse.objects.filter(
                servidor=Servidor.objects.get(pk=servidor)
            ).order_by("data_exercicio", "data_desligamento")

            obj.update(totalRows=query.count())
            query = query[start:end]
            result = []
            for posse in query:
                try:
                    provimento_dados_publicacao = (
                        str(posse.publicacao_movimentacao)
                        if posse.publicacao_movimentacao
                        else "Não existe!"
                    )
                    desligamento_dados_publicacao = "Não existe!"
                    controller_desligamento = ""
                    data_desligamento = ""
                    desligamento = ""
                    tipo_desligamento = ""
                    if hasattr(posse, "desligamento"):
                        desligamento_dados_publicacao = str(
                            posse.desligamento.publicacao_movimentacao
                            if posse.desligamento.publicacao_movimentacao
                            else "Não existe!"
                        )
                        controller_desligamento = "RHMovimentacaoDesligamento"
                        tipo_desligamento = "DESLIGADO - "
                        data_desligamento = DateUtils.date_to_str(
                            posse.desligamento.data_desligamento
                        )
                        desligamento = posse.desligamento.pk
                        try:
                            if posse.desligamento.movimentacaoaposentadoria:
                                controller_desligamento = "RHMovimentacaoAposentadoria"
                                tipo_desligamento = "APOSENTADO - "
                        except Exception:
                            pass

                    item = {
                        "pk": posse.pk,
                        "quadro": "%s%s" % (tipo_desligamento, str(posse.quadro)),
                        "tipo_cargo": str(posse.quadro.cargo.tipo_lei_cargo),
                        "data_exercicio": (
                            DateUtils.date_to_str(posse.data_exercicio)
                            if posse.data_exercicio
                            else ""
                        ),
                        "dados_provimento": provimento_dados_publicacao,
                        "provimento": TIPO_MOVIMENTACAO_CARREIRA[
                            posse.tipo_movcarreira
                        ],
                        "status": {
                            "icon": "/%s/static/engine/images/icons/%s"
                            % (
                                context,
                                (
                                    "athenas-0073.png"
                                    if posse.ativo
                                    else "athenas-0226.png"
                                ),
                            ),
                            "title": "Sim" if posse.ativo else "Não",
                            "alt": "Sim" if posse.ativo else "Não",
                        },
                        "publicacao_link": RHServidorEspecializado.get_parametro_download(
                            posse.publicacao_movimentacao
                        ),
                        "desligamento_publicacao_link": RHServidorEspecializado.get_parametro_download(
                            posse.desligamento.publicacao_movimentacao
                            if hasattr(posse, "desligamento")
                            else None
                        ),
                        "controller": (posse.controller),
                        "dados_desligamento": desligamento_dados_publicacao,
                        "data_desligamento": data_desligamento,
                        "desligamento": desligamento,
                        "controller_desligamento": controller_desligamento,
                        "bond": posse.bond,
                    }
                except Exception as e:
                    self.log.exception(e)
                else:
                    result.append(item)

            obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

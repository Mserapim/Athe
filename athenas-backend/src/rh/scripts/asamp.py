# -*- coding: utf-8 -*-

import codecs
import json

from django.db.models import Sum

from contrib.utils import DateUtils
from rh.gfp.models import ContraCheque, Folha, FolhaEvento
from rh.models import Servidor, UnidadeAdministrativa
from standard.models import Choice


def tipo_servidor(tipo_servidor):
    if tipo_servidor == "EF":
        return "Efetivo"
    elif tipo_servidor == "CM":
        return "Comissionado"
    elif tipo_servidor == "AC":
        return "Acordo Cooperação"
    else:
        return "VERIFICAR #####"


def run():
    f = Folha.objects.get(
        tipo_folha__titulo="NORMAL", periodo__mes=0o4, periodo__ano=2019
    )
    servidores = (
        FolhaEvento.objects.filter(evento__numero="53000", folha=f)
        .distinct()
        .values_list("servidor__pk", flat=True)
    )
    servidores = Servidor.objects.filter(pk__in=servidores)

    employers = []

    for s in servidores:
        all_endereco = s.pessoa_fisica.address.filter().first()
        unicode_endereco = (
            all_endereco.logradouro + " - " + all_endereco.numero
            if all_endereco.numero
            else "S/N"
        )
        # ultima_remuneracao = FolhaEvento.objects.filter()
        unidade_gestora = UnidadeAdministrativa.objects.filter(sigla="PGJ-TO").first()
        cc = ContraCheque.objects.get(servidor=s, folha=f, pensioner=None)
        json_servidor = {"servidor": []}
        servidor = {
            "cpf": s.pessoa_fisica.cpf,
            "nome": s.pessoa_fisica.nome,
            "rg": s.pessoa_fisica.rg,
            "data_nascimento": DateUtils.datetime_to_str(
                s.pessoa_fisica.data_nascimento
            ),
            "sexo": s.pessoa_fisica.sexo,
            "estado_civil": Choice.objects.get(
                app_label="rh",
                name="GRAU_PARENTESCO_CHOICES",
                value=s.pessoa_fisica.estado_civil,
            ).label,
            "cep": all_endereco.cep,
            "bairro": all_endereco.bairro,
            "endereco": unicode_endereco,
            "complemento": all_endereco.complemento,
            "numero": all_endereco.numero,
            "telefone": s.pessoa_fisica.phone.exclude(tipo_telefone=6).first(),
            "celular": s.pessoa_fisica.phone.filter(main=True).first(),
            "email": s.pessoa_fisica.email_institucional,
            "naturalidade_cidade": s.pessoa_fisica.municipio_naturalidade,
            "naturalidade_cep": s.pessoa_fisica.municipio_naturalidade.cep,
            "nome_mae": s.pessoa_fisica.nome_mae,
            "nome_pai": s.pessoa_fisica.nome_pai,
            "num_cartao_sus": "",
            "dados_profissionais": [],
            "dependentes": [],
        }

        servidor["dados_profissionais"].append(
            {
                "matricula": s.matricula,
                "pis": (
                    s.pessoa_fisica.pis_pasep.numero
                    if s.pessoa_fisica.pis_pasep
                    else ""
                ),
                "num_carteira_trabalho": (
                    s.pessoa_fisica.ctps.numero if s.pessoa_fisica.ctps else ""
                ),
                "serie_carteira_trabalho": (
                    s.pessoa_fisica.ctps.ctps_series.valor
                    if s.pessoa_fisica.ctps and s.pessoa_fisica.ctps.ctps_series
                    else ""
                ),
                "titulo_eleitor": (
                    s.pessoa_fisica.voter.numero if s.pessoa_fisica.voter else ""
                ),
                "vinculo": tipo_servidor(s.tipo_servidor),
                "esfera": "Estadual",
                "local_trabalho": s.workplace_only.first().lotacao,
                "salario": FolhaEvento.objects.filter(
                    contracheque=cc,
                    evento__numero__in=[
                        "00100",
                        "00400",
                        "00500",
                        "00600",
                        "01100",
                        "53020",
                    ],
                )
                .aggregate(salario=Sum("valor"))
                .get("salario"),
                "cargo": cc.cargo_efetivo if cc.cargo_efetivo else cc.cargo_comissao,
                "cod_unidade_gestora": "",
                "nome_unidade_gestora": unidade_gestora.nome,
                "cnpj_unidade_gestora": unidade_gestora.pessoa_juridica.cnpj,
                "data_admissao": DateUtils.datetime_to_str(s.data_exercicio),
            }
        )

        # dependentes = []
        for dep in s.dependentes.filter():
            json_dependente = {"dependente": []}
            json_dependente["dependente"].append(
                {
                    "nome": dep.pessoa_fisica.nome,
                    "cpf": dep.pessoa_fisica.cpf,
                    "rg": dep.pessoa_fisica.rg,
                    "data_nascimento": (
                        DateUtils.datetime_to_str(dep.pessoa_fisica.data_nascimento)
                        if dep.pessoa_fisica.data_nascimento
                        else ""
                    ),
                    "grau_parentesco": Choice.objects.get(
                        app_label="rh",
                        name="GRAU_PARENTESCO_CHOICES",
                        value=dep.grau_parentesco,
                    ).label,
                    "num_cartao_sus": "",
                }
            )
            servidor["dependentes"].append(json_dependente)
        json_servidor["servidor"].append(servidor)
        employers.append(json_servidor)

    with codecs.open("/app/root/text.txt", "w+", encoding="utf8") as arquivo:
        arquivo.write(
            json.dumps(employers, indent=2, ensure_ascii=False, encoding="utf8")
        )

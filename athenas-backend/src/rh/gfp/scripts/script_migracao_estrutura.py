# -*- coding: utf-8 -*-

import datetime

from django.db import transaction
from django.contrib.auth.models import User

from contrib.middleware import set_current_user
from rh.gfp.models import (
    CategoriaSalarial,
    Enquadramento,
    EstruturaTabelaSalarial,
    MovimentacaoEnquadramento,
    MovimentacaoProgressao,
    NivelSalarial,
    ReferenciaNiveis2D,
)

# Migrações das dependencias de aux. creche, após ser criado o modelo de dependencia
# em detrimento das informações existentes no proprio depenente
from rh.models import AnotacaoGeral, Cargo, Dependente, Publicacao, Servidor


@transaction.atomic
def migre_estrutura_lei2580():

    # -------------------------------------------------------------------------------------------
    #        "Criando Categorias para os cargos existentes, com base nos cargos do MPE"
    cat_padrao = CategoriaSalarial.objects.get_or_create(titulo="Padrão", tipo="H")
    cat_classe = CategoriaSalarial.objects.get_or_create(titulo="Classe", tipo="V")
    #        Criando as publicacoes que alteraram os valores da lei 1652/2005

    #       Criando todos os níveis salarias existentes na estrutura da lei 01652/2005 e dos membros
    publicacao = Publicacao.objects.get(pk=8068)  # Verificar qual o id da publicacao
    ESTRUTURAS = {
        "AME": {"IA": [1, 6], "IB": [2, 9], "IC": [3, 12]},
        "AMI": {"HA": [1, 6], "HB": [2, 9], "HC": [3, 12]},
        "OFD": {"GA": [1, 6], "GB": [2, 9], "GC": [3, 12]},
        "TME": {"FA": [1, 6], "FB": [2, 9], "FC": [3, 12]},
        "TCM": {"EA": [1, 6], "EB": [2, 9], "EC": [3, 12]},
        "MOP": {"DA": [1, 6], "DB": [2, 9], "DC": [3, 12]},
        "MOT": {"CA": [1, 6], "CB": [2, 9], "CC": [3, 12]},
        "AXE": {"BA": [1, 6], "BB": [2, 9], "BC": [3, 12]},
        "AXM": {"AA": [1, 6], "AB": [2, 9], "AC": [3, 12]},
        "DAM": {
            None: [1, 7],
        },
        "FC": {
            None: [1, 4],
        },
    }
    #        Criando as estruturas existentes e tabelas salariais para cada cargo efetivo do MPE
    print(
        "CRIANDO ESTRUTURA DAS TABELAS SALARIAIS: LEI 2580----------------------------"
    )
    for cod in ESTRUTURAS:

        print("CRIANDO : %s" % cod)
        tb = EstruturaTabelaSalarial.objects.get_or_create(
            codigo=cod,
            publicacao=publicacao,
            formatacao="{nivel_vertical}{nivel_horizontal}",
        )
        print("%s - %s" % (tb[0], "NOVO" if tb[1] else "---"))
        ordem = 1
        for classe in sorted(ESTRUTURAS[cod]):
            ns_classe, created = NivelSalarial.objects.get_or_create(
                categoria=cat_classe[0], ordem=ESTRUTURAS[cod][classe][0], valor=classe
            )
            for padrao in range(1, ESTRUTURAS[cod][classe][1] + 1):
                ns_padrao, created = NivelSalarial.objects.get_or_create(
                    categoria=cat_padrao[0], ordem=padrao, valor=padrao
                )
                rnc = ReferenciaNiveis2D.objects.get_or_create(
                    estrutura_salarial=tb[0],
                    nivel_horizontal=ns_padrao,
                    nivel_vertical=ns_classe,
                    ordem=ordem,
                )
                ordem += 1
                print("%s - %s : %s" % (rnc[0], rnc[1], rnc[0].ordem))

        # tbs = TabelaSalarial.objects.get_or_create(estrutura_salarial=tb[0], publicacao=publicacao)


def unmigre_estrutura_lei2580():
    publicacao = Publicacao.objects.get(pk=8068)  # Verificar qual o id da publicacao
    for ts in publicacao.estruturas_salariais.all():
        ts.delete()


@transaction.commit_on_success
def update_progressoes():
    print("ATUALIZANDO ANOTAÇÔES DAS PROGRESSÔES")

    pk_anot = [
        mp.anotacao_geral.pk
        for mp in MovimentacaoProgressao.objects.exclude(anotacao_geral=None)
    ]
    MovimentacaoProgressao.objects.exclude(anotacao_geral=None).update(
        anotacao_geral=None
    )
    AnotacaoGeral.objects.filter(pk__in=pk_anot).delete()

    for mp in MovimentacaoProgressao.objects.filter(
        movimentacao_posse__servidor__tipo="S",
        movimentacao_posse__quadro__cargo__tipo_lei_cargo="EF",
    ).order_by("movimentacao_posse__servidor"):
        try:
            progs = mp.movimentacao_posse.progressoes.filter(
                data_vigencia__lt=mp.data_vigencia
            ).order_by("-data_vigencia")
            valor_n = (
                int(mp.referencia_nivel2d.nivel_horizontal.valor)
                + ord(mp.referencia_nivel2d.nivel_vertical.valor)
                - 65
            )
            valor_a = (
                (
                    int(progs[0].referencia_nivel2d.nivel_horizontal.valor)
                    + (ord(progs[0].referencia_nivel2d.nivel_vertical.valor) - 65)
                )
                if progs
                else 0
            )
            if valor_n - 1 == valor_a:
                print(
                    "%s:%s(%s):%s(%s)"
                    % (
                        mp.movimentacao_posse.servidor,
                        mp.referencia_nivel2d,
                        valor_n,
                        progs[0] if progs else None,
                        valor_a,
                    )
                )
                mp.progressao_anterior = progs[0] if progs else None
                mp.save()
        except Exception:
            # print e
            print(
                "ERRO COM PROGRESSOES DO SERVIDOR %s" % mp.movimentacao_posse.servidor
            )


@transaction.atomic
def enquadrar(only_erros=False):

    for e in Enquadramento.objects.all().order_by("matricula"):
        s = Servidor.objects.get(matricula=e.matricula)
        ref_nova = ReferenciaNiveis2D.objects.get(sigla_cache=e.classe_padrao_prox)
        data_vigencia = datetime(2012, 5, 1).date()
        posses = s.get_posses_ativas(data_vigencia).filter(
            quadro__cargo__tipo_lei_cargo="EF"
        )
        if posses:
            posse_atual = posses[0]
            progs = posse_atual._progressoes.order_by("-data_vigencia")
            if progs:
                prog_atual = progs[0]
                if str(prog_atual) != e.classe_padrao_atual:
                    print("DIF CP %s:%s:%s" % (prog_atual, e.classe_padrao_atual, s))
                data_admissao = posse_atual.data_admissao
                if data_admissao != e.data_exercicio:
                    print(
                        "DIF DATAS %s:%s:%s"
                        % (data_admissao, s.data_referencia_ferias, s)
                    )
                # data_referencia = datetime(2012 ,data_admissao.month, data_admissao.day).date()
                # # if s.data_referencia_ferias and s.data_referencia_ferias > posse_atual.data_exercicio:
                # #     data_referencia = datetime(
                #     2012 ,s.data_referencia_ferias.month, s.data_referencia_ferias.day).date()
                # # else: data_referencia = datetime(
                #     2012 ,posse_atual.data_exercicio.month, posse_atual.data_exercicio.day).date()

                # if data_referencia > data_vigencia:
                #     data_referencia = datetime(2011 ,data_admissao.month, data_admissao.day).date()
                # data_referencia = data_referencia if ref_nova.ordem>1 else data_admissao
                if not only_erros:
                    enq, created = MovimentacaoEnquadramento.objects.get_or_create(
                        servidor=s,
                        publicacao_movimentacao=Publicacao.objects.get(pk=8131),
                        progressao_anterior=prog_atual,
                        movimentacao_posse=posse_atual,
                        referencia_nivel2d=ref_nova,
                        anota=True,
                        indireto=True,
                        data_vigencia=data_vigencia,
                    )
                    enq.data_referencia = e.data_referencia
                    try:
                        enq.save()
                    except Exception:
                        print(
                            "ERRO (%s) %s:%s:%s:%s"
                            % (
                                "N" if created else "A",
                                enq.progressao_anterior,
                                enq.data_referencia.strftime("%d/%m/%Y"),
                                ref_nova,
                                s,
                            )
                        )
                    else:
                        pass
            else:
                print("PROG:::%s" % s)
        else:
            print("POSSE:::%s" % s)


@transaction.atomic
def update_cargos_referencias():
    for c in Cargo.objects.filter(
        tipo_lei_cargo="EF",
        codigo__in=[
            "AME",
            "AMI",
            "OFD",
            "MOP",
            "AXE",
            "MOT",
            "AXM",
            "TME",
            "TCM",
            "DAM",
            "FC",
        ],
    ):
        for es in EstruturaTabelaSalarial.objects.filter(
            codigo=c.codigo, publicacao__numero="02580"
        ):
            for r2d in es.referencias_niveis.all():
                if c not in r2d.cargos.all():
                    print(r2d, c.codigo, c)
                    r2d.cargos.add(c, bulk=False)


@transaction.atomic
def update_cargos_referencias_cm():
    for c in Cargo.objects.filter(
        referencias_salariais__estrutura_salarial__publicacao__numero__in=[
            "01651",
            "01878",
        ]
    ):
        ref = ReferenciaNiveis2D.objects.get(
            cargos=c, estrutura_salarial__publicacao__numero__in=["01651", "01878"]
        )
        ref_nova = ReferenciaNiveis2D.objects.get(
            sigla_cache=ref.sigla_cache,
            estrutura_salarial__publicacao__numero__in=["02580"],
            estrutura_salarial__codigo__in=["DAM", "FC"],
        )
        if c not in ref_nova.cargos.all():
            print(ref_nova, c.codigo, c)
            ref_nova.cargos.add(c, bulk=False)


set_current_user(User.objects.get(username="athenas"))
for dep in Dependente.objects.filter(auxilio_creche=True):
    print(
        dep,
        dep.dependencias.create(
            tipo=4,
            data_inicio=dep.data_inicio or dep.pessoa_fisica.data_nascimento,
            idade_limite=6,
        ),
    )

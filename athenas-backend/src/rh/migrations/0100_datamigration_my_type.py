# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_my_type_mov(apps, schema_editor):
    print("ATUALIZACAO DE MOVIMENTACAOPESSOAL my_type")
    MovimentacaoPessoalModel = apps.get_model("rh", "MovimentacaoPessoal")
    updated = 1
    movs = MovimentacaoPessoalModel.objects.filter(my_type=None)
    total = movs.count()
    for mov in movs:
        MovimentacaoPessoalModel.objects.filter(pk=mov.pk).update(
            my_type=instance_model_mov(mov)._meta.model_name
        )
        print("ATUALIZACAO DE MOVIMENTACAOPESSOAL my_type: %s de %s" % (updated, total))
        updated += 1


def migrate_my_type_an(apps, schema_editor):
    print("ATUALIZACAO DE ANOTACAOGERAL my_type")
    AnnotationModel = apps.get_model("rh", "AnotacaoGeral")
    updated = 1
    ans = AnnotationModel.objects.filter(my_type=None)
    total = ans.count()
    for mov in ans:
        AnnotationModel.objects.filter(pk=mov.pk).update(
            my_type=instance_model_an(mov)._meta.model_name
        )
        print("ATUALIZACAO DE ANOTACAOGERAL my_type:  %s de %s" % (updated, total))
        updated += 1


def instance_model_an(instance):
    if hasattr(instance, "anotacaocarreira"):
        instance = instance.anotacaocarreira
    elif hasattr(instance, "anotacaocomunicacao"):
        instance = instance.anotacaocomunicacao
    elif hasattr(instance, "anotacaoelogio"):
        instance = instance.anotacaoelogio
    elif hasattr(instance, "anotacaoenquadramento"):
        instance = instance.anotacaoenquadramento
    elif hasattr(instance, "anotacaoevento"):
        instance = instance.anotacaoevento
    elif hasattr(instance, "anotacaofalta"):
        instance = instance.anotacaofalta
    elif hasattr(instance, "anotacaoferias"):
        instance = instance.anotacaoferias
    elif hasattr(instance, "anotacaogratificacao"):
        instance = instance.anotacaogratificacao
    elif hasattr(instance, "anotacaohorarioespecial"):
        instance = instance.anotacaohorarioespecial
    elif hasattr(instance, "anotacaolicenca"):
        instance = instance.anotacaolicenca
    elif hasattr(instance, "anotacaopenadisciplinar"):
        instance = instance.anotacaopenadisciplinar
    elif hasattr(instance, "anotacaorecesso"):
        instance = instance.anotacaorecesso
    elif hasattr(instance, "anotacaofolgaeleitoral"):
        instance = instance.anotacaofolgaeleitoral
    elif hasattr(instance, "anotacaofolgaaniversario"):
        instance = instance.anotacaofolgaaniversario
    elif hasattr(instance, "anotacaofolgacompensacao"):
        instance = instance.anotacaofolgacompensacao
    elif hasattr(instance, "anotacaoBancodeHoras"):
        instance = instance.anotacaoBancodeHoras
    elif hasattr(instance, "anotacaoplantao"):
        instance = instance.anotacaoplantao
    elif hasattr(instance, "anotacaoviagem"):
        instance = instance.anotacaoviagem
    elif hasattr(instance, "anotacaoremocao"):
        instance = instance.anotacaoremocao
    elif hasattr(instance, "anotacaotempoDobro"):
        instance = instance.anotacaotempoDobro
    elif hasattr(instance, "anotacaotempoServico"):
        instance = instance.anotacaotempoServico
    elif hasattr(instance, "anotacaotransposicao"):
        instance = instance.anotacaotransposicao
    elif hasattr(instance, "anotacaoafastamento"):
        instance = instance.anotacaoafastamento
    elif hasattr(instance, "anotacaoausencia"):
        instance = instance.anotacaoausencia
    return instance


def instance_model_mov(instance):
    if hasattr(instance, "movimentacaoposse"):
        instance = instance.movimentacaoposse
        if hasattr(instance, "movimentacaoaproveitamento"):
            instance = instance.movimentacaoaproveitamento
        elif hasattr(instance, "movimentacaopromocao"):
            instance = instance.movimentacaopromocao
            if hasattr(instance, "movimentacaotitularizacao"):
                instance = instance.movimentacaotitularizacao
        elif hasattr(instance, "movimentacaoremocaomembro"):
            instance = instance.movimentacaoremocaomembro
        elif hasattr(instance, "movimentacaoreadaptacao"):
            instance = instance.movimentacaoreadaptacao
        elif hasattr(instance, "movimentacaoreconducao"):
            instance = instance.movimentacaoreconducao
        elif hasattr(instance, "movimentacaoreintegracao"):
            instance = instance.movimentacaoreintegracao
        elif hasattr(instance, "movimentacaoreversao"):
            instance = instance.movimentacaoreversao
    elif hasattr(instance, "movimentacaodesligamento"):
        instance = instance.movimentacaodesligamento
        if hasattr(instance, "movimentacaoaposentadoria"):
            instance = instance.movimentacaoaposentadoria
    elif hasattr(instance, "movimentacaorequisicao"):
        instance = instance.movimentacaorequisicao
    elif hasattr(instance, "movimentacaosubstituicao"):
        instance = instance.movimentacaosubstituicao
        if hasattr(instance, "movimentacaosubstituicaomembro"):
            instance = instance.movimentacaosubstituicaomembro
    elif hasattr(instance, "movimentacaoconcessao"):
        instance = instance.movimentacaoconcessao
    elif hasattr(instance, "movimentacaoremocao"):
        instance = instance.movimentacaoremocao
    elif hasattr(instance, "movimentacaoredistribuicao"):
        instance = instance.movimentacaoredistribuicao
    elif hasattr(instance, "movimentacaodescontoLegal"):
        instance = instance.movimentacaodescontoLegal
    elif hasattr(instance, "movimentacaoestabilizacao"):
        instance = instance.movimentacaoestabilizacao
    elif hasattr(instance, "declaracaoatividade"):
        instance = instance.declaracaoatividade
    elif hasattr(instance, "movimentacaoprogressao"):
        instance = instance.movimentacaoprogressao
        if hasattr(instance, "movimentacaoenquadramento"):
            instance = instance.movimentacaoenquadramento
    elif hasattr(instance, "baselicencaafastamento"):
        instance = instance.baselicencaafastamento
        if hasattr(instance, "afastamento"):
            instance = instance.afastamento
            if hasattr(instance, "afastamentocompeticao"):
                instance = instance.afastamentocompeticao
            elif hasattr(instance, "afastamentocursoconcurso"):
                instance = instance.afastamentocursoconcurso
            elif hasattr(instance, "afastamentodeslocamento"):
                instance = instance.afastamentodeslocamento
            elif hasattr(instance, "afastamentoeleitoral"):
                instance = instance.afastamentoeleitoral
            elif hasattr(instance, "afastamentoestudar"):
                instance = instance.afastamentoestudar
            elif hasattr(instance, "afastamentomandatoeletivo"):
                instance = instance.afastamentomandatoeletivo
            elif hasattr(instance, "afastamentomissao"):
                instance = instance.afastamentomissao
            elif hasattr(instance, "afastamentodisponibilidade"):
                instance = instance.afastamentodisponibilidade
            elif hasattr(instance, "afastamentooutroorgao"):
                instance = instance.afastamentooutroorgao
            elif hasattr(instance, "afastamentoprisao"):
                instance = instance.afastamentoprisao
            elif hasattr(instance, "afastamentosuspensao"):
                instance = instance.afastamentosuspensao
            elif hasattr(instance, "afastamentocomparecimentojuizo"):
                instance = instance.afastamentocomparecimentojuizo
            elif hasattr(instance, "afastamentoservirjuri"):
                instance = instance.afastamentoservirjuri
            elif hasattr(instance, "afastamentotreinamento"):
                instance = instance.afastamentotreinamento
        elif hasattr(instance, "licenca"):
            instance = instance.licenca
            if hasattr(instance, "licencaafastamentoconjuge"):
                instance = instance.licencaafastamentoconjuge
            elif hasattr(instance, "licencaatividadepolitica"):
                instance = instance.licencaatividadepolitica
            elif hasattr(instance, "licencacapacitacao"):
                instance = instance.licencacapacitacao
            elif hasattr(instance, "licencainteresseparticular"):
                instance = instance.licencainteresseparticular
            elif hasattr(instance, "licencamandatoclassista"):
                instance = instance.licencamandatoclassista
            elif hasattr(instance, "licencaservicomilitar"):
                instance = instance.licencaservicomilitar
            elif hasattr(instance, "licencasaude"):
                instance = instance.licencasaude
                if hasattr(instance, "licencasaude3dias"):
                    instance = instance.licencasaude3dias
                elif hasattr(instance, "licencasaude30dias"):
                    instance = instance.licencasaude30dias
                elif hasattr(instance, "baselicencasaudejuntamedica"):
                    instance = instance.baselicencasaudejuntamedica
                    if hasattr(instance, "licencasaudejuntamedica"):
                        instance = instance.licencasaudejuntamedica
                    if hasattr(instance, "licencaadocao"):
                        instance = instance.licencaadocao
                    elif hasattr(instance, "licencadoencapessoafamilia"):
                        instance = instance.licencadoencapessoafamilia
                    elif hasattr(instance, "licencamaternidade"):
                        instance = instance.licencamaternidade
        elif hasattr(instance, "ausencia"):
            instance = instance.ausencia
            if hasattr(instance, "ausenciacasamento"):
                instance = instance.ausenciacasamento
            elif hasattr(instance, "ausenciaconclusao"):
                instance = instance.ausenciaconclusao
            elif hasattr(instance, "ausenciadoacaosangue"):
                instance = instance.ausenciadoacaosangue
            elif hasattr(instance, "ausenciaeleitor"):
                instance = instance.ausenciaeleitor
            elif hasattr(instance, "ausencianascimento"):
                instance = instance.ausencianascimento
            elif hasattr(instance, "ausenciafalecimento"):
                instance = instance.ausenciafalecimento
        elif hasattr(instance, "feriasafastamento"):
            instance = instance.feriasafastamento
        elif hasattr(instance, "viagem"):
            instance = instance.viagem
        elif hasattr(instance, "recesso"):
            instance = instance.recesso
        elif hasattr(instance, "folgacompensacao"):
            instance = instance.folgacompensacao
        elif hasattr(instance, "folgaeleitoral"):
            instance = instance.folgaeleitoral
        elif hasattr(instance, "folgaaniversario"):
            instance = instance.folgaaniversario
        elif hasattr(instance, "atuacaogrupotrabalho"):
            instance = instance.atuacaogrupotrabalho
        elif hasattr(instance, "desempenhofuncao"):
            instance = instance.desempenhofuncao
        elif hasattr(instance, "plantao"):
            instance = instance.plantao
        elif hasattr(instance, "bancodehoras"):
            instance = instance.bancodehoras
    return instance


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0099_auto_20191018_1745"),
    ]

    operations = [
        migrations.RunPython(migrate_my_type_mov, _null_function),
        migrations.RunPython(migrate_my_type_an, _null_function),
    ]

# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from contrib.utils import getLogger
from rh.gfp.models import MovimentacaoProgressao
from rh.afastamento.models import (
    FeriasAfastamento,
    Recesso,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeJuntaMedica,
    LicencaDoencaPessoaFamilia,
    LicencaMaternidade,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaServicoMilitar,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    AfastamentoDisponibilidade,
    HealthPrevent,
    AfastamentoOutroOrgao,
    AfastamentoMandatoEletivo,
    AfastamentoEstudar,
    AfastamentoMissao,
    AfastamentoEleitoral,
    AfastamentoServirJuri,
    AfastamentoTreinamento,
    AfastamentoDeslocamento,
    AfastamentoCompeticao,
    AfastamentoCursoConcurso,
    AfastamentoPrisao,
    AfastamentoSuspensao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
    AusenciaCasamento,
    AusenciaNascimento,
    AusenciaFalecimento,
    AusenciaConclusao,
    FolgaEleitoral,
    BancoDeHoras,
)


log = getLogger(__name__)


@receiver(post_save, sender=FeriasAfastamento)
@receiver(post_save, sender=Recesso)
@receiver(post_save, sender=LicencaSaude3Dias)
@receiver(post_save, sender=LicencaSaude30Dias)
@receiver(post_save, sender=LicencaSaudeJuntaMedica)
@receiver(post_save, sender=LicencaDoencaPessoaFamilia)
@receiver(post_save, sender=LicencaMaternidade)
@receiver(post_save, sender=LicencaAdocao)
@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaServicoMilitar)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaCapacitacao)
@receiver(post_save, sender=LicencaInteresseParticular)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=AfastamentoDisponibilidade)
@receiver(post_save, sender=HealthPrevent)
@receiver(post_save, sender=AfastamentoOutroOrgao)
@receiver(post_save, sender=AfastamentoMandatoEletivo)
@receiver(post_save, sender=AfastamentoEstudar)
@receiver(post_save, sender=AfastamentoMissao)
@receiver(post_save, sender=AfastamentoEleitoral)
@receiver(post_save, sender=AfastamentoServirJuri)
@receiver(post_save, sender=AfastamentoTreinamento)
@receiver(post_save, sender=AfastamentoDeslocamento)
@receiver(post_save, sender=AfastamentoCompeticao)
@receiver(post_save, sender=AfastamentoCursoConcurso)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=AfastamentoSuspensao)
@receiver(post_save, sender=AusenciaDoacaoSangue)
@receiver(post_save, sender=AusenciaEleitor)
@receiver(post_save, sender=AusenciaCasamento)
@receiver(post_save, sender=AusenciaNascimento)
@receiver(post_save, sender=AusenciaFalecimento)
@receiver(post_save, sender=AusenciaConclusao)
@receiver(post_save, sender=FolgaEleitoral)
@receiver(post_save, sender=BancoDeHoras)
def progression_departure_event(sender, instance, **kwargs):
    try:
        if instance.prorroga_progressao:
            progression = MovimentacaoProgressao.objects.filter(
                Q(servidor=instance.servidor)
            ).filter(
                Q(data_inicio_vigencia__lte=instance.data_inicio)
                & (
                    Q(data_fim_vigencia__gte=instance.data_inicio)
                    | Q(data_fim_vigencia=None)
                )
            )
            if progression.exists():
                progression = progression.last()
                result = progression.classcode.cls(progression).calculate()
                if (
                    progression.expected_date != result.get("expected_date")
                    or progression.dias_suspenso_afastamento
                    != result.get("dias_suspenso_afastamento")
                    or progression.initial_expected_date
                    != result.get("initial_expected_date")
                    or progression.period_absences != result.get("period_absences")
                ):
                    progression.save()
    except Exception as err:
        log.exception(err)

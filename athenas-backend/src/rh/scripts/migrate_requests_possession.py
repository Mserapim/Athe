# -.- coding: utf-8 -.-

from rh.models import EncargoFinanceiro, MovimentacaoRequisicao, PeriodoRequisicao
from datetime import date, timedelta
from contrib.middleware import set_current_user


def migrate_requests(registers=[], cut_date=None):
    set_current_user('athenas')

    if not cut_date:
        cut_date = date(2022, 1, 1)
    before_cut_date = cut_date - timedelta(days=1)

    query = MovimentacaoRequisicao.objects.
    (data=cut_date)
    if registers:
        query = query.filter(servidor__matricula__in=registers)

    for mq in query:
        print(f'MIGRANDO: ({mq.pk}) {mq}')
        MovimentacaoRequisicao.objects.filter(pk=mq.pk).update(data_fim=before_cut_date)
        new_mq = MovimentacaoRequisicao()
        new_mq.servidor = mq.servidor
        new_mq.orgao_origem = mq.orgao_origem
        new_mq.posse_origem = mq.posse_origem
        new_mq.onus = mq.onus
        new_mq.ativo = mq.ativo
        new_mq.data_inicio = cut_date
        new_mq.data_fim = mq.data_fim
        new_mq.category = mq.category
        new_mq.publicacao_movimentacao = mq.publicacao_movimentacao
        new_mq.data_alteracao = mq.data_alteracao
        new_mq.publicacao_alteracao = mq.publicacao_alteracao
        new_mq.texto = mq.texto
        new_mq.anota = mq.anota
        new_mq.save()
        print(f'> MQ CRIADO: ({new_mq.pk}) {new_mq}')
        for ef in mq.encargos_financeiros.filter(data_fim__gte=cut_date).order_by('-data_inicio'):
            print(f'>> EF: {ef}', end='')
            if ef.data_inicio >= cut_date:
                ups = EncargoFinanceiro.objects.filter(pk=ef.pk).update(requisicao=new_mq.pk)
                print(f'TO {new_mq.pk} ({ups})')
            else:
                dt_fim = ef.data_fim
                ups = EncargoFinanceiro.objects.filter(pk=ef.pk).update(data_fim=before_cut_date)
                print(f'EF DF {ef} ({ups})', end='')
                obj, created = new_mq.encargos_financeiros.update_or_create(
                    data_inicio=cut_date,
                    defaults={
                        'data_fim': dt_fim,
                        'remuneracao': ef.remuneracao,
                        'base_previdenciaria': ef.base_previdenciaria
                    }
                )
                print(f'TO EF {ef} ({created})', end='')
        for pr in mq.periodo.filter(data_fim__gte=cut_date).order_by('-data_inicio'):
            if pr.data_inicio >= cut_date:
                PeriodoRequisicao.objects.filter(pk=pr.pk).update(requisicao=new_mq.pk)
            else:
                dt_fim = pr.data_fim
                PeriodoRequisicao.objects.filter(pk=pr.pk).update(data_fim=before_cut_date)
                pr.save()
                new_mq.periodo.update_or_create(
                    data_inicio=cut_date,
                    defaults={
                        'data_fim': dt_fim,
                        'publicacao': pr.publicacao,
                    }
                )

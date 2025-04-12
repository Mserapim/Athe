# from django.db.models import Sum, Count
# from rh.gfp.models import FinancialReportPayroll
# from rh.gfp.planoconta.models import PlanoConta
# from standard.models import Choice


# def financial(payroll):
#     # payroll = models.ForeignKey(Folha, verbose_name='Folha', related_name='financial_summary', on_delete=models.CASCADE)
#     # account_plan = models.ForeignKey('planoconta.PlanoConta', on_delete=models.CASCADE, verbose_name='PlanoConta',
#     #                                  related_name='financial_summary')
#     # quantity = models.PositiveIntegerField(default=0, verbose_name='Quantidade')
#     # value = models.DecimalField(max_digits=19, decimal_places=2, default=0, verbose_name='Valor total')
#     # reference_year = models.PositiveSmallIntegerField(default=2020, verbose_name='Exercicio')
#     years = [fr['reference_year'] for fr in FinancialReportPayroll.objects.filter(payroll=payroll).order_by('-reference_year').values('reference_year').distinct()]
#     total = total_rp = total_tp = total_year = 0
#     q_account_plans = PlanoConta.objects.filter(plano__ano_calendario=2020, plano__folha_tipo=payroll.tipo_folha, finalidade=2)
#     rps = Choice.get_dict_choices_for('rh', 'REGIME_PREVIDENCIARIO')
#     tps = Choice.get_dict_choices_for('gfp', 'TIPO_PLANO')
#     print('*' * 100)
#     for rp in rps:
#         total_rp = 0
#         print(rps[rp])
#         for year in years:
#             total_year = 0
#             print(f'>>> {year}')
#             for tp in tps:
#                 print(f'   >>> {tps[tp]}')
#                 q_rp_account_plans = q_account_plans.filter(regime_previdenciario=rp, plano__tipo=tp)
#                 total_tp = 0
#                 for ap in q_rp_account_plans:
#                     fpr = FinancialReportPayroll.objects.filter(
#                         payroll=payroll,
#                         account_plan=ap,
#                         reference_year=year
#                     ).aggregate(qnt=Count('id'), value=Sum('value'))
#                     value = fpr.get('value', 0)
#                     if value:
#                         total_tp += value
#                         print(f'       >>> {value:.2f} {ap.plano}')
#                 if total_tp:
#                     print(f'   >>> {tps[tp]} {total_tp:.2f}')
#                     total_year += total_tp
#             if total_year:
#                 print(f'>>> {year} {total_year:.2f}')
#                 total_rp += total_year

#         if total_rp:
#             total += total_rp
#             print(f'{rps[rp]} {total_rp:.2f}')
#     print(f'TOTAL {total}')

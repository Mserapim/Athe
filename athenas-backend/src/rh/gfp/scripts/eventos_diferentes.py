# -*- coding: utf-8 -*-

import re
from django.db.models import Q, Max, F
from rh.gfp.models import FolhaEvento
from contrib.utils import getLogger
from dateutil.relativedelta import relativedelta

log = getLogger("script eventos diferentes")
# VERIFICANDO NOVOS CALCULOS ------------------------------------------------------------------------------------

# res =  re.match('^([0-9]{4,6})\.(valor|patronal)\=(.*);?$', str.replace(' ', ''))


# --------- ATUALIZAR FOLHAEVENTO DE FÉRIAS, ADICIONANDO O JSON_CALC_VARS com os ids dos PASUS -------------------
def get_pasu_by_pas(pas):
    pasus = (
        pas.usufrutos.filter(estado__in=[4, 8, 16, 32, 64, 128, 256])
        .exclude(
            Q(
                data_inicio__lt=pas.folha_evento_terco_constitucional.folha.date_range.first
            )
            | Q(
                data_inicio__gt=pas.folha_evento_terco_constitucional.folha.date_range.last
                + relativedelta(months=1)
            )
        )
        .order_by("data_inicio")
    )
    pasus_ = pasus.exclude(estado__in=[8, 16])
    pasu = pasus_.first() if pasus_ else pasus.first()
    return pasu


def update_calc_vars():
    print(">>>>>>>>>> UPDATING FolhaEvento calc_vars de férias...")
    updateds = FolhaEvento.objects.filter(evento__numero__in=["0234", "0236"]).update(
        json_calc_vars="{}"
    )
    print("... %d JSON_CALC_VARS de FolhaEvento zerados ...")
    updateds = 0
    for fe in (
        FolhaEvento.objects.filter(evento__numero__in=["0234", "0236"])
        .exclude(periodoaquisitivoservidor=None)
        .order_by("folha", "servidor")
    ):
        pks = []
        for pas in fe.periodoaquisitivoservidor_set.all():
            pasu = get_pasu_by_pas(pas)
            if pasu and pasu.pk not in pks:
                pks.append(pasu.pk)
        if pks:
            fe.vars = {"pasus_ids": pks}
            print(fe.folha, fe.servidor, fe.evento, fe.vars)
            updateds += 1
    print("... %d UPDATEDS")

    print(">>>>>>>>>> UPDATING FolhaEvento differences atributes...")
    updateds = FolhaEvento.objects.update(
        correct_valor=F("valor"),
        correct_contribution_base=F("base_previdencia"),
        correct_patronal=F("patronal"),
    )
    print("... %s UPDATEDS" % updateds)


# def create_provisions_13(year, month=None, ):
#     #CRIACAO DAS PROVISOES ------------------------------------------------
#     from rh.gfp.planoconta.models import ProvisionPlan
#     from rh.gfp.models import ContraCheque, FolhaEvento, Evento
#     from django.db import models
#     from rh.gfp.calcs.mpto.provisions import ChristmasGratificationProvision, ProvisionSocialSecurity
#     from datetime import datetime
#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     pp = ProvisionPlan.objects.get(type_provision=2)

#     print u'CREATING PROVISIONS - %s' % pp
#     matriculas = []

#     paid_events_value_ids = [ev.pk for ev in pp.paid_events_value.all()]
#     paid_events_employer_ids = [ev.pk for ev in pp.paid_events_employer.all()]

#     q_cc = ContraCheque.objects.filter(
#               models.Q(folha__periodo__ano=year) &
#               models.Q(folha__tipo_folha__principal=True)).order_by('-folha__periodo', 'servidor')
#     if month:
#         q_cc = q_cc.filter(folha__periodo__mes=month)

#     for cc in q_cc:
#         month = cc.folha.periodo.mes
#         print '%10s:%10s:%60s:' % (cc.servidor.data_exercicio, cc.servidor.data_desligamento or '', cc.servidor),
#         pe, created = pp.provisions_employee.get_or_create(
#             employee=cc.servidor,
#             info='%d' % cc.folha.periodo.ano,
#             defaults={
#                 'start_acquisition': max(cc.servidor.data_exercicio, datetime(cc.folha.periodo.ano, 1, 1).date()),
#                 'end_acquisition': min(cc.servidor.data_desligamento or datetime(
#                                       cc.folha.periodo.ano, 12, 31).date(),
#                                       datetime(cc.folha.periodo.ano, 12, 31).date())
#             }
#         )
#         print '%s:%10s:%10s:' % ('S' if created else 'N', pe.start_acquisition, pe.end_acquisition)

#         pm, created = pp.summaries.get_or_create(
#             reference_year=cc.folha.periodo.ano,
#             reference_month=cc.folha.periodo.mes if cc.folha.periodo.mes != 13 else 12,
#         )

#         prov, created = pe.provisions.get_or_create(
#             provision_manager=pm,
#             defaults={
#                 'provisioned_value': 0.0,
#                 'paid_value': 0.0,
#                 'provisioned_employer': 0.0,
#                 'paid_employer': 0.0,
#                 'previous_balance_value': 0.0,
#                 'previous_balance_employer': 0.0
#             }
#         )
#         q_events = FolhaEvento.objects.filter(contracheque__servidor=pe.employee)
#         if cc.folha.periodo.mes == 12:
#             q_events = q_events.filter(
#                 contracheque__folha__periodo__ano=cc.folha.periodo.ano,
#                 contracheque__folha__periodo__mes__in=[12, 13],
#             )
#         else:
#             q_events = q_events.filter(contracheque__folha__periodo=cc.folha.periodo)
#         # log.debug('PROVISION 13TH SALARY FOR %s' % (cc))
#         calc_prov = ChristmasGratificationProvision(cc.servidor, cc.folha).calculate()
#         calc_ss = ProvisionSocialSecurity(cc.servidor, cc.folha, params={
#                                   'base_value': calc_prov.get('base_previdencia', 0.00)}).calculate()
#         # log.debug('PROVISION 13TH SALARY %7.2f/%7.2f/%7.2f/%7.2f %s' % (
#               round(calc_prov.get('valor_base', 0.00), 2),
#               round(calc_prov.get('valor', 0.00), 2),
#               round(calc_prov.get('base_previdencia', 0.00), 2),
#               round(calc_ss.get('patronal', 0.00), 2), cc))
#         total_values = q_events.filter(evento__pk__in=paid_events_value_ids).aggregate(
#                           value=models.Sum('value'))['value'] or 0.00
#         calc_ss_paid = ProvisionSocialSecurity(cc.servidor, cc.folha, params={'base_value': total_values})
#         total_employer = float(calc_ss_paid.value())
#         # total_employer = q_events.filter(evento__pk__in=paid_events_employer_ids).aggregate(
#                               value=models.Sum('employer_contribution'))['value'] or 0.00
#         prov.paid_value = total_values * -1
#         prov.paid_employer = total_employer * -1
#         prov.provisioned_value = calc_prov.get('valor_base', 0.00) / pe.quantity
#         prov.provisioned_employer = calc_ss.get('patronal', 0.00) / pe.quantity
#         prov.base_salary = calc_prov.get('valor_base', 0.00)
#         if not prov.previous:
#             q_prev_events_value = FolhaEvento.objects.filter(contracheque__servidor=pe.employee,
#                                                              evento__pk__in=paid_events_value_ids,
#                                                              reference_year=year,
#                                                              reference_month=month)
#             q_prev_events_ss = FolhaEvento.objects.filter(contracheque__servidor=pe.employee,
#                                                           evento__pk__in=paid_events_employer_ids,
#                                                           reference_year=year,
#                                                           reference_month=month)
#             prov.previous_balance_value = float(q_prev_events_value.aggregate(
#                                               value=models.Sum('value'))['value'] or 0.00) * -1
#             prov.previous_balance_employer = float(q_prev_events_ss.aggregate(
#                                                   value=models.Sum('employer_contribution'))['value'] or 0.00) * -1
#             log.debug('PROVISION 13TH SALARY PREVIOUS %7.2f/%7.2f' % (round(prov.previous_balance_value, 2),
#                                                                        round(prov.previous_balance_employer, 2)))
#         prov.save()


# def create_provisions_vacation(year, month=None, employers=[]):
#     #CRIACAO DAS PROVISOES ------------------------------------------------
#     from rh.gfp.planoconta.models import ProvisionPlan
#     from rh.gfp.models import ContraCheque, FolhaEvento, Evento
#     from rh.ferias.models import PeriodoAquisitivoServidor
#     from django.db import models
#     from rh.gfp.calcs.mpto.provisions import VacationProvision, ProvisionSocialSecurity
#     from datetime import datetime, date
#     from contrib.utils import getLogger, NewDateRange
#     from dateutils import relativedelta

#     log = getLogger(__name__)

#     pp = ProvisionPlan.objects.get(type_provision=1)

#     print u'CREATING PROVISIONS - %s' % pp
#     matriculas = []

#     paid_events_value_ids = [ev.pk for ev in pp.paid_events_value.all()]
#     paid_events_employer_ids = [ev.pk for ev in pp.paid_events_employer.all()]

#     q_cc = ContraCheque.objects.filter(models.Q(folha__periodo__ano=year) &
#                                         models.Q(folha__tipo_folha__principal=True)).order_by(
#                                             '-folha__periodo', 'servidor')
#     if employers:
#         q_cc = q_cc.filter(servidor__matricula__in=employers)

#     if month:
#         q_cc = q_cc.filter(folha__periodo__mes=month)

#     cutting_date = date(year, month, 15)
#     # print cc.servidor.periodos_aquisitivos.get(data_inicio_aquisicao__lte=cc.folha.date_range.first,
#                                                   data_fim_aquisicao__gt=cc.folha.date_range.first)
#     for cc in q_cc:
#         month = cc.folha.periodo.mes
#         print '%10s:%10s:%60s:' % (cc.servidor.data_exercicio, cc.servidor.data_desligamento or '', cc.servidor),
#         pas = None
#         try:
#             pas = cc.servidor.periodos_aquisitivos.get(data_inicio_aquisicao__lte=cutting_date,
#                                                         data_fim_aquisicao__gte=cutting_date)
#         except PeriodoAquisitivoServidor.DoesNotExist as e:
#             print 'PROVISION HOLIDAYS does not have PAS'
#             log.debug('PROVISION HOLIDAYS does not have PAS')
#         except Exception, e:
#             raise e
#         else:
#             pe, created = pp.provisions_employee.get_or_create(
#                 employee=cc.servidor,
#                 info=u'%s' % pas.periodo_aquisitivo,
#                 defaults={
#                     'start_acquisition': pas.data_inicio_aquisicao,
#                     'end_acquisition': pas.data_fim_aquisicao,
#                     'quantity': 12 / pas.periodo_aquisitivo.configuracao.quantidade_periodos
#                 }
#             )
#             if not created:
#                 pe.start_acquisition = pas.data_inicio_aquisicao
#                 pe.end_acquisition = pas.data_fim_aquisicao
#                 pe.quantity = 12 / pas.periodo_aquisitivo.configuracao.quantidade_periodos

#                 pe.save()
#             print '%s:%10s:%10s:' % ('S' if created else 'N', pe.start_acquisition, pe.end_acquisition),

#             pm, created = pp.summaries.get_or_create(
#             reference_year=cc.folha.periodo.ano,
#             reference_month=cc.folha.periodo.mes if cc.folha.periodo.mes != 13 else 12,
#             )

#             prov, created = pe.provisions.get_or_create(
#                 provision_manager=pm,
#                 defaults={
#                     'provisioned_value': 0.0,
#                     'paid_value': 0.0,
#                     'provisioned_employer': 0.0,
#                     'paid_employer': 0.0,
#                     'previous_balance_value': 0.0,
#                     'previous_balance_employer': 0.0
#                 }
#             )
#             if not created:
#                 prov.previous_balance_value = 0.0
#                 prov.previous_balance_employer = 0.0
#                 prov.acquired = 1

#             q_events = FolhaEvento.objects.filter(contracheque__servidor=pe.employee,
#                                                    evento__pk__in=paid_events_value_ids)
#             qqs = None
#             qqs_periods = {cc.folha.periodo.ano: [cc.folha.periodo.mes]}
#             if cc.folha.periodo.mes == 12:
#                 qqs_periods[cc.folha.periodo.ano].append(13)

#             # log.debug('PROVISION HOLIDAYS SALARY FOR %s' % (cc))
#             calc_prov = VacationProvision(cc.servidor, cc.folha).calculate()
#             prov.provisioned_value = calc_prov.get('valor', 0.00) / pe.quantity
#             calc_ss_prov = ProvisionSocialSecurity(cc.servidor,
#                                                     cc.folha,
#                                                     params={'base_value': prov.provisioned_value}).calculate()
#             prov.base_salary = calc_prov.get('valor_base', 0.00)
#             prov.provisioned_employer = calc_ss_prov.get('patronal', 0.00)
#             # calc_ss_prov = ProvisionSocialSecurity(cc.servidor,
#                                                       cc.folha,
#                                                       params={'base_value': calc_prov.get('valor', 0.00)}).calculate()
#             # log.debug('PROVISION HOLIDAYS SALARY %7.2f/%7.2f/%7.2f/%7.2f %s' % (
#                                       round(calc_prov.get('valor_base', 0.00), 2),
#                                       round(calc_prov.get('valor', 0.00), 2),
#                                       round(calc_prov.get('base_previdencia', 0.00), 2),
#                                       round(calc_ss_prov.get('patronal', 0.00), 2), cc))
#             if not prov.previous:
#                 prov.previous_balance_value = prov.previous_balance_employer = 0.0
#                 if pas.pago and pas.folha_evento_terco_constitucional and\
#                        pas.folha_evento_terco_constitucional.folha.periodo < cc.folha.periodo:
#                     calc_ss_prev = ProvisionSocialSecurity(pas.servidor,
#                                           pas.folha_evento_terco_constitucional.folha,
#                                           params={'base_value': calc_prov.get('base_previdencia', 0.00)}).calculate()
#                     prov.previous_balance_value = float(pas.folha_evento_terco_constitucional.valor) * -1
#                     prov.previous_balance_employer = calc_ss_prev.get('patronal', 0.00) * -1
#                     log.debug('PROVISION HOLIDAYS PREVIOUS FOR %7.2f/%7.2f (%s): %s' % (
#                                       prov.previous_balance_value,
#                                   prov.previous_balance_employer,
#                                   pas.folha_evento_terco_constitucional.folha.periodo,
#                                   pas.servidor))

#                 if pe.provision_plan.update_previous_balance:
#                     qnt = cc.servidor.periodos_aquisitivos.exclude(
#                         models.Q(pago_sem_folha=True) |
#                         models.Q(bloqueado=True)
#                     ).filter(
#                         models.Q(data_fim_aquisicao__lt=datetime(year, month, 1).date()) &
#                          (models.Q(folha_evento_terco_constitucional=None) |
#                           models.Q(
#                       folha_evento_terco_constitucional__folha__periodo__ano__gt=pas.data_inicio_aquisicao.year) |
#                             (models.Q(
#                               folha_evento_terco_constitucional__folha__periodo__ano=pas.data_inicio_aquisicao.year) &
#                               models.Q(
#                           olha_evento_terco_constitucional__folha__periodo__mes__gte=pas.data_inicio_aquisicao.month)
#                             )
#                         )
#                     ).count()
#                     cc_base = cc.servidor.paychecks.filter(folha__status__in=[3, 4],
#                                   folha__tipo_folha=cc.folha.tipo_folha).order_by('-folha__periodo').last()
#                     calc_prev_prov = VacationProvision(cc.servidor, cc_base.folha).calculate()
#                     prov.previous_balance_value = (calc_prev_prov.get('valor', 0.00) * qnt)
#                     calc_ss = ProvisionSocialSecurity(cc.servidor, cc.folha,
#                               params={'base_value': calc_prev_prov.get('valor', 0.00)}).calculate()
#                     prov.previous_balance_employer = (calc_ss.get('patronal', 0.00) * qnt)

#                 dr = NewDateRange(pe.start_acquisition, pe.end_acquisition)
#                 dt_rel = date(pe.start_acquisition.year, pe.start_acquisition.month, 15)
#                 qnt_months = 0
#                 # qqs_periods = {}
#                 while dt_rel <= min(pe.end_acquisition, datetime(cc.folha.date_range.first.year,
#                       cc.folha.date_range.first.month, 15).date()):
#                     # dr_rel = NewDateRange.from_month(dt_rel.year, dt_rel.month)
#                     # if dr_rel.intersect(dr).business_days >= 15:
#                     if pe.start_acquisition <= dt_rel <= pe.end_acquisition:
#                         qnt_months += 1
#                         if dt_rel.year not in qqs_periods:
#                             qqs_periods[dt_rel.year] = []
#                         qqs_periods[dt_rel.year].append(dt_rel.month)
#                         if dt_rel.month == 12:
#                             qqs_periods[dt_rel.year].append(13)
#                     dt_rel += relativedelta(months=1)
#                 prov.acquired = qnt_months
#                 prov.provisioned_value *= qnt_months
#                 prov.provisioned_employer *= qnt_months
#                 print '(%02d/%02d %-7.2f) %7.2f/%7.2f: %7.2f/%7.2f' % (prov.acquired, pe.quantity,
#                                                                        calc_prov.get('valor_base', 0.00),
#                                                                        prov.provisioned_value,
#                                                                        prov.provisioned_employer,
#                                                                        prov.previous_balance_value,
#                                                                        prov.previous_balance_employer)
#             else:
#                 print ''
#             qqs = models.Q()
#             for qqs_year in qqs_periods:
#                 qqs = qqs | models.Q(contracheque__folha__periodo__ano=qqs_year,
#                                      contracheque__folha__periodo__mes__in=qqs_periods[qqs_year])
#             log.debug('QQSP: %s QQS: %s' % (qqs_periods, qqs))
#             total_values = q_events.filter(qqs).aggregate(value=models.Sum('value'))['value'] or 0.00
#             calc_ss_paid = ProvisionSocialSecurity(cc.servidor, cc.folha,
#                                                    params={'base_value': total_values}).calculate()
#             total_employer = calc_ss_paid.get('patronal', 0.00)
#             prov.paid_value = total_values * -1
#             prov.paid_employer = total_employer * -1
#             prov.save()
#             pm.save()

# def change_events(folhas):
#     from rh.pensao.models import PensaoEvento, PensaoAlimenticia, PensaoFolhaEvento
#     from rh.gfp.models import User, Folha, Evento, GenreEvent, SpecieEvent, FolhaEvento, FolhaModelo
#     from django.db.models import Q


#     lancamentos = FolhaEvento.objects.filter(folha__in=folhas)
#     for evn in EVENTS:
#         ev_old = Evento.objects.filter(numero__in=EVENTS[evn].split('/'))
#         if lancamentos.filter(Q(evento__in=ev_old) | Q(evento__numero=evn)):
#             print evn, EVENTS[evn].split('/'),
#             if ev_old.exists():
#                 genre, created = GenreEvent.objects.get_or_create(genre_number=evn[0:3],
#                     defaults={'type_event': ev_old[0].tipo,
#                               'character': ev_old[0].carater,
#                               'title': ev_old[0].titulo,
#                               'config_transparency': ev_old[0].config_transparencia}
#                 )
#                 print 'GENRE: %s' % ('C' if created else 'A'),
#                 specie = SpecieEvent.objects.get(specie_number=evn[3:])
#                 ev, created = Evento.objects.get_or_create(genre_event=genre, specie_event=specie, defaults={
#                     'lancamento': ev_old[0].lancamento,
#                     'tipo_calculo': ev_old[0].tipo_calculo,
#                     'automatico': ev_old[0].automatico,
#                     'calculo_invertido': ev_old[0].calculo_invertido,
#                     'aplica_consignado': ev_old[0].aplica_consignado,
#                     'aplica_consignavel': ev_old[0].aplica_consignavel,
#                     'evaluate_difference': ev_old[0].evaluate_difference,
#                     'quantidade': ev_old[0].quantidade,
#                     'quantidade_max': ev_old[0].quantidade_max,
#                     'porcentagem': ev_old[0].porcentagem,
#                     'valor_base': ev_old[0].valor_base,
#                     'teto': ev_old[0].teto,
#                     'piso': ev_old[0].piso,
#                     'config_transparencia': ev_old[0].config_transparencia,
#                     'base_de_calculo': ev_old[0].base_de_calculo,
#                     'previous_event': ev_old[0]
#                 })
#                 if not ev.previous_event:
#                     ev.previous_event = ev_old[0]
#                     ev.save()
#                 print 'EVENTS: ', lancamentos.filter(
#                       evento__numero__in=EVENTS[evn].split('/')).update(evento=Evento.objects.get(numero=evn)),
#                 print 'PENSION EVENTS: ', PensaoEvento.objects.filter(
#                           evento__numero__in=EVENTS[evn].split('/')).update(evento=Evento.objects.get(numero=evn)),
#                 print 'PENSION EVENTS: ', PensaoFolhaEvento.objects.filter(
#                           evento__numero__in=EVENTS[evn].split('/')).update(evento=Evento.objects.get(numero=evn)),
#                 print 'PENSION SOURCE EVENTS: ', PensaoAlimenticia.objects.filter(
#               evento_pensao__numero__in=EVENTS[evn].split('/')).update(evento_pensao=Evento.objects.get(numero=evn)),
#                 print 'PAYROLL MODELS: ',
#                 for fm in FolhaModelo.objects.filter(principais__numero__in=EVENTS[evn].split('/')):
#                     print u' %s OK' % fm,
#                     fm.principais.remove(*[ev for ev in Evento.objects.filter(numero__in=EVENTS[evn].split('/'))])
#                     fm.principais.add(Evento.objects.get(numero=evn))
#                 print ''
#                 # print 'PAYROLL MODEL: ', FolhaModelo.objects.PensaoAlimenticia.objects.filter(
#                 evento_pensao__numero__in=EVENTS[evn].split('/')).update(evento_pensao=Evento.objects.get(numero=evn))
#             else:
#                 print '<<<<<<<<<<<<< ERRO >>>>>>>>>>>>>'


# def load_fixtures_with_nk(file_path):
#     from rh.gfp.models import User
#     from contrib.middleware import set_current_user
#     from django.core.serializers.python import _get_model
#     from contrib.utils import DateUtils, getLogger, NewDateRange, get_json_engine
#     from rh.gfp.calcs.mpto import ferias, socialsecurity, remuneracao, aid, irrf, base, pension
#     from django.db import IntegrityError
#     import codecs

#     json = get_json_engine()

#     set_current_user(User.objects.get(username='athenas'))

#     with codecs.open(file_path, 'r', 'utf-8') as fd:
#         str_ = fd.read()

#     objs = json.decode(str_)
#     # LOAD NON M2M
#     for obj in objs:
#         try:
#             Model = _get_model(obj['model'])
#             if obj.get('pk', None):
#                 try:
#                     instance = Model.objects.get(pk=obj.get('pk'))
#                 except Model.DoesNotExist as e:
#                     instance = Model()
#                     instance.pk = obj.get('pk')
#                 except Exception, e:
#                     raise e
#             else:
#                 instance = Model()
#             _meta = instance._meta
#             for fn in obj['fields']:
#                 f = _meta.get_field_by_name(fn)[0]
#                 if obj['fields'][fn] is not None:
#                     if f.get_internal_type() == 'ForeignKey':
#                         cls_fk = f.related_field.model
#                         # print '>>> %s: %s' % (cls_fk, obj['fields'][fn])
#                         if hasattr(cls_fk, 'natural_key'):
#                             rel_obj = cls_fk.objects.get_by_natural_key(*obj['fields'][fn])
#                         else:
#                             rel_obj = cls_fk.objects.get(pk=obj['fields'][fn])
#                         setattr(instance, fn, rel_obj)
#                     elif f.get_internal_type() == 'ManyToManyField':
#                         pass
#                     else:
#                         setattr(instance, fn, obj['fields'][fn])
#             instance.save()
#             obj['pk'] = instance.natural_key() if hasattr(instance, 'natural_key') else instance.pk
#         except IntegrityError as e:
#             print ('ERROR: %s, %s' % (obj['model'], obj['pk']))
#         except Exception as e:
#             print obj
#             print unicode(e)
#             obj['loaded'] = False
#         else:
#             obj['loaded'] = True
#             print u'%-60s' % instance, 'OK'
#     # LOAD M2M
#     print '>>>>>>>> LOADING M2M FOR OBJECTS ...'
#     for obj in objs:
#         if obj.get('loaded', False):
#             Model = _get_model(obj['model'])
#             instance = Model.objects.get_by_natural_key(*obj['pk']) if hasattr(Model,
#                                                                   'natural_key') else Model.objects.get(pk=obj['pk'])
#             _meta = instance._meta
#             for fn in obj['fields']:
#                 f = _meta.get_field_by_name(fn)[0]
#                 if f.get_internal_type() == 'ManyToManyField':
#                     cls_fk = f.related.parent_model
#                     rel = getattr(instance, fn)
#                     if hasattr(cls_fk, 'natural_key'):
#                         for value in obj['fields'][fn]:
#                             rel_obj = cls_fk.objects.get_by_natural_key(*value)
#                             rel.add(rel_obj)
#                     else:
#                         for value in obj['fields'][fn]:
#                             rel_obj = cls_fk.objects.get(pk=value)
#                             rel.add(rel_obj)
#             print u'%-60s' % instance, 'OK'


# def load_incide_sobre_from_previous_event(payrolls):
#     from rh.gfp.models import Evento
#     from django.db.models import Count, F

#     for ef in Evento.objects.filter(
#              lancamentos__contracheque__folha__in=payrolls).exclude(
#                   calculo=None).exclude(genre_event=None).annotate(qnt=Count('lancamentos')):
#         print '%03d' % ef.qnt, '%-40s' % ef, ef.calculo,

#         incide_sobre = []
#         if ef.previous_event:
#             incide_sobre = [ev for ev in ef.previous_event.incide_sobre.all()]
#             if incide_sobre:
#                 for evi in incide_sobre:
#                     for eva in evi.replacement_events.all():
#                         if eva not in ef.incide_sobre.all():
#                             ef.incide_sobre.add(eva)
#         print 'IS: %s' % ef.incide_sobre.count()


# def migrate_events(payrolls=[], scape_fixture=False):
#     from rh.gfp.models import User, Folha, FolhaEvento, Evento
#     from standard.models import ClassCode
#     from django.conf import settings
#     import os
#     from contrib.middleware import set_current_user
#     set_current_user(User.objects.get(username='athenas'))

#     print 'UPDATIND CALC FOR OLD EVENTS: %s' % Evento.objects.exclude(
#               calculo_id__in=[cc.pk for cc in ClassCode.objects.all()]).update(calculo=None)

#     if not scape_fixture:
#         load_fixtures_with_nk(os.path.join(settings.BASE_DIR, 'rh/gfp/fixtures/events.json'))
#         load_fixtures_with_nk(os.path.join(settings.BASE_DIR, 'rh/gfp/fixtures/estrutura_sup.json'))

#     if not payrolls:
#         payrolls = [f.pk for f in Folha.objects.filter(periodo__ano=2015)]
#     change_events(payrolls)
#     load_incide_sobre_from_previous_event(payrolls)
#     print 'UPDATING BASE_PREVIDENCIA: %s' % FolhaEvento.objects.filter(
#       folha__periodo__ano=2015, evento__numero__in=['90000', '90500', '91000', '91500']).update(base_previdencia=0)
#     print 'UPDATING QNT AUXILIOS: %s' % FolhaEvento.objects.filter(
#                   folha__periodo__ano=2015, evento__numero__in=['06600', '06800']).update(qnt=30)
#     for f in payrolls:
#         check_events_without_genre(f)

# def check_events_without_genre(payroll):
#     from django.db.models import Count
#     from rh.gfp.models import Folha, Evento
#     print '-----------------------------------------------------'
#     print Folha.objects.get(pk=payroll)
#     for ev in Evento.objects.filter(lancamentos__evento__genre_event=None,
#                                      lancamentos__folha=payroll).annotate(t=Count('lancamentos')):
#         print ev.t, ev


# def compare_entries(payroll, target_db, entries=[]):
#     from django.db.models import Count, F, Sum, Q
#     from rh.gfp.models import Evento, ContraCheque

#     paychecks = {}
#     q_s = q_t = Q()
#     if entries:
#         q_s = Q(evento__numero__in=entries)
#         q_t = Q(evento__numero__in=[ev.previous_event.numero for ev in Evento.objects.filter(numero__in=entries)])
#     for ccp in ContraCheque.objects.using(target_db).filter(folha=payroll):
#         tp = ccp.lancamentos.filter(Q(evento__tipo='P')).filter(q_t).aggregate(total=Sum('valor'))['total'] or 0.00
#         td = ccp.lancamentos.filter(Q(evento__tipo='D')).filter(q_t).aggregate(total=Sum('valor'))['total'] or 0.0
#         paychecks[ccp.servidor.matricula] = float(tp) - float(td)

#     for cc in ContraCheque.objects.filter(folha=payroll):
#         tp = cc.lancamentos.filter(Q(evento__tipo='P')).filter(q_s).aggregate(total=Sum('valor'))['total'] or 0.00
#         td = cc.lancamentos.filter(Q(evento__tipo='D')).filter(q_s).aggregate(total=Sum('valor'))['total'] or 0.0
#         total = float(tp) - float(td)

#         if abs(paychecks.get(cc.servidor.matricula, 0.00) - total) > 0.019:
#             print '%-05.2f %-05.2f %-05.2f %s' % (total, paychecks[cc.servidor.matricula],
#                                                    total - paychecks[cc.servidor.matricula], cc.servidor)


# def verify_diffs_on_recalculate(payroll):
#     from django.db.models import Count, F, Sum, Q
#     from rh.gfp.models import Evento, ContraCheque, Folha
#     for cc in ContraCheque.objects.filter(folha=payroll):
#         res = {}
#         q1 = cc.lancamentos.aggregate(total=Sum('valor'), count=Count('pk'))
#         total1 = q1['total'] or 0
#         count1 = float(q1['count']) or 0.0
#         # while res.get('changed', True):
#         res = cc.recalculate()
#         q2 = cc.lancamentos.aggregate(total=Sum('valor'), count=Count('pk'))
#         total2 = q2['total'] or 0
#         count2 = float(q2['count']) or 0.0
#         if abs(round(total1, 2) - round(total2, 2)) > 0.019:
#             print '%s/%s %s/%s %s' % (total1, total2, count1, count2, cc)


# CREATE JSON fixtures
# ./manage.py exportdata --indent=2 --import-module=rh.gfp --use-primary-key --with-natural-keys --outfile='/home/raysonsilva/envs/athenas/src/rh/gfp/fixtures/estrutura_sup2.json' '[es for es in ModeloTabelaSalarial.objects.filter()] + [rn for rn in ReferenciaNiveis2D.objects.filter()] + [es for es in EstruturaTabelaSalarial.objects.filter()] + [ts for ts in TabelaSalarial.objects.filter()] + [rs for rs in ReferenciaSalario.objects.filter()] + [ce for ce in CargosEstrutura.objects.filter()] + [fm for fm in FolhaModelo.objects.filter()]'
# ./manage.py exportdata --indent=2 --import-module=rh.gfp --use-primary-key --with-natural-keys --outfile='/home/raysonsilva/envs/athenas/src/rh/gfp/fixtures/events2.json' '[o for o in GenreEvent.objects.all()] + [o for o in SpecieEvent.objects.all()] + [o for o in Evento.objects.exclude(genre_event=None)]'


# def update_dirf_2014():
#     import codecs
#     from rh.models import PessoaFisica
#     from rh.gfp.dirf.models import Demonstrativo
#     pfs = {}
#     with codecs.open('/home/raysonsilva/Downloads/DIRF2014 OK.txt', 'r') as fd:
#         line1 = line2 = None
#         for line in fd.readlines():
#             if line.startswith('BPFDEC'):
#                 line1 = line
#                 cpf = line.split('|')[1]
#                 pf = PessoaFisica.objects.get(cpf=cpf)
#             if line.startswith('RTIRF') and line.split('|')[13]:
#                 line2 = line
#                 pfs[cpf] = round(float(line.split('|')[13])/100.0, 2)
#     return pfs

# def migrate_planocontas(ano_calendario=2015):
#     from rh.gfp.planoconta import models as mpc
#     from rh.gfp import models as mgfp

#     reverse_events = {}
#     for new_ev in EVENTS:
#         for old_ev in EVENTS[new_ev].split('/'):
#             reverse_events[old_ev] = new_ev
#     # return reverse_events

#     for p in mpc.Plano.objects.filter(ano_calendario=ano_calendario).order_by('folha_tipo'):
#         if p.eventos.count():
#             print 'MIGRATING PLANO: %s >>> %s' % (p.folha_tipo, p)
#             for ev in p.eventos.all():
#                 new = '---'
#                 try:
#                     new = mgfp.Evento.objects.get(
#                                   numero=reverse_events[ev.numero]) if ev.numero in reverse_events else '---'
#                     if new != '---' and new not in p.eventos.all():
#                         p.eventos.add(new)
#                 except mgfp.Evento.DoesNotExist as e:
#                     new = '>> NE <<'
#                 except Exception, e:
#                     raise e
#                 print '>>>> %-050s - %s' % (ev, new)


# def migrate_viabillize_events(file_):

#     reverse_events = {}
#     for new_ev in EVENTS:
#         for old_ev in EVENTS[new_ev].split('/'):
#             reverse_events[old_ev] = new_ev

#     fd = open(file_, 'r')
#     content = fd.read()
#     print content
#     fd.close()

#     # content = content
#     for ev in reverse_events:
#         # print (';%s;' % ev, ';%s;' % reverse_events[ev])
#         content = content.replace(';%s;' % ev, ';%s;' % reverse_events[ev])

#     fd = open('%s.new' % file_, 'w')
#     fd.write(content)
#     fd.close()


# # ---------------------- SPRITFY FOPAG ---------------------------------------------
# #cd
# #spritify.py -o fopag.html -p images/ -s fopag

# def pmargins(payroll_id):
#     from rh.gfp.models import Folha

#     class Bcolors:
#         HEADER = '\033[95m'
#         OKBLUE = '\033[94m'
#         OKGREEN = '\033[92m'
#         WARNING = '\033[93m'
#         FAIL = '\033[91m'
#         ENDC = '\033[0m'
#         BOLD = '\033[1m'
#         UNDERLINE = '\033[4m'

#     f = Folha.objects.get(pk=payroll_id)

#     for cc in f.paychecks.filter():
#         mc1 = cc.margin_paychecks.get(margin__identification='M030GERAL')
#         value_consigned = mc1.total_value - mc1.value
#         if value_consigned > 0:
#             print '%0.2f:%0.2f:' % (value_consigned, mc1.total_value),
#             pct = value_consigned / mc1.total_value
#             if pct >= 1:
#                 print Bcolors.FAIL,
#             elif 1 < pct <= 0.7:
#                 print Bcolors.WARNING,
#             elif pct <= 0.3:
#                 print Bcolors.OKGREEN,
#             print '%0.2f%%:' % (float(pct) * 100.0), Bcolors.ENDC, cc

# def compare_margins(payroll_id, force_update_margins=False):
#     from rh.gfp.models import Folha, User
#     from contrib.middleware import set_current_user
#     set_current_user(User.objects.get(username='athenas'))
#     f = Folha.objects.get(pk=payroll_id)

#     for cc in f.paychecks.order_by('servidor'):
#         mc1 = cc.margin_paychecks.filter(margin__identification='M030GERAL').first()
#         if mc1:
#             mc2 = cc.margin_paychecks.filter(margin__identification='M005CC').first()
#             total_value = mc1.total_value + (mc2.total_value if mc2 else 0)
#             if abs(total_value - cc.margem_consignada_total) > 0.01:
#                 if force_update_margins:
#                     cc._update_or_create_margins()
#                 print total_value, cc.margem_consignada_total, mc1, mc2, cc
#         else:
#             print u'DONT EXIST MARGINS FOR %s' % cc

# def add_events_for_genre(token, event):
#     if event.genre_event:
#         for e in event.genre_event.events.all():
#             if e not in token.eventos.all():
#                 print '>> %s' % e
#                 token.eventos.add(e)

# def update_tokens_dirf(dialect):
#     for t in dialect.tokens.all():
#         print '>>>>>>>> %s <<<<<<<<<<<<' % t
#         for e in t.eventos.all():
#             print '> %s' % e
#             for ee in e.replacement_events.filter():
#                 print '>> %s' % ee
#                 t.eventos.add(ee)
#         pks = [e1.pk for e1 in t.eventos.all()]
#         for e in t.eventos.exclude(genre_event=None):
#             for ee in e.genre_event.events.exclude(pk__in=pks):
#                 print '>> %s' % ee
#                 t.eventos.add(ee)


# def evaluate_dirf_event(dialect, not_configureds=True):
#     tokens = [t for t in Token.objects.filter(dialect=dialect)]
#     events = []
#     if not_configureds:
#         # EVENTOS NAO CONFIGURADOS ---------------------------------------------------------
#         print(' >>>> EVENTOS NAO CONFIGURADOS <<<<')
#         configured_events = [ev for ev in Evento.objects.filter(as_token__in=tokens)]
#         for fe in FolhaEvento.objects.filter(
#                   folha__dt_pagamento__year=2015).exclude(evento__carater__in=[6, 7]).order_by('evento'):
#             if fe.evento not in configured_events:
#                 configured_events.append(fe.evento)
#                 print fe.evento.get_carater_display(), fe.evento
#     # EVENTOS REPETIDOS -----------------------------------------------------------------
#     print('>>>> EVENTOS REPETIDOS <<<<')
#     for ev in Evento.objects.filter(as_token__in=tokens):
#         if ev.as_token.filter(dialect=dialect).count() > 1 and ev not in events:
#             events.append(ev)
#             if ev.as_token.filter(
#                   dialect=dialect).count() == ev.as_token.filter(dialect=dialect, slug__startswith='outros').count():
#                 dialect.tokens.get(slug='outros').eventos.remove(ev)
#                 print('REMOVENDO FROM "OUTROS": %s' % ev)
#             if ev.as_token.filter(dialect=dialect).count() > 1:
#                 print ev, [t.slug for t in ev.as_token.filter(dialect=dialect).all()]


def whereis_event(year, number_event):
    from rh.gfp.models import Evento as Event

    ev = Event.objects.get(numero=number_event)
    for token in ev.as_token.filter(dialect__dirf__ano_calendario=year):
        print(">>> %s" % token)


def configure_order_events(ordered=[], event=None, update=False):
    from rh.gfp.models import Evento

    if event in ordered:
        return ordered
    query = Evento.objects.exclude(genre_event=None).order_by("numero")
    if event:
        query_ = query.filter(pk=event.pk)
    else:
        query_ = query
    pks = [e.pk for e in ordered]
    for ev in query_:
        incide = (
            ev.incide_sobre.exclude(genre_event=None)
            .exclude(pk__in=pks)
            .order_by("numero")
        )
        # print 'EV: %s: %s' % (ev.numero, [e.numero for e in incide])
        for ev1 in incide:
            configure_order_events(ordered, ev1)
        ordered.append(ev)

    if update:
        order = 1
        for ev in ordered:
            Evento.objects.filter(pk=ev.pk).update(order=order)
            order += 1
            e = Evento.objects.get(pk=ev.pk)
            max_order = e.incide_sobre.aggregate(ord=Max("order")).get("ord") or 0
            print(" " if max_order < e.order else "*", max_order, e.order, e)

    return ordered


def update_pension_paychecks(payroll):
    from rh.gfp.models import (
        ContraCheque as Paycheck,
        ContraChequePensionista,
        Folha as Payroll,
        FolhaEvento,
    )
    from rh.pensao.models import Pensao
    from django.db.models import Q, Sum
    from contrib.middleware import set_current_user, get_current_user
    import copy
    import datetime

    set_current_user("athenas")

    # PENSION FOOD
    old_status = payroll.status
    Payroll.objects.filter(pk=payroll.pk).update(status=2)
    payroll = Payroll.objects.get(pk=payroll.pk)
    payroll.lancamentos.filter(evento__automatico=True).exclude(
        evento__calculo=None
    ).update(automated=True)

    confirm_ = []

    total = payroll.lancamentos.filter(evento__numero="70100", status="CT").count()
    pct = factor = float(100.0 / float(max(total, 1)))
    errors = pdne = ccpdne = 0

    print_message("")

    # print '**** MODIFICANDO STATUS %s: %s>%s ****' % (payroll, old_status, 2)
    for fe in payroll.lancamentos.filter(evento__numero="70100", status="CT"):
        # print '   [PA](%s)' % fe.oIds, fe.contracheque.servidor,
        try:
            pension = Pensao.objects.get(Q(pk__in=fe.oIds))
            cc = fe.contracheque
            ccp_old = ContraChequePensionista.objects.get(
                pensionista=pension.pensionista, contracheque_servidor=cc
            )
            ccp, created = Paycheck.objects.get_or_create(
                folha=fe.folha, servidor=fe.servidor, pensioner=pension.pensionista
            )
            ccp.employee_source = 6
            ccp.employee_pays_pension = pension.tipo
            ccp.lancamentos.all().delete()
            values = ccp_old.lancamentos_pensionitas.aggregate(
                Sum("valor"), Sum("valor_base")
            )
            if pension.tipo == 1:
                base_value = pension.valor
                pct_ = None
            elif pension.tipo == 3:
                base_value = fe.contracheque.folha.periodo.salario_minimo
                pct_ = pension.valor
            else:
                base_value = values["valor_base__sum"]
                pct_ = pension.valor
            new_fe = FolhaEvento.objects.create(
                contracheque=ccp,
                evento=pension.event_pensioner,
                valor=values["valor__sum"],
                valor_base=base_value,
                pct=pct_,
                confirma_folha=get_current_user(),
                confirma_controle=get_current_user(),
                dt_confirma_folha=datetime.datetime.now(),
                dt_confirma_controle=datetime.datetime.now(),
            )
            ccp.consolidate(changes=ccp.ALL, force=True)
            cc.consolidate(changes=ccp.ALL, force=True)
            confirm_.append(new_fe.pk)
            # UPDATING oIds FOR PENSION ENTRY
            FolhaEvento.objects.filter(pk=fe.pk).update(
                json_calc_vars='{"oIds": [%s]}' % pension.pensionista.pk
            )
            # print u'%-040s' % (pension.pensionista.abbreviation)
        except Pensao.DoesNotExist:
            # print 'ERRO - PDNE'
            pdne += 1
        except ContraChequePensionista.DoesNotExist:
            # print 'ERRO - CCPDNE'
            ccpdne += 1
        except Exception as e:
            print(e)
            Payroll.objects.filter(pk=payroll.pk).update(status=old_status)
            log.exception(e)
            raise e
        finally:
            print_message(
                ">>> PENSÃO ALIMENTICIA [\033[92m%0.1f%%\033[0m] [PNDE: %d CCPDNE: %d]"
                % (pct, pdne, ccpdne),
                same_line=True,
            )
            pct += factor

    if payroll.lancamentos.filter(evento__numero="70100", status="CT").count() > 0:
        print_message("")

    # PENSION DEATH
    total = payroll.paychecks.filter(pensioner=None).count()
    pct = factor = float(100.0 / max(total, 1))
    errors = pm = ccpdne = 0
    for cc in payroll.paychecks.filter(pensioner=None):
        pensions = cc.servidor.pensao_pagador.filter(type_of_pension=2).exclude(
            Q(data_inicio__gt=cc.folha.date_range.last)
            | (~Q(data_fim=None) & Q(data_fim__lt=cc.folha.date_range.first))
        )
        # FolhaEvento.objects.filter(evento__numero='70500', contracheque=cc).delete()
        if pensions:
            #     cc.consolidate()
            # total_liquido = cc.total_liquido
            for p in pensions.order_by("pk"):
                # print '   [PM]', cc.servidor,
                ccp_old = ContraChequePensionista.objects.filter(
                    pensionista=p.pensionista, contracheque_servidor=cc
                ).first()
                if ccp_old:
                    ccp, created = Paycheck.objects.get_or_create(
                        folha=payroll, servidor=cc.servidor, pensioner=p.pensionista
                    )
                    ccp.employee_source = 6
                    ccp.employee_pays_pension = p.tipo
                    ccp.lancamentos.all().delete()
                    for fep in ccp_old.lancamentos_pensionitas.all():
                        if old_status in [3, 4] or fep.evento in p.events.all():
                            # print '%s OK' % fep.evento.numero,
                            new_fe = copy.copy(fep.folha_evento)
                            new_fe.pk = None
                            new_fe.valor = fep.valor
                            new_fe.pct = p.valor if not new_fe.pct else new_fe.pct
                            new_fe.contracheque = ccp
                            new_fe.automated = False
                            new_fe.save()
                            confirm_.append(new_fe.pk)
                        # else:
                        #     print '%s NO' % fep.evento.numero,
                    ccp.consolidate(force=True)
                    pm += 1
                else:
                    errors += 1
                # print u'%-040s' % (p.pensionista.abbreviation)
            try:
                cc.consolidate(force=True)
            except Exception:
                errors += 1
                # print 'ERRO: %s' % cc
        print_message(
            ">>> PENSÃO MORTE [\033[92m%0.1f%%\033[0m] [PM: %d ERRORS: %d]"
            % (pct, pm, errors),
            same_line=True,
        )
        pct += factor

    FolhaEvento.objects.filter(pk__in=confirm_).update(
        dt_confirma_folha=datetime.date.today(),
        dt_confirma_controle=datetime.date.today(),
        confirma_folha=get_current_user(),
        confirma_controle=get_current_user(),
    )

    Payroll.objects.filter(pk=payroll.pk).update(status=old_status)
    # print '**** REVERTENDO STATUS %s: %s>%s ****' % (payroll, 2, old_status)


def copy_pensions_without_RRA(start_year, start_month):
    # from rh.gfp.models import ContraCheque as Paycheck, ContraChequePensionista, Folha as Payroll
    from rh.pensao.models import Pensao
    from django.db.models import Q
    from contrib.middleware import set_current_user
    import copy
    import datetime
    from dateutil.relativedelta import relativedelta

    set_current_user("athenas")
    Pensao.objects.filter(data_inicio=None).delete()
    start_date = datetime.date(start_year, start_month, 1)
    for p in Pensao.objects.filter(type_of_pension=2).filter(
        Q(data_fim=None)
        | (Q(data_inicio__lte=start_date) & Q(data_fim__gte=start_date))
    ):
        if p.events.filter(titulo__icontains="RRA"):
            new_p = copy.copy(p)
            new_p.pk = None
            new_p.data_inicio = start_date
            new_p.data_fim = p.data_fim
            p.data_fim = start_date - relativedelta(days=1)
            p.save()
            new_p.save()
            for ev in p.events.exclude(titulo__icontains="RRA"):
                new_p.events.add(ev.pk)
            print(new_p, new_p.data_inicio, new_p.data_fim)


def update_data_for_pensions(year, month, only_month=False):
    from rh.gfp.models import Folha, FolhaModelo, Evento, FolhaTipo
    from rh.gfp.planoconta.models import Plano
    from standard.models import ClassCode
    from contrib.middleware import set_current_user

    set_current_user("athenas")

    # -------------------------------------------------------
    fm1 = FolhaModelo.objects.get(pk=41)  # AUX. ALIMENTAÇÃO
    fm2 = FolhaModelo.objects.get(pk=101)  # NORMAL
    fm3 = FolhaModelo.objects.get(pk=121)  # PAE
    ev1 = Evento.objects.get(numero="70100")
    ev1.como_principal.add(fm1, fm2, fm3)
    ev2 = Evento.objects.get(numero="70500")
    ev2.como_principal.add(fm3)
    ev3 = Evento.objects.get(numero="70600")
    ev1.como_principal.add(fm1, fm2, fm3)

    # ------------------------------------------------------
    tf1 = FolhaTipo.objects.get(pk=104)  # AUX. ALIMENTAÇÃO
    tf1.modelo = fm1
    tf1.save()
    tf3 = FolhaTipo.objects.get(pk=111)  # PAE
    tf3.modelo = fm3
    tf3.save()

    # ------------------------------------------------------
    cc1 = ClassCode.objects.get(slug="gfp-mpto-pension-employee")
    cc2 = ClassCode.objects.get(slug="gfp-mpto-pension-pensioner")

    # ------------------------------------------------------
    ev1.automatico = True
    ev1.calculo = cc1
    ev1.save()
    ev2.automatico = True
    ev2.calculo = cc1
    ev2.save()
    ev3.automatico = True
    ev3.calculo = cc2
    ev3.save()
    # ------------------------------------------------------

    Plano.objects.filter(ano_calendario=2016).filter(titulo__icontains="PENS").update(
        composes_total_net=True
    )
    Plano.objects.filter(ano_calendario=2016, tipo=2).exclude(
        titulo__icontains="IRRF"
    ).update(composes_total_net=True)
    # ---------------------------------------------------------

    copy_pensions_without_RRA(year, month)
    q_paychecks = Folha.objects.filter(periodo__ano=year)

    if only_month:
        q_paychecks = q_paychecks.filter(periodo__mes=month)

    for f in q_paychecks.order_by("periodo"):
        print_message("************* %s" % f)
        update_pension_paychecks(f)


def print_message(message, same_line=False):
    import sys

    try:
        if same_line:
            message = "\r\x1b[K" + message
        else:
            message = "\n" + message
        sys.stdout.write(message)
        sys.stdout.flush()
    except Exception as e:
        print("ENCODE ERROR1 %s " % e)


def create_summary_reports(payroll_id, show=False):
    from rh.gfp.models import OverviewReport, FinancialReportPayroll, Folha
    from rh.gfp.planoconta.models import Plano
    from django.db.models import Sum, Count

    payroll = Folha.objects.get(pk=payroll_id)

    OverviewReport.objects.filter(payroll=payroll).delete()
    FinancialReportPayroll.objects.filter(payroll=payroll).delete()

    total = payroll.lancamentos.values("evento").distinct().count()
    pct = factor = 50.0 / total

    q_entries = payroll.lancamentos.exclude(
        contracheque__employee_pays_pension=2, contracheque__pensioner__isnull=True
    )

    for obj in payroll.lancamentos.order_by("evento__numero").distinct(
        "evento__numero"
    ):
        ev = obj.evento
        pk = ev.pk
        character = 0
        q_ev = q_entries.filter(evento=pk)
        # PENSIONISTAS

        if ev.carater in [4, 5, 6, 7, 8]:
            character = 2
        elif ev.carater in [1, 2, 3]:
            character = 1

        q_pensioner = q_ev.filter(contracheque__pensioner__isnull=False).aggregate(
            v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk")
        )
        ev.overview_summary.create(
            payroll=payroll,
            type_of_employee=3,
            type_of_entry=character,
            value=q_pensioner["v"] or 0,
            employer_contribution=q_pensioner["ec"] or 0,
            quantity=q_pensioner["c"],
        )
        # ATIVOS
        q_active = q_ev.filter(
            contracheque__pensioner__isnull=True, contracheque__servidor__ativo=True
        ).aggregate(v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk"))
        ev.overview_summary.create(
            payroll=payroll,
            type_of_employee=1,
            type_of_entry=character,
            value=q_active["v"] or 0,
            employer_contribution=q_active["ec"] or 0,
            quantity=q_active["c"],
        )
        # INATIVOS
        q_inactive = q_ev.filter(
            contracheque__pensioner__isnull=True, contracheque__servidor__ativo=False
        ).aggregate(v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk"))
        ev.overview_summary.create(
            payroll=payroll,
            type_of_employee=2,
            type_of_entry=character,
            value=q_inactive["v"] or 0,
            employer_contribution=q_inactive["ec"] or 0,
            quantity=q_inactive["c"],
        )

        print_message(">>> SUMMARING %s [%0.1f%%]" % (payroll, pct), same_line=True)
        pct += factor

    total = Plano.objects.filter(
        ano_calendario=payroll.periodo.ano, folha_tipo=payroll.tipo_folha
    ).count()
    factor = 50.0 / total
    for plan in Plano.objects.filter(
        ano_calendario=payroll.periodo.ano, folha_tipo=payroll.tipo_folha
    ):
        q_entries_plan = q_entries.filter(
            evento__genre_event__in=plan.genre_events.all()
        )
        for pc in plan.contas.filter():
            q_pension_system = q_entries_plan.filter(
                contracheque__servidor__regime_previdenciario=pc.regime_previdenciario
            )
            if q_pension_system.exists():
                q_values = q_pension_system.aggregate(
                    v=Sum("value"), ec=Sum("employer_contribution"), c=Count("pk")
                )

                if plan.tipo != 3:  # LIQUIDO/CONSIGNAÇÃO
                    value = (
                        -(q_values["v"] or 0)
                        if plan.invert_negative or plan.tipo == 1
                        else (q_values["v"] or 0)
                    )
                else:  # PATRONAL
                    value = q_values["ec"] or 0
                pc.financial_summary.create(
                    payroll=payroll, value=value, quantity=q_values["c"]
                )

        print_message(">>> SUMMARING %s [%0.1f%%]" % (payroll, pct), same_line=True)
        pct += factor

    result = verify_totals_payroll(payroll, show)
    if result.get("SUCCESS", False):
        print_message(
            ">>> SUMMARING %s [\033[92mOK\033[0m]" % (payroll), same_line=True
        )

    print_message("")


def verify_totals_payroll(payroll, show=False):
    from rh.gfp.models import OverviewReport, FinancialReportPayroll, ContraCheque
    from django.db.models import Sum

    # RESUMO GERAL -------------------------------------------------------
    query_ow = OverviewReport.objects.filter(payroll=payroll)
    p_ow = query_ow.filter(type_of_entry=1).aggregate(
        Sum("value"), Sum("employer_contribution"), Sum("quantity")
    )
    d_ow = query_ow.filter(type_of_entry=2).aggregate(
        Sum("value"), Sum("employer_contribution"), Sum("quantity")
    )
    total_net_ow = round(
        float(p_ow["value__sum"] or 0.00) + float(d_ow["value__sum"] or 0.00), 2
    )
    total_ow = round(
        float(p_ow["value__sum"] or 0.00)
        + float(p_ow["employer_contribution__sum"] or 0.00)
        + float(d_ow["employer_contribution__sum"] or 0.00),
        2,
    )
    count_ow = float(p_ow["quantity__sum"] or 0) + float(d_ow["quantity__sum"] or 0)

    # NL -----------------------------------------------------------------
    query_fr = FinancialReportPayroll.objects.filter(payroll=payroll)
    nl_fr = query_fr.filter(account_plan__finalidade=1).aggregate(
        Sum("value"), Sum("quantity")
    )
    nl_net_fr = query_fr.filter(
        account_plan__finalidade=1, account_plan__plano__composes_total_net=True
    ).aggregate(Sum("value"), Sum("quantity"))
    total_net_nl_fr = round(nl_net_fr["value__sum"] or 0.00, 2)
    total_nl_fr = round(nl_fr["value__sum"] or 0.00, 2)
    count_nl_fr = nl_fr["quantity__sum"] or 0

    # PD -----------------------------------------------------------------
    pd_fr = query_fr.filter(account_plan__finalidade=2).aggregate(
        Sum("value"), Sum("quantity")
    )
    pd_net_fr = query_fr.filter(
        account_plan__finalidade=2, account_plan__plano__composes_total_net=True
    ).aggregate(Sum("value"), Sum("quantity"))
    total_net_pd_fr = round(pd_net_fr["value__sum"] or 0.00, 2)
    total_pd_fr = round(pd_fr["value__sum"] or 0.00, 2)
    count_pd_fr = pd_fr["quantity__sum"] or 0

    # LIQUIDO BANCARIO ---------------------------------------------------
    query_nb = ContraCheque.objects.filter(folha=payroll).exclude(
        employee_pays_pension=2, pensioner__isnull=True
    )
    net_nb = query_nb.aggregate(Sum("total_liquido"))
    # query_nb.exclude(dado_bancario_pessoa__isnull=True).aggregate(Sum('total_liquido'))
    total_net_nb = round(net_nb["total_liquido__sum"] or 0.00, 2)
    total_nb_without_db = query_nb.filter(dado_bancario_pessoa__isnull=True).count()

    ok = (total_ow == total_nl_fr == total_pd_fr) and (
        total_net_ow == total_net_nl_fr == total_net_pd_fr == total_net_nb
    )

    if not ok or show:
        print_message(
            "================================================================"
        )
        print_message("%15s %15s %15s %10s" % ("", "TOTAL", "LIQUIDO", "QTD"))
        print_message(
            "%15s %15.2f %15.2f %10d"
            % ("RESUMO GERAL", total_ow, total_net_ow, count_ow)
        )
        print_message(
            "%15s %15.2f %15.2f %10d"
            % ("NL", total_nl_fr, total_net_nl_fr, count_nl_fr)
        )
        print_message(
            "%15s %15.2f %15.2f %10d"
            % ("PD", total_pd_fr, total_net_pd_fr, count_pd_fr)
        )
        print_message(
            "%15s %15.2f %15.2f %10d"
            % ("LIQUIDO", 0, total_net_nb, total_nb_without_db)
        )
        print_message(
            "%17s %024s %026s"
            % (
                "",
                (
                    "\033[1;32mOK\033[0m"
                    if total_ow == total_nl_fr == total_pd_fr
                    else "\033[0;31mERRO\033[0m"
                ),
                (
                    "\033[1;32mOK\033[0m"
                    if total_net_ow
                    == total_net_nl_fr
                    == total_net_pd_fr
                    == total_net_nb
                    else "\033[0;31mERRO\033[0m"
                ),
            )
        )
        print_message(
            "================================================================"
        )

    return ok


# import time
# for x in range(820, 832):
#     # verifica o tempo de resposta da função soma1
#     ini2 = time.time()
#     create_summary_reports2(x)
#     fim2 = time.time()
#     t2 = fim2 - ini2

#     ini1 = time.time()
#     create_summary_reports(x)
#     fim1 = time.time()
#     t1 = fim1 - ini1
#     pct = (t2/t1)*100
#     print "Time: CSR %0.2f %0.2f(\033[1;%dm%0.1f%%\033[0m)" % (t1, t2, 31 if pct > 100 else 32, pct)
# # CORRIGINDO DIFERENÇAS DE PENSOES 05/2016 e 06/2016 NA FOLHA 07/2016 WESLEY MEURER
# from rh.gfp.models import *
# from rh.pensao.models import *
# PensaoFolhaEvento.objects.filter(pk=8356).update(valor=1692.05 + 124.40)
# PensaoFolhaEvento.objects.filter(pk=8355).update(valor=1692.05 + 124.39)
# f = Folha.objects.get(pk=819)
# cc = f.paychecks.get(servidor__matricula=1973)
# ccp = cc.paychecks.all()[0]
# ccp.delete()


# VERIFICAND PESSOAS FISICAS PARA ESOCIAL
def generate_esocial_validations_employee():
    errors = []
    from rh.gfp.models import Servidor
    from rh.models import Documento
    import datetime

    print("SERVIDORES APTOS A SEREM AVALIADOS")
    dt_now = datetime.datetime.now().date()
    for s in Servidor.objects.order_by("pessoa_fisica__nome"):
        valid_trainee = s.is_trainee() and s.tipo == "E" and s.ativo
        if (
            valid_trainee
            or s.paychecks.filter(
                folha__periodo__ano=dt_now.year, folha__periodo__mes=dt_now.month
            ).exists()
        ):
            pf = s.pessoa_fisica
            cpf = pf.cpf.replace(".", "").replace("-", "")
            try:
                nis_pis_pasep = (
                    pf.documento.filter(tipo_documento__in=[5, 6]).first().numero
                    if pf.documento.filter(tipo_documento__in=[5, 6])
                    else ""
                )
                if not valid_trainee and not nis_pis_pasep:
                    errors.append(
                        "%s;%s;%s;%s"
                        % (s.tipo, cpf, str(pf), "NIS/PIS/PASEP inexistente!")
                    )
                elif not pf.data_nascimento:
                    errors.append(
                        "%s;%s;%s;%s"
                        % (s.tipo, cpf, str(pf), "Data de nascimento inexistente!")
                    )
                else:
                    print(
                        "%s;%s;%s;%s"
                        % (
                            cpf,
                            nis_pis_pasep,
                            pf.nome,
                            pf.data_nascimento.strftime("%d%m%Y"),
                        )
                    )
            # except Documento.DoesNotExist, e:
            #     if pf.servidor_set.filter(ativo=True):
            #         errors.append('%s;%s;%s;%s' % (cpf, unicode(pf), 'NIS/PIS/PASEP inexistente!', s.tipo))
            except Exception as e:
                if pf.servidor_set.filter(ativo=True):
                    errors.append("%s;%s;%s;%s" % (s.tipo, cpf, str(pf), str(e)))
    print("")
    print("=================================")
    print("SERVIDORES INAPTOS A SEREM AVALIADOS")
    for l in errors:
        print(l)
        for doc in Documento.objects.filter(
            naturalpersons__cpf=l.split(";")[0], tipo_documento__in=[5, 6]
        ):
            print(doc, doc.created_by, doc.created_at, doc.modified_by, doc.modified_at)


def compare_credit_files(file1, file2):
    import codecs

    paid_values = {}
    with codecs.open(file1, "r", encoding="utf-8") as infile:
        for line in infile:
            if line[13:14] == "A":
                emp = line[43:73]
                v = round(int(line[119:133]) / 100.0, 2)
                print(line[13:14], line[43:73], v)
                if emp not in paid_values:
                    paid_values[emp] = 0
                paid_values[emp] += v

    with codecs.open(file2, "r", encoding="utf-8") as infile:
        for line in infile:
            if line[13:14] == "A":
                emp = line[43:73]
                v = round(int(line[119:133]) / 100.0, 2)
                print(line[13:14], line[43:73], v)
                if emp not in paid_values:
                    paid_values[emp] = 0
                paid_values[emp] -= v

    print("************** RESULT ******************")
    for emp in list(paid_values.keys()):
        if paid_values[emp] != 0:
            print(paid_values[emp], emp)

    return paid_values


def const_to_parameter(app, const, new_const_name):
    from standard.models import Choice

    _dict_const = const
    if isinstance(_dict_const, tuple):
        _dict_const = dict((x, y) for x, y in _dict_const)
    for k in _dict_const:
        prefix = ("%s_" % app).upper()
        name = new_const_name
        if name.startswith(prefix):
            name = name.replace(prefix, "")
        c, created = Choice.objects.get_or_create(
            app_label=app, name=name, value=k, defaults={"label": _dict_const[k]}
        )
        if not created and c.label != _dict_const[k]:
            print(
                "WARN: Label diferent! %s.%s.%s %s != %s"
                % (c.app_label, c.name, c.value, c.label, _dict_const[k])
            )


def show_(payroll, type_of=1):
    from rh.gfp.models import FinancialReportPayroll

    rp_ = type_ = None
    sum_p1 = sum_p2 = 0
    for fr in FinancialReportPayroll.objects.filter(
        payroll=payroll, account_plan__finalidade=type_of
    ).order_by(
        "account_plan__regime_previdenciario",
        "account_plan__plano__tipo",
        "account_plan__plano__titulo",
    ):
        if rp_ != fr.account_plan.regime_previdenciario:
            if rp_:
                print("\033[93m%9.2f\033[0m" % sum_p2)
                print("\033[91m%9.2f\033[0m" % sum_p1)
                sum_p1 = 0
                type_ = None
            rp_ = fr.account_plan.regime_previdenciario
            print(
                "\n%s ======================================="
                % fr.account_plan.get_regime_previdenciario_display()
            )
        if type_ != fr.account_plan.plano.tipo:
            if type_:
                print("\033[93m%9.2f\033[0m" % sum_p2)
                sum_p2 = 0
            type_ = fr.account_plan.plano.tipo
            print(
                "%s ---------------------------------------"
                % fr.account_plan.plano.get_tipo_display()
            )
        sum_p1 += fr.value
        sum_p2 += fr.value
        print("%9.2f" % fr.value, fr.account_plan.plano.titulo)
    print("\033[93m%9.2f\033[0m" % sum_p2)
    print("\033[91m%9.2f\033[0m" % sum_p1)


def correct_vacation_events(event):
    from rh.gfp.models import FolhaEvento
    from rh.ferias.models import (
        PeriodoAquisitivoServidorUsufruto,
        PeriodoAquisitivoServidor,
    )

    pas = {}
    for fe in FolhaEvento.objects.filter(evento__numero=event):
        try:
            pasu = PeriodoAquisitivoServidorUsufruto.objects.get(pk__in=fe.oIds)
            if pasu.pas not in pas:
                pas[pasu.pas] = []
            pas[pasu.pas].append(fe)
            if pasu.pas.folha_evento_terco_constitucional != fe:
                print(
                    fe.pk,
                    fe.oIds,
                    pasu.pas.folha_evento_terco_constitucional,
                    ">>",
                    fe.folha,
                )
                ups = 0
                if (
                    not pasu.pas.folha_evento_terco_constitucional
                    or fe.folha.periodo
                    < pasu.pas.folha_evento_terco_constitucional.folha.periodo
                ):
                    ups = PeriodoAquisitivoServidor.objects.filter(
                        pk=pasu.pas.pk
                    ).update(folha_evento_terco_constitucional=fe)
                print(
                    "\033[9%dm%s\033[0m"
                    % (3 if ups else 2, ("UPDATED(%d)" % ups) if ups else "OK")
                )
        except PeriodoAquisitivoServidorUsufruto.DoesNotExist:
            print(fe.pk, fe.oIds, "\033[91m>>NE<<\033[0m >> ", fe.folha)
        except Exception as e:
            raise e
    print("")
    print(
        "*********************************** ERROS *****************************************"
    )
    for p in pas:
        if len(pas[p]) > 1:
            p1 = PeriodoAquisitivoServidor.objects.get(pk=p.pk)
            print(
                p,
                [fe.folha for fe in pas[p]],
                p1.folha_evento_terco_constitucional.folha,
            )


def paychecks_classifications(year):
    from rh.gfp.models import Periodo, ContraCheque
    from standard.models import Choice

    print(
        ">> \033[91m%-20s" % "TIPO",
    )
    for p in Periodo.objects.filter(ano=year):
        print(
            "%9s" % p,
        )
    print("\033[0m")
    for c in Choice.get_choices_for("gfp", "CLASSIFICATION_EMPLOYEE"):
        print(
            ">> %-20s" % c[1],
        )
        for p in Periodo.objects.filter(ano=2016):
            q = ContraCheque.objects.filter(classification=c[0], folha__periodo=p)
            print(
                "%04d:\033[93m%04d\033[0m"
                % (
                    q.filter(folha__tipo_folha=101).count(),
                    q.filter(folha__tipo_folha=104).count(),
                ),
            )
        print("")
    print(">> \033[94m%-20s\033[0m" % "TOTAL")
    for p in Periodo.objects.filter(ano=year):
        q = ContraCheque.objects.filter(folha__periodo=p)
        print(
            "%04d:\033[93m%04d\033[0m"
            % (
                q.filter(folha__tipo_folha=101).count(),
                q.filter(folha__tipo_folha=104).count(),
            )
        )
    print("")


def normalize_timestamps_fields_in_dumpdata_file(file):
    import codecs

    res1 = ""
    with codecs.open(file, "r") as input:
        txt = input.read()
        p1 = re.compile(r"\"created_by\": \[\"(?P<user>[a-z]+)\"\]")
        p2 = re.compile(r"\"modified_by\": \[\"(?P<user>[a-z]+)\"\]")
        res = re.sub(p1, '"created_by": ["athenas"]', txt)
        res1 = re.sub(p2, '"modified_by": ["athenas"]', res)

    with codecs.open(file, "w") as fout:
        fout.write(res1)

    ok = (
        len(
            set(re.findall(p1, res1))
            .union(set(re.findall(p2, res1)))
            .difference(set(["athenas"]))
        )
        == 0
    )
    print(ok)


def update_paycheck_differences():
    from rh.gfp import models as gfpm
    from django.db.models import F
    from contrib.middleware import set_current_user

    set_current_user("athenas")

    print(
        "UPDATEDS PDIs: %d"
        % gfpm.PaycheckDifferenceItem.objects.filter(
            fixed_value=0, fixed_employer_contribution=0, correction_factor=1
        ).update(fixed_value=F("value"))
    )

    for pd in gfpm.PaycheckDifference.objects.exclude(status__in=[4, 5, 6]):
        try:
            pd.save()
            # for pdi in pd.difference_items.all():
            #     pdi.save()
            if not pd.paid:
                print(pd.get_status_display(), pd, pd.payables)
        except gfpm.Evento.DoesNotExist:
            print("\033[94m%s\033[0m" % pd)
        except Exception as e:
            print(str(e))


def dir_lower(root):
    import os
    import shutil

    for r, sf, fs in os.walk(root, False):
        for d in sf:
            path_old = "%s/%s" % (r, d)
            path_new = "%s/%s" % (r, d.lower())
            # print path_old
            print("%s/%s >> %s" % (r, d, shutil.move(path_old, path_new)))


def update_RRA(payroll_id):
    from rh.gfp import models as gfpm
    from contrib.middleware import set_current_user

    set_current_user("athenas")
    rrapae = gfpm.RRA.objects.get(pk=3)
    payroll = gfpm.Folha.objects.get(pk=payroll_id)
    gfpm.FolhaEvento.objects.exclude(rra_employee=None).update(rra_employee=None)
    for res in rrapae.employeers.all():
        print("%050s" % res.employee)
        fe = payroll.lancamentos.get(
            servidor=res.employee, evento__numero="03500", contracheque__pensioner=None
        )
        print(res.months, res.factor, fe.prazo, res.factor * fe.prazo)
        res.months = res.factor * fe.prazo
        res.save()
        qnt = gfpm.FolhaEvento.objects.filter(
            folha__tipo_folha__abreviatura="PAE",
            servidor=res.employee,
            evento__numero__in=["03500", "03600", "99200"],
        ).update(rra_employee=res)
        gfpm.FolhaEvento.objects.filter(
            folha__tipo_folha__abreviatura="PAE",
            servidor=res.employee,
            evento__numero__in=["03500", "03600"],
        ).update(qnt=res.factor, correct_qnt=res.factor, qnt_max=0, correct_qnt_max=0)
        print(qnt)


def update_13_entries_references():
    from rh.gfp import models as gfpm

    ups = gfpm.FolhaEvento.objects.filter(
        folha__periodo__ano=2016,
        evento__genre_event__genre_number__in=[
            "017",
            "991",
            "901",
            "906",
            "911",
            "916",
        ],
    ).update(reference_month=13)
    print("UPDATEDS ENTRY REFERENCES FOR 13: %d" % ups)


def create_dirf_file(year, filename="dirf2017.txt"):
    from rh.gfp.generators.dirf.protocol import File
    from contrib.middleware import set_current_user
    from rh.gfp.dirf.models import Dialect

    set_current_user("athenas")

    dl = Dialect.objects.get(reference_year=year)
    fl = File(dl)
    data = str(fl)
    out = open(filename, "w")
    out.write(data)
    out.close()


def create_demonstrative_dirf(year=2017):
    from rh.gfp.dirf.models import DirfSummary

    evaluateds_persons = []
    for ds in DirfSummary.objects.filter(calendar_year=year - 1):
        if ds.person not in evaluateds_persons:
            pass


def _get_classification(cc):
    cargos = [p.quadro.cargo.tipo_lei_cargo for p in cc.servidor.posses.all()]
    classification = 8
    if cc.pensioner:
        if cc._get_pays_pension() == 2:
            classification = 7  # PARTILHA
        else:
            classification = 6  # PENSIONISTA
    elif "ES" in cargos or (not cc.servidor.ativo and cc.servidor.tipo == "E"):
        classification = 5  # ESTAGIARIO
    elif "AC" in cargos:
        if cc.servidor.bond:
            classification = 4  # A DISPOSICAO
        else:
            classification = 8  # SEM VINCULO
    elif cc.servidor.tipo == "M" and ("EF" in cargos or not cc.servidor.ativo):
        classification = 2  # MEMBRO
    elif "EF" in cargos:
        classification = 1  # EFETIVO
    elif "CM" in cargos:
        classification = 3  # COMISSIONADO
    else:
        classification = 8  # INDEFINIDO

    return classification


def update_classification_and_totals_paychecks():
    from rh.gfp import models as gfpm

    # from contrib.middleware import get_current_user, set_current_user
    # set_current_user('athenas')
    print("UPDATING PAYCHECKS ...")
    payroll = None
    for cc in gfpm.ContraCheque.objects.filter(pensioner=None).order_by(
        "folha__periodo", "folha"
    ):
        if payroll != cc.folha:
            payroll = cc.folha
            print(">>>>>>> %s" % payroll)
        cc.classification = _get_classification(cc)
        cc.total_liquido = cc._get_total_liquido()
        cc.total_bruto = cc._get_total_bruto()
        if cc.old_fields:
            print(cc)
            for k in cc.old_fields:
                print("%s: %s >> %s" % (k, cc.old_fields[k], getattr(cc, k)))
            print(
                gfpm.ContraCheque.objects.filter(pk=cc.pk).update(
                    total_liquido=cc.total_liquido,
                    total_bruto=cc.total_bruto,
                    classification=cc.classification,
                )
            )


def show_demonstratives(reference_year=2017):
    # from django.db import models
    # from rh.gfp import models as gfpm
    from rh.gfp.dirf import models as dirfm

    print("NATUREZA;NOME;3.1;3.2;3.4;3.5;4.2;4.3;4.6;4.7;5.1;5.2;QNTM")
    for dem in dirfm.Demonstrativo.objects.filter(
        declaracao__ano_base=reference_year - 1
    ).order_by("pessoa_fisica__nome"):
        print(
            "%s;%-50s;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%10.2f;%4.1f"
            % (
                dem.natureza.codigo,
                dem.pessoa_fisica,
                dem.rendimento or 0,
                dem.previdencia_oficial or 0,
                dem.pensao_alimenticia or 0,
                dem.imposto_retido or 0,
                dem.ajuda_custo or 0,
                dem.rendimento_molestia or 0,
                dem.idenizacao or 0,
                dem.outros or 0,
                dem.decimoterceiro or 0,
                dem.decimoterceiro_imposto or 0,
                dem.qnt_meses or 0,
            )
        )


# from rh.gfp.models import *
# for c in Cargo.objects.filter(carreira=4).exclude(level_instance__isnull=True).order_by('level_instance'):
#     print c.entrancia, c.instancia, c.level_instance, c,
#     ce, created = es.cargos_estrutura.get_or_create(cargo=c, data_vigencia_inicio=date(2015,1,1), publicacao_id=1)
#     refs = ce.referencias.filter(pk=c.level_instance+59)
#     if not refs:
#         ce.referencias.add(c.level_instance+59)
#     print [rn for rn in ce.referencias.all()]


# import datetime
# with open('../migrations.txt', 'r') as f:
#     app = ''
#     ts = datetime.datetime.now()
#     for l in f.readlines():
#         obj = l.split(':')
#         if len(obj) == 1:
#             app = obj[0][:-1]
#         else:
#             print "\"INSERT INTO films (app, name, applied) VALUES (
#                       '%s', '%s', '%s');\"" % (app, obj[1][:-1], ts.strftime('%Y-%m-%d')


def correction_paycheck_differences():
    from rh.gfp.models import PaycheckDifference, FolhaEvento
    from django.db import models
    from contrib.middleware import set_current_user

    set_current_user("athenas")

    RED = "\033[0;31m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"

    for pd in PaycheckDifference.objects.filter(installments__gt=1).order_by(
        "status", "identifier"
    ):
        pd.save()
        vvs = pd.difference_items.aggregate(
            v=models.Sum("value"),
            fv=models.Sum("fixed_value"),
            ec=models.Sum("employer_contribution"),
            fec=models.Sum("fixed_employer_contribution"),
        )
        print(
            "%s%s %d %d %0.2f/%0.2f %0.2f/%0.2f"
            % (
                WHITE if pd.paid else RED,
                pd.identifier,
                pd.installments,
                pd.entries_payment.aggregate(total=models.Sum("installments_paid"))[
                    "total"
                ]
                or 0,
                vvs["v"],
                vvs["fv"],
                vvs["ec"],
                vvs["fec"],
            )
        )
        first = pd.entries_payment.order_by("parcela").first()
        if first:
            last = pd.entries_payment.order_by("parcela").last()
            fe_n = FolhaEvento.objects.filter(
                contracheque__servidor=pd.employee,
                evento=first.evento,
                info=first.info,
                paycheck_difference__isnull=True,
            ).aggregate(total=models.Sum("installments_paid"))
            print(
                first.contracheque.folha.periodo,
                last.contracheque.folha.periodo,
                fe_n["total"] or 0,
            )
        else:
            print("")
        print("%s%s" % (NC, pd.get_status_display()))
        if not pd.paid:
            print(pd.payable)
        else:
            print("")


def check_differences(update_pdi=False):
    from rh.gfp.models import PaycheckDifference, PaycheckDifferenceItem
    from contrib.middleware import set_current_user

    set_current_user("athenas")
    GREEN = "\033[0;32m"
    NC = "\033[0m"

    if update_pdi:
        print("Updating PDI (aguarde): ")
        for pdi in PaycheckDifferenceItem.objects.all():
            pdi.save()
            pdi.difference.save()
        print("%sOK%s" % (GREEN, NC))

    for pd in PaycheckDifference.objects.exclude(status__in=[6, 4]).order_by(
        "status", "reference_year", "reference_month", "employee"
    ):
        pp = pd.payable
        if pp["value"] != 0 or pp["employer_contribution"] != 0:
            print(
                pd.reference_month,
                pd.reference_year,
                pd.get_status_display(),
                pd.identifier,
            )
            print(pd.entries_payment.count(), pd.payable)


def clear_null_entries():
    from rh.gfp.models import FolhaEvento, PaycheckDifference

    for fe in FolhaEvento.objects.filter(
        valor=0, correct_valor=0, patronal=0, correct_patronal=0, folha=855
    ):
        print(fe.info, fe.folha.periodo, fe, fe.delete())

    for pd in PaycheckDifference.objects.filter(
        event__numero="51000",
        status=6,
        reference_year=2017,
        reference_month__in=[2, 3, 4, 5],
    ).order_by("employee", "reference_month"):
        pd.delete()


def rollup_payroll(payroll, loop=1, registrations=[]):
    from rh.gfp.models import Periodo, Folha
    from datetime import date
    from dateutil.relativedelta import relativedelta

    new_payroll = None
    base_payroll = payroll

    while loop:
        base_next_date = date(
            base_payroll.periodo.ano, base_payroll.periodo.mes, 1
        ) + relativedelta(months=1)

        periodo_to, p_created = Periodo.objects.get_or_create(
            ano=base_next_date.year,
            mes=base_next_date.month,
            defaults={
                "salario_minimo": base_payroll.periodo.salario_minimo,
                "salario_teto_adm": base_payroll.periodo.salario_teto_adm,
                "salario_teto_membros": base_payroll.periodo.salario_teto_membros,
                "salario_familia": base_payroll.periodo.salario_familia,
                "auxilio_creche": base_payroll.periodo.auxilio_creche,
                "auxilio_alimentacao": base_payroll.periodo.auxilio_alimentacao,
            },
        )

        new_payroll, created = Folha.objects.get_or_create(
            periodo=periodo_to,
            tipo_folha=base_payroll.tipo_folha,
            defaults={
                # TODO Procurar um configuração para a data provável de pagamento
                "dt_pagamento": (
                    base_payroll.dt_fechamento + relativedelta(months=1)
                    if base_payroll.dt_fechamento
                    else None
                )
            },
        )
        print("ROLL %s TO %s" % (base_payroll, new_payroll))
        base_payroll.copy_to(
            new_payroll,
            to_exists=False,
            to_can_clear=False,
            registrations=registrations,
        )
        print("\033[0;32mOK\033[0m")

        loop -= 1
        base_payroll = new_payroll

    return new_payroll


def update_differences_totals(registrations=[], years=[], only_in_installment=False):
    from rh.gfp.models import PaycheckDifference  # , PaycheckDifferenceItem
    from contrib.middleware import set_current_user

    set_current_user("athenas")
    RED = "\033[0;31m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"
    GREEN = "\033[0;32m"
    q_differences = PaycheckDifference.objects.exclude(status__in=[4, 6])

    if registrations:
        q_differences = q_differences.filter(employee__matricula__in=registrations)

    if years:
        q_differences = q_differences.filter(reference_year__in=years)

    if only_in_installment:
        q_differences = q_differences.filter(installments__gt=1)

    for pd in q_differences:

        if pd.installments > 1 and pd.entries_payment.exists():
            fe = pd.entries_payment.last()
            fe1 = fe.origem_para.first()
            while fe1:
                if not fe1.paycheck_difference:
                    fe1.paycheck_difference = pd
                    fe1.save()
                    print(".")
                fe1 = fe1.origem_para.first()

        qnt_paids = len(pd.payables)
        if pd.difference_items.count():
            #  totals = pd.difference_items.aggregate(v=Sum('fixed_value'), ec=Sum('employer_contribution'))
            # t_paid = pd.entries_payment.aggregate(v=Sum('valor'), ec=Sum('patronal'))

            pd.total_value = 0
            pd.total_employer_contribution = 0
        # paid = pd.total_value == t_paid['v'] and pd.total_employer_contribution == t_paid['ec']
        if qnt_paids == 1:
            pd.payment_event = list(pd.payables.keys())[0]

            fe_payment = pd.entries_payment.last()
            if fe_payment and pd.payment_event != fe_payment.evento:
                print(
                    "%s%s/%s%s"
                    % (RED, pd.payment_event.numero, fe_payment.evento.numero, NC)
                )
                pd.payment_event = fe_payment.evento
                if fe_payment.evento.numero == "51500":
                    pd.total_employer_contribution = 0

        pd.save()
        print(
            "%s%d%s" % (RED if qnt_paids != 1 else WHITE, qnt_paids, NC),
            pd.paid,
            pd.status,
            pd.get_status_display(),
            pd,
        )
        # print('%s%0.2f/%0.2f <> %0.2f/%0.2f%s %s' % (
        #     RED if paid != pd.paid else GREEN, pd.total_value,
        #     pd.total_employer_contribution, t_paid['v'] or 0, t_paid['ec'] or 0, NC, paid))


def correct_dif(self):
    from contrib.middleware import set_current_user
    from rh.gfp.models import FolhaEvento, PaycheckDifference

    set_current_user("raysonsilva")

    fe = FolhaEvento.objects.filter(
        folha=865, evento__numero="70700", servidor__matricula=112359001
    ).first()
    pd = PaycheckDifference.objects.get(identifier="b0bad7050d284c41879d6155d73d0aeb")

    while fe:
        print(FolhaEvento.objects.filter(pk=fe.pk).update(paycheck_difference=pd))
        fe = fe.copia_de


def dif_16597():
    from rh.gfp.models import FolhaEvento, Folha, CorrectionFactor
    from django.db.models import Sum
    from contrib.middleware import set_current_user

    set_current_user("athenas")
    f = Folha.objects.get(pk=873)

    CorrectionFactor.objects.filter(ref_payment_year=2017, ref_payment_month=10).update(
        ref_payment_month=9
    )
    for cf in CorrectionFactor.objects.all():
        cf.save()

    qfe = FolhaEvento.objects.filter(
        servidor__matricula=16597, evento__numero="00800", folha__periodo__ano=2015
    )
    pd = f.create_difference(
        qfe, installments=28, correction_factor_identifier="JEBRN.092017"
    )
    pd.apply_correction_factor(f)
    pd.total_value = pd.difference_items.aggregate(value=Sum("fixed_value"))["value"]
    pd.save()
    pd.apply_to(f, recalculate=True)
    qfe = FolhaEvento.objects.filter(
        servidor__matricula=16597, evento__numero="01500", folha__periodo__ano=2015
    )
    pd = f.create_difference(
        qfe, installments=28, correction_factor_identifier="JEBRN.092017"
    )
    pd.apply_correction_factor(f)
    pd.total_value = pd.difference_items.aggregate(value=Sum("fixed_value"))["value"]
    pd.save()
    pd.apply_to(f, recalculate=True)
    qfe = FolhaEvento.objects.filter(
        servidor__matricula=16597, evento__numero="01000", folha__periodo__ano=2016
    )
    pd = f.create_difference(
        qfe, installments=28, correction_factor_identifier="JEBRN.092017"
    )
    pd.apply_correction_factor(f)
    pd.total_value = pd.difference_items.aggregate(value=Sum("fixed_value"))["value"]
    pd.save()
    pd.apply_to(f, recalculate=True)
    qfe = FolhaEvento.objects.filter(
        servidor__matricula=16597, evento__numero="01000", folha__periodo__ano=2017
    )
    pd = f.create_difference(
        qfe, installments=28, correction_factor_identifier="JEBRN.092017"
    )
    pd.apply_correction_factor(f)
    pd.total_value = pd.difference_items.aggregate(value=Sum("fixed_value"))["value"]
    pd.save()
    pd.apply_to(f, recalculate=True)


def antecipar_diferencas(payroll, parcels_to_anticipate=1, query_entries=[]):
    for fe in query_entries:
        total = fe.paycheck_difference.payable["value"] + float(fe.valor)
        new_deadline = fe.prazo - parcels_to_anticipate
        value = round(total / (new_deadline - fe.parcela + 1), 2)
        fe.valor = value
        fe.prazo = new_deadline
        fe.save()
        pd = fe.paycheck_difference
        # ups = payroll.lancamentos.filter(pk=fe.pk).update(
        #     valor=value,
        #     correct_valor=value,
        #     correct_value=value,
        #     prazo=new_deadline
        # )
        pd.installments = new_deadline
        pd.save()
        print(fe.paycheck_difference.payable["value"], fe.diff, fe, fe.servidor)


# from rh.gfp.models import Folha
# from rh.gfp.scripts import eventos_diferentes
# from contrib.middleware import set_current_user
# f = Folha.objects.get(pk=955)
# set_current_user('eliasoliveira')
# events = ['05306', '07906', '07106', '05406', '05506']
# query_entries = f.lancamentos.filter(evento__numero__in=events, prazo=8).exclude(paycheck_difference__isnull=True)
# eventos_diferentes.antecipar_diferencas(f, query_entries=query_entries)

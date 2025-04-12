# -*- coding: utf-8 -*-

# from datetime import date, datetime
# from decimal import Decimal

# from dateutil.relativedelta import relativedelta
# from django import forms as django_forms
# from django.contrib.auth.models import User
# from django.db.models import Q

from contrib import extjs
from django import forms
from contrib.utils import DateUtils, get_json_engine, getLogger
from planejamento.contrato import models

# from rh.models import Pessoa, PessoaFisica, PessoaJuridica
# from standard.views import AutoCompleteField

json = get_json_engine()

log = getLogger(__name__)


# class SPCGestor(extjs.ExtCrud):

#     titles = {

#         'PANEL': u'Gestores',

#         'LIST': u'Lista de Gestores',

#         'NEW': u'Adicionar um novo Gestor',

#         'EDIT': u'Editando um Gestor',

#         'DELETE': u'Deletando um Gestor'

#     }

#     class Form(forms.ModelForm):

#         user = AutoCompleteField(

#             model=User,

#             controller='AUTHUser',

#             label=u'Usuário'

#         )

#         class Meta:

#             exclude = []

#             model = models.Gestor

#     def get_columns_grid(self, args=[]):

#         obj = [

#             {'header': 'Chave', 'sortable': True, 'dataIndex': 'id', 'key': 'id'},

#             {'header': 'Tipo', 'sortable': True, 'dataIndex': 'tipo', 'key': 'tipo', 'width': 250},

#             {'header': 'Usuário', 'sortable': True, 'dataIndex': 'user', 'key': 'user', 'width': 250}

#         ]

#         obj = self._apply_to_search_for_columns_grid(obj)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCGestorContrato(extjs.ExtWidget):

#     @property
#     def last_day_month(self, args=[]):

#         import calendar

#         today = datetime.now()

#         last_day_month = calendar.monthrange(today.year, today.month)[1]

#         return last_day_month

#     def get_date_payday(self, row):

#         today = datetime.now()

#         if int(row.dia_pagamento) > int(self.last_day_month):

#             return date(today.year, today.month, int(self.last_day_month))

#         else:

#             return date(today.year, today.month, int(row.dia_pagamento))

#     @decorator.login_required(type='JSON')
#     def commit_action(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': 'Nada foi feito ainda.'

#         }

#         values = {

#             'contrato': int(self.request.POST['contrato']),

#             'tipo': int(self.request.POST['tipo']),

#             'user': self.request.user.pk,

#             'observacao': self.request.POST['observacao']

#         }

#         class Form(forms.ModelForm):

#             class Meta:

#                 exclude = []

#                 model = models.AcaoContrato

#         frm = Form(values)

#         if frm.is_valid():

#             try:

#                 if values.get('tipo') == 2:

#                     if self.request.POST.get('tipo_prorrogacao') == '2':

#                         self.log.info(u'Tipo de prorrogação: %s' % self.request.POST.get('tipo_prorrogacao'))

#                         self.log.info(u'Periodo solicitado: %s' % self.request.POST.get('periodo'))

#                         frm.instance._prorroga_mes = int(self.request.POST.get('periodo'))

#                 frm.save()

#                 obj['success'] = True

#             except Exception as e:

#                 obj['msg'] = unicode(e)

#         else:

#             obj['errors'] = [{'field': err, 'error': frm.errors[err].as_text()} for err in frm.errors]

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     def get_action_information(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': 'Nada foi feito ainda.'

#         }

#         try:

#             acao = models.AcaoContrato.objects.get(pk=int(self.request.POST['pk']))

#             obj['object'] = {

#                 'pk': acao.pk,

#                 'contrato': acao.contrato.pk,

#                 'tipo': (acao.tipo, acao.get_tipo_display()),

#                 'observacao': acao.observacao

#             }

#             obj['success'] = True

#         except:

#             obj['msg'] = u'Não foi possivel encontrar ou carregar as informações desta ação.'

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     def update(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': u'Nada foi feito ainda.'

#         }

#         class Form(forms.ModelForm):

#             class Meta:

#                 exclude = []

#                 model = models.Contrato

#         self.log.info(self.request.POST)

#         # self.log.info(self.request.user.como_gestor.tipo)

#         # self.log.info(self.request.POST.getlist('contratado'))

#         contrato = models.Contrato.objects.get(pk=int(self.request.POST['pk']))

#         numero_pasta = self.request.POST['numero_pasta'] if 'numero_pasta' in self.request.POST else None

#         if numero_pasta == '':

#             numero_pasta = '0'

#         values = {

#             'responsaveis': self.request.POST.getlist('responsaveis') if 'responsaveis' in self.request.POST else None,

#             'pessoa': self.request.POST.getlist('contratado') if 'contratado' in self.request.POST else None,

#             'numero': self.request.POST['numero'] if 'numero' in self.request.POST else None,

#             'numero_processo': self.request.POST['numero_processo'] if 'numero_processo' in self.request.POST else None,

#             'numero_processo_mae': self.request.POST['numero_processo_mae'] if 'numero_processo_mae' in self.request.POST else None,

#             # 'data_inicio': contrato.data_inicio,

#             'data_inicio': self.request.POST['data_inicio'] if 'data_inicio' in self.request.POST else None,

#             'data_vencimento': contrato.data_vencimento,

#             'dias_para_aviso': self.request.POST['dias_para_aviso'] if 'dias_para_aviso' in self.request.POST else 90,

#             'objeto_contrato': self.request.POST['objeto_contrato'] if 'objeto_contrato' in self.request.POST else None,

#             'gestor': self.request.POST['pk_gestor'] if 'pk_gestor' in self.request.POST else self.request.user.como_gestor.pk,

#             'tipo_licitacao': self.request.POST['tipo_licitacao'] if 'tipo_licitacao' in self.request.POST else None,

#             'numero_licitacao': self.request.POST['numero_licitacao'] if 'numero_licitacao' in self.request.POST else None,

#             'valor': self.request.POST['valor'] if 'valor' in self.request.POST else None,

#             'tipo_medicao': self.request.POST['tipo_medicao'] if 'tipo_medicao' in self.request.POST else None,

#             'dia_pagamento': self.request.POST['dia_pagamento'] if 'dia_pagamento' in self.request.POST else None,

#             'tipo_contrato': self.request.POST['tipo_contrato'] if 'tipo_contrato' in self.request.POST else None,

#             'numero_pasta': numero_pasta,

#             'data_publicacao': self.request.POST['data_publicacao'] if 'data_publicacao' in self.request.POST else None,

#             'data_publicacao_fiscal': self.request.POST['data_publicacao_fiscal']
#               if 'data_publicacao_fiscal' in self.request.POST else None,

#         }

#         values['status'] = contrato.status

#         values['max_mes'] = contrato.max_mes

#         values['data_vencimento_original'] = contrato.data_vencimento_original

#         values['prorrogado'] = contrato.prorrogado

#         frm = Form(values, instance=contrato)

#         try:

#             frm.save()

#             obj['pk'] = contrato.id

#             obj['success'] = True

#             obj['msg'] = 'Dados salvos com sucesso!'

#         except Exception as e:

#             obj['errors'] = [{'field': err, 'error': frm.errors[err].as_text()} for err in frm.errors]

#             obj['msg'] = unicode(e)

#             self.log.exception(e)

#         # self.log.info(obj)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     def create(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': u'Nada foi feito ainda.'

#         }

#         class Form(forms.ModelForm):

#             class Meta:

#                 exclude = []

#                 model = models.Contrato

#         numero_pasta = self.request.POST['numero_pasta'] if 'numero_pasta' in self.request.POST else None

#         if numero_pasta == '':

#             numero_pasta = '0'

#         values = {

#             'responsaveis': self.request.POST.getlist('responsaveis') if 'responsaveis' in self.request.POST else [],

#             'pessoa': self.request.POST.getlist('contratado') if 'contratado' in self.request.POST else [],

#             'numero': self.request.POST['numero'] if 'numero' in self.request.POST else None,

#             'numero_processo': self.request.POST['numero_processo'] if 'numero_processo' in self.request.POST else None,

#             'numero_processo_mae': self.request.POST['numero_processo_mae'] if 'numero_processo_mae' in self.request.POST else None,

#             'data_inicio': self.request.POST['data_inicio'] if 'data_inicio' in self.request.POST else None,

#             'data_vencimento': self.request.POST['data_vencimento_flag'] if 'data_vencimento_flag' in self.request.POST else None,

#             'dias_para_aviso': self.request.POST['dias_para_aviso'] if 'dias_para_aviso' in self.request.POST else 90,

#             'objeto_contrato': self.request.POST['objeto_contrato'] if 'objeto_contrato' in self.request.POST else None,

#             'gestor': self.request.POST['pk_gestor'] if 'pk_gestor' in self.request.POST else self.request.user.como_gestor.pk,

#             'tipo_licitacao': self.request.POST['tipo_licitacao'] if 'tipo_licitacao' in self.request.POST else None,

#             'numero_licitacao': self.request.POST['numero_licitacao'] if 'numero_licitacao' in self.request.POST else None,

#             'valor': self.request.POST['valor'] if 'valor' in self.request.POST else None,

#             'tipo_medicao': self.request.POST['tipo_medicao'] if 'tipo_medicao' in self.request.POST else None,

#             'dia_pagamento': self.request.POST['dia_pagamento'] if 'dia_pagamento' in self.request.POST else None,

#             'tipo_contrato': self.request.POST['tipo_contrato'] if 'tipo_contrato' in self.request.POST else None,

#             'numero_pasta': numero_pasta,

#             'data_publicacao': self.request.POST['data_publicacao'] if 'data_publicacao' in self.request.POST else None,

#             'data_publicacao_fiscal': self.request.POST['data_publicacao_fiscal']
#               if 'data_publicacao_fiscal' in self.request.POST else None,

#             'status': 0

#         }

#         if values['gestor'] == '':

#             values['gestor'] = self.request.user.como_gestor.pk

#         # if values['gestor'] != self.request.user.como_gestor.pk:

#         #     values['responsaveis'].append(self.request.user.como_gestor.pk)

#         # self.log.debug(values)

#         try:

#             frm = Form(values)

#             if frm.is_valid():

#                 frm.save()

#                 obj['success'] = True

#                 models.AcaoContrato(

#                     contrato=frm.instance,

#                     tipo=0,

#                     observacao=u'Criação do contrato no sistema.',

#                     user=self.request.user

#                 ).save()

#                 obj['pk'] = frm.instance.id

#                 obj['msg'] = 'Dados salvos com sucesso!'

#                 self.log.info('>> erro ao salvar antes do else')

#             else:

#                 self.log.info('>> erro ao salvar')

#                 obj['msg'] = u'O formulário não foi preenchido de forma correta.'

#                 obj['errors'] = [{'field': err, 'error': frm.errors[err].as_text()} for err in frm.errors]

#         except Exception as e:

#             obj['msg'] = unicode(e)

#             # raise e

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     def autocomplete(self, args=[]):

#         obj = {

#             'result': []

#         }

#         model = None

#         qs = []

#         if 'model' in self.request.POST and 'query' in self.request.POST:

#             if self.request.POST['model'] == 'PessoaJuridica':

#                 qs.append(Q(nome__icontains=self.request.POST['query']))

#                 qs.append(Q(cnpj__icontains=self.request.POST['query']))

#                 qs.append(Q(razao_social__icontains=self.request.POST['query']))

#                 model = PessoaJuridica

#             elif self.request.POST['model'] == 'PessoaFisica':

#                 qs.append(Q(nome__icontains=self.request.POST['query']))

#                 qs.append(Q(cpf__icontains=self.request.POST['query']))

#                 model = PessoaFisica

#             elif self.request.POST['model'] == 'Gestor':

#                 qs.append(Q(user__username__icontains=self.request.POST['query']))

#                 qs.append(Q(user__first_name__icontains=self.request.POST['query']))

#                 qs.append(Q(user__last_name__icontains=self.request.POST['query']))

#                 qs.append(Q(user__email__icontains=self.request.POST['query']))

#                 qs.append(Q(user__servidor__pessoa_fisica__nome__icontains=self.request.POST['query']))

#                 model = models.Gestor

#         if model is not None:

#             q = None

#             for qN in qs:

#                 q = qN if q is None else Q(q | qN)

#             obj['result'] = [{'pk': row.pk, 'description': unicode(row)} for row in model.objects.filter(q)]

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     def json(self, args=[]):

#         self.response['content-type'] = 'text/javascript'

#         try:

#             tipo = self.request.user.como_gestor.tipo

#         except Exception as e:

#             tipo = 1

#             g = models.Gestor(user=self.request.user, tipo=tipo)

#             g.save()

#         self.response.write(

#             'new toolkit.planejamento.contrato.GestorContrato(%d)' % tipo

#         )

#     @decorator.login_required(type='JSON')
#     def get_list_gestor(self):

#         gestor = self.request.user.como_gestor

#         query = models.Contrato.objects.filter(Q(gestor=gestor) | Q(responsaveis=gestor))

#         ids = set()

#         for row in query:

#             ids.add(row.pk)

#         ids = list(ids)

#         return ids

#     def get_list_geral(self):

#         query = models.Contrato.objects.all()

#         ids = set()

#         for row in query:

#             ids.add(row.pk)

#         ids = list(ids)

#         return ids

#     def get_list_contrato(self):

#         query = models.Contrato.objects.filter(status__in=(0, 1, 2, 3))

#         ids = set()

#         for row in query:

#             ids.add(row.pk)

#         ids = list(ids)

#         self.log.debug(ids)

#         return ids

#     def get_list_licitacao(self):

#         query = models.Contrato.objects.filter(status=2)

#         ids = set()

#         for row in query:

#             ids.add(row.pk)

#         ids = list(ids)

#         return ids

#     def apply_filter(self, query):

#         qs = []

#         log.info(self.request.POST)

#         if 'keyword' in self.request.POST:

#             qs.append(Q(numero_processo__icontains=self.request.POST['keyword']))

#             qs.append(Q(numero__icontains=self.request.POST['keyword']))

#             # qs.append(Q(pessoa__nome__icontains=self.request.POST['keyword']))

#             qs.append(Q(gestor__user__username__icontains=self.request.POST['keyword']))

#             qs.append(Q(gestor__user__first_name__icontains=self.request.POST['keyword']))

#             qs.append(Q(gestor__user__last_name__icontains=self.request.POST['keyword']))

#             qs.append(Q(gestor__user__servidor__pessoa_fisica__nome__icontains=self.request.POST['keyword']))

#             qs.append(Q(objeto_contrato__icontains=self.request.POST['keyword']))

#         q = None

#         for qN in qs:

#             q = qN if q is None else Q(q | qN)

#         return query.filter(q) if q else query

#     def get_list(self, ids, ativo=False):

#         obj = []

#         totalRows = 0

#         if len(ids) > 0:

#             q = None

#             while len(ids) > 0:

#                 if q is None:

#                     q = Q(pk__in=ids[0:200])

#                 else:

#                     q = Q(q | Q(pk__in=ids[:200]))

#                 ids = ids[200:]

#             query = models.Contrato.objects.filter(q)

#             if 'sort' in self.request.POST and 'dir' in self.request.POST:

#                 if self.request.POST['dir'] == 'ASC':

#                     query = query.order_by(self.request.POST['sort'])

#                 else:

#                     query = query.order_by('-%s' % self.request.POST['sort'])

#             else:

#                 query = query.order_by('data_vencimento_flag', 'numero')

#             query = query.exclude(status=4) if ativo else query.filter(status=4)

#             if 'keyword' in self.request.POST:

#                 query = self.apply_filter(query)

#             totalRows = query.count()

#             start = int(self.request.POST['start']) if 'start' in self.request.POST else 0

#             limit = int(self.request.POST['limit']) if 'limit' in self.request.POST else 50

#             # today = datetime.now()

#             for row in query[start: (start + limit)]:

#                 states = self.get_state_icons(self.get_status(row))

#                 pgto = 0

#                 pgto_agendado = 0

#                 # data_pag_agendado = date(today.year, today.month, int(row.dia_pagamento)) if row.dia_pagamento is not None else None

#                 data_pag_agendado = self.get_date_payday(row) if row.dia_pagamento is not None else None

#                 if row.tipo_medicao is not None and row.tipo_medicao == 2 and row.dia_pagamento is not None and \
#                       datetime.now().date() > data_pag_agendado:

#                     for med in row.medicoes.all():

#                         if med.status != 2 and med.data_pagamento is None:

#                             pgto_agendado += 1

#                             # states.append({'iconCls': 'icon-contrato icon-warn', 'alt': 'Pendência em pagamentos agendados.'})

#                 else:

#                     for med in row.medicoes.all():

#                         if med.status != 2 and med.data_pagamento is None:

#                             pgto += 1

#                             # states.append({'iconCls': 'icon-contrato icon-warn', 'alt': 'Pendência em pagamentos.'})

#                 if pgto > 0:

#                     states.append({'iconCls': 'icon-contrato icon-warn', 'alt': u'Pendência em %s pagamento(s).' % pgto})

#                 elif pgto_agendado > 0:

#                     states.append(
#                           {'iconCls': 'icon-contrato icon-warn', 'alt': u'Pendência em %s pagamento(s) agendado(s).' % pgto_agendado})

#                 if row.prorrogado > 0:

#                     states.append(
#                       {'iconCls': 'icon-contrato icon-qtd-prorrogacao', 'alt': u'Contrato prorrogado %s vez(es)' % row.prorrogado})

#                 if not row.ne.all().count():

#                     states.append({'iconCls': 'icon-contrato icon-warn', 'alt': 'Ainda não existe NE cadastrada para este contrato.'})

#                 item = {

#                     'pk': row.pk,

#                     'numero': row.numero,

#                     'numero_processo': row.numero_processo,

#                     'numero_processo_mae': row.numero_processo_mae,

#                     'servico': row.numero_processo,

#                     'contratado': [],

#                     'data_inicio': row.data_inicio.strftime('%d/%m/%Y'),

#                     'data_vencimento_flag': DateUtils.date_to_str(row.data_vencimento_flag) if row.data_vencimento_flag else '',

#                     # 'gestor_unicode': unicode(row.gestor),

#                     'gestor': unicode(row.gestor),

#                     'pk_gestor': row.gestor.pk,

#                     # 'gestor': row.gestor.pk,

#                     'tipo_gestor': row.gestor.tipo,

#                     'objeto_contrato': row.objeto_contrato,

#                     'dias_para_aviso': row.dias_para_aviso,

#                     'responsaveis': [],

#                     'tipo_licitacao': row.tipo_licitacao,

#                     'tipo_contrato': row.tipo_contrato,

#                     'tipo_contrato_display': row.get_tipo_contrato_display(),

#                     'numero_licitacao': row.numero_licitacao,

#                     'valor': unicode(row.valor),

#                     'valor_contrato': unicode(row._valor_contrato),

#                     'tipo_medicao': row.tipo_medicao,

#                     'dia_pagamento': row.dia_pagamento,

#                     'numero_pasta': row.numero_pasta,

#                     'status': self.get_status(row),

#                     'tipo_contratado': self.get_status(row),

#                     'data_publicacao': row.data_publicacao.strftime('%d/%m/%Y') if row.data_publicacao else '',

#                     'data_publicacao_fiscal': row.data_publicacao_fiscal.strftime('%d/%m/%Y') if row.data_publicacao_fiscal else '',

#                     'icons': [

#                         {

#                             'iconCls': st['iconCls'],

#                             'alt': st['alt'],

#                             'title': st['alt']

#                         } for st in states

#                     ],

#                 }

#                 if row.responsaveis is not None and row.responsaveis.count() > 0:

#                     item['responsaveis'] = [(r.pk, unicode(r)) for r in row.responsaveis.all()]

#                 if row.pessoa is not None and row.pessoa.count() > 0:

#                     item['contratado'] = [(c.pk, unicode(c)) for c in row.pessoa.all()]

#                 obj.append(item)

#         return (totalRows, obj)

#     def get_status(self, e):

#         now = datetime.now().date()

#         days = relativedelta(days=e.dias_para_aviso)

#         if now >= e.data_vencimento_flag if e.data_vencimento_flag else e.data_vencimento:

#             atraso = 2

#         elif (now + days) > e.data_vencimento_flag if e.data_vencimento_flag else e.data_vencimento:

#             atraso = 1

#         elif e.dias_para_aviso == 0:

#             atraso = 0

#         else:

#             atraso = 0

#         pendencias = e.status

#         return {

#             'aviso_tempo': atraso,

#             'pendencia': pendencias,

#             'tipo_contratado': 0 if hasattr(e.pessoa.all()[0], 'pessoajuridica') else 1

#         }

#     def get_state_icons(self, param=None):

#         valor = param

#         status = []

#         if valor['tipo_contratado'] == 0:

#             status.append({'iconCls': 'icon-contrato icon-pessoa-juridica', 'alt': 'Contrato com pessoa jurídica'})

#         elif valor['tipo_contratado'] == 1:

#             status.append({'iconCls': 'icon-contrato icon-pessoa-fisica', 'alt': 'Contrato com pessoa física'})

#         if valor['aviso_tempo'] == 0:

#             status.append({'iconCls': 'icon-contrato icon-aviso-tempo-green', 'alt': 'Contrato dentro do prazo'})

#         elif valor['aviso_tempo'] == 1:

#             status.append({'iconCls': 'icon-contrato icon-aviso-tempo-yellow', 'alt': 'Contrato próximo do vencimento'})

#         elif valor['aviso_tempo'] == 2:

#             status.append({'iconCls': 'icon-contrato icon-aviso-tempo-red', 'alt': 'Contrato com prazo vencido'})

#         if valor['pendencia'] == 1:

#             status.append({'iconCls': 'icon-contrato icon-aviso-pendencia-prorrogacao', 'alt': 'Solicitado Prorrogação'})

#         elif valor['pendencia'] == 2:

#             status.append({'iconCls': 'icon-contrato icon-aviso-pendencia-licitacao', 'alt': 'Solicitado Licitação'})

#         elif valor['pendencia'] == 3:

#             status.append({'iconCls': 'icon-contrato icon-aviso-pendencia-recisao', 'alt': 'Solicitado Recisão do Contrato'})

#         return status

#     @decorator.login_required(type='JSON')
#     def list_action(self, args=[]):

#         obj = {

#             'result': []

#         }

#         gestor = self.request.user.como_gestor

#         q1 = Q(pk=int(self.request.POST['pk']))

#         try:

#             contrato = models.Contrato.objects.get(q1)

#             # self.apply_filter(contrato)

#             for acao in contrato.acoes.all().order_by('-data_acao'):

#                 obj['result'].append({

#                     'pk': acao.pk,

#                     'horario': acao.data_acao.strftime('%d/%m/%Y %H:%M'),

#                     'description': unicode(acao)

#                 })

#         except Exception as e:

#             self.log.exception(e)

#             self.log.warn(u'%s não é gestor do contrato PK(%s)' % (gestor, self.request.POST['pk']))

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def apply_filter_acao(self, query):

#         qs = []

#         if 'keyword' in self.request.POST:

#             qs.append(
#               Q(contrato__pk=int(self.request.POST['pk'])) & \
#               Q(user__servidor__pessoa_fisica__nome__icontains=self.request.POST['keyword']))

#         else:

#             qs.append(Q(contrato__pk=int(self.request.POST['pk'])))

#         q = None

#         for qN in qs:

#             q = qN if q is None else Q(q | qN)

#         # self.log.info(query.filter(q).count())

#         return query.filter(q)

#     def list_action_acao(self, args=[]):

#         obj = {

#             'result': []

#         }

#         # self.log.info(self.request.POST)

#         gestor = self.request.user.como_gestor

#         try:

#             acoes = models.AcaoContrato.objects.all()

#             query = self.apply_filter_acao(acoes).order_by('-data_acao')

#             for acao in query:

#                 obj['result'].append({

#                     'pk': acao.pk,

#                     'pk_contrato': acao.contrato.pk,

#                     'horario': acao.data_acao.strftime('%d/%m/%Y %H:%M'),

#                     'description': unicode(acao)

#                 })

#         except Exception as e:

#             self.log.exception(e)

#             self.log.warn(u'%s não é gestor do contrato PK(%s)' % (gestor, self.request.POST['pk']))

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     @decorator.login_required(type='JSON')
#     # @decorator.update_timeout_session(enable = False)
#     def list(self, args=[]):

#         obj = {

#             'result': [],

#             'totalRows': 0

#         }

#         # self.log.debug('Tipo de gestor -%d-' % self.request.user.como_gestor.tipo)

#         ids = []

#         if self.request.user.como_gestor.tipo == 2 or self.request.user.como_gestor.tipo == 3 or self.request.user.como_gestor.tipo == 5:

#             ids = self.get_list_geral()

#         else:

#             ids = self.get_list_gestor()

#             if self.request.user.como_gestor.tipo == 4:

#                 ids = set(ids)

#                 ids = ids.union(self.get_list_licitacao())

#         ativo = self.request.POST['active'] == '1' if 'active' in self.request.POST else True

#         # self.log.info('Total ids %s' % len(ids))

#         obj['totalRows'], obj['result'] = self.get_list(list(ids), ativo)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def list_contratados(self, args=[]):

#         obj = {

#             'result': [],

#             'totalRows': 0

#         }

#         # self.log.info(self.request.POST)

#         try:

#             R = self.request.REQUEST

#             start = int(R.get('start', 0))

#             end = int(R.get('limit', 50)) + start

#             contrato = models.Contrato.objects.get(pk=int(self.request.POST['pk_contrato']))

#             for forn in contrato.pessoa.all()[start:end]:

#                 obj['result'].append({

#                     'pk': forn.pk,

#                     'nome': u'%s' % forn.nome,

#                     'cpf_cnpj': u'%s' % forn.pessoafisica.cpf if hasattr(forn, 'pessoafisica') else forn.pessoajuridica.cnpj

#                 })

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCNotaEmpenho(extjs.ExtWidget):

#     class Form(forms.ModelForm):

#         class Meta:

#             exclude = []

#             model = models.NotaEmpenho

#     def apply_filter(self, query):

#         qs = []

#         if 'keyword' in self.request.POST:

#             pass

#             # qs.append(Q(contrato__pk=int(self.request.POST['pk']))

#         else:

#             qs.append(Q(contrato__pk=int(self.request.POST['pk_contrato'])))

#         q = None

#         for qN in qs:

#             q = qN if q is None else Q(q | qN)

#         return query.filter(q)

#     def list(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             # self.log.info(self.request.POST)

#             R = self.request.REQUEST

#             start = int(R.get('start', 0))

#             end = int(R.get('limit', 15)) + start

#             query = models.NotaEmpenho.objects.all()

#             query = self.apply_filter(query)

#             for ne in query[start:end]:

#                 states = ne.get_envio()

#                 obj['result'].append({

#                     'pk': ne.pk,

#                     'numero_ne': ne.numero_ne,

#                     'ne_principal': u'%s' % ne.ne_anterior.numero_ne if ne.ne_anterior else 'Principal',

#                     'numero_contrato': ne.contrato.numero,

#                     'fornecedor': u'%s' % ne.fornecedor,

#                     'fornecedor_id': ne.fornecedor_id,

#                     'valor_contrato': u'%s' % ne.ref_valor_contrato if ne.ref_valor_contrato else '',

#                     'valor_contrato_id': ne.ref_valor_contrato_id,

#                     'valor': ne.get_valor_ne(),

#                     # 'valor': float(ne.valor or 0),

#                     'saldo_ne': float(ne.get_saldo()),

#                     'tipo': ne.get_tipo_display(),

#                     'cadastrado_por': u'%s' % ne.criado_por.get_full_name(),

#                     'status_envio_ne': [

#                         {

#                             'iconCls': st['iconCls'],

#                             'alt': st['alt'],

#                             'title': st['alt']

#                         } for st in states

#                     ],

#                 })

#             obj.update(count=query.count())

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def get_list(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             ne = models.NotaEmpenho.objects.get(pk=self.request.POST['pk'])

#         except Exception as e:

#             obj.update({

#                 'message': u'Não consegui encontrar a NE desejada.',

#                 'success': False

#             })

#             self.log.info(e)

#         else:

#             obj.update({

#                 'collection': {

#                     'pk': ne.pk,

#                     'numero_ne': ne.numero_ne,

#                     'numero_contrato': ne.contrato.numero,

#                     'fornecedor': u'%s' % ne.fornecedor,

#                     'fornecedor_id': ne.fornecedor_id,

#                     'valor_contrato': u'%s' % ne.ref_valor_contrato.get_ordem_display() if ne.ref_valor_contrato else '',

#                     'valor_contrato_id': ne.ref_valor_contrato_id,

#                     'valor': float(ne.valor or 0),

#                     'saldo_ne': float(ne.get_saldo()),

#                     # 'saldo_ne':ne.get_saldo(),

#                     'prazo_entrega': ne.prazo_entrega,

#                     'tipo': ne.tipo,

#                     'classificacao': ne.classificacao,

#                     'cadastrado_por': u'%s' % ne.criado_por

#                 },

#                 'success': True

#             })

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def get_ne_contrato(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         # self.log.info(self.request.POST)

#         try:

#             nota_empenho = models.NotaEmpenho.objects.filter(
#               contrato__id=self.request.POST['pk_contrato']).exclude(ne_anterior__isnull=False).order_by('id')

#             for ne in nota_empenho:

#                 if ne.get_saldo() > 0:

#                     obj['result'].append({

#                         'pk': ne.pk,

#                         'ne': u'%s - %s - %s' % (ne.numero_ne, ne.get_classificacao_display(), ne.fornecedor)

#                     })

#                 # if ne.tipo==2:

#                 #     n = nota_empenho[0]

#                 #     obj['result'].append({

#                 #         'pk': n.pk,

#                 #         'ne': u'%s - %s - %s' % (n.numero_ne,n.get_classificacao_display(), n.fornecedor)

#                 #     })

#                 # else:

#                 #     obj['result'].append({

#                 #         'pk': ne.pk,

#                 #         'ne': u'%s - %s - %s' % (ne.numero_ne,ne.get_classificacao_display(), ne.fornecedor)

#                 #     })

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def create(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda',

#             'success': False

#         }

#         # self.log.info(self.request.POST)

#         try:

#             contrato = models.Contrato.objects.get(pk=int(self.request.POST['contrato_id']))

#             fornecedor = Pessoa.objects.get(pk=int(self.request.POST['fornecedor']))

#             valor_contrato = models.ValorContrato.objects.get(pk=int(self.request.POST['valor_contrato']))

#             ne_anterior = models.NotaEmpenho.objects.get(pk=int(self.request.POST['ne_id'])) if self.request.POST['ne_id'] else None

#             ne = models.NotaEmpenho(

#                 ne_anterior=ne_anterior,

#                 contrato=contrato,

#                 numero_ne=self.request.POST['numero_ne'].upper(),

#                 valor=self.request.POST['valor'],

#                 tipo=self.request.POST['tipo'],

#                 classificacao=self.request.POST['classificacao'],

#                 prazo_entrega=self.request.POST['prazo_entrega'],

#                 reforco_estorno=self.request.POST['reforco_estorno'] if self.request.POST['reforco_estorno'] else None,

#                 fornecedor=fornecedor,

#                 criado_por=self.request.user,

#                 ref_valor_contrato=valor_contrato

#             )

#             ne.save()

#             self.log.info('%s salvou NE: %s' % (self.request.user, ne.numero_ne))

#         except Exception as e:

#             # transaction.rollback()

#             self.log.info(e)

#             obj.update(success=False)

#             obj.update(message=unicode(e))

#             # obj.update(message = 'Ocorreu um erro ao salvar NE!')

#         else:

#             # transaction.commit()

#             obj.update(success=True)

#             obj.update(message='NE salva com Sucesso!')

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def update(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda'

#         }

#         # self.log.info(self.request.POST)

#         try:

#             ne = models.NotaEmpenho.objects.get(pk=self.request.POST['pk'])

#             fornecedor = Pessoa.objects.get(pk=int(self.request.POST['fornecedor']))

#             valor_contrato = models.ValorContrato.objects.get(pk=int(self.request.POST['valor_contrato']))

#             ne.numero_ne = self.request.POST['numero_ne']

#             ne.tipo = int(self.request.REQUEST.get('tipo'))

#             ne.classificacao = int(self.request.REQUEST.get('classificacao'))

#             ne.prazo_entrega = int(self.request.REQUEST.get('prazo_entrega'))

#             ne.valor = self.request.REQUEST.get('valor')

#             ne.fornecedor = fornecedor

#             ne.criado_por = self.request.user

#             ne.ref_valor_contrato = valor_contrato

#             ne.save()

#         except Exception as e:

#             self.log.info(e)

#             # transaction.rollback()

#             obj.update(success=False)

#             obj.update(message=unicode(e))

#             # obj.update(message = 'Ocorreu um erro ao alterar NE!')

#         else:

#             # transaction.commit()

#             obj.update(success=True)

#             obj.update(message='NE alterada com Sucesso!')

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def remove(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             nota_empenho = models.NotaEmpenho.objects.filter(pk__in=self.request.POST.getlist('pk'))

#             for ne in nota_empenho:

#                 ne.delete()

#         except Exception as e:

#             self.log.error(e)

#             obj.update({

#                 'success': False,

#                 'message': e.message

#             })

#         else:

#             obj.update({

#                 'success': True

#             })

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def enviar_ne_fornecedor(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda'

#         }

#         self.log.info(self.request.POST)

#         self.log.info(datetime.now().date())

#         try:

#             ne = models.NotaEmpenho.objects.get(pk=self.request.POST['pk'])

#             if int(self.request.POST['prorrogacao']) == 0:

#                 # é uma prorrogacao

#                 envio_ne = models.EnvioNEFornecedor(

#                     nota_empenho=ne,

#                     prorrogacao=self.request.POST['prorrogacao'],

#                     dias_prorrogacao=self.request.POST['dias_prorrogacao']

#                 )

#             else:

#                 # não é uma prorrogacao

#                 envio_ne = models.EnvioNEFornecedor(

#                     nota_empenho=ne,

#                     prorrogacao=int(self.request.POST['prorrogacao'])

#                 )

#             envio_ne.save()

#         except Exception as e:

#             self.log.info(e)

#             obj.update(success=False)

#             # obj.update(message=unicode(e))

#             obj.update(message='Ocorreu um erro ao gravas os dados.')

#         else:

#             obj.update(success=True)

#             obj.update(message='Salvo com Sucesso!')

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def get_fornecedores(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda'

#         }

#         # self.log.info(self.request.POST)

#         try:

#             contrato = models.Contrato.objects.get(pk=int(self.request.POST['pk_contrato']))

#             for forn in contrato.pessoa.all():

#                 obj['result'].append({

#                     'pk': forn.pk,

#                     'description': u'%s' % forn.nome

#                 })

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def get_valores_contrato(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda'

#         }

#         # self.log.info(self.request.POST)

#         try:

#             contrato = models.Contrato.objects.get(pk=int(self.request.POST['pk_contrato']))

#             for valor_contrato in contrato.valores_contrato.all():

#                 obj['result'].append({

#                     'pk': valor_contrato.pk,

#                     'descricao': valor_contrato.get_ordem_display()

#                     # 'descricao': u'%s' % ( valor_contrato.ordem if valor_contrato.ordem != 0 else 'Principal')

#                     #     DateUtils.date_to_str(valor_contrato.data_ref_inicio),

#                     #     DateUtils.date_to_str(valor_contrato.data_ref_fim),

#                     #     br_money(round(valor_contrato.valor, 2))

#                     # )

#                 })

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCMedicao(extjs.ExtWidget):

#     nota_empenho = AutoCompleteField(

#         model=models.NotaEmpenho,

#         controller='SPCNotaEmpenho',

#         label=u'Nota de Empenho'

#     )

#     def commit(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': u'Não foi feito nada ainda.'

#         }

#         # self.log.info(self.request.POST)

#         try:

#             ne = models.NotaEmpenho.objects.get(pk=int(self.request.POST['nota_empenho']))

#             values = {

#                 'nota_empenho': ne.pk,

#                 'inicio_periodo_referencia': self.request.POST['inicio_periodo'],

#                 'fim_periodo_referencia': self.request.POST['fim_periodo'],

#                 'contrato': self.request.POST['contrato'] if 'contrato' in self.request.POST else None,

#                 'user': self.request.user.pk,

#                 'valor': str(self.request.POST['valor']) if 'valor' in self.request.POST else '0.0',

#                 'nota_fiscal': self.request.POST['nota_fiscal'] if 'nota_fiscal' in self.request.POST else '',

#                 'observacao': self.request.POST['observacao'] if 'observacao' in self.request.POST else None,

#             }

#             class Form(forms.ModelForm):

#                 class Meta:

#                     exclude = []

#                     model = models.Medicao

#             frm = Form(values)

#             if frm.is_valid():

#                 try:

#                     frm.save()

#                     obj['msg'] = u'Salvo com sucesso.'

#                     obj['success'] = True

#                 except Exception as e:

#                     self.log.exception(e)

#                     obj['msg'] = unicode(e)

#             else:

#                 obj['errors'] = []

#                 for field in frm.errors:

#                     obj['errors'].append({

#                         'field': field,

#                         'msg': frm.errors[field].as_text()

#                     })

#                 obj['msg'] = u'Erro de validação.'

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def update(self, args=[]):

#         obj = {

#             'success': False,

#             'msg': u'Não foi feito nada ainda.'

#         }

#         self.log.info(self.request.POST)

#         try:

#             ne = models.NotaEmpenho.objects.get(pk=int(self.request.POST['nota_empenho']))

#             contrato = models.Contrato.objects.get(pk=self.request.POST['contrato'])

#             medicao = models.Medicao.objects.get(pk=self.request.POST['pk'])

#             if int(medicao.status) == 2 and medicao.data_pagamento is not None:

#                 obj.update(msg=u'Não é possivel alterar este pagamento!')

#                 # transaction.rollback()

#             else:

#                 if float(self.request.POST['valor']) > contrato._valor_contrato:

#                     raise Exception(u'O valor desta medição estrapola o valor do contrato')

#                 else:

#                     med = models.Medicao.objects.filter(pk=self.request.POST['pk']).update(

#                         nota_empenho=ne,

#                         inicio_periodo_referencia=DateUtils.str_to_date(self.request.POST['inicio_periodo']),

#                         fim_periodo_referencia=DateUtils.str_to_date(self.request.POST['fim_periodo']),

#                         valor=self.request.POST['valor'],

#                         nota_fiscal=self.request.POST['nota_fiscal'],

#                         user=self.request.user,

#                         observacao=self.request.POST['observacao']

#                     )

#                 obj.update(success=True)

#                 obj.update(msg=u'Pagamento alterado com Sucesso!')

#                 # transaction.commit()

#         except Exception as e:

#             obj.update(success=False)

#             obj.update(msg=unicode(e))

#             # transaction.rollback()

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def remove(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'success': False

#             # 'message': 'Nada feito ainda'

#         }

#         self.log.info(self.request.POST)

#         try:

#             medicao = models.Medicao.objects.filter(pk__in=self.request.POST.getlist('pk'))

#             for med in medicao:

#                 med.delete()

#         except Exception as e:

#             self.log.info(e)

#             obj.update(message=unicode(e))

#         else:

#             obj.update({

#                 'success': True,

#                 'message': 'Removido com sucesso!'

#             })

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def apply_filter(self, query):

#         qs = []

#         q = None

#         for qN in qs:

#             q = qN if q is None else Q(q | qN)

#         query = query.filter(q) if q else query

#         if 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'pagos':

#             query = query.filter(Q(contrato__id=self.request.POST['contrato']) & Q(status=2))

#         elif 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'nao_pagos':

#             query = query.filter(Q(contrato__id=self.request.POST['contrato']) & Q(status=1))

#         elif 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'todos':

#             query = query.filter(Q(contrato__id=self.request.POST['contrato']))

#         else:

#             query = query.filter(Q(contrato__id=self.request.POST['contrato']))

#         return query

#     def list(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             # self.log.info(self.request.POST)

#             R = self.request.REQUEST

#             start = int(R.get('start', 0))

#             end = int(R.get('limit', 15)) + start

#             medicao = models.Medicao.objects.all()

#             medicao = self.apply_filter(medicao)

#             for med in medicao[start:end]:

#                 states = med.get_state()

#                 obj['result'].append({

#                     'pk': med.pk,

#                     'valor': float(med.valor),

#                     'observacao': med.observacao,

#                     'periodo': u'%s - %s ' % (
#                       DateUtils.date_to_str(med.inicio_periodo_referencia), DateUtils.date_to_str(med.fim_periodo_referencia)),

#                     'inicio_periodo': DateUtils.date_to_str(med.inicio_periodo_referencia),

#                     'fim_periodo': DateUtils.date_to_str(med.fim_periodo_referencia),

#                     'user': unicode(med.user.servidor.pessoa_fisica),

#                     'nota_empenho_': med.nota_empenho.numero_ne,

#                     'fornecedor': u'%s' % med.nota_empenho.fornecedor,

#                     'classificacao_ne': med.nota_empenho.get_classificacao_display(),

#                     'nota_empenho_pk': med.nota_empenho_id,

#                     'nota_fiscal': unicode(med.nota_fiscal),

#                     'status': [

#                         {

#                             'iconCls': st['iconCls'],

#                             'alt': st['alt'],

#                             'title': st['alt']

#                         } for st in states

#                     ],

#                 })

#         except Exception as e:

#             self.log.info(e)

#         else:

#             obj.update(count=medicao.count())

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def apply_filter_pagamentos(self, query):

#         qs = []

#         q = None

#         for qN in qs:

#             q = qN if q is None else Q(q | qN)

#         query = query.filter(q) if q else query

#         if 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'pagos':

#             query = query.filter(Q(contrato__id=self.request.POST['pk_contrato']) & Q(status=2))

#         elif 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'nao_pagos':

#             query = query.filter(Q(contrato__id=self.request.POST['pk_contrato']) & Q(status=1))

#         elif 'tipo' in self.request.POST and self.request.POST.get('tipo') == 'todos':

#             query = query.filter(Q(contrato__id=self.request.POST['pk_contrato']))

#         else:

#             query = query.filter(Q(contrato__id=self.request.POST['pk_contrato']))

#         return query

#     def get_pagamentos(self, args=[]):

#         obj = {

#             'result': []

#         }

#         # self.log.info(self.request.POST)

#         try:

#             R = self.request.REQUEST

#             start = int(R.get('start', 0))

#             end = int(R.get('limit', 50)) + start

#             medicao = models.Medicao.objects.all()

#             medicao = self.apply_filter_pagamentos(medicao)

#             for med in medicao[start:end]:

#                 states = med.get_state()

#                 obj['result'].append({

#                     'pk': med.pk,

#                     'contrato': med.contrato.numero,

#                     'data_solicitacao': med.horario.strftime('%d/%m/%Y %H:%M'),

#                     'valor': u'%0.2f' % med.valor,

#                     'observacao': med.observacao,

#                     'inicio_periodo': DateUtils.date_to_str(med.inicio_periodo_referencia),

#                     'fim_periodo': DateUtils.date_to_str(med.fim_periodo_referencia),

#                     'user': unicode(med.user.servidor.pessoa_fisica),

#                     'nota_empenho_': med.nota_empenho.numero_ne,

#                     'nota_empenho_pk': med.nota_empenho_id,

#                     'valor_ne': med.nota_empenho.get_valor_ne(),

#                     'saldo_ne': med.nota_empenho.get_saldo(),

#                     'ordem_bancaria': med.ordem_bancaria if med.ordem_bancaria else 'Aguardando...',

#                     'periodo': u'%s - %s ' % (
#                           DateUtils.date_to_str(med.inicio_periodo_referencia), DateUtils.date_to_str(med.fim_periodo_referencia)),

#                     'nota_fiscal': unicode(med.nota_fiscal),

#                     'status': [

#                         {

#                             'iconCls': st['iconCls'],

#                             'alt': st['alt'],

#                             'title': st['alt']

#                         } for st in states

#                     ],

#                 })

#         except Exception as e:

#             self.log.info(e)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def lanca_ordem_bancaria(self, args=[]):

#         obj = {

#             'success': False,

#             'message': u'Não foi feito nada ainda.'

#         }

#         self.log.info(self.request.POST)

#         try:

#             medicao = models.Medicao.objects.get(pk=self.request.POST['pk'])

#             medicao.ordem_bancaria = self.request.POST['ordem_bancaria'].upper()

#             # medicao.status= 2

#             medicao.save()

#         except Exception as e:

#             self.log.info(e)

#             # transaction.rollback()

#             obj.update(message=u'Erro ao lançar Pagamento!')

#             # obj.update(message = unicode(e))

#         else:

#             # transaction.commit()

#             obj.update(message=u'Pagamento lançado com Sucesso!')

#             obj.update(success=True)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def realiza_estorno(self, args=[]):

#         obj = {

#             'success': False,

#             'message': u'Não foi feito nada ainda.'

#         }

#         self.log.info(self.request.POST)

#         try:

#             medicao = models.Medicao.objects.filter(pk=self.request.POST['pk']).update(ordem_bancaria=None, status=1, data_pagamento=None)

#         except Exception as e:

#             self.log.info(e)

#             # transaction.rollback()

#             obj.update(message=u'Erro ao lançar Estorno!')

#             # obj.update(message = unicode(e))

#         else:

#             # transaction.commit()

#             obj.update(message=u'Estorno lançado com Sucesso!')

#             obj.update(success=True)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCValorContrato(extjs.ExtWidget):

#     class Form(forms.ModelForm):

#         class Meta:

#             exclude = []

#             model = models.ValorContrato

#     # def apply_filter(self, query):

#     #     qs = []

#     #     if 'keyword' in self.request.POST:

#     #         pass

#     #         # qs.append(Q(contrato__pk=int(self.request.POST['pk']))

#     #     else:

#     #         qs.append(Q(contrato__pk = int(self.request.POST['pk_contrato'])))

#     #     q = None

#     #     for qN in qs: q = qN if q is None else Q(q | qN)

#     #     return query.filter(q)

#     def list(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             R = self.request.REQUEST

#             start = int(R.get('start', 0))

#             end = int(R.get('limit', 15)) + start

#             valores_contratos = models.ValorContrato.objects.filter(contrato__pk=int(self.request.POST['pk_contrato']))

#             # valores_contratos = self.apply_filter(valores_contratos)

#             for valor_contrato in valores_contratos[start:end]:

#                 obj['result'].append({

#                     'pk': valor_contrato.pk,

#                     'valor': round(valor_contrato.valor, 2),

#                     'tipo_valor_contrato': valor_contrato.tipo_valor_contrato,

#                     'tipo_valor_contrato_display': valor_contrato.get_tipo_valor_contrato_display(),

#                     # 'ordem': u'%sª' % valor_contrato.ordem if valor_contrato.ordem != 0 else 'Principal',

#                     'ordem': valor_contrato.get_ordem_display(),

#                     'data_ref_inicio': DateUtils.date_to_str(valor_contrato.data_ref_inicio),

#                     'data_ref_fim': DateUtils.date_to_str(valor_contrato.data_ref_fim),

#                     'data_publicacao': DateUtils.date_to_str(valor_contrato.data_publicacao) if valor_contrato.data_publicacao else '',

#                 })

#         except Exception as e:

#             self.log.info(e)

#         else:

#             obj.update(count=valores_contratos.count())

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def get_list(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0

#         }

#         try:

#             self.log.info(self.request.POST['pk'])

#             valor_contrato = models.ValorContrato.objects.get(pk=self.request.POST['pk'])

#         except Exception as e:

#             obj.update({

#                 'message': u'Não consegui encontrar encontrar a referência solicitada.',

#                 'success': False

#             })

#             self.log.info(e)

#         else:

#             obj.update({

#                 'collection': {

#                     'pk': valor_contrato.pk,

#                     'valor_contrato': round(valor_contrato.valor, 2),

#                     'tipo_valor_contrato': valor_contrato.tipo_valor_contrato,

#                     'ordem': valor_contrato.ordem,

#                     'periodo_inicial_valor': DateUtils.date_to_str(valor_contrato.data_ref_inicio),

#                     'periodo_final_valor': DateUtils.date_to_str(valor_contrato.data_ref_fim),

#                     'data_publicacao': DateUtils.date_to_str(valor_contrato.data_publicacao) if valor_contrato.data_publicacao else '',

#                 },

#                 'success': True

#             })

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def create(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda'

#         }

#         self.log.info(self.request.POST)

#         self.log.info(self.request.POST['valor_contrato'].replace(',', '.'))

#         try:

#             contrato = models.Contrato.objects.get(pk=self.request.POST['contrato_id'])

#             valor_contrato = models.ValorContrato(

#                 contrato=contrato,

#                 data_ref_inicio=DateUtils.str_to_date(self.request.POST['periodo_inicial_valor']),

#                 data_ref_fim=DateUtils.str_to_date(self.request.POST['periodo_final_valor']),

#                 valor=Decimal(self.request.POST['valor_contrato'].replace(',', '.')),

#                 tipo_valor_contrato=self.request.POST['tipo_valor_contrato'],

#                 ordem=int(self.request.POST['ordem']),

#                 data_publicacao=DateUtils.str_to_date(
#                       self.request.POST['data_publicacao']) if self.request.POST['data_publicacao'] != '' else None

#             )

#             valor_contrato.save()

#         except Exception as e:

#             # transaction.rollback()

#             self.log.info(e)

#             obj.update(success=False)

#             obj.update(message=unicode(e))

#         else:

#             # transaction.commit()

#             obj.update(success=True)

#             obj.update(message='Valor salvo com sucesso!')

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     # @transaction.commit_manually

#     def update(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'message': u'Nada aconteceu ainda',

#             'success': False

#         }

#         self.log.info(self.request.POST)

#         try:

#             valor_contrato = models.ValorContrato.objects.get(pk=self.request.POST['pk'])

#             valor_contrato.valor = Decimal(self.request.POST['valor_contrato'].replace(',', '.'))

#             valor_contrato.tipo_valor_contrato = self.request.POST['tipo_valor_contrato']

#             valor_contrato.ordem = int(self.request.POST['ordem'])

#             valor_contrato.data_ref_inicio = DateUtils.str_to_date(self.request.POST['periodo_inicial_valor'])

#             valor_contrato.data_ref_fim = DateUtils.str_to_date(self.request.POST['periodo_final_valor'])

#             valor_contrato.data_publicacao = DateUtils.str_to_date(
#               self.request.POST['data_publicacao']) if self.request.POST['data_publicacao'] != '' else None

#             valor_contrato.save()

#         except Exception as e:

#             self.log.info(e)

#             # transaction.rollback()

#             obj.update(success=False)

#             obj.update(message=unicode(e))

#         else:

#             # transaction.commit()

#             obj.update(success=True)

#             obj.update(message='Referência alterada com Sucesso!')

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))

#     def remove(self, args=[]):

#         obj = {

#             'result': [],

#             'count': 0,

#             'success': False

#             # 'message': 'Nada feito ainda'

#         }

#         self.log.info(self.request.POST)

#         try:

#             valores = models.ValorContrato.objects.filter(pk__in=self.request.POST.getlist('pk'))

#             for val in valores:

#                 val.delete()

#         except Exception as e:

#             self.log.info(e)

#             obj.update(message=unicode(e))

#         else:

#             obj.update({

#                 'success': True,

#                 'message': 'Removido com sucesso!'

#             })

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCContratoLista(extjs.ExtCrud):

#     class Form(forms.ModelForm):

#         class Meta:

#             exclude = []

#             model = models.Contrato

#     titles = {

#         'PANEL': u'Contratos',

#         'LIST': u'Lista de Contratos',

#         'NEW': u'Adicionar um novo Contrato',

#         'EDIT': u'Editando um Contrato',

#         'DELETE': u'Deletando um Contrato'

#     }

#     def get_columns_grid(self, args=[]):

#         obj = [

#             {'header': 'Chave', 'sortable': True, 'dataIndex': 'id', 'key': 'id'},

#             {'header': 'Numero', 'sortable': True, 'dataIndex': 'numero', 'key': 'numero', 'width': 250},

#             {'header': 'Objeto Contratado', 'sortable': True, 'dataIndex': 'objeto_contrato', 'key': 'objeto_contrato', 'width': 250},

#             {'header': 'Numero do Processo', 'sortable': True, 'dataIndex': 'numero_processo', 'key': 'numero_processo', 'width': 250},

#             {'header': 'Fiscal', 'sortable': True, 'dataIndex': 'gestor', 'key': 'gestor', 'width': 250}

#         ]

#         obj = self._apply_to_search_for_columns_grid(obj)

#         self.response['content-type'] = 'text/javascript'

#         self.response.write(json.encode(obj))


# class SPCPrintReport(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         num_processo = django_forms.CharField()

#         data_inicio = django_forms.CharField()

#         data_final = django_forms.CharField()

#         contratado = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     # log.info('---> %s - %s - %s - %s  <---' % (servidor, cargo, etapa, questionario_avaliacao, questionario_manifestacao))

#     report_src = '/to/mpe/planejamento/contrato/extrato/contrato_extrato_pagamento_main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/planejamento/contrato/extrato/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioExtratoPagamentos.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportSaldoContrato(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         contrato = django_forms.CharField()

#         data_inicio = django_forms.DateField()

#         data_final = django_forms.DateField()

#         contratado = django_forms.CharField()

#         tipo_licitacao = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     # log.info('---> %s - %s - %s - %s  <---' % (servidor, cargo, etapa, questionario_avaliacao, questionario_manifestacao))

#     report_src = '/to/mpe/planejamento/contrato/objeto_saldo/objeto_saldo_main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': '/to/mpe/planejamento/contrato/objeto_saldo/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioSaldoContrato.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportPagContratoOrdemBancaria(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         num_processo = django_forms.CharField()

#         contratado = django_forms.CharField()

#         data_inicio = django_forms.DateField()

#         data_final = django_forms.DateField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     # log.info('---> %s - %s - %s - %s  <---' % (servidor, cargo, etapa, questionario_avaliacao, questionario_manifestacao))

#     report_src = '/to/mpe/planejamento/contrato/listagem_detalhada/contrato_listagem_main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/planejamento/contrato/listagem_detalhada/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioPagamentosOrdemBancaria.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportPayment(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         num_processo = django_forms.CharField()

#         data_inicio = django_forms.CharField()

#         data_final = django_forms.CharField()

#         contratado = django_forms.CharField()

#         tipo = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     # log.info('---> %s - %s - %s - %s  <---' % (servidor, cargo, etapa, questionario_avaliacao, questionario_manifestacao))

#     report_src = '/to/mpe/planejamento/contrato/listagem/contrato_listagem_main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/planejamento/contrato/listagem/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioListagemPagamentos.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportDespacho(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         contrato = django_forms.CharField()

#         medicao = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     report_src = '/to/mpe/planejamento/contrato/solicitacao_pagamento/main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/planejamento/contrato/solicitacao_pagamento/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioDespachodePagamentos.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportPaymentSummary(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         num_processo = django_forms.CharField()

#         contratado = django_forms.CharField()

#         data_inicio = django_forms.CharField()

#         data_final = django_forms.CharField()

#         tipo = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     report_src = '/to/mpe/planejamento/contrato/pagamento_resumido/pagamento_resumido_main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/planejamento/contrato/pagamento_resumido/'

#         }

#     ]

#     def get_generated_filename(self):

#         report_servidor = u'RelatórioResumidodePagamentos.pdf'

#         report_servidor = report_servidor.encode('utf-8')

#         return report_servidor


# class SPCPrintReportSupervisorContract(extjs.ExtReportBuild):

#     class Form(django_forms.Form):

#         gestor = django_forms.CharField()

#         ativo = django_forms.CharField()

#     from contrib.utils import getLogger

#     log = getLogger(__name__)

#     report_src = '/to/mpe/adm/contrato/lista_por_fiscal/main'

#     params = [

#         {

#             'nome': 'SUBREPORT_DIR',

#             'tipo': 'String',

#             'valor': 'to/mpe/adm/contrato/lista_por_fiscal/'

#         }

#     ]

#     def get_generated_filename(self):

#         report = u'RelatorioFiscalContrato.pdf'

#         report = report.encode('utf-8')

#         return report


class SPCContratoCSV(extjs.ExtFileBuild):

    titles = {
        "TITLE": "Exportar Planilha",
        "SUB_TITLE": "Gerar planilha de Contratos",
    }

    minetype = "text/csv"

    def get_generate_filename(self):

        return "contratos.csv"

    def len_buffer(self, buffer):

        return len(buffer.encode("utf-8"))

    def builder_buffer(self):

        try:

            text = "TIPO DE CONTRATO; NUMERO CONTRATO; PROCESSO; OBJETO DO CONTRATO; CONTRATADO; DATA INÍCIO; DATA FINAL; VALOR\n"

            # log.info(self.request.GET["status"])

            status = (
                int(self.request.GET["status"])
                if self.request.GET["status"] != ""
                else 0
            )

            if status == 1:

                contratos = models.Contrato.objects.filter().exclude(status=4)

            elif status == 2:

                contratos = models.Contrato.objects.filter(status=4)

            else:

                contratos = models.Contrato.objects.filter()

            contratos = contratos.order_by("tipo_contrato")

            for row in contratos:

                text += "{tipo_contrato};{numero_contrato};{numero_processo};{objeto_contrato};{contratado};{data_inicio};{data_vencimento_flag};{valor}\n".format(
                    tipo_contrato=row.get_tipo_contrato_display(),
                    numero_contrato=row.numero,
                    numero_processo=row.numero_processo,
                    objeto_contrato=row.objeto_contrato,
                    contratado=str(row.pessoa.first() if row.pessoa.exists() else ""),
                    data_inicio=DateUtils.date_to_str(row.data_inicio),
                    data_vencimento_flag=(
                        DateUtils.date_to_str(row.data_vencimento_flag)
                        if row.data_vencimento_flag
                        else ""
                    ),
                    valor=row._valor_contrato,
                )

        except Exception as e:

            raise e

            log.error(e)

        else:

            return text

    class Form(forms.Form):

        status = forms.ChoiceField(
            label="STATUS DO CONTRATO",
            choices=(
                (1, "ATIVO"),
                (2, "INATIVO"),
                (3, "TODOS"),
            ),
        )

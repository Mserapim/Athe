# #Inserir choices do app dayoff ---------------

# from rh.afastamento.models import Choice

# dayoff_choices = []

# dayoff_choices.append({'app_label': 'dayoff', 'name': 'PERIODS_YEAR_CHOICES', 'value': 1, 'label': 'Único'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'PERIODS_YEAR_CHOICES', 'value': 2, 'label': 'Semestre'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'PERIODS_YEAR_CHOICES', 'value': 3, 'label': 'Trimeste'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'PERIODS_YEAR_CHOICES', 'value': 4, 'label': 'Quadrimeste'})

# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 1, 'label': 'Férias'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 2, 'label': 'Recesso'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 3, 'label': 'Folga de Aniversário'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 4, 'label': 'Folga Eleitoral'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 5, 'label': 'Plantão'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TYPE_OF_USUFRUCT', 'value': 6, 'label': 'Compensação'})

# dayoff_choices.append({'app_label': 'dayoff', 'name': 'ESTADO_PAS', 'value': 1, 'label': 'Aguardando Liberação p/ Marcação'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'ESTADO_PAS', 'value': 2, 'label': 'Em Andamento'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'ESTADO_PAS', 'value': 3, 'label': 'Fruída'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'ESTADO_PAS', 'value': 4, 'label': 'Indenizado Total ou Parcialmente'})

# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 1, 'label': 'Marcação'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 2, 'label': 'Alteração'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 3, 'label': 'Suspensão'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 4, 'label': 'Interrupção'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 5, 'label': 'Indenização'})
# dayoff_choices.append({'app_label': 'dayoff', 'name': 'TIPO_ANOTACAO_FERIAS', 'value': 6, 'label': 'Autorização'})


# for dc in dayoff_choices:
#     Choice.objects.get_or_create(
#         app_label = dc.get('app_label'),
#         name = dc.get('name'),
#         value = dc.get('value'),
#         label = dc.get('label')
#     )


# ### Configuração do menu ---------------- ------------------------------------------------------------------------------

# # Primeiro coloque no INSTALLED_APPS do settings.py o namespace do app: 'rh.dayoff'

# from engine.models import Application

# a = Application.objects.get(pk=15) #GESTÃO DE PESSOAS
# result_dayoff = a.application_set.get_or_create(icon='athenas-0515.png', title='DayOff')
# dayoff = result_dayoff[0]
# dayoff.controller_set.get_or_create(icon='athenas-0696.png', title=u'Configuração', controller='DAYOFFConfiguration', module='rh.dayoff')

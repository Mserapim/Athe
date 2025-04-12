# -*- coding: utf-8 -*-
from rh.api.workplace import RHWorkplaceRestful
from contrib.utils import getLogger
from contrib.controller import ContentType, DefaultController
from judicial.models import ExecutionOrgan
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_date
from contrib.nil import nil_datetime


log = getLogger(__name__)


class ExecutionOrgansReport(DefaultController):

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("judicial.reports.ExecutionOrgansReport")')


class EJudExecutionOrgan(RHWorkplaceRestful):

    _model = ExecutionOrgan

    # force_upper = False

    full_text_index = (
        "nome__icontains",
        "responsavel__matricula__icontains",
        "responsavel__pessoa_fisica__nome__icontains",
        "localidade__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.county.ExecutionOrganManage')")

    # def get_params(self, *args, **kargs):
    #     params = RHWorkplaceRestful.get_params(self, *args, **kargs)
    #     if 'executivo' in params:
    #         params.update(executivo=params.get('executivo', 'off') == 'on')

    #     if 'data_alteracao' in params:
    #         if params.get('data_alteracao') != '':
    #             params.update(data_alteracao=DateUtils.str_to_date(params.get('data_alteracao')))
    #         else:
    #             params.update(data_alteracao=None)

    #     if 'comarca' in params:
    #         if params.get('comarca') != '':
    #             field = getattr(self.Model, 'comarca')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     comarca=query.get(pk=params.get('comarca'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(comarca=None)

    #     if 'pai' in params:
    #         if params.get('pai') != '':
    #             field = getattr(self.Model, 'pai')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     pai=query.get(pk=params.get('pai'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(pai=None)

    #     if 'responsavel' in params:
    #         if params.get('responsavel') != '':
    #             field = getattr(self.Model, 'responsavel')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     responsavel=query.get(pk=params.get('responsavel'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(responsavel=None)

    #     if 'modified_by' in params:
    #         if params.get('modified_by') != '':
    #             field = getattr(self.Model, 'modified_by')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     modified_by=query.get(pk=params.get('modified_by'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(modified_by=None)

    #     if 'localidade' in params:
    #         if params.get('localidade') != '':
    #             field = getattr(self.Model, 'localidade')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     localidade=query.get(pk=params.get('localidade'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(localidade=None)

    #     if 'instancia' in params:
    #         if params.get('instancia') != '':
    #             field = getattr(self.Model, 'instancia')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     instancia=query.get(pk=params.get('instancia'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(instancia=None)

    #     if 'entrancia' in params:
    #         if params.get('entrancia') != '':
    #             field = getattr(self.Model, 'entrancia')

    #             # mater compatibilidade com django-1.4.x
    #             get_queryset = field.get_queryset
    #             query = get_queryset()

    #             try:
    #                 params.update(
    #                     entrancia=query.get(pk=params.get('entrancia'))
    #                 )
    #             except Exception as e:
    #                 log.exception(e)
    #                 raise e
    #         else:
    #             params.update(entrancia=None)

    #     if 'ativo' in params:
    #         params.update(ativo=params.get('ativo', 'off').lower() == 'on')

    #     if 'organograma' in params:
    #         params.update(organograma=params.get('organograma', 'off').lower() == 'on')

    #     if 'grupo_lotacao' in params:
    #         params.update(grupo_lotacao=params.get('grupo_lotacao', 'off').lower() == 'on')

    #     if 'acesso_protocolo_geral' in params:
    #         params.update(acesso_protocolo_geral=params.get('acesso_protocolo_geral', 'off').lower() == 'on')

    #     if 'designacao' in params:
    #         params.update(designacao=params.get('designacao', 'off').lower() == 'on')

    #     if 'habilita_protocolo' in params:
    #         params.update(habilita_protocolo=params.get('habilita_protocolo', 'off').lower() == 'on')

    #     if 'ouvidoria' in params:
    #         params.update(ouvidoria=params.get('ouvidoria', 'off').lower() == 'on')

    #     if 'administrativo' in params:
    #         params.update(administrativo=params.get('administrativo', 'off').lower() == 'on')

    #     if 'publica_doc' in params:
    #         params.update(publica_doc=params.get('publica_doc', 'off').lower() == 'on')

    #     return params

    def model_to_dict(self, instance):
        rst = RHWorkplaceRestful.model_to_dict(self, instance)

        rst.update(
            executivo=instance.executivo,
            data_alteracao=nil_date(instance.data_alteracao, None),
            ativo=instance.ativo,
            organograma=instance.organograma,
            andar=instance.andar,
            esfera_governamental=instance.esfera_governamental,
            esfera_governamental_display=nil_display(
                instance, "esfera_governamental", None
            ),
            comarca=nil_pk(instance.comarca, None),
            comarca_unicode=nil_unicode(instance.comarca, None),
            pai=nil_pk(instance.pai, None),
            pai_unicode=nil_unicode(instance.pai, None),
            responsavel=nil_pk(instance.responsavel, None),
            responsavel_unicode=nil_unicode(instance.responsavel, None),
            acesso_protocolo_geral=instance.acesso_protocolo_geral,
            designacao=instance.designacao,
            order_nome=instance.order_nome,
            habilita_protocolo=instance.habilita_protocolo,
            codigo=instance.codigo,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            nome=instance.nome,
            localidade=nil_pk(instance.localidade, None),
            localidade_unicode=nil_unicode(instance.localidade, None),
            created_at=nil_datetime(instance.created_at, None),
            # title=instance.title,
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            ouvidoria=instance.ouvidoria,
            sala=instance.sala,
            administrativo=instance.administrativo,
            instancia=nil_pk(instance.instancia, None),
            instancia_unicode=nil_unicode(instance.instancia, None),
            publica_doc=instance.publica_doc,
            entrancia=nil_pk(instance.entrancia, None),
            entrancia_unicode=nil_unicode(instance.entrancia, None),
            abreviacao=instance.abreviacao,
            codigo_igeprev=int(instance.codigo_igeprev or 0),
            poder=instance.poder,
            poder_display=nil_display(instance, "poder", None),
            descricao=instance.descricao,
            sigla=instance.sigla,
            owner_unicode=nil_unicode(instance.owner_unicode(), None),
            employee_exercise_unicode=nil_unicode(
                instance.employee_exercise_unicode(), None
            ),
            attribution=instance.attribution,
        )

        return rst

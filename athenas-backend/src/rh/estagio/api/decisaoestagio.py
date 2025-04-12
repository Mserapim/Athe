# -*- coding: utf-8 -*-

from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_pk
from contrib.utils import getLogger
from rh.estagio.models import DecisaoChefeOrgao, EstagioComissaoServidor

# from rh.models import Servidor


log = getLogger(__name__)


class GepDecisaoEstagio(Restful):

    _model = EstagioComissaoServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.decisaoestagio.Manage")')

    def permission_list(self, args=[]):
        servidor = self.request.user.servidor
        return servidor.user.has_perm("estagio.can_valid_stage_prob")

    def decisao_gestor_orgao(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            with transaction.atomic():
                ecs = EstagioComissaoServidor.objects.get(
                    pk=self.request.POST.get("pk")
                )
                if (
                    ecs.is_liberado_para_decisao()
                    and not ecs.is_julgado()
                    and self.permission_list()
                ):
                    cdo = DecisaoChefeOrgao(
                        estagio_comissao_servidor=ecs,
                        decisao=self.request.POST.get("decisao"),
                        fundamentacao=self.request.POST.get("fundamentacao"),
                    )
                    cdo.save()
                    rst.update(success=True, message="Dados salvos com sucesso!")
                else:
                    rst.update(
                        success=False,
                        message="Ainda há recomendações pendentes por integrantes da comissão de estágio!",
                    )

        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("estagio.estagio_decisao"):
            query = query.filter(
                decisao_chefe_orgao__isnull=True,
                decisao_chefe_orgao__decisao__isnull=True,
            )
        else:
            query = query.exclude(id__gt=0)

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            status=instance.get_status_gestor_orgao(),
            estagio_prob_servidor=nil_pk(instance.estagio_prob_servidor, None),
            estagio_prob_servidor_unicode=str(
                instance.estagio_prob_servidor.posse_servidor
            )
            or None,
            servidor_id=instance.estagio_prob_servidor.posse_servidor.servidor.pk,
            questionario=str(instance.estagio_prob_servidor.configuracao.questionario)
            or None,
            questionario_id=nil_pk(
                instance.estagio_prob_servidor.configuracao.questionario, None
            ),
            questionario_manifestacao_id=nil_pk(
                instance.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor,
                None,
            ),
            questionario_manifestacao=str(
                instance.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor
            )
            or None,
            etapa_atual=instance.estagio_prob_servidor.current_stage,
            cargo_id=nil_pk(
                instance.estagio_prob_servidor.posse_servidor.quadro.cargo, None
            ),
            posse_servidor=nil_pk(instance.estagio_prob_servidor.posse_servidor, None),
            posse_servidor_unicode=str(instance.estagio_prob_servidor.posse_servidor)
            or None,
            data_exercicio=nil_date(
                instance.estagio_prob_servidor._inicio_estagio, None
            ),
            ultima_avaliacao=nil_date(
                instance.estagio_prob_servidor.ultima_avaliacao, None
            ),
            media=float(instance.estagio_prob_servidor.media or 0),
        )

        return rst

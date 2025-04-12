# -*- coding: utf-8 -*-


from contrib.utils import getLogger
from standard.models import RunCodeManager
from standard.loader.models import FileLoader

# from rh.gfp import models as gfp_models
# from rh import models as rh_models
from django.db.models import Q, F
from esocial.models import RegistrationQualification
from contrib.middleware import get_current_user
from engine.mq.models import Task

import os
import datetime

log = getLogger("rh.gfp.loaders")


@RunCodeManager.register("esocial-qualif-loader")
class QualifLoader(FileLoader):
    typeof = "LOADER"
    titulo = "Carregador para arquivos de qualificação do eSocial"
    descricao = "Este carregador carrega arquivos genéricos de lançamentos nos contracheques de uma determinada folha."

    CONFIG = {
        # 'CPF': 1,
        # 'NIS': 2,
        # 'NOME': 3,
        # 'DN': 4,
        # 'COD_NIS_INV': 5,
        # 'COD_CPF_INV': 6,
        # 'COD_NOME_INV': 7,
        # 'COD_DN_INV': 8,
        # 'COD_CNIS_NIS': 9,
        # 'COD_CNIS_DN': 10,
        # 'COD_CNIS_OBITO': 11,
        # 'COD_CNIS_CPF': 12,
        # 'COD_CNIS_CPF_NAO_INF': 13,
        # 'COD_CPF_NAO_CONSTA': 14,
        # 'COD_CPF_NULO': 15,
        # 'COD_CPF_CANCELADO': 16,
        # 'COD_CPF_SUSPENSO': 17,
        # 'COD_CPF_DN': 18,
        # 'COD_CPF_NOME': 19,
        # 'COD_ORIENTACAO_CPF': 20,
        # 'COD_ORIENTACAO_NIS': 21,
    }
    SEPARATOR = ";"
    HEADER_LINES = 1
    CODE_TYPE = "utf-8"
    TRANSACTION_FULL = True
    RETURN_ONLY_ERRORS = False
    CONFIG_FROM_HEADER_LINE = 1

    def __init__(self, path, original_basename="", **kargs):
        basename = (
            os.path.basename(path) if not original_basename else original_basename
        )
        dict_ = basename.split(".")
        if len(dict_) != 9:
            raise self.ValidateError(
                "Nome de arquivo inválido! Utilize o nome conforme liberado pelo eSocial!"
            )

        self.status = dict_[-1]
        self.typeof = dict_[-1][0] if len(dict_[-1]) else ""
        if self.status not in ["PROCESSADO", "REJEITADO"]:
            raise self.ValidateError(
                "Nome de arquivo inválido! Utilize o nome conforme liberado pelo eSocial!"
            )

        value = dict_[4]
        try:
            self.processing_date = datetime.datetime.strptime(value, "%Y%m%d%H%M%S")
        except Exception:
            raise self.ValidateError(
                "Nome de arquivo inválido! Data de processamento incorreta!"
            )

        log.debug(
            "LOADER: %s:%s:%s:%s:%s"
            % (self.__class__.__name__, path, self.typeof, original_basename, kargs)
        )
        super(QualifLoader, self).__init__(path, **kargs)
        # self.remove_only_equal_info = kargs['remove_only_equal_info'] if 'remove_only_equal_info' in kargs else True
        # self.payroll = payroll
        # self.create_paycheck = create
        # if not hasattr(self, 'evento'):
        #     self.evento = None

    def validate_line(self, linec):
        if len(linec) == 1:
            return False
        return True

    def pre_validate(self):
        # if not hasattr(self, 'payroll'):
        #     log.exception('O parâmetro folha deve ser passado para o construtor da classe. Ex.: folha= objeto da classe gfp.models.Folha')
        #     raise self.ValidateError('Erro de validação. Informe o administrador do sistema')
        # if not isinstance(self.payroll, gfp_models.Folha):
        #     raise self.ValidateError('Folha (%s) inválida!' % self.payroll)

        # if hasattr(self, 'evento') and not isinstance(self.evento, gfp_models.Evento):
        #     raise self.ValidateError('Evento (%s) inválido!' % self.evento)
        pass

    # def line_to_dict(self, linec):
    #     try:
    #         dict_ = super(QualifLoader, self).line_to_dict(linec)
    #     except gfp_models.Evento.DoesNotExist as e:
    #         raise self.ValidateError('Evento inexistente!')
    #     except Exception as e:
    #         raise e
    #     else:
    #         if 'evento' not in dict_:
    #             if not self.evento:
    #                 raise self.ValidateError('Número do evento não indicado!')
    #             else:
    #                 dict_['evento'] = self.evento
    #         else:
    #             if self.evento and dict_['evento'] != self.evento:
    #                 log.debug('Evento do registro (%s) diferente do evento informado (%s)!' % (dict_['evento'], self.evento))
    #                 return {}
    #     return dict_

    # def get_line(self, dict_):
    #     line = super(QualifLoader, self).get_line(dict_)
    #     line = '%s;%s' % (line, dict_.get('msg', ''))
    #     return line

    def _convert_dn(self, value):
        return datetime.datetime.strptime(value, "%d%m%Y").date() if value else None
        # return datetime.date(int(value[4:9]), int(value[2:4]), int(value[0:2]))

    # def _convert_cpf(self, value):
    #     return int(value)

    # def _convert_nis(self, value):
    #     return int(value)

    # def _convert_nome(self, value):
    #     return int(value)

    # def _convert_dn(self, value):
    #     return int(value)

    def _convert_cod_nis_inv(self, value):
        return int(value)

    def _convert_cod_cpf_inv(self, value):
        return int(value)

    def _convert_cod_nome_inv(self, value):
        return int(value)

    def _convert_cod_dn_inv(self, value):
        return int(value)

    def _convert_cod_cnis_nis(self, value):
        return int(value)

    def _convert_cod_cnis_dn(self, value):
        return int(value)

    def _convert_cod_cnis_obito(self, value):
        return int(value)

    def _convert_cod_cnis_cpf(self, value):
        return int(value)

    def _convert_cod_cnis_cpf_nao_inf(self, value):
        return int(value)

    def _convert_cod_cpf_nao_consta(self, value):
        return int(value)

    def _convert_cod_cpf_nulo(self, value):
        return int(value)

    def _convert_cod_cpf_cancelado(self, value):
        return int(value)

    def _convert_cod_cpf_suspenso(self, value):
        return int(value)

    def _convert_cod_cpf_dn(self, value):
        return int(value)

    def _convert_separador(self, value):
        return int(value)

    def _convert_reg_desformatado(self, value):
        return int(value)

    # def _convert_cod_cpf_nome(self, value):
    #     return int(value)

    def _convert_cod_orientacao_cpf(self, value):
        return int(value)

    def _convert_cod_orientacao_nis(self, value):
        return int(value)

    def get_identification_obj(self, obj):
        return "%011s" % (obj.get("cpf", ""))

    def get_typeof(self):
        return "ESC"

    def execute(self, task=None):

        task = (
            Task.objects.create(
                description="Carregando arquivo: %s" % os.path.basename(self.file)
            )
            if not task
            else task
        )

        result = {"file": self.file, "hash": "", "result": {}}
        log.debug("STATING EXECUTION %s" % self.__class__.__name__)

        try:
            self.load()
        except self.ValidateError as e:
            log.exception(e)
            task.info("{}".format(e), 3)
            task.finish_execution("ERROR", "Erro na validação do arquivo")
        except Exception as e:
            log.exception(e)
            raise e
        else:

            total = len(self.objects)
            inc_progress = 100.0 / total if total else 0

            default_nis = RegistrationQualification.default_nis

            for obj in self.objects:

                try:
                    # dn = datetime.datetime.strptime(obj.get('dn'), '%d%m%Y') if obj.get('dn') else None
                    query_np_qualif = RegistrationQualification.objects.filter(
                        Q(cpf=obj.get("cpf", ""))
                    )
                    if query_np_qualif.count() > 1:
                        regs = ""
                        for nq in query_np_qualif:
                            regs += "<p>CPF: %s DN: %s %s</p>" % (
                                nq.cpf,
                                nq.dn.strftime("%d/%m/%Y") if nq.dn else "",
                                nq.nome,
                            )
                        task.info(
                            "Registros com mesmo CPF, isso deve ser corrigido!%s"
                            % regs,
                            2,
                        )
                        query_np_qualif = query_np_qualif.filter(
                            Q(cpf=obj.get("cpf", ""), nome=obj.get("nome", ""))
                            | Q(cpf=obj.get("cpf", ""), dn=obj.get("dn", None))
                        )
                    if query_np_qualif.count() == 1:
                        np_qualif = query_np_qualif.first()
                        for k in self.config:
                            if hasattr(np_qualif, k):
                                if k in ["nome", "cpf", "nis", "dn"]:
                                    if getattr(np_qualif, k) != obj.get(k) and not (
                                        k == "nis" and obj.get(k) == default_nis
                                    ):
                                        task.info(
                                            "Registro diferente do enviado para o CPF %s! %s: %s/%s"
                                            % (
                                                obj.get("cpf", ""),
                                                k,
                                                getattr(np_qualif, k),
                                                obj.get(k),
                                            ),
                                            2,
                                        )
                                else:
                                    setattr(np_qualif, k, obj.get(k))
                        np_qualif.last_qualification_at = self.processing_date.date()
                        np_qualif.last_qualification_by = get_current_user()
                        np_qualif.type_of_last_qualification = 3  # LOTE
                        if self.status == "PROCESSADO":
                            np_qualif.separador = 0
                            np_qualif.reg_desformatado = 0
                            np_qualif.status = (
                                3  # DEIXANDO INICIALMENTE EM PROCESSADO COM ERRO
                            )
                        else:
                            np_qualif.status = 4  # DEIXANDO STATUS DE REJEITADO

                        np_qualif.save()
                    else:
                        task.info("Registro não encontrado! %s" % obj.get("_line_"), 2)

                except Exception as e:
                    log.exception("{}".format(e))
                    task.info("Registro não carregado! %s" % "{}".format(e), 3)
                finally:
                    Task.objects.filter(pk=task.pk).update(
                        progress=F("progress") + inc_progress
                    )

            task.finish_execution()

        return result

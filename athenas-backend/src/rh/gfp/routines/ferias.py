# -*- coding: utf-8 -*-

import os

from contrib.utils import getLogger
from engine.models import TaskSession
from rh import models as rh_models
from rh.gfp import models as gfp_models
from standard.loader.models import FileLoader

log = getLogger("rh.gfp.loaders")


# @RunCodeManager.register('gfp-loader-generic')
class GFPLoader(FileLoader):
    typeof = "LOADER"
    titulo = "Carregador genérico de arquivos da FOPAG"
    descricao = "Este carregador carrega arquivos genéricos de lançamentos nos contracheques de uma determinada folha."

    CONFIG = {
        "tipo": 0,
        "matricula": 1,
        "evento": 2,
        "qnt": 3,
        "pct": 4,
        "prazo": 5,
        "valor": 6,
        "valor_base": 7,
        "patronal": 8,
        "base_previdencia": 9,
        "info": 10,
    }
    HEADER_LINES = 1
    CODE_TYPE = "utf-8"
    TRANSACTION_FULL = True
    RETURN_ONLY_ERRORS = False

    def __init__(self, file_, payroll, **kargs):
        log.debug(
            "LOADER: %s:%s:%s:%s" % (self.__class__.__name__, file_, payroll, kargs)
        )
        super(GFPLoader, self).__init__(file_, **kargs)
        self.payroll = payroll
        if not hasattr(self, "evento"):
            self.evento = None

    def pre_validate(self):
        if not isinstance(self.payroll, gfp_models.Folha):
            raise self.ValidateError("Folha (%s) inválida!" % self.payroll)

    def _convert_evento(self, value):
        return gfp_models.Evento.objects.get(numero=value)

    def line_to_dict(self, linec):
        try:
            dict_ = super(GFPLoader, self).line_to_dict(linec)
        except gfp_models.Evento.DoesNotExist:
            raise self.ValidateError("Evento inexistente!")
        except Exception as e:
            raise e
        else:
            if "evento" not in dict_:
                if not self.evento:
                    raise self.ValidateError("Número do evento não indicado!")
                else:
                    dict_["evento"] = self.evento
            else:
                if self.evento and dict_["evento"] != self.evento:
                    raise self.ValidateError(
                        "Evento do registro (%s) diferente do evento informado (%s)!"
                        % (dict_["evento"], self.evento)
                    )
        return dict_

    def get_line(self, dict_):
        line = super(GFPLoader, self).get_line(dict_)
        line = "%s;%s" % (line, dict_.get("msg", ""))
        return line

    def remove_events(self, paycheck, params):
        log.debug("REMOVING EVENTS: %s" % params)
        params_ = {}
        if "pk" in params:
            params_["pk"] = params["pk"]
        else:
            params_["evento"] = params.get("evento")
            params_["info"] = params.get("info", "")

        log.debug("REMOVING EVENTS: %s" % params_)
        fe = paycheck.lancamentos.get(**params_)
        params_ = {
            "evento": fe.evento,
            "info": fe.info,
            "valor": fe.valor,
            "prazo": fe.prazo,
            "qnt": fe.qnt,
            "pct": fe.pct,
        }

        deleteds = paycheck.delete_evento([fe.pk])
        paycheck.consolidate()

        log.debug("DELETEDS: %s" % deleteds)

        if deleteds:
            params_["pk"] = deleteds[0].pk

        return params_

    def add_event(self, paycheck, params):
        """DOCSTRING."""
        params_ = params.copy()

        if params["evento"].automatico and params["evento"].calculo:
            # Incluindo um evento automatico
            calc = params["evento"].calculo.cls(
                paycheck.servidor, paycheck.folha, params["evento"], params=params_
            )
            # params_ = calc.calcular()
            params_.update(calc.calcular())

        log.debug("PARAMS >>>> %s" % params_)

        fe, created_or_updated = paycheck.add_evento(True, True, **params_)
        paycheck.consolidate()

        params_.update({"pk": fe.pk})

        return params_

    def update_event(self, paycheck, params):
        params_ = params.copy()

        if "id" not in params_:
            params_["id"] = paycheck.lancamentos.get(
                evento=params_.get("evento"), info=params_.get("info", "")
            ).pk

        if params["evento"].automatico and params["evento"].calculo:
            # Incluindo um evento automatico
            calc = params["evento"].calculo.cls(
                paycheck.servidor, paycheck.folha, params["evento"], params=params
            )
            params_.update(calc.calcular())

        log.debug("PARAMS >>>> %s" % params_)

        fe, created, old_fields = paycheck.update_or_create_entry(True, True, **params_)
        paycheck.consolidate()

        params_.update({"pk": fe.pk})

        return params_

    def execute(self, task=None):

        task = (
            TaskSession.start_execution(
                "Carregando arquivo: %s > %s"
                % (os.path.basename(self.file), self.payroll)
            )
            if not task
            else task
        )

        result = {
            "year": "%4d" % self.payroll.periodo.ano,
            "month": "%02d" % self.payroll.periodo.mes,
            "hash": "",
            "result": {},
        }
        log.debug("STATING EXECUTION %s" % self.__class__.__name__)

        task["pctText"] = "Carregando arquivo..."
        # if not self.objects:
        try:
            self.load()
        except self.ValidateError as e:
            task.info(e, 3)
            task.finish_execution("ERROR", "Erro na validação do arquivo")
        except Exception as e:
            log.exception(e)
            raise e
        else:

            count = 0
            task["total"] = len(self.objects)
            for obj in self.objects:
                log.debug("OBJ: %s" % obj)

                # TODO Verificar se a rubrica não veio repitida no arquivo
                res = {}
                count += 1
                task["pct"] = count
                try:
                    params_evento = {
                        "valor": obj["valor"] if "valor" in obj else 0,
                        "pct": obj["pct"] if "pct" in obj else 0,
                        "qnt": obj["qnt"] if "qnt" in obj else 0,
                        "prazo": obj["prazo"] if "prazo" in obj else 0,
                        "info": obj["info"] if "info" in obj else "",
                        "valor_base": obj["valor_base"] if "valor_base" in obj else 0,
                        "patronal": obj["patronal"] if "patronal" in obj else 0,
                        "base_previdencia": (
                            obj["base_previdencia"] if "base_previdencia" in obj else 0
                        ),
                    }

                    cc = gfp_models.ContraCheque.objects.get(
                        folha=self.payroll,
                        servidor=rh_models.Servidor.objects.get(
                            matricula=int(obj["matricula"])
                        ),
                    )

                    params_evento.update({"evento": obj["evento"]})

                    res = {}
                    if obj["tipo"] == "I":
                        # Incluindo novo folhaevento
                        res = self.add_event(cc, params_evento)
                    elif obj["tipo"] == "E":
                        # Excluindo folhaevento
                        log.debug("REMOVE EVENTS: %s/%s" % (cc, params_evento))
                        res = self.remove_events(cc, params_evento)
                    elif obj["tipo"] == "A":
                        # TODO Alteração de folhaevento
                        res = self.update_event(cc, params_evento)

                    obj["msg"] = "OK"

                    obj.update(res)

                except gfp_models.ContraCheque.DoesNotExist:
                    obj["msg"] = (
                        "CONTRACHEQUE para a matricula %s NÃO EXISTE na folha %s!"
                        % (obj["matricula"], self.payroll)
                    )
                except gfp_models.FolhaEvento.DoesNotExist:
                    obj["msg"] = "GFP_RUBRICA %s NÃO EXISTE no contracheque %s!" % (
                        obj["evento"],
                        cc,
                    )
                except gfp_models.FolhaEvento.MultipleObjectsReturned:
                    obj["msg"] = (
                        "Existe mais de uma GFP_RUBRICA %s no contracheque %s!"
                        % (obj["evento"], cc)
                    )
                except gfp_models.ContraCheque.DuplicateFolhaEvento as e:
                    obj["msg"] = e
                except rh_models.Servidor.DoesNotExist:
                    obj["msg"] = (
                        "Servidor inexistente para a matricula %s" % obj["matricula"]
                    )
                except Exception as e:
                    log.exception(e)
                    obj["msg"] = "%s" % e

                if obj["msg"] != "OK":
                    task.info(obj["msg"], 2)

            # print '>>>>>> CRIANDO ARQUIVO DE RETORNO ...',

            try:
                task["pctText"] = "Criando arquivo de retorno."
                self.create_return_file()
            except Exception as e:
                log.exception(e)
                # print ' ERRO'
                # transaction.rollback()
                task.info("Erro ao criar arquivo de retorno.", 3)

            task.finish_execution()

        return result

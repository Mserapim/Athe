# -*- coding: utf-8 -*-

import os

from contrib.utils import getLogger
from engine.models import TaskSession
from ged.models import Arquivo as Ged
from rh import models as rh_models
from rh.gfp import models as gfp_models
from standard.loader.models import FileLoader
from standard.models import RunCodeManager

log = getLogger("rh.gfp.loaders")


@RunCodeManager.register("gfp-loader-generic")
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
        "reference_year": 11,
        "reference_month": 12,
        # 'parcela': 5,
    }
    HEADER_LINES = 1
    CODE_TYPE = "utf-8"
    TRANSACTION_FULL = True
    RETURN_ONLY_ERRORS = False

    def __init__(self, file_, payroll, create=False, **kargs):
        log.debug(
            "LOADER: %s:%s:%s:%s:%s"
            % (self.__class__.__name__, file_, payroll, create, kargs)
        )
        super(GFPLoader, self).__init__(file_, **kargs)
        # self.remove_only_equal_info = kargs['remove_only_equal_info'] if 'remove_only_equal_info' in kargs else True
        self.payroll = payroll
        self.create_paycheck = create
        if not hasattr(self, "evento"):
            self.evento = None

    def pre_validate(self):
        if not isinstance(self.payroll, gfp_models.Folha):
            raise self.ValidateError("Folha (%s) inválida!" % self.payroll)

    def _convert_valor(self, value):
        try:
            return float(value or 0)
        except ValueError:
            self.ValidateError('Campo "valor" (%s) com formato inválido!' % (value))

    def _convert_base_previdencia(self, value):
        try:
            return float(value or 0)
        except ValueError:
            self.ValidateError(
                'Campo "base_previdencia" (%s) com formato inválido!' % (value)
            )

    def _convert_valor_base(self, value):
        try:
            return float(value or 0)
        except ValueError:
            self.ValidateError(
                'Campo "valor base" (%s) com formato inválido!' % (value)
            )

    def _convert_patronal(self, value):
        try:
            return float(value or 0)
        except ValueError:
            self.ValidateError('Campo "patronal" (%s) com formato inválido!' % (value))

    def _convert_prazo(self, value):
        return int(value.strip()) if value else 0

    def _convert_parcela(self, value):
        return int(value.strip()) if value else 0

    def _convert_pct(self, value):
        try:
            return float(value) if value else None
        except ValueError:
            self.ValidateError('Campo "pct" (%s) com formato inválido!' % (value))

    def _convert_qnt(self, value):
        try:
            return float(value) if value else 0
        except ValueError:
            self.ValidateError('Campo "qnt" (%s) com formato inválido!' % (value))

    def _convert_evento(self, value):
        return gfp_models.Evento.objects.get(numero=value)

    def line_to_dict(self, linec):
        try:
            dict_ = super(GFPLoader, self).line_to_dict(linec)
        except gfp_models.Evento.DoesNotExist:
            raise self.ValidateError(
                f'Evento inexistente! ({linec[self.config.get("evento", "NI")]})'
            )
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
                    log.debug(
                        "Evento do registro (%s) diferente do evento informado (%s)!"
                        % (dict_["evento"], self.evento)
                    )
                    return {}
        return dict_

    def get_line(self, dict_):
        line = super(GFPLoader, self).get_line(dict_)
        line = "%s;%s" % (line, dict_.get("msg", ""))
        return line

    def get_identification_obj(self, obj):
        return "%015s%s%05d%s%s" % (
            obj.get("matricula", ""),
            obj.get("tipo", "X"),
            self.payroll.pk,
            obj.get("evento").numero,
            obj.get("info", ""),
        )

    def get_typeof(self):
        return "GFP"

    def create_or_update_history(self, obj, status):
        _id = self.get_identification_obj(obj)
        leh, created = gfp_models.LoadedEntryHistory.objects.get_or_create(
            payroll=self.payroll,
            identification=_id,
            typeof=self.get_typeof(),
            defaults={"status": status},
        )
        if obj.get("tipo") != "E":
            leh.entry_id = obj.get("pk", None)
        if leh.status != 1:
            leh.status = status
        leh.line_text = obj.get("_line_", "")
        leh.save()

        return leh, created

    def remove_events(self, paycheck, params, recalc=False):
        # log.debug(u'REMOVING EVENTS: %s' % params)
        params_ = {}
        if "pk" in params:
            params_["pk"] = params["pk"]
        else:
            params_["evento"] = params.get("evento")
            params_["info"] = params.get("info", "")

        # log.debug(u'REMOVING EVENTS: %s' % params_)
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

        # log.debug(u'DELETEDS: %s' % deleteds)

        if deleteds:
            params_["pk"] = deleteds[0].pk

        return params_

    def add_event(self, paycheck, params):
        params_ = params.copy()

        if params["evento"].automatico and params["evento"].calculo:
            # Incluindo um evento automatico
            calc = params["evento"].calculo.cls(
                paycheck.servidor,
                paycheck.folha,
                params["evento"],
                params=params_,
                pension=paycheck.pensioner,
            )
            params_.update(calc.calcular())

        # log.debug(u'PARAMS >>>> %s' % params_)
        params_.update({"insertion_type": 3})
        fe, created_or_updated = paycheck.add_evento(False, True, **params_)

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
                paycheck.servidor,
                paycheck.folha,
                params["evento"],
                params=params,
                pension=paycheck.pensioner,
            )
            params_.update(calc.calcular())

        # log.debug(u'PARAMS >>>> %s' % params_)
        params_.update({"insertion_type": 3})
        fe, created, old_fields = paycheck.update_or_create_entry(
            False, True, **params_
        )

        params_.update({"pk": fe.pk})

        return params_

    def _change_values(self, params):
        return params

    def execute(self, task=None):
        paycheck_ = None
        ged_file = Ged.objects.get(file=os.path.basename(self.file))
        log.debug(task)
        task.info(
            msg="Carregando arquivo: %s > %s" % (ged_file.filename, self.payroll),
            type_of=1,
        )

        result = {
            "year": "%4d" % self.payroll.periodo.ano,
            "month": "%02d" % self.payroll.periodo.mes,
            "hash": "",
            "result": {},
        }

        try:
            self.load()
        except Exception as e:
            task.info(msg=str(e), type_of=3)
            task.finish_execution(msg="ERRO ao carregar arquivo", status="ERROR")
            log.exception(e)
        else:
            count = 0
            progress = 100.0 / len(self.objects) if len(self.objects) > 0 else 1
            for obj in self.objects:
                paycheck = None
                # log.debug(u'OBJ: %s' % obj)

                # if not obj['matricula'] in result:
                #     result['result'][obj['matricula']] = {}

                # TODO Verificar se a rubrica não veio repetida no arquivo
                res = {}
                count += 1
                # task['pct'] = count
                try:
                    event = obj.get("evento", None)
                    matricula = obj.get("matricula", "")
                    if event and event.automatico:
                        raise Exception(
                            f"O evento {str(event)} do servidor de matrícula {matricula} está cadastrado como automático nos sistema, portanto, não será calculado."
                        )
                    params_evento = {
                        "valor": obj.get("valor", 0),
                        "pct": obj.get("pct", 0),
                        "qnt": obj.get("qnt", 0),
                        "parcela": obj.get("parcela", 0),
                        "prazo": obj.get("prazo", 0),
                        "info": obj.get("info", ""),
                        "valor_base": obj.get("valor_base", 0),
                        "patronal": obj.get("patronal", 0),
                        "base_previdencia": obj.get("base_previdencia", 0),
                        "reference_year": obj.get(
                            "reference_year", self.payroll.periodo.ano
                        ),
                        "reference_month": obj.get(
                            "reference_month", self.payroll.periodo.mes
                        ),
                    }
                    employee = rh_models.Servidor.objects.get(
                        matricula=int(obj["matricula"])
                    )
                    if self.create_paycheck:
                        paycheck, created = (
                            gfp_models.ContraCheque.objects.get_or_create(
                                folha=self.payroll, servidor=employee, pensioner=None
                            )
                        )
                    else:
                        paycheck = gfp_models.ContraCheque.objects.get(
                            folha=self.payroll, servidor=employee, pensioner=None
                        )

                    params_evento.update({"evento": obj["evento"]})

                    params_evento = self._change_values(params_evento)

                    res = {}
                    if obj["tipo"] == "I":
                        # Incluindo novo folhaevento
                        log.info(params_evento)
                        try:
                            res = self.add_event(paycheck, params_evento)
                        except Exception as e:
                            task.info(msg="ERRO AO Adicionar: " + str(e), type_of=3)
                    elif obj["tipo"] == "E":
                        # Excluindo folhaevento
                        # log.debug(u'REMOVE EVENTS: %s/%s' % (paycheck, params_evento))
                        try:
                            res = self.remove_events(paycheck, params_evento)
                        except Exception as e:
                            task.info(msg="ERRO AO remover: " + str(e), type_of=3)
                    elif obj["tipo"] == "A":
                        # TODO Alteração de folhaevento
                        try:
                            res = self.update_event(paycheck, params_evento)
                        except Exception as e:
                            task.info(msg="ERRO AO alterar: " + str(e), type_of=3)

                    task.info(pct_progress=progress)
                    obj["msg"] = "OK"

                    obj.update(res)

                    # recalculando ultimo contracheque, caso seja diferente do atual
                    if (
                        paycheck_ and paycheck_ != paycheck
                    ):  # and paycheck_ != last_paycheck_recalc:
                        paycheck_aux = paycheck_
                        paycheck_ = paycheck
                        paycheck_aux.recalculate()
                        paycheck_aux.consolidate()
                        # last_paycheck_recalc = paycheck_aux

                except gfp_models.ContraCheque.DoesNotExist:
                    obj["msg"] = (
                        "CONTRACHEQUE para a matricula %s NÃO EXISTE na folha %s!"
                        % (obj["matricula"], self.payroll)
                    )
                    self.create_or_update_history(obj, 3 if not employee.ativo else 4)
                except gfp_models.FolhaEvento.DoesNotExist:
                    obj["msg"] = "GFP_RUBRICA %s NÃO EXISTE no contracheque %s!" % (
                        obj["evento"],
                        paycheck,
                    )
                    if obj["tipo"] == "E":
                        self.create_or_update_history(obj, 1)
                    else:
                        self.create_or_update_history(obj, 9)
                except gfp_models.FolhaEvento.MultipleObjectsReturned:
                    self.create_or_update_history(obj, 9)
                    obj["msg"] = (
                        "Existe mais de uma GFP_RUBRICA %s no contracheque %s!"
                        % (obj["evento"], paycheck)
                    )
                except gfp_models.ContraCheque.DuplicateFolhaEvento as e:
                    self.create_or_update_history(obj, 1)
                    obj["msg"] = e
                except rh_models.Servidor.DoesNotExist:
                    self.create_or_update_history(obj, 2)
                    obj["msg"] = (
                        "Servidor inexistente para a matricula %s" % obj["matricula"]
                    )
                except Exception as e:
                    log.exception(e)
                    self.create_or_update_history(obj, 9)
                    obj["msg"] = "%s" % e
                else:
                    self.create_or_update_history(obj, 1)

                if obj["msg"] != "OK":
                    task.info(msg=obj["msg"], type_of=2)

            # print '>>>>>> CRIANDO ARQUIVO DE RETORNO ...',
            # XXX: Verficar comportamento da função, considerando que o if statement abaixo foi retirado no merge 17/11/2022
            if paycheck_:
                # recalculando ultimo contracheque do for
                paycheck_.recalculate()
                paycheck_.consolidate()

            try:
                return_file = self.create_return_file()
                task.add_file(
                    return_file, msg="Arquivo de histórico de carregamento disponível."
                )
            except Exception as e:
                log.exception(e)
                task.info(msg="Erro ao criar arquivo de retorno.", type_of=3)

        return result

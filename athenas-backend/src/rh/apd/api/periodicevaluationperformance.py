# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_display, nil_pk, nil_str
from contrib.utils import DateUtils, getLogger
from rh.apd.models import Commission, Configuration, PeriodicEvaluationPerformance

# from standard.questionario.models import
from standard.questionario.views import QMontarQuestionario

log = getLogger(__name__)


class ApdPeriodicEvaluationPerformance(Restful, QMontarQuestionario):
    """Classe representativa do modelo PeriodicEvaluationPerformance. Herda ainda os metodos
    da classe QMontarQuestionario que é responsável pela exibição de um questionario."""

    _model = PeriodicEvaluationPerformance

    full_text_index = (
        "employee__servidor__matricula__icontains",
        "employee__servidor__pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        """Json do Manager."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.periodicevaluationperformance.Manage")')

    def repeat_last_evaluation(self, args=[]):
        """Realiza uma cópia de uma avaliação existente para uma etapa nova da APD."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info('Finalizando etapa de APD')

            present_apd = self.Model.objects.get(pk=int(self.request.POST.get("pk")))

            text_justification_repetition = self.request.POST.get(
                "text_justification_repetition"
            )

            present_apd.repeat_last_evaluation(
                justification=text_justification_repetition
            )

            rst.update(message="avaliação repetida com sucesso!", success=True)
        except PeriodicEvaluationPerformance.DoesNotExist as e:
            log.exception(e)
            rst.update(message="Nenhuma avaliação periódica encontrada!")
        except Configuration.DoesNotExist as e:
            log.exception(e)
            rst.update(message="Nenhuma configuração encontrada!")
        except Commission.DoesNotExist as e:
            log.exception(e)
            rst.update(message="Nenhuma comissão de avaliação encontrada!")
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def finish_stage(self, args=[]):
        """Finaliza uma etapa da APD."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info('Finalizando etapa de APD')
            with transaction.atomic():
                old_apd = self.Model.objects.get(pk=int(self.request.POST.get("pk")))

                old_apd.validate_modified()

                if (
                    not old_apd.exists_evaluation()
                    or not old_apd.exists_manifestation()
                ):
                    raise Exception(
                        "Não é possível finalizar essa etapa. Avaliação ou Manifestação pendente!"
                    )

                if not old_apd.action_state_evaluation(3):
                    raise Exception(
                        "Não é possível finalizar essa etapa. Pendências em avaliação ou Manifestação!"
                    )

                configuration = Configuration.objects.get(end_date__isnull=True)
                commission = Commission.objects.get(end_date__isnull=True)
                new_apd = PeriodicEvaluationPerformance(
                    previous_apd=old_apd,
                    configuration=configuration,
                    commission=commission,
                    employee=old_apd.employee,
                    start_date=old_apd.end_date + relativedelta(days=1),
                    end_date=old_apd.end_date
                    + relativedelta(months=configuration.interval_periodic_evaluation),
                )
                new_apd.save()

                old_apd.finish()

                rst.update(success=True, message="Procedimento realizado com sucesso.")

        except PeriodicEvaluationPerformance.DoesNotExist as e:
            log.error(e)
            rst.update(message="Nenhuma avaliação periódica encontrada!")
        except Configuration.DoesNotExist as e:
            log.error(e)
            rst.update(message="Nenhuma configuração encontrada!")
        except Commission.DoesNotExist as e:
            log.error(e)
            rst.update(message="Nenhuma comissão de avaliação encontrada!")
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def postpone_lock(self, args=[]):
        """Adia o bloqueio da APD."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            apd = self.request.POST.getlist("pk")
            days = int(self.request.POST.get("days"))
        except ValueError as e:
            log.exception(e)
            rst.update(
                message="Algum problema com seus dados: {}".format(
                    self.request.POST.get("days")
                )
            )
        else:
            try:
                self.Model.postpone_lock(apd, days)
                rst.update(success=True, message="Deu tudo certo")
            except Exception as e:
                log.exception(e)
                rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_text_reconsideration(self, args=[]):
        """Retorna o texto do pedido de reconsideração de uma avaliação."""
        rst = {"message": "nada foi feito ainda.", "collection": [], "success": False}
        try:
            # log.info(self.request.POST)
            apd = self.Model.objects.get(pk=int(self.request.POST.get("pk")))
            if apd.exists_evaluation():
                evaluation = apd.get_evaluation()
                if not evaluation.date_reconsideration:
                    raise Exception("Nenhum pedido de reconsideração encontrado!")
                else:
                    rst["collection"].append(
                        {
                            "text_reconsideration": "%s"
                            % evaluation.text_reconsideration,
                            "date_reconsideration": DateUtils.date_to_str(
                                evaluation.date_reconsideration
                            ),
                        }
                    )
                rst.update(success=True)
            else:
                rst.update(message="Nenhuma avaliação encontrada!")
        except PeriodicEvaluationPerformance.DoesNotExist as e:
            log.error(e)
            rst.update(message="Nenhuma avaliação periódica encontrada!")
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_text_opinion_reconsideration(self, args=[]):
        """Retorna o texto do parecer do chefe quanto ao pedido de reconsideração de uma avaliação."""
        rst = {"message": "nada foi feito ainda.", "collection": [], "success": False}
        try:
            # log.info(self.request.POST)
            apd = self.Model.objects.get(pk=int(self.request.POST.get("pk")))
            if apd.exists_evaluation():
                evaluation = apd.get_evaluation()
                if not evaluation.date_reconsideration:
                    raise Exception("Nenhum pedido de reconsideração encontrado!")
                else:
                    rst["collection"].append(
                        {
                            "text_reconsideration": "%s"
                            % evaluation.opinion_request_reconsideration,
                            "date_reconsideration": DateUtils.date_to_str(
                                evaluation.date_opinion_request_reconsideration
                            ),
                        }
                    )
                rst.update(success=True)
            else:
                rst.update(message="Nenhuma avaliação encontrada!")
        except PeriodicEvaluationPerformance.DoesNotExist as e:
            log.error(e)
            rst.update(message="Nenhuma avaliação periódica encontrada!")
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_query(self):
        """Retorna a query."""
        query = (
            super(ApdPeriodicEvaluationPerformance, self)
            .get_query()
            .order_by("end_date", "employee__servidor")
        )

        if not (
            self.request.user.has_perm("apd.apd_admin")
            or self.request.user.has_perm("apd.apd_boss")
            or self.request.user.has_perm("apd.apd_subordinate")
        ):
            query = query.exclude(id__gt=0)
        return query

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        if "modified_by" in params:
            if params.get("modified_by") != "":
                field = getattr(self.Model, "modified_by")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(modified_by=query.get(pk=params.get("modified_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(modified_by=None)

        if (
            "date_automatica_science" in params
            and params.get("date_automatica_science") == ""
        ):
            params.update(date_automatica_science=None)

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                params.update(end_date=None)

        if "employee" in params:
            if params.get("employee") != "":
                field = getattr(self.Model, "employee")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(employee=query.get(pk=params.get("employee")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(employee=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

        if "configuration" in params:
            if params.get("configuration") != "":
                field = getattr(self.Model, "configuration")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        configuration=query.get(pk=params.get("configuration"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(configuration=None)

        if "modified_at" in params:
            if params.get("modified_at") != "":
                params.update(
                    modified_at=DateUtils.str_to_datetime(params.get("modified_at"))
                )
            else:
                params.update(modified_at=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                params.update(start_date=None)

        if "created_by" in params:
            if params.get("created_by") != "":
                field = getattr(self.Model, "created_by")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(created_by=query.get(pk=params.get("created_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(created_by=None)

        if "previous_apd" in params:
            if params.get("previous_apd") != "":
                field = getattr(self.Model, "previous_apd")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(previous_apd=query.get(pk=params.get("previous_apd")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previous_apd=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)
        rst.update(
            icons=instance.icons,
            status=str(instance.status),
            percent=instance.get_scores_obtained(),
            status_display=nil_display(instance, "status", None),
            days_suspended=str(instance.days_suspended),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            end_date=nil_date(instance.end_date, None),
            employee=nil_pk(instance.employee, None),
            employee_unicode=str(instance.employee) or None,
            created_at=nil_datetime(instance.created_at, None),
            configuration=nil_pk(instance.configuration, None),
            configuration_unicode=str(instance.configuration) or None,
            modified_at=nil_datetime(instance.modified_at, None),
            start_date=nil_date(instance.start_date, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            previous_apd=nil_pk(instance.previous_apd, None),
            previous_apd_unicode=nil_str(instance.previous_apd, ""),
            questionnaire_boss=str(instance.configuration.questionnaire_boss) or None,
            questionnaire_boss_id=str(instance.configuration.questionnaire_boss_id),
            questionnaire_subordinate=str(
                instance.configuration.questionnaire_subordinate
            )
            or None,
            questionnaire_subordinate_id=str(
                instance.configuration.questionnaire_subordinate_id
            ),
            deadline=str(instance.deadline),
            boss_unicode=str(instance.employee.servidor.chefe_imediato) or None,
            period_unicode=instance.get_evaluation_period(),
            days_off_while_apd=instance.days_off_while_apd(),
            can_boss_evaluate=instance.can_boss_evaluate(),
            lock_in=str(instance.lock_in),
        )

        return rst

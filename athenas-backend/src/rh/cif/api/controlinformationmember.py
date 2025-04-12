# -*- coding: utf-8 -*-

from django.db import transaction

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_new_display, nil_pk, nil_new_unicode
from contrib.utils import DateUtils, getLogger
from rh.cif.models import (
    AddressCif,
    ControlInformationMember,
    DebtsEncumbrances,
    Property,
    ReferencePeriod,
    Teaching,
)

# from rh.cif.cif_signal import *


log = getLogger(__name__)


class CifControlInformationMember(Restful):

    _model = ControlInformationMember

    full_text_index = (
        "employee__servidor__matricula__icontains",
        "employee__servidor__pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"

        if self.request.user.has_perm("cif.cif_admin"):
            self.response.write('Ext._create("cif.Manage")')
        elif self.request.user.has_perm("cif.cif_membro"):
            self.response.write('Ext._create("cif.controlinformationmember.Manage")')
        elif self.request.user.has_perm("cif.cif_auditoria"):
            self.response.write('Ext._create("cif.Manage")')

    def has_perm_admin(self):
        current_user = self.request.user.servidor
        return True if current_user.user.has_perm("cif.cif_admin") else False

    def copy_referenceperiod(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            if self.has_perm_admin():
                with transaction.atomic():
                    previous_referenceperiod = ReferencePeriod.objects.get(
                        pk=int(self.request.POST.get("previous_referenceperiod"))
                    )
                    old_controlinformation = ControlInformationMember.objects.filter(
                        referenceperiod=previous_referenceperiod
                    )
                    # Cria um novo periodo de referencia
                    new_referenceperiod = ReferencePeriod(
                        previous_referenceperiod=previous_referenceperiod,
                        exercise=self.request.POST.get("exercise"),
                        start_date=DateUtils.str_to_date(
                            self.request.POST.get("start_date")
                        ),
                        end_date=DateUtils.str_to_date(
                            self.request.POST.get("end_date")
                        ),
                    )
                    new_referenceperiod.save()
                    # Cria um novo controle de informacoes referentes a um novo periodo para cada membro
                    for old_information in old_controlinformation.all():
                        new_controlinformation = ControlInformationMember(
                            previous_controlinformation=old_information,
                            employee=old_information.employee,
                            referenceperiod=new_referenceperiod,
                        )
                        new_controlinformation.save()

                        # Copia atividades de docencia de um controle anteiror para o novo controle
                        if old_information.teaching.exists():
                            for old_teaching in old_information.teaching.all():
                                new_teaching = Teaching(
                                    member=new_controlinformation,
                                    educational_institution=old_teaching.educational_institution,
                                    discipline=old_teaching.discipline,
                                    work_hours=old_teaching.work_hours,
                                    start_date=old_teaching.start_date,
                                    end_date=old_teaching.end_date,
                                    refperiod_teaching=new_referenceperiod,
                                )
                                new_teaching.save()
                                if old_teaching.schedule.exists():
                                    for sc in old_teaching.schedule.all():
                                        new_teaching.schedule.add(sc)
                                new_teaching.save()

                        # Copia endereços de um controle anteiror para o novo controle
                        if old_information.address.exists():
                            for old_address in old_information.address.all():
                                log.info(new_controlinformation.pk)
                                new_address = AddressCif(
                                    previus_addres=old_address,
                                    member=new_controlinformation,
                                    start_date=old_address.start_date,
                                    end_date=old_address.end_date,
                                    type_residence=old_address.type_residence,
                                    # municipio=old_address.municipio,
                                    # logradouro=old_address.logradouro,
                                    # tipo_logradouro=old_address.tipo_logradouro,
                                    # numero=old_address.numero,
                                    # complemento=old_address.complemento,
                                    # bairro=old_address.bairro,
                                    # cep=old_address.cep,
                                    # tipo_endereco=old_address.tipo_endereco,
                                    refperiod_address=new_referenceperiod,
                                    ref_address=old_address.ref_address,
                                )
                                new_address.save()

                        # # Copia bens e valores para o novo controle
                        if old_information.property.exists():
                            for old_property in old_information.property.all():
                                new_property = Property(
                                    member=new_controlinformation,
                                    code=old_property.code,
                                    country=old_property.country,
                                    description=old_property.description,
                                    current_value=old_property.current_value,
                                    last_value=old_property.current_value,
                                    refperiod_property=new_referenceperiod,
                                )
                                new_property.save()

                        # # Copia dividas e onus reais para o novo controle
                        if old_information.debtsencumbrances.exists():
                            for old_debts in old_information.debtsencumbrances.all():
                                new_debts = DebtsEncumbrances(
                                    member=new_controlinformation,
                                    code=old_debts.code,
                                    description=old_debts.description,
                                    current_value=old_debts.current_value,
                                    last_value=old_debts.current_value,
                                    refperiod_debts=new_referenceperiod,
                                )
                                new_debts.save()

                        old_information.status = 2
                        old_information.save()
                    rst.update(
                        success=True,
                        message="Dados persistidos com sucesso!",
                    )

            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except ReferencePeriod.DoesNotExist:
            rst.update(message="Período de Referência não encontrado!")
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def notification(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            if self.has_perm_admin():
                cif = self._model.objects.get(pk=int(self.request.POST.get("pk")))
                cif.notification_member(self.request.POST.get("message"))
                rst.update(success=True, message="Procedimento realizado com sucesso.")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except ControlInformationMember.DoesNotExist:
            rst.update(message="Controle de Informação não encontrado!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def notificationall(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            if self.has_perm_admin():
                pks = self.request.POST.get("pks")
                cifs = (
                    ControlInformationMember.objects.filter(status=1)
                    if pks == ""
                    else ControlInformationMember.objects.filter(pk__in=pks.split(","))
                )
                for cif in cifs:
                    cif.notification_member(self.request.POST.get("message"))
                rst.update(success=True, message="Procedimento realizado com sucesso.")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except ControlInformationMember.DoesNotExist:
            rst.update(message="Controle de Informação não encontrado!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def routine_lock_unlock(self, obj=None, model_name=None, param=None):
        if model_name == "Teaching":
            obj.lock_teaching = param
        elif model_name == "AddressCif":
            obj.lock_address = param
        elif model_name == "Property":
            obj.lock_property = param
        elif model_name == "DebtsEncumbrances":
            obj.lock_debts = param
        obj.save()

    def lock_member(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            model_name = self.request.POST.get("model_name")
            if self.has_perm_admin():
                for cif in ControlInformationMember.objects.filter(
                    pk__in=self.request.POST.getlist("pks")
                ):
                    self.routine_lock_unlock(cif, model_name, True)
                rst.update(success=True, message="Dados persistidos com sucesso!")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def unlock_member(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            model_name = self.request.POST.get("model_name")
            if self.has_perm_admin():
                for cif in ControlInformationMember.objects.filter(
                    pk__in=self.request.POST.getlist("pks")
                ):
                    self.routine_lock_unlock(cif, model_name, False)
                rst.update(success=True, message="Dados persistidos com sucesso!")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def lock_all_member(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            model_name = self.request.POST.get("model_name")
            if self.has_perm_admin():
                for cif in ControlInformationMember.objects.filter(status=1):
                    self.routine_lock_unlock(cif, model_name, True)
                rst.update(success=True, message="Dados persistidos com sucesso!")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def unlock_all_member(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            model_name = self.request.POST.get("model_name")
            if self.has_perm_admin():
                for cif in ControlInformationMember.objects.filter(status=1):
                    self.routine_lock_unlock(cif, model_name, False)
                rst.update(success=True, message="Dados persistidos com sucesso!")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def reactivate(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            if self.has_perm_admin():
                for cif in ControlInformationMember.objects.filter(
                    pk__in=self.request.POST.getlist("pks")
                ):
                    cif.status = 1
                    cif.save()
                rst.update(success=True, message="Dados persistidos com sucesso!")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def deactivate(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            for cif in ControlInformationMember.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            ):
                cif.status = 2
                cif.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "previous_controlinformation" in params:
            if params.get("previous_controlinformation") != "":
                field = getattr(self.Model, "previous_controlinformation")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        previous_controlinformation=query.get(
                            pk=params.get("previous_controlinformation")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previous_controlinformation=None)

        if "employee" in params:
            if params.get("employee") != "":
                field = getattr(self.Model, "employee")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(employee=query.get(pk=params.get("employee")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(employee=None)

        if "referenceperiod" in params:
            if params.get("referenceperiod") != "":
                field = getattr(self.Model, "referenceperiod")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        referenceperiod=query.get(pk=params.get("referenceperiod"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(referenceperiod=None)

        # if 'flag_not_exercise_teaching' in params:
        #     params.update(flag_not_exercise_teaching=params.get('flag_not_exercise_teaching', 'off').lower() == 'on')

        return params

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("cif.cif_admin"):
            query = query.filter()
        elif self.request.user.has_perm("cif.cif_membro"):
            query = query.filter(employee__servidor=self.request.user.servidor)
        elif self.request.user.has_perm("cif.cif_auditoria"):
            query = query = query.filter()

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        _workplace = None

        try:
            _workplace = (
                instance.employee.servidor.workplace.first().lotacao.localidade.id
            )
        except Exception:
            _workplace = 0

        rst.update(
            status=instance.status,
            status_display=nil_new_display(instance, "status", ""),
            icons=instance.icons,
            lock_teaching=nil_new_unicode(instance.lock_teaching, ""),
            lock_address=nil_new_unicode(instance.lock_address, ""),
            lock_property=nil_new_unicode(instance.lock_property, ""),
            lock_debts=nil_new_unicode(instance.lock_debts, ""),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            employee=nil_pk(instance.employee, None),
            employee_unicode=nil_new_unicode(instance.employee, ""),
            employee_name_unicode=nil_new_unicode(instance.employee.servidor, ""),
            previous_controlinformation=nil_pk(
                instance.previous_controlinformation, None
            ),
            previous_controlinformation_unicode=(
                "%s" % instance.previous_controlinformation
            ),
            referenceperiod=nil_pk(instance.referenceperiod, None),
            referenceperiod_unicode=nil_new_unicode(instance.referenceperiod, ""),
            workplace=_workplace,
            person=nil_pk(instance.employee.servidor.pessoa_fisica, None),
        )

        return rst

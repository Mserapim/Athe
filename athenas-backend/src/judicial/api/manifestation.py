# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Manifestation, Bloke, PartLawsuit
from contrib.utils import DateUtils, person_from_user, employee_from_user
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_date
from rh.models import Pessoa as Person
from django.contrib.auth.models import User


log = getLogger(__name__)


class EJudManifestation(Restful):

    _model = Manifestation

    force_upper = False

    def rendered(self, args=[]):
        rst = {"message": "nada feito até o momento", "success": False}

        try:
            person = None

            if "person" in self.request.GET:
                person = Person.objects.get(pk=self.request.GET.get("person"))
            elif "bloke" in self.request.GET:
                person = Bloke.person_from_bloke_id(self.request.GET.get("bloke"))

            reference = PartLawsuit.objects.get(pk=self.request.GET.get("reference"))
            menifestation = Manifestation.objects.get(
                reference=reference,
                who=person,
                who_type=int(self.request.GET.get("who_type") or 0),
            )
        except PartLawsuit.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento de referência no procedimento."
            )
        except Person.DoesNotExist:
            rst.update(
                message="Não consegui encontrar informações da pessoa natural, física ou juridica desejada."
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Ainda não foi feita solicitação de manifestação para %s"
                % person
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Processado com sucesso.",
                content=menifestation.renderer,
            )

        self.renderer(rst)

    def sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        self._read_special_verb()

        try:
            person = None

            if "citizen" in self.request.PUT:
                """
                comunicação com portal do cidadão
                """
            elif self.request.user.is_authenticated:
                person = person_from_user(self.request.user)

            manifestation = self.Model.objects.get(pk=args[0])
            manifestation.sign(person)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Documento assinado com sucesso.")

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        log.debug(kargs)

        if "who" in params:
            if params.get("who") != "":
                field = getattr(self.Model, "who")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(who=query.get(pk=params.get("who")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(who=None)

        if "diligence" in params:
            if params.get("diligence") != "":
                field = getattr(self.Model, "diligence")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(diligence=query.get(pk=params.get("diligence")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(diligence=None)

        if "deadline" in params:
            if params.get("deadline") != "":
                params.update(
                    deadline=DateUtils.str_to_datetime(params.get("deadline"))
                )
            else:
                params.update(deadline=None)

        if "reference" in params:
            if params.get("reference") != "":
                field = getattr(self.Model, "reference")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(reference=query.get(pk=params.get("reference")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(reference=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            content=instance.content,
            who=nil_pk(instance.who, None),
            who_unicode=nil_unicode(instance.who, None),
            deadline=nil_date(instance.deadline, None),
            reference=nil_pk(instance.reference, None),
            reference_unicode=nil_unicode(instance.reference, None),
            diligence=nil_pk(instance.diligence, None),
            diligence_unicode=nil_unicode(instance.diligence, None),
            diligence_formated_number=(
                ("*" * 3)
                if not instance.diligence
                else instance.diligence.formated_number
            ),
            who_type=instance.who_type,
            who_type_display=nil_display(instance, "who_type", None),
            manifestation_type=instance.manifestation_type,
            manifestation_type_display=nil_display(
                instance, "manifestation_type", None
            ),
        )

        return rst

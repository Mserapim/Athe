# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import TriagePart, County
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudTriagePart(Restful):

    _model = TriagePart

    force_orm_single = True

    def do_concurrence(self, args=[]):
        rst = {"success": False, "message": "Não foi feito nada ainda"}

        try:
            obj = self.get_query().get(pk=args[0])
            log.info("Sorteando distribuição para o assunto %s", obj.matter)
            obj.do_concurrence()
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar a divisão de assunto da triagem."
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, instance=self.model_to_dict(obj))

        self.renderer(rst)

    def prepare_concurrence(self, args=[]):
        rst = {"success": False, "message": "Não foi feito nada ainda"}

        try:
            obj = self.get_query().get(pk=args[0])
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar a divisão de assunto da triagem."
            )
        else:
            log.info("Fazendo distribuição para o assunto %s", obj.matter)
            log.info(
                "Nas cidades %s",
                ", ".join([loc.nome for loc in obj.locations.filter()]),
            )

            query = County.objects.filter(
                locations__in=obj.locations.filter()
            ).distinct()
            if not query.exists():
                rst.update(
                    message="Fora da área de atuação deste órgão ou não foram definidas as localidades."
                )
            else:
                log.info("Foram encontradas %d comarca(s)", query.count())
                obj.concurrence.clear()
                for county in query:
                    log.info(
                        "Buscando Órgãos de execução na comarca %s para o assunto %s",
                        county.title,
                        obj.matter.title,
                    )
                    obj.concurrence_in_county(county)

                rst.update(success=True)

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "matter" in params:
            if params.get("matter") != "":
                field = getattr(self.Model, "matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(matter=query.get(pk=params.get("matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(matter=None)

        if "distributed" in params:
            if params.get("distributed") != "":
                field = getattr(self.Model, "distributed")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(distributed=query.get(pk=params.get("distributed")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(distributed=None)

        if "triage" in params:
            if params.get("triage") != "":
                field = getattr(self.Model, "triage")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(triage=query.get(pk=params.get("triage")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(triage=None)

        if "acting_zone" in params:
            if params.get("acting_zone") != "":
                field = getattr(self.Model, "acting_zone")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(acting_zone=query.get(pk=params.get("acting_zone")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(acting_zone=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            matter=nil_pk(instance.matter, None),
            matter_unicode=nil_unicode(instance.matter, None),
            distributed=nil_pk(instance.distributed, None),
            distributed_unicode=nil_unicode(instance.distributed, None),
            triage=nil_pk(instance.triage, None),
            triage_unicode=nil_unicode(instance.triage, None),
            text=instance.text,
            acting_zone=nil_pk(instance.acting_zone, None),
            acting_zone_unicode=nil_unicode(instance.acting_zone, None),
        )

        return rst

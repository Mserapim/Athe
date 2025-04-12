# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_unicode
from raf.models import Quiz, WorkerLocation
from django.db.models import Q
from standard.models import Configuration
from . import util

log = getLogger(__name__)


class RAFQuiz(RestfulDRY):

    force_upper = False

    force_orm_single = True

    full_text_index = (
        "yearbase__title__icontains",
        "typequiz__title__icontains",
    )

    _model = Quiz

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.quiz.Launcher")')

    def model_to_dict(self, instance):
        rst = super(RAFQuiz, self).model_to_dict(instance)

        rst.update(
            {
                "icons": instance.icons,
                "typequiz_unicode": nil_unicode(instance.typequiz, None),
                "yearbase_unicode": nil_unicode(instance.yearbase, None),
                # 'list_classes': instance.list_classes,
                # 'list_taxonomy': nil_unicode(instance.list_taxonomy, None),
            }
        )

        return rst

    def copy_quiz(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
        }

        try:

            params = util.request_params(self)

            if not params.get("typequiz", 0):
                raise Exception("Tipo do questionário não informado.")

            if not params.get("yearbase", 0):
                raise Exception("Ano base não informado.")

            if not params.get("quiz", 0):
                raise Exception("Questionário a ser copiado não informado.")

            quiz = self.get_query().get(pk=params.get("quiz"))

            quiz.create_from(
                typequiz=params.get("typequiz"), yearbase=params.get("yearbase")
            )

        except self.Model.DoesNotExist:
            rst.update(message="Questionário informado não existe.")
        except Exception as e:
            rst.update(message=str(e))
        else:

            rst.update(
                success=True,
                message="Questionário copiado.",
            )

        return self.renderer(rst)

    def enable(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            quiz = self.get_query().get(pk=args[0])
            quiz.activated = not quiz.activated
            quiz.save()

        except self.Model.DoesNotExist:
            rst.update(message="Questionário não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True)

        return self.renderer(rst)

    def all_items(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }

        try:

            params = util.request_params(self)

            query = Q(Q(activated=True))

            quiz = self.get_query().get(pk=params.get("quiz"))
            workerlocation = WorkerLocation.objects.get(pk=params.get("workerlocation"))
            cfg = Configuration.get_or_create("raf")

            data = []

            for item in quiz.item_set.filter(query):
                for si in item.subitems.filter(query):
                    activity = (
                        si.activities.filter(
                            workerlocation__pk=params.get("workerlocation"),
                            item=item,
                            subitem=si,
                        ).first()
                        if si.activities.exists()
                        else None
                    )

                    data.append(
                        {
                            "item": item.pk,
                            "item_unicode": str(item.title),
                            "subitem": si.pk,
                            "subitem_unicode": str(si.title),
                            "subitem_description": str(si.description),
                            # 'subitem_list_taxonomy': nil_unicode(si.list_taxonomy, None),
                            # 'subitem_tooltip': nil_unicode('<b>'+si.get_typesubitem_display()+'</b><br />'+ si.description+'<br />'+ si.list_taxonomy, None),
                            "subitem_tooltip": nil_unicode(
                                "<b>"
                                + si.get_typesubitem_display()
                                + "</b><br />"
                                + si.description
                                + "<br />",
                                None,
                            ),
                            "subitem_typeicons": si.typeicons,
                            "manual_amount": si.manual_amount,
                            "blocked": si.blocked,
                            "activity": activity.pk if activity else None,
                            "activity_amount_submitted": (
                                activity.amount_submitted if activity else None
                            ),
                            "activity_amount": activity.amount if activity else None,
                            "workerlocation_monthyear": str(workerlocation.raf.month)
                            + str(workerlocation.raf.year),
                            "icons": activity.icons if activity else None,
                            "item_number_order": item.number_order,
                            "conf_activities_maintenance": cfg.get(
                                "activities_maintenance", None
                            ),
                        }
                    )

        except Exception as e:
            rst.update(message=str(e))
        else:

            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=quiz.item_set.filter(query).count(),
                collection=data,
            )

        return self.renderer(rst)

    def change_order(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            params = util.request_params(self)

            if not params.get("me", 0) and not params.get("other", 0):
                raise Exception("Não foi possível ordernar os questionários.")

            me = self.get_query().get(pk=params.get("me"))
            other = self.get_query().get(pk=params.get("other"))

            me.swap_order(other)

        except self.Model.DoesNotExist:
            rst.update(message="Questionário não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True, message="Questionários ordenados")

        return self.renderer(rst)

    def get_taxonomyClass(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            quiz = self.get_query().get(id=params.get("quiz"))
            data = []
            taxonomy = quiz.legalclasses
            for c in quiz.legalclasses.all():
                data.append(
                    {
                        "classe_code": nil_unicode(c.cnmp_code, None),
                        "classe_unicode": nul_unicode(c.path_cache, None),
                        "classe_glossary": nil_unicode(c.glossary, None),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=quiz.legalclasses.count(),
                collection=data,
            )
        return self.renderer(rst)

    def get_taxonomyExcludeClass(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            quiz = self.get_query().get(id=params.get("quiz"))
            data = []
            taxonomy = quiz.exclude_classes
            for c in quiz.exclude_classes.all():
                data.append(
                    {
                        "classe_code": nil_unicode(c.cnmp_code, None),
                        "classe_unicode": nul_unicode(c.path_cache, None),
                        "classe_glossary": nil_unicode(c.glossary, None),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=quiz.exclude_classes.count(),
                collection=data,
            )
        return self.renderer(rst)

# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Tag, OutCourtLawsuit
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudTag(Restful):

    _model = Tag

    force_upper = False

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.TagSystemManage")')

    def root(self, args=[]):
        rst = [
            {
                "text": tag.title,
                "leaf": True,
                "type": "bookmark_item",
                "pk": tag.pk,
                "iconCls": "icon-judicial icon-ejud-bookmark",
            }
            for tag in self.get_query()
            .filter(tag_type=2, work_place_id=args[0])
            .order_by("priority", "title")
        ]

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "owner" in params:
            if params.get("owner") != "":
                field = getattr(self.Model, "owner")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(owner=query.get(pk=params.get("owner")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(owner=None)

        if "work_place" in params:
            if params.get("work_place") != "":
                field = getattr(self.Model, "work_place")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(work_place=query.get(pk=params.get("work_place")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(work_place=None)

        return params

    def get_query(self):
        query = super(EJudTag, self).get_query()
        return query.order_by("priority", "title")

    def _build_icon_cls(self, instance):
        return (
            "icon-judicial icon-ejud-procedimento-administrativo-in-grid"
            if instance.slug in ["caixa-da-secretaria", "proc-devolvidos"]
            else ""
        )

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            owner=nil_pk(instance.owner, None),
            owner_unicode=nil_unicode(instance.owner, None),
            work_place=nil_pk(instance.work_place, None),
            work_place_unicode=nil_unicode(instance.work_place, None),
            tag_type=instance.tag_type,
            tag_type_display=nil_display(instance, "tag_type", None),
            slug=instance.slug,
            title=instance.title,
            icon_cls=self._build_icon_cls(instance),
        )

        return rst

    def get_tags_context_location(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        try:
            tags = []
            oidLocation = args[0] if args else 0
            outcourtlawsuit = OutCourtLawsuit.objects.get(
                pk=self.request.GET.get("oidOutCourtLawsuit")
            )
            query = self.Model.objects.filter(work_place_id=oidLocation)

            for tag in query:
                tag_dict = self.model_to_dict(tag)
                check = True if tag in outcourtlawsuit.tags.all() else False
                tag_dict.update(checked=check)
                tags.append(tag_dict)

            rst.update(success=True, message="Dados processados com sucesso", tags=tags)
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

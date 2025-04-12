from contrib.newrest import RestfulDRY
from engine.models import Controller
from django.template.defaultfilters import slugify


class IntranetIconsRestful(RestfulDRY):
    _model = Controller

    full_text_index = (
        "title__icontains",
        "controller__icontains",
        "application__title__icontains",
        "module__icontains",
    )

    def model_to_dict(self, instance):
        params = super().model_to_dict(instance)

        params.update(
            application_active=instance.application.is_active,
            icons=(
                [{"iconCls": "icon-%s" % slugify(instance.icon.replace(".png", ""))}]
                if instance.icon
                else None
            ),
            uuid=instance.uuid,
        )

        return params

    def get_query(self, *args, **kwargs):
        query = super().get_query(*args, **kwargs)

        return query.filter(application=150).order_by("position", "title")

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("web.intranet.icons.Manage")')

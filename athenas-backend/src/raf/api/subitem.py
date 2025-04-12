# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_unicode
from raf.models import SubItem
from . import util

log = getLogger(__name__)


class RAFSubItem(RestfulDRY):

    force_upper = False

    force_orm_single = True

    full_text_index = ("title__icontains",)

    _model = SubItem

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.subitem.Launcher")')

    def model_to_dict(self, instance):
        _dict_ = super(RAFSubItem, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": instance.icons,
                # 'list_taxonomy': u'', #nil_unicode(instance.list_taxonomy, None),
            }
        )

        return _dict_

    def enable(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            sub_item = self.get_query().get(pk=args[0])
            sub_item.activated = not sub_item.activated
            sub_item.save()

        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True)

        return self.renderer(rst)

    def change_order(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            params = util.request_params(self)

            if not params.get("me", 0) and not params.get("other", 0):
                raise Exception("Não foi possível ordernar os itens.")

            me = self.get_query().get(pk=params.get("me"))
            other = self.get_query().get(pk=params.get("other"))

            me.swap_order(other)

        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True, message="Itens ordenados")

        return self.renderer(rst)

    def copy_item(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            sub_item = self.get_query().get(pk=args[0])
            sub_item.copy_me()

        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True)

        return self.renderer(rst)

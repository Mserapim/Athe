# -*- coding: utf-8 -*-

# from django.db import transaction
from django.core.checks import messages
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from web.models import Comment
import json

log = getLogger()


class CommentRestful(RestfulDRY):
    _model = Comment
    force_upper = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_restful("json")

    def delete(self, args=[]):
        obj = {"success": False, "message": ""}

        pk = self.request.GET.get("pk")

        try:
            comment = Comment.objects.get(pk=pk)
            user = get_current_user()
            if comment.user == user or user.has_perms("web.can_disable_comment"):
                comment.active = False
                comment.save()
                obj.update(success=True, message="Processado com sucesso!")
            else:
                obj.update(
                    message="O usuário não possui permissão para excluir esse comentário."
                )

        except Comment.DoesNotExist as e:
            log.exception(e)
            obj.update(message="O comentário não existe.")

        except Exception as e:
            log.exception(e)
            obj.updade(message="Não foi possível excluir o comentário.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_query(self):

        qs = super(CommentRestful, self).get_query()

        return qs.filter(active=True)

    def model_to_dict(self, obj):
        m2d = super(CommentRestful, self).model_to_dict(obj)

        m2d["username"] = obj.user.username if getattr(obj, "user", None) else ""

        return m2d

# -*- coding: utf-8 -*-
from app.settings import AUTO_PERMISSIONS_FUNCS
from contrib.newrest import Restful, RestfulDRY
from contrib.controller import CommandController
from engine import models as engine_models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from contrib.utils import getLogger, get_json_engine
from contrib.middleware import get_current_user
from contrib.decorator import update_timeout_session
from django.conf import settings

# import random
# import hashlib
import datetime

json = get_json_engine()

log = getLogger(__name__)


class ENGControllerRestful(RestfulDRY):

    _model = engine_models.Controller

    force_upper = False

    full_text_index = (
        "title__icontains",
        "controller__icontains",
        "application__title__icontains",
        "module__icontains",
    )

    # def get_params(self, querydict=None, **kargs):
    #     params = super(ENGControllerRestful, self).get_params(
    #         querydict, **kargs
    #     )

    #     if 'application' in params:
    #         try:
    #             application = engine_models.Application.objects.get(
    #                 pk=params.get('application')
    #             )
    #         except engine_models.Application.DoesNotExist:
    #             application = None
    #         finally:
    #             params.update(
    #                 application=application
    #             )

    #     return params

    def model_to_dict(self, instance):
        params = super(ENGControllerRestful, self).model_to_dict(instance)

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

    def installeds(self, args=[]):
        obj = {"success": False}

        obj = {
            "success": True,
            "count": len(settings.INSTALLED_APPS),
            "collection": [
                {
                    "module": m,
                }
                for m in sorted(settings.INSTALLED_APPS)
            ],
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class ENGControllerPermissionRestful(RestfulDRY):

    _model = engine_models.ControllerPermission

    full_text_index = (
        "name__icontains",
        # 'users__username__icontains',
        # 'controllers__controller__icontains',
        # 'controllers__title__icontains',
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("engine.ControllerPermissionManage", {autoPermissionsFuncs: "%s"})'
            % (AUTO_PERMISSIONS_FUNCS)
        )

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            name=instance.name,
            is_default=instance.is_default,
            manager_permission=instance.manager_permission,
        )

        return params

    def get_params(self, querydict=None, **kargs):
        params = super(ENGControllerPermissionRestful, self).get_params(
            querydict, **kargs
        )

        log.debug(params)

        if "controllers" in params:
            rst = []

            for controller_id in self.get_item_as_list(params, "controllers"):
                try:
                    controller = engine_models.Controller.objects.get(pk=controller_id)
                except Exception as e:
                    log.exception(e)
                    controller = None
                else:
                    rst.append(controller)

            params.update(controllers=rst)

        if "users" in params:
            rst = []

            for user_id in self.get_item_as_list(params, "users"):
                try:
                    user = User.objects.get(pk=user_id)
                except Exception as e:
                    log.exception(e)
                    user = None
                else:
                    rst.append(user)

            params.update(users=rst)

        log.debug(params)

        return params


class CommandControllerTask(CommandController, RestfulDRY):
    """ """

    _model = engine_models.TaskSession

    exclude_fields = ["params_cache"]

    _description = "Sem descrição"

    def getTask(self, sid=None):
        sid = sid or self.request.POST.get("sid") or self.request.GET.get("sid")
        # log.debug(self.request)
        return engine_models.TaskSession.objects.get(sid=sid)

    def __contains__(self, key):
        try:
            task = self.getTask(
                self.request.POST.get("sid") or self.request.GET.get("sid")
            )
            return key in task
        except engine_models.TaskSession.DoesNotExist:
            return False

    def createSessionId(self, args=[]):
        obj = {}
        # random.seed(os.urandom(10))
        # magic = random.randint(0, 999999999)
        # h = hashlib.new('md5')
        # h.update(str(magic))

        # obj.update(sid=h.hexdigest())
        task = engine_models.TaskSession()
        task.description = self._description
        task.save()

        for k in self.request.POST:
            if isinstance(self.request.POST.getlist(k), (list, tuple)):
                obj[k] = self.request.POST.get(k)
            else:
                obj[k] = self.request.POST.getlist(k)

        task.update(**obj)
        task.save()

        obj = task.params
        obj.update(self.model_to_dict(task))

        self.log.debug("CREATESESSIONID %s" % task.sid)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def getSessionInformation(self, args=[]):
        log.debug("GETSESSIONINFORMATION SID: %s" % self.request.POST.get("sid"))
        task = self.getTask(self.request.POST.get("sid"))

        obj = task.params
        obj.update(self.model_to_dict(task))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def getMessages(self, args=[]):
        task = self.getTask()
        obj = {"root": []}

        for msg in task.messages.all():
            obj.get("root").append(
                {
                    "pk": msg.pk,
                    "description": msg.message,
                    "link": (
                        msg.file_ged.permalink()
                        if msg.type_of == 4 and msg.file_ged
                        else ""
                    ),
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def getSessionFilename(self, sid):
        return ""

    def get(self, key, sid=None):
        sid = sid if sid is not None else self.request.POST.get("sid")
        task = self.getTask(sid)
        return task[key]

    def set(self, key, value, sid=None):
        try:
            sid = sid if sid is not None else self.request.POST.get("sid")
            task = self.getTask(sid)
            task.update(**{key: value})

        except Exception as e:
            self.log.exception(e)

    def send_message(self, msg, sid=None):
        sid = sid if sid is not None else self.request.POST.get("sid")
        task = self.getTask(sid)
        task.info(msg)

    def model_to_dict(self, instance):
        _dict_ = super(CommandControllerTask, self).model_to_dict(instance)
        # log.debug('%s PARAMS %s' % (instance.sid, instance.params))
        _dict_.update(instance.params)
        if instance.messages.exists():
            _dict_.update(
                **{
                    "has_messages": instance.messages.exists(),
                    "has_files": instance.messages.filter(type_of=4).exists(),
                    "msg": instance.messages.filter(type_of__in=[1, 2, 3])
                    .order_by("-id")[0]
                    .message,
                }
            )

        return _dict_

    def update(self, **kargs):
        sid = self.request.POST.get("sid")
        task = self.getTask(sid)
        task.update(**kargs)

    def destroySession(self, args=[]):
        obj = {"success": True}

        task = self.getTask()
        self.log.debug("DESTROYSESSION %s" % task.sid)
        task.finished_task = datetime.datetime.now()
        task.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class CommandControllerTaskViewer(CommandControllerTask):

    @update_timeout_session(False)
    def v1(self, args):
        super(CommandControllerTaskViewer, self).v1(args)

    def get_query(self):
        log.info("user authenticated: %s", self.request.user.is_authenticated)

        return (
            super(CommandControllerTaskViewer, self)
            .get_query()
            .filter(
                visualized=False,
                user=self.request.user if self.request.user.is_authenticated else 0,
            )
        )


class ENGTaskSessionRestful(RestfulDRY):
    _model = engine_models.TaskSession

    force_upper = False

    full_text_index = (
        "sid__iexact",
        "description__icontains",
        "user__username__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("engine.TaskSessionManage")')


class ENGTaskMessageRestful(RestfulDRY):
    _model = engine_models.TaskMessages

    force_upper = False

    full_text_index = (
        "session__sid__iexact",
        "message__icontains",
    )

    def model_to_dict(self, instance):
        params = super(ENGTaskMessageRestful, self).model_to_dict(instance)

        params.update(
            icons=[
                {
                    "iconCls": "icon-core icon-core-%s"
                    % instance.get_type_of_display().lower(),
                    "title": instance.get_type_of_display(),
                },
            ],
            file_ged_permalink=(
                instance.file_ged.permalink() if instance.file_ged else ""
            ),
        )

        return params

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("engine.TaskMessageManage")')

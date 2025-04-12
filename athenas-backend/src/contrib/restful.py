# -*- coding: utf-8 -*-
from contrib.controller import DefaultController
from contrib.utils import get_json_engine, getLogger
from django.db.models import ManyToManyField

json = get_json_engine()
log = getLogger(__name__)


class Restful(DefaultController):

    model = None

    def doDelete(self, **kargs):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            if "pk" in self.request.POST:
                self.model.objects.filter(pk=self.request.POST.get("pk")).delete()
            elif "pks" in self.request.POST:
                self.model.objects.filter(
                    pk__in=self.request.POST.getlist("pks")
                ).delete()
        except Exception as e:
            obj = {"success": False, "message": str(e)}
        else:
            obj.update(success=True)

        return obj

    def doPut(self, **kargs):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            n = self.model.objects.get(pk=self.request.POST.get("pk"))
            del kargs["pk"]

            for k in list(kargs.keys()):
                field, model, direct, m2m = self.model._meta.get_field_by_name(k)

                if m2m is False:
                    setattr(n, k, kargs.get(k))
                else:
                    getattr(n, k).clear()
                    if isinstance(kargs.get(k), (list, tuple)):
                        self.log.debug("mult")
                        for v in kargs.get(k):
                            getattr(n, k).add(v)
                    else:
                        self.log.debug("single")
                        getattr(n, k).add(kargs.get(k))
            n.save()
        except Exception as e:
            obj = {"success": False, "message": str(e)}
            self.log.exception(e)
        else:
            obj.update(success=True)

        return obj

    def doPost(self, **kargs):
        obj = {}

        if "pk" in list(kargs.keys()) and kargs.get("pk") in (None, ""):
            del kargs["pk"]

        try:
            if "pk" in list(kargs.keys()):
                try:
                    n = self.model.objects.get(pk=kargs.get("pk"))
                except self.model.DoesNotExit:
                    n = self.model()
                finally:
                    del kargs["pk"]
            else:
                n = self.model()

            for k in list(kargs.keys()):
                # self.log.debug('%s -> %s (%s)' % (k, kargs.get(k), type(kargs.get(k))))
                try:
                    if not isinstance(n._meta.get_field(k), ManyToManyField):
                        # self.log.debug('%s -> %s (%s)' % (k, kargs.get(k), type(kargs.get(k))))
                        setattr(n, k, kargs.get(k))
                except Exception as e:
                    self.log.exception(e)

            n.save()

            for k in list(kargs.keys()):
                if isinstance(n._meta.get_field(k), ManyToManyField):
                    if isinstance(kargs.get(k), (list, tuple)):
                        for v in kargs.get(k):
                            getattr(n, k).add(v)
                    else:
                        getattr(n, k).add(kargs.get(k))

        except Exception as e:
            obj = {"success": False, "message": "%s" % e}
            self.log.debug(kargs)
            self.log.exception(e)
        else:
            obj = {"success": True, "pk": n.pk, "description": str(n)}

        return obj

    def get_values(self, e):
        obj = {"pk": e.pk, "description": str(e)}

        for field in self.model._meta.get_fields():
            value = ""
            fieldobj = getattr(e, field.name, None)

            if hasattr(fieldobj, "pk"):
                value = fieldobj.pk
            else:
                value = str(fieldobj)

            obj.update({field.name: value})

        return obj

    def doGet(self, **kargs):
        """ """
        obj = {}
        f = kargs.get("filter", self.model.objects.all())

        if "pk" not in list(kargs.keys()):
            obj = {"totalRows": f.count(), "root": [self.get_values(r) for r in f]}
            return obj
        else:
            try:
                obj = f.objects.get(pk=kargs.get("pk"))
            except f.DoesNotExist:
                obj = {"pk": None, "description": None}
            finally:
                return obj

    def to_dict(self, qdict):
        d = {}

        for k in qdict:
            value = qdict.getlist(k)
            d[k] = value if len(value) > 1 else value[0]

        return d

    def index(self, args=[]):
        obj = None

        if self.request.META.get("HTTP_RESTFUL_METHOD") in ("PUT", "put"):
            obj = self.doPut(**self.to_dict(self.request.POST))
        elif self.request.META.get("HTTP_RESTFUL_METHOD") in ("DELETE", "delete"):
            obj = self.doDelete(**self.to_dict(self.request.POST))
        elif self.request.method in ("GET", "get"):
            obj = self.doGet(**self.to_dict(self.request.GET))
        elif self.request.method in ("POST", "post"):
            obj = self.doPost(**self.to_dict(self.request.POST))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def do(self, args=[]):
        self.index(args)

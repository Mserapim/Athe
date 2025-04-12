# -.- coding: utf-8 -.-
from django.db import models


class Processo(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    numero = models.IntegerField()
    titulo = models.CharField(max_length=100)
    # Parametro "on_delete" adicionado. (Django 2)
    interessado = models.ForeignKey("rh.Servidor", on_delete=models.CASCADE)
    descricao = models.TextField()
    # Parametro "on_delete" adicionado. (Django 2)
    excluido_por = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.CASCADE
    )
    numero_cache = models.CharField(max_length=16, unique=True, null=True, blank=True)

    _types = [
        {
            "attribute": None,
            "icon": "static/adm/images/processo.png",
            "type": "processo",
            "controller": "toolkit.adm.eproc.Processo",
        },
    ]

    def __str__(self):
        return self.numero_cache

    @staticmethod
    def register_type(type_, icon=None, controller="EPProcesso"):
        def decorator(cls):
            attribute = cls._meta.object_name.lower()
            if attribute is None or type_ is None:
                raise Exception(
                    "Não posso registrar um tipo de processo sem o seu identificador."
                )
            if True not in [t["attribute"] == attribute for t in Processo._types]:
                Processo._types.append(
                    {
                        "type": type_,
                        "icon": icon,
                        "controller": controller,
                        "attribute": attribute,
                        "class": cls,
                    }
                )
            #            else:
            #                raise Exception('O tipo %s de processo ja foi utilizado.' % type_)
            return cls

        return decorator

    def save(self, force_insert=False, force_update=False):
        self.numero_cache = "%(ano)d.0701.%(numero)06d" % {
            "ano": self.dt.year,
            "numero": int(self.numero),
        }

        models.Model.save(self, force_insert, force_update)

    def get_type(self):
        for t in self._types:
            if t.get("attribute", None) is not None and hasattr(
                self, t.get("attribute")
            ):
                return t.get("type", None)
        return "processo"

    def get_controller(self):
        for t in self._types:
            if t.get("attribute", None) is not None and hasattr(
                self, t.get("attribute")
            ):
                return t["controller"]
        return self._types[0]["controller"]

    def get_type_information(self):
        for t in self._types:
            if t.get("attribute", None) is not None and hasattr(
                self, t.get("attribute")
            ):
                obj = getattr(self, t.get("attribute"))
                if hasattr(obj, "get_type_information"):
                    r = obj.get_type_information()
                    r.insert(
                        0,
                        {"icon": t.get("icon"), "alt": "Processo", "title": "Processo"},
                    )
                    return r
                else:
                    return (
                        {"icon": t.get("icon"), "alt": "Processo", "title": "Processo"},
                    )
        return (
            {
                "icon": self._types[0].get("icon"),
                "alt": "Processo",
                "title": "Processo",
            },
        )


class Pagina(models.Model):
    numero = models.IntegerField(blank=True)
    # Parametro "on_delete" adicionado. (Django 2)
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False):
        if self.numero is None:
            self.numero = 0
        else:
            self.numero = self.numero + 1
        super(Pagina, self).save(force_insert, force_update)

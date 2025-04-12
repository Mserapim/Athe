# -*- coding: utf-8 -*-
from adm.patrimonio.models import Especie, GrupoEspecie
from contrib.newrest import Restful


class PATEspecie(Restful):

    _model = Especie

    full_text_index = (
        "codigo__icontains",
        "codigo_cache__icontains",
        "titulo__icontains",
    )

    def has_perm_admin(self):
        current_user = self.request.user.servidor
        return (
            True if current_user.user.has_perm("patrimonio.mov_grupoespecie") else False
        )

    def movimentar_grupo(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            if self.has_perm_admin():
                pks = self.request.POST.get("pks")
                grupo = GrupoEspecie.objects.get(pk=self.request.POST.get("grupo"))
                for especie in self._model.objects.filter(pk__in=pks.split(",")):
                    especie.grupo = grupo
                    especie.save()
                rst.update(success=True, message="Procedimento realizado com sucesso.")
            else:
                rst.update(
                    success=False,
                    message="Você não tem permissão para realizar essa operação!",
                )
        except Exception as e:
            rst.update(message=str(e))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "titulo": instance.titulo,
                "codigo": instance.codigo,
                "codigo_cache": instance.codigo_cache,
                "status": instance.status,
            }
        )
        return _dict_

    def get_params(self, querydict=None, **kargs):
        _dict_ = super(PATEspecie, self).get_params(querydict, **kargs)

        if "grupo" in _dict_:
            _dict_.update(grupo=GrupoEspecie.objects.get(pk=_dict_.get("grupo", 0)))

        return _dict_

# -*- coding: utf-8 -*-
from adm.patrimonio.models import GrupoContabil, GrupoEspecie
from contrib.newrest import Restful


class PATGrupoEspecie(Restful):

    _model = GrupoEspecie

    full_text_index = (
        "codigo__icontains",
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
                grupo_contabil = GrupoContabil.objects.get(
                    pk=self.request.POST.get("grupo")
                )
                for grupo_especie in self._model.objects.filter(pk__in=pks.split(",")):
                    grupo_especie.grupo_contabil = grupo_contabil
                    grupo_especie.save()
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

    def get_params(self, querydict=None, **kargs):
        _dict_ = super(PATGrupoEspecie, self).get_params(querydict, **kargs)

        if "grupo_contabil" in _dict_:
            _dict_.update(
                grupo_contabil=GrupoContabil.objects.get(
                    pk=_dict_.get("grupo_contabil", 0)
                )
            )

        return _dict_

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update({"titulo": instance.titulo, "codigo": instance.codigo})
        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("adm.patrimonio.parametro.GrupoEspecieManage")'
        )

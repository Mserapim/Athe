from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from contrib.mastiff import get_permission

EDIT_METHODS = ("PUT", "PATCH")


class IsPermissionVDF(BasePermission):
    """
    Permissões do Vida Funcional
    """

    app = "VDF"

    def has_permission(self, request, view):
        return True
        # content = get_permission(request,self.app)
        # if request.method in SAFE_METHODS:
        #     return 'vdf-permissao-basico' in content.get('permissoes',[])
        # if request.method in EDIT_METHODS:
        #     return 'vdf-permissao-editor' in content.get('permissoes',[])
        # if request.method in ['POST','DELETE']:
        #     return 'vdf-permissao-editor' in content.get('permissoes',[])
        # return False

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import Http404


class RolePermissionMixin:
    def get_user_role(self, request):
        if not hasattr(request.user, 'userprofile'):
            return None
        return request.user.userprofile.grupo_extra

    def has_coordenador_subevento_access(self, request, obj=None):
        role = self.get_user_role(request)
        if role != 'COORD':
            return False
        
        if obj is None:
            return True
        
        if hasattr(obj, 'subevento'):
            return obj.subevento in request.user.userprofile.ligas.all()
        elif hasattr(obj, 'evento'):
            user_ligas = request.user.userprofile.ligas.all()
            return user_ligas.filter(evento=obj.evento).exists()
        
        return False

    def has_representante_local_access(self, request, obj=None):
        role = self.get_user_role(request)
        if role != 'REPRESENTANTE':
            return False
        
        user_estado = request.user.userprofile.estado
        if not user_estado:
            return False
        
        if obj is None:
            return True
        
        if hasattr(obj, 'estado'):
            return obj.estado == user_estado
        
        return False

    def has_marketing_access(self, request, obj=None):
        role = self.get_user_role(request)
        return role == 'MARKETING'

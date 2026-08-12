from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import UserRole


def admin_required(view_func):
    """Только для администраторов"""
    def wrapper(request, *args, **kwargs):
        role = UserRole.objects.filter(user=request.user).first()
        if not role or not role.is_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    """Для администраторов и менеджеров"""
    def wrapper(request, *args, **kwargs):
        role = UserRole.objects.filter(user=request.user).first()
        if not role or not role.is_manager:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
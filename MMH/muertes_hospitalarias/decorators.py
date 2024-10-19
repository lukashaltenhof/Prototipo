from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    perfil = request.user.perfilusuario  # Obtener el perfil del usuario logueado
                    if perfil.rol in allowed_roles:
                        return view_func(request, *args, **kwargs)
                    else:
                        raise PermissionDenied  # Denegar acceso si el rol no es permitido
                except AttributeError:
                    raise PermissionDenied  # Si el usuario no tiene perfil asociado
            return redirect('login')  # Redirigir al login si no está autenticado
        return _wrapped_view
    return decorator

from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, reverse, Resolver404

EXEMPT_URLS = {
    'welcome',
    'register',
    'login',
    'logout',
    'logged_out',
    'about',

    'password_reset',
    'password_reset_done',
    'password_reset_complete',

    'admin:index',
}

def _is_exempt(resolver_match) -> bool:
    if not resolver_match:
        return False
    url_name = resolver_match.url_name
    namespace = resolver_match.namespace
    full_name = f'{namespace}:{url_name}' if namespace else url_name
    return (url_name in EXEMPT_URLS) or (full_name in EXEMPT_URLS)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        if request.user.is_authenticated or _is_exempt(match):
            return self.get_response(request)

        if request.path.startswith('/admin/login'):
            return self.get_response(request)

        return redirect(reverse('welcome'))


class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        if (not request.user.is_authenticated) or _is_exempt(match):
            return self.get_response(request)

        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        url_name = match.url_name
        namespace = match.namespace
        role = getattr(request.user, 'role', 'user')

        if role == 'admin':
            return self.get_response(request)

        if role == 'guest':
            allowed = {'welcome', 'about', 'logout', 'logged_out'}
            full_name = f'{namespace}:{url_name}' if namespace else url_name
            if (url_name in allowed) or (full_name in allowed):
                return self.get_response(request)
            return redirect(reverse('welcome'))

        if role == 'user':
            if namespace == 'users' or url_name == 'users':
                return redirect(reverse('welcome'))
            return self.get_response(request)

        return redirect(reverse('welcome'))


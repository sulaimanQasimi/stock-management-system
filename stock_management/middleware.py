from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

from .tenancy import (
    TENANT_SESSION_KEY,
    get_current_database,
    reset_current_database,
    set_current_database,
    validate_tenant_database,
)


class TenantDatabaseMiddleware:
    EXEMPT_PATHS = {
        '/login/',
        '/admin/login/',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        selected_database = request.session.get(
            TENANT_SESSION_KEY,
            getattr(settings, 'DEFAULT_TENANT_DATABASE', 'default'),
        )

        token = set_current_database(selected_database)

        request.tenant_database = selected_database

        try:
            if request.path not in self.EXEMPT_PATHS:
                validate_tenant_database(selected_database)

            response = self.get_response(request)
            return response
        finally:
            reset_current_database(token)


class TenantSessionProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_database = request.session.get(TENANT_SESSION_KEY)

        if request.user.is_authenticated:
            current_database = get_current_database()

            if session_database and session_database != current_database:
                logout(request)
                return redirect('/login/')

        return self.get_response(request)

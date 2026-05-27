from __future__ import annotations

from contextvars import ContextVar
from typing import Iterable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

TENANT_SESSION_KEY = 'selected_database'

_current_database: ContextVar[str | None] = ContextVar('current_database', default=None)


def get_current_database() -> str:
    return _current_database.get() or getattr(settings, 'DEFAULT_TENANT_DATABASE', 'default')


def set_current_database(alias: str | None):
    return _current_database.set(alias)


def reset_current_database(token) -> None:
    _current_database.reset(token)


def get_tenant_database_aliases() -> list[str]:
    configured = getattr(settings, 'TENANT_DATABASE_ALIASES', None)
    if configured:
        return list(configured)
    return ['default']


def get_tenant_database_choices() -> list[dict[str, str]]:
    labels = getattr(settings, 'TENANT_DATABASE_LABELS', {})
    return [
        {'value': alias, 'label': labels.get(alias, alias.replace('_', ' ').title())}
        for alias in get_tenant_database_aliases()
    ]


def validate_tenant_database(alias: str | None) -> str:
    if not alias:
        raise PermissionDenied('Please select a company database.')

    allowed = get_tenant_database_aliases()
    if alias not in allowed:
        raise PermissionDenied('Invalid company database selected.')

    if alias not in settings.DATABASES:
        raise ImproperlyConfigured(f'Database alias "{alias}" is not configured.')

    return alias


def user_database_from_request(request) -> str | None:
    return request.session.get(TENANT_SESSION_KEY)

from django.middleware.csrf import get_token
from inertia import render


def render_inertia(request, component, props=None, status=200, template_data=None):
    """Compatibility wrapper around inertia-django's render().

    Existing views in this project call render_inertia(request, component, props, status).
    The actual Inertia response is now produced by inertia-django, which handles
    Inertia headers, JSON responses, layout rendering, and prop serialization.
    """
    props = props or {}
    props.setdefault('csrfToken', get_token(request))

    response = render(
        request,
        component,
        props=props,
        template_data=template_data,
    )
    response.status_code = status
    return response

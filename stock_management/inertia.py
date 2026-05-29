import json

from django.shortcuts import render


def render_inertia(request, component, props=None, status=200):
    """Render an Inertia page payload for the React frontend."""
    props = props or {}
    return render(
        request,
        'app.html',
        {
            'page': {
                'component': component,
                'props': props,
                'url': request.get_full_path(),
                'version': None,
            },
            'page_json': json.dumps({
                'component': component,
                'props': props,
                'url': request.get_full_path(),
                'version': None,
            }),
        },
        status=status,
    )

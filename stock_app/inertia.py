import json

from django.http import JsonResponse
from django.shortcuts import render


def inertia(request, component, props=None, template='startup/app.html'):
    page = {
        'component': component,
        'props': props or {},
        'url': request.get_full_path(),
        'version': None,
    }

    if request.headers.get('X-Inertia'):
        response = JsonResponse(page)
        response['X-Inertia'] = 'true'
        return response

    return render(request, template, {'page': json.dumps(page)})

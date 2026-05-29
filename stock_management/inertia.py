import json

from django.conf import settings
from django.shortcuts import render


def _vite_assets():
    manifest_path = settings.BASE_DIR / 'frontend' / 'dist' / '.vite' / 'manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text())
    except FileNotFoundError:
        return {
            'js': 'assets/index.js',
            'css': ['assets/index.css'],
        }

    entry = manifest.get('index.html') or manifest.get('src/main.jsx') or next(iter(manifest.values()), {})
    return {
        'js': entry.get('file', 'assets/index.js'),
        'css': entry.get('css', ['assets/index.css']),
    }


def render_inertia(request, component, props=None, status=200):
    """Render an Inertia page payload for the React frontend."""
    props = props or {}
    page = {
        'component': component,
        'props': props,
        'url': request.get_full_path(),
        'version': None,
    }
    return render(
        request,
        'app.html',
        {
            'page': page,
            'page_json': json.dumps(page),
            'vite_assets': _vite_assets(),
        },
        status=status,
    )

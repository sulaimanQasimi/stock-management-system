import json

from django.conf import settings
from django.middleware.csrf import get_token
from django.shortcuts import render


def _vite_assets():
    dist_dir = settings.BASE_DIR / 'frontend' / 'dist'
    manifest_path = dist_dir / '.vite' / 'manifest.json'

    try:
        manifest = json.loads(manifest_path.read_text())
        entry = manifest.get('index.html') or manifest.get('src/main.jsx') or next(iter(manifest.values()), {})
        return {
            'js': entry.get('file'),
            'css': entry.get('css', []),
        }
    except FileNotFoundError:
        pass

    js_files = sorted(dist_dir.glob('assets/*.js'))
    css_files = sorted(dist_dir.glob('assets/*.css'))
    return {
        'js': js_files[0].relative_to(dist_dir).as_posix() if js_files else None,
        'css': [path.relative_to(dist_dir).as_posix() for path in css_files],
    }


def render_inertia(request, component, props=None, status=200):
    """Render an Inertia page payload for the React frontend."""
    props = props or {}
    props.setdefault('csrfToken', get_token(request))
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

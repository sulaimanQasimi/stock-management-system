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
        js_file = entry.get('file')
        css_files = entry.get('css', [])
    except FileNotFoundError:
        js_files = sorted(dist_dir.glob('assets/*.js'))
        css_paths = sorted(dist_dir.glob('assets/*.css'))
        js_file = js_files[0].relative_to(dist_dir).as_posix() if js_files else None
        css_files = [path.relative_to(dist_dir).as_posix() for path in css_paths]

    js_content = None
    if js_file:
        try:
            js_content = (dist_dir / js_file).read_text()
        except FileNotFoundError:
            js_content = None

    return {
        'js': js_file,
        'js_content': js_content,
        'css': css_files,
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

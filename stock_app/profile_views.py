from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from stock_management.inertia import render_inertia
from .views import _auth

User = get_user_model()


def _profile_payload(request, errors=None, status_message=''):
    user = request.user
    return {
        'auth': _auth(request),
        'profile': {
            'id': user.id,
            'username': user.get_username(),
            'email': user.email or '',
            'firstName': user.first_name or '',
            'lastName': user.last_name or '',
            'fullName': user.get_full_name(),
            'isActive': user.is_active,
            'isStaff': user.is_staff,
            'isSuperuser': user.is_superuser,
            'lastLogin': user.last_login.isoformat() if user.last_login else None,
            'dateJoined': user.date_joined.isoformat() if getattr(user, 'date_joined', None) else None,
        },
        'errors': errors or {},
        'status': status_message,
    }


@login_required
@require_http_methods(['GET', 'POST'])
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'profile')
        errors = {}
        user = request.user

        if action == 'profile':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()

            if not username:
                errors['username'] = ['Username is required.']
            elif User.objects.filter(username=username).exclude(pk=user.pk).exists():
                errors['username'] = ['This username is already taken.']

            if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
                errors['email'] = ['This email is already used by another account.']

            if errors:
                return render_inertia(request, 'Profile', _profile_payload(request, errors), status=422)

            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=['username', 'email', 'first_name', 'last_name'])
            return render_inertia(request, 'Profile', _profile_payload(request, status_message='Profile updated successfully.'))

        if action == 'password':
            current_password = request.POST.get('current_password', '')
            password = request.POST.get('password', '')
            password_confirmation = request.POST.get('password_confirmation', '')

            if not user.check_password(current_password):
                errors['current_password'] = ['Current password is incorrect.']

            if not password:
                errors['password'] = ['New password is required.']
            elif password != password_confirmation:
                errors['password_confirmation'] = ['Password confirmation does not match.']
            else:
                try:
                    validate_password(password, user)
                except ValidationError as exc:
                    errors['password'] = list(exc.messages)

            if errors:
                return render_inertia(request, 'Profile', _profile_payload(request, errors), status=422)

            user.set_password(password)
            user.save(update_fields=['password'])
            update_session_auth_hash(request, user)
            return render_inertia(request, 'Profile', _profile_payload(request, status_message='Password changed successfully.'))

        errors['action'] = ['Invalid profile action.']
        return render_inertia(request, 'Profile', _profile_payload(request, errors), status=422)

    return render_inertia(request, 'Profile', _profile_payload(request))

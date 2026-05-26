from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render_inertia

from .models import Sale, SaleServiceItem, Service


def _auth(request):
    return {'user': {'username': request.user.get_username(), 'email': request.user.email}}


def _can(user, action, model):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    model_name = model._meta.model_name
    django_action = {'create': 'add', 'edit': 'change'}.get(action, action)
    app_label = model._meta.app_label
    return (
        user.has_perm(f'{app_label}.{action}_{model_name}')
        or user.has_perm(f'{app_label}.{action}_all_{model_name}')
        or user.has_perm(f'{app_label}.{action}_own_{model_name}')
        or user.has_perm(f'{app_label}.{django_action}_{model_name}')
    )


def _sales_options(user):
    return [{'value': sale.id, 'label': sale.sale_number} for sale in Sale.objects.for_user(user).order_by('-date', '-id')[:200]]


def _service_options(user):
    return [{'value': service.id, 'label': f'{service.name} — {service.price}', 'price': str(service.price)} for service in Service.objects.for_user(user).filter(is_active=True).order_by('name')[:500]]


@login_required
@require_http_methods(['GET', 'POST'])
def services_index(request):
    if request.method == 'POST' and _can(request.user, 'create', Service):
        service = Service(
            name=request.POST.get('name', '').strip(),
            price=request.POST.get('price') or 0,
            description=request.POST.get('description', '').strip(),
            is_active=request.POST.get('is_active', 'on') == 'on',
        )
        service.set_created_user(request.user)
        service.set_updated_user(request.user)
        service.save()
        return redirect('services.index')
    services = Service.objects.for_user(request.user).order_by('name')[:500]
    return render_inertia(request, 'Services', {
        'auth': _auth(request),
        'services': list(services.values('id', 'name', 'price', 'description', 'is_active')),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def sale_service_items_index(request):
    if request.method == 'POST' and _can(request.user, 'create', SaleServiceItem):
        item = SaleServiceItem(
            sale_id=request.POST.get('sale'),
            service_id=request.POST.get('service'),
            quantity=request.POST.get('quantity') or 1,
            unit_price=request.POST.get('unit_price') or 0,
            note=request.POST.get('note', '').strip(),
        )
        item.set_created_user(request.user)
        item.set_updated_user(request.user)
        item.save()
        return redirect('sale-service-items.index')
    items = SaleServiceItem.objects.for_user(request.user).select_related('sale', 'service').order_by('-id')[:500]
    return render_inertia(request, 'SaleServiceItems', {
        'auth': _auth(request),
        'saleServiceItems': [
            {'id': item.id, 'sale': item.sale.sale_number, 'service': item.service.name, 'quantity': str(item.quantity), 'unit_price': str(item.unit_price), 'total': str(item.total), 'note': item.note}
            for item in items
        ],
        'options': {'sales': _sales_options(request.user), 'services': _service_options(request.user)},
    })

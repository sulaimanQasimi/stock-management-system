from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render_inertia

from finance.models import Account, Currency, Expense, ExpenseType, Transaction
from stock_management.i18n import get_language_payload
from stock_management.tenancy import TENANT_SESSION_KEY, get_tenant_database_choices, set_current_database, validate_tenant_database
from .forms import DepartmentForm, StockMovementForm
from .models import Category, Department, Party, Product, PurchaseBatch, PurchaseItem, PurchasePayment, Sale, SaleItem, SalePayment, StockMovement, StockProfitReport, Unit
from .models import ProductReorderRule, ApprovalRequest, BusinessDocument, PartyLedgerEntry, ReturnRecord, StockAdjustmentReason, StockCountSession, ProductBatchTracking, CostingConfiguration, AdvancedReportRequest, ExportJob

User = get_user_model()


def _rows(queryset, *fields):
    return list(queryset.values(*fields))


def _options(queryset, label_field='name'):
    return [{'value': row.id, 'label': str(getattr(row, label_field, row))} for row in queryset]


def _can(user, action, model_or_name, app_label='stock_app'):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    model_name = model_or_name if isinstance(model_or_name, str) else model_or_name._meta.model_name
    django_action = {'create': 'add', 'edit': 'change'}.get(action, action)
    return (user.has_perm(f'{app_label}.{action}_{model_name}') or user.has_perm(f'{app_label}.{action}_all_{model_name}') or user.has_perm(f'{app_label}.{action}_own_{model_name}') or user.has_perm(f'{app_label}.{django_action}_{model_name}'))


def _require(user, action, model_or_name, app_label='stock_app'):
    if not _can(user, action, model_or_name, app_label):
        raise PermissionDenied


def _common_options(user, keys=()):
    data = {}
    if 'categories' in keys and _can(user, 'view', Category): data['categories'] = _options(Category.objects.for_user(user).order_by('name'))
    if 'units' in keys and _can(user, 'view', Unit): data['units'] = _options(Unit.objects.for_user(user).order_by('name'))
    if 'parties' in keys and _can(user, 'view', Party): data['parties'] = _options(Party.objects.for_user(user).order_by('name'))
    if 'products' in keys and _can(user, 'view', Product): data['products'] = [{'value': row.id, 'label': row.name, 'quantity': str(row.quantity)} for row in Product.objects.for_user(user).order_by('name')[:500]]
    if 'departments' in keys and _can(user, 'view', Department): data['departments'] = _options(Department.objects.for_user(user).order_by('name'))
    if 'currencies' in keys and _can(user, 'view', 'currency', 'finance'): data['currencies'] = _options(Currency.objects.for_user(user).order_by('code'), 'code')
    if 'accounts' in keys and _can(user, 'view', 'account', 'finance'): data['accounts'] = _options(Account.objects.for_user(user).order_by('code'), 'name')
    if 'transactions' in keys and _can(user, 'view', 'transaction', 'finance'): data['transactions'] = [{'value': item.id, 'label': str(item)} for item in Transaction.objects.for_user(user).order_by('-created_at')[:100]]
    if 'purchaseBatches' in keys and _can(user, 'view', PurchaseBatch): data['purchaseBatches'] = _options(PurchaseBatch.objects.for_user(user).order_by('-date', '-id')[:200], 'batch_number')
    if 'purchaseItems' in keys and _can(user, 'view', PurchaseItem): data['purchaseItems'] = [{'value': item.id, 'label': str(item)} for item in PurchaseItem.objects.for_user(user).select_related('product').order_by('-id')[:500]]
    if 'sales' in keys and _can(user, 'view', Sale): data['sales'] = _options(Sale.objects.for_user(user).order_by('-date', '-id')[:200], 'sale_number')
    if 'expenseTypes' in keys and _can(user, 'view', 'expensetype', 'finance'): data['expenseTypes'] = _options(ExpenseType.objects.for_user(user).order_by('name'))
    return data


def _auth(request):
    return {
        'user': {'username': request.user.get_username(), 'email': request.user.email},
        'database': getattr(request, 'tenant_database', 'default'),
        'i18n': get_language_payload(request),
    }


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    databases = get_tenant_database_choices()

    if request.method == 'POST':
        database = request.POST.get('database')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        validate_tenant_database(database)

        request.session[TENANT_SESSION_KEY] = database
        request.tenant_database = database

        token = set_current_database(database)

        try:
            user = authenticate(request, username=username, password=password)
        finally:
            pass

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render_inertia(request, 'Login', {
            'databases': databases,
            'error': 'Invalid username or password for selected database.',
        }, status=422)

    return render_inertia(request, 'Login', {'databases': databases})


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('/login/')


def _render_index(request, page, prop, queryset, fields, options=()):
    return render_inertia(request, page, {prop: _rows(queryset, *fields), 'options': _common_options(request.user, options), 'auth': _auth(request)})


@login_required
def dashboard(request):
    return render_inertia(request, 'Dashboard', {'cards': [
        {'label': 'Products', 'translationKey': 'nav.products', 'value': Product.objects.for_user(request.user).count()},
        {'label': 'Purchases', 'translationKey': 'nav.purchases', 'value': PurchaseBatch.objects.for_user(request.user).count()},
        {'label': 'Sales', 'translationKey': 'nav.sales', 'value': Sale.objects.for_user(request.user).count()},
        {'label': 'Accounts', 'translationKey': 'finance.accounts', 'value': Account.objects.for_user(request.user).count() if _can(request.user, 'view', 'account', 'finance') else 0},
    ], 'auth': _auth(request)})

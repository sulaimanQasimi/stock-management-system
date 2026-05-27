from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
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
        'user': {'username': request.user.get_username(), 'email': request.user.email, 'isSuperuser': request.user.is_superuser},
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
        set_current_database(database)

        user = authenticate(request, username=username, password=password)

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


def _permission_options():
    permissions = Permission.objects.select_related('content_type').filter(
        content_type__app_label__in=['auth', 'stock_app', 'finance', 'party', 'hr']
    ).order_by('content_type__app_label', 'content_type__model', 'codename')

    grouped = {}
    for permission in permissions:
        group = f'{permission.content_type.app_label}.{permission.content_type.model}'
        grouped.setdefault(group, []).append({
            'id': permission.id,
            'codename': permission.codename,
            'name': permission.name,
        })

    return [{'group': group, 'permissions': items} for group, items in grouped.items()]


def _user_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'isActive': user.is_active,
        'isStaff': user.is_staff,
        'isSuperuser': user.is_superuser,
        'permissionIds': list(user.user_permissions.values_list('id', flat=True)),
    }


@login_required
@require_http_methods(['GET', 'POST'])
def users_index(request):
    if not request.user.is_superuser and not request.user.has_perm('auth.view_user'):
        raise PermissionDenied

    if request.method == 'POST':
        if not request.user.is_superuser and not request.user.has_perm('auth.add_user'):
            raise PermissionDenied

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        errors = {}
        if not username:
            errors['username'] = ['Username is required.']
        if not password:
            errors['password'] = ['Password is required for new users.']
        if User.objects.filter(username=username).exists():
            errors['username'] = ['A user with this username already exists in this database.']

        if errors:
            return render_inertia(request, 'Users', _users_page_props(request, errors), status=422)

        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_active = request.POST.get('is_active', 'true') == 'true'
        user.is_staff = request.POST.get('is_staff', 'false') == 'true'
        user.is_superuser = request.POST.get('is_superuser', 'false') == 'true' and request.user.is_superuser
        user.save()
        _sync_user_permissions(user, request.POST.getlist('permissions'))
        return redirect('users.index')

    return render_inertia(request, 'Users', _users_page_props(request))


@login_required
@require_http_methods(['POST'])
def user_update(request, user_id):
    if not request.user.is_superuser and not request.user.has_perm('auth.change_user'):
        raise PermissionDenied

    user = get_object_or_404(User, pk=user_id)
    user.email = request.POST.get('email', '').strip()
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name = request.POST.get('last_name', '').strip()
    user.is_active = request.POST.get('is_active', 'false') == 'true'
    user.is_staff = request.POST.get('is_staff', 'false') == 'true'

    if request.user.is_superuser and user.id != request.user.id:
        user.is_superuser = request.POST.get('is_superuser', 'false') == 'true'

    password = request.POST.get('password', '')
    if password:
        user.set_password(password)

    user.save()

    if request.user.is_superuser or request.user.has_perm('auth.change_permission'):
        _sync_user_permissions(user, request.POST.getlist('permissions'))

    return redirect('users.index')


def _sync_user_permissions(user, permission_ids):
    cleaned_ids = [int(item) for item in permission_ids if str(item).isdigit()]
    permissions = Permission.objects.filter(id__in=cleaned_ids)
    user.user_permissions.set(permissions)


def _users_page_props(request, errors=None):
    users = User.objects.order_by('username').prefetch_related('user_permissions')
    return {
        'users': [_user_payload(user) for user in users],
        'permissions': _permission_options(),
        'errors': errors or {},
        'auth': _auth(request),
    }


@login_required
def dashboard(request):
    return render_inertia(request, 'Dashboard', {'cards': [
        {'label': 'Products', 'translationKey': 'nav.products', 'value': Product.objects.for_user(request.user).count()},
        {'label': 'Purchases', 'translationKey': 'nav.purchases', 'value': PurchaseBatch.objects.for_user(request.user).count()},
        {'label': 'Sales', 'translationKey': 'nav.sales', 'value': Sale.objects.for_user(request.user).count()},
        {'label': 'Accounts', 'translationKey': 'finance.accounts', 'value': Account.objects.for_user(request.user).count() if _can(request.user, 'view', 'account', 'finance') else 0},
    ], 'auth': _auth(request)})


@login_required
def operations_index(request):
    low_stock_rules = ProductReorderRule.objects.for_user(request.user).select_related('product', 'preferred_supplier')[:100]
    near_expiry = ProductBatchTracking.objects.for_user(request.user).select_related('product').exclude(expiry_date__isnull=True)[:100]
    return render_inertia(request, 'Operations', {
        'auth': _auth(request),
        'summary': {
            'lowStock': sum(1 for rule in low_stock_rules if rule.is_low_stock),
            'pendingApprovals': ApprovalRequest.objects.for_user(request.user).filter(status='pending').count(),
            'openReturns': ReturnRecord.objects.for_user(request.user).exclude(status__in=['posted', 'cancelled']).count(),
            'queuedExports': ExportJob.objects.for_user(request.user).exclude(status='completed').count(),
        },
        'lowStockRules': [{'id': r.id, 'product': r.product.name, 'current': str(r.product.quantity), 'minimum': str(r.minimum_stock), 'reorderQuantity': str(r.reorder_quantity), 'supplier': r.preferred_supplier.name if r.preferred_supplier else ''} for r in low_stock_rules],
        'approvals': _rows(ApprovalRequest.objects.for_user(request.user).order_by('-created_at')[:100], 'id', 'workflow_type', 'status', 'title', 'reference_number', 'created_at'),
        'documents': _rows(BusinessDocument.objects.for_user(request.user).order_by('-issued_at')[:100], 'id', 'document_type', 'title', 'reference_number', 'issued_at'),
        'partyLedger': _rows(PartyLedgerEntry.objects.for_user(request.user).select_related('party').order_by('-posted_at')[:100], 'id', 'party__name', 'entry_type', 'debit', 'credit', 'reference_number', 'posted_at'),
        'returns': _rows(ReturnRecord.objects.for_user(request.user).order_by('-return_date', '-id')[:100], 'id', 'return_number', 'return_type', 'status', 'return_date'),
        'stockReasons': _rows(StockAdjustmentReason.objects.for_user(request.user).order_by('name')[:100], 'id', 'name', 'requires_approval'),
        'stockCounts': _rows(StockCountSession.objects.for_user(request.user).order_by('-scheduled_date')[:100], 'id', 'count_number', 'status', 'scheduled_date'),
        'batchTracking': [{'id': b.id, 'product': b.product.name, 'batchNumber': b.batch_number, 'expiryDate': b.expiry_date, 'quantity': str(b.quantity), 'expired': b.is_expired} for b in near_expiry],
        'costing': _rows(CostingConfiguration.objects.for_user(request.user).order_by('name')[:50], 'id', 'name', 'method', 'is_default'),
        'advancedReports': _rows(AdvancedReportRequest.objects.for_user(request.user).order_by('-created_at')[:100], 'id', 'report_type', 'title', 'date_from', 'date_to'),
        'exports': _rows(ExportJob.objects.for_user(request.user).order_by('-created_at')[:100], 'id', 'export_type', 'file_format', 'status', 'created_at'),
    })


@login_required
def product_search_index(request):
    _require(request.user, 'view', Product)
    query = request.GET.get('q', '').strip()
    products = Product.objects.for_user(request.user).select_related('category', 'unit').order_by('name')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(barcode__icontains=query) | Q(category__name__icontains=query) | Q(description__icontains=query))

    results = [{
        'id': product.id,
        'name': product.name,
        'sku': product.sku or '',
        'barcode': product.barcode or '',
        'category': product.category.name if product.category else '',
        'unit': product.unit.name if product.unit else '',
        'quantity': str(product.quantity),
        'price': str(product.price),
        'packSalePrice': str(product.pack_sale_price),
        'unitSalePrice': str(product.unit_sale_price),
    } for product in products[:100]]

    return render_inertia(request, 'ProductSearch', {'auth': _auth(request), 'query': query, 'products': results})


@login_required
@require_http_methods(['GET', 'POST'])
def departments_index(request):
    _require(request.user, 'view', Department)
    if request.method == 'POST':
        _require(request.user, 'create', Department)
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.set_created_user(request.user)
            department.set_updated_user(request.user)
            department.save()
            return redirect('departments.index')
        return render_inertia(request, 'Departments', {'departments': _rows(Department.objects.for_user(request.user), 'id', 'name', 'code', 'description'), 'errors': form.errors}, status=422)
    return _render_index(request, 'Departments', 'departments', Department.objects.for_user(request.user), ['id', 'name', 'code', 'description'])


@login_required
@require_http_methods(['GET', 'POST'])
def stock_movements_index(request):
    _require(request.user, 'view', StockMovement)
    if request.method == 'POST':
        _require(request.user, 'create', StockMovement)
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.set_created_user(request.user)
            movement.set_updated_user(request.user)
            movement.save()
            return redirect('stock-movements.index')
        movements = StockMovement.objects.for_user(request.user).select_related('product', 'from_department', 'to_department')[:200]
        return render_inertia(request, 'StockMovements', {'stockMovements': _stock_movement_rows(movements), 'options': _common_options(request.user, ('products', 'departments')), 'errors': form.errors}, status=422)
    movements = StockMovement.objects.for_user(request.user).select_related('product', 'from_department', 'to_department')[:200]
    return render_inertia(request, 'StockMovements', {'stockMovements': _stock_movement_rows(movements), 'options': _common_options(request.user, ('products', 'departments')), 'auth': _auth(request)})


def _stock_movement_rows(queryset):
    return [{'id': item.id, 'product': item.product.name, 'movement_type': item.movement_type, 'quantity': str(item.quantity), 'from_department': item.from_department.name if item.from_department else '', 'to_department': item.to_department.name if item.to_department else '', 'reference_number': item.reference_number, 'reason': item.reason, 'movement_date': item.movement_date.isoformat() if item.movement_date else ''} for item in queryset]


def _secured_index(view_name, prop, model, fields, order_by, options=(), app_label='stock_app'):
    @login_required
    def view(request):
        _require(request.user, 'view', model, app_label)
        queryset = model.objects.for_user(request.user).order_by(*order_by)[:500]
        return _render_index(request, view_name, prop, queryset, fields, options)
    return view


categories_index = _secured_index('Categories', 'categories', Category, ['id', 'name', 'description'], ['name'])
units_index = _secured_index('Units', 'units', Unit, ['id', 'name', 'abbreviation'], ['name'])
parties_index = _secured_index('Parties', 'parties', Party, ['id', 'name', 'party_type', 'phone', 'address', 'description'], ['name'])
products_index = _secured_index('Products', 'products', Product, ['id', 'name', 'sku', 'barcode', 'quantity', 'price', 'pack_sale_price', 'unit_sale_price', 'description'], ['name'], ('categories', 'units'))
purchase_batches_index = _secured_index('PurchaseBatches', 'purchaseBatches', PurchaseBatch, ['id', 'batch_number', 'date', 'total', 'reference_number', 'invoice_number', 'note'], ['-date', '-id'], ('parties', 'currencies'))
purchase_items_index = _secured_index('PurchaseItems', 'purchaseItems', PurchaseItem, ['id', 'quantity', 'piece_or_pack', 'per_pack', 'total_base_unit', 'unit_price', 'total', 'note'], ['-id'], ('products', 'units', 'purchaseBatches'))
purchase_payments_index = _secured_index('PurchasePayments', 'purchasePayments', PurchasePayment, ['id'], ['-id'], ('accounts', 'currencies', 'transactions', 'purchaseBatches'))
sales_index = _secured_index('Sales', 'sales', Sale, ['id', 'sale_number', 'date', 'total', 'discount', 'net_total', 'reference_number', 'invoice_number', 'note'], ['-date', '-id'], ('parties', 'currencies'))
sale_items_index = _secured_index('SaleItems', 'saleItems', SaleItem, ['id', 'quantity', 'pack_or_piece', 'per_pack', 'total_base_unit', 'unit_price', 'total', 'gross_profit', 'profit_margin_percent', 'note'], ['-id'], ('purchaseItems', 'sales'))
sale_payments_index = _secured_index('SalePayments', 'salePayments', SalePayment, ['id', 'amount'], ['-id'], ('accounts', 'currencies', 'transactions', 'sales'))
stock_profit_reports_index = _secured_index('StockProfitReports', 'stockProfitReports', StockProfitReport, ['id', 'report_scope', 'total_sales', 'gross_profit', 'profit_margin_percent', 'remaining_stock_value'], ['-created_at'], ('products', 'purchaseBatches', 'currencies'))
currencies_index = _secured_index('Currencies', 'currencies', Currency, ['id', 'code', 'name', 'symbol'], ['code'], app_label='finance')
accounts_index = _secured_index('Accounts', 'accounts', Account, ['id', 'code', 'name', 'balance'], ['code'], ('currencies',), 'finance')
transactions_index = _secured_index('Transactions', 'transactions', Transaction, ['id', 'transaction_type', 'amount', 'description'], ['-created_at'], ('accounts',), 'finance')
expense_types_index = _secured_index('ExpenseTypes', 'expenseTypes', ExpenseType, ['id', 'name', 'description'], ['name'], app_label='finance')
expenses_index = _secured_index('Expenses', 'expenses', Expense, ['id', 'name', 'amount', 'description'], ['-created_at'], ('expenseTypes', 'transactions'), 'finance')

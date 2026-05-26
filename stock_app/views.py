from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render_inertia

from finance.models import Account, Currency, Expense, ExpenseType, Transaction
from .forms import DepartmentForm, StockMovementForm
from .models import Category, Department, Party, Product, PurchaseBatch, PurchaseItem, PurchasePayment, Sale, SaleItem, SalePayment, StockMovement, StockProfitReport, Unit

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
    return (
        user.has_perm(f'{app_label}.{action}_{model_name}')
        or user.has_perm(f'{app_label}.{action}_all_{model_name}')
        or user.has_perm(f'{app_label}.{action}_own_{model_name}')
        or user.has_perm(f'{app_label}.{django_action}_{model_name}')
    )


def _require(user, action, model_or_name, app_label='stock_app'):
    if not _can(user, action, model_or_name, app_label):
        raise PermissionDenied


def _safe_queryset(user, model, app_label='stock_app'):
    if app_label == 'finance':
        return model.objects.for_user(user)
    return model.objects.for_user(user)


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


def _render_index(request, page, prop, queryset, fields, options=()):
    return render_inertia(request, page, {prop: _rows(queryset, *fields), 'options': _common_options(request.user, options), 'auth': {'user': {'username': request.user.get_username(), 'email': request.user.email}}})


@login_required
def dashboard(request):
    return render_inertia(request, 'Dashboard', {'cards': [
        {'label': 'Products', 'value': Product.objects.for_user(request.user).count()},
        {'label': 'Purchases', 'value': PurchaseBatch.objects.for_user(request.user).count()},
        {'label': 'Sales', 'value': Sale.objects.for_user(request.user).count()},
        {'label': 'Accounts', 'value': Account.objects.for_user(request.user).count() if _can(request.user, 'view', 'account', 'finance') else 0},
    ], 'auth': {'user': {'username': request.user.get_username(), 'email': request.user.email}}})


@login_required
def users_index(request):
    if not request.user.is_superuser and not request.user.has_perm('auth.view_user'):
        raise PermissionDenied
    users = User.objects.filter(is_active=True).order_by('username').values('id', 'username', 'email')
    return render_inertia(request, 'Users', {'users': list(users), 'auth': {'user': {'username': request.user.get_username(), 'email': request.user.email}}})


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
    return render_inertia(request, 'StockMovements', {'stockMovements': _stock_movement_rows(movements), 'options': _common_options(request.user, ('products', 'departments'))})


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
products_index = _secured_index('Products', 'products', Product, ['id', 'name', 'quantity', 'price', 'pack_sale_price', 'unit_sale_price', 'description'], ['name'], ('categories', 'units'))
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

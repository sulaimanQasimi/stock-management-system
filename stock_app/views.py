from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from inertia import render_inertia

from finance.models import Account, Currency, Expense, ExpenseType, Transaction
from .models import (
    Category,
    Department,
    Party,
    Product,
    PurchaseBatch,
    PurchaseItem,
    PurchasePayment,
    Sale,
    SaleItem,
    SalePayment,
    StockMovement,
    StockProfitReport,
    Unit,
)

User = get_user_model()


def _rows(queryset, *fields):
    return list(queryset.values(*fields))


def _options(queryset, label_field='name'):
    return [{'value': row.id, 'label': str(getattr(row, label_field, row))} for row in queryset]


def _common_options():
    return {
        'categories': _options(Category.objects.order_by('name')),
        'units': _options(Unit.objects.order_by('name')),
        'parties': _options(Party.objects.order_by('name')),
        'products': _options(Product.objects.order_by('name')),
        'departments': _options(Department.objects.order_by('name')),
        'currencies': _options(Currency.objects.order_by('code'), 'code'),
        'accounts': _options(Account.objects.order_by('code'), 'name'),
        'transactions': [{'value': item.id, 'label': str(item)} for item in Transaction.objects.order_by('-created_at')[:200]],
        'purchaseBatches': _options(PurchaseBatch.objects.order_by('-date', '-id'), 'batch_number'),
        'purchaseItems': [{'value': item.id, 'label': str(item)} for item in PurchaseItem.objects.select_related('product').order_by('-id')[:500]],
        'sales': _options(Sale.objects.order_by('-date', '-id'), 'sale_number'),
        'expenseTypes': _options(ExpenseType.objects.order_by('name')),
    }


def _render_index(request, page, prop, queryset, fields):
    return render_inertia(request, page, {
        prop: _rows(queryset, *fields),
        'options': _common_options(),
    })


def _can(user, action, model_name):
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser
        or user.has_perm(f'stock_app.{action}_{model_name}')
        or user.has_perm(f'stock_app.{action}_all_{model_name}')
        or user.has_perm(f'stock_app.{action}_own_{model_name}')
    )


def _permission_denied_page(request, title='Permission denied'):
    return render_inertia(request, 'PermissionDenied', {'title': title})


def dashboard(request):
    return render_inertia(request, 'Dashboard', {
        'cards': [
            {'label': 'Products', 'value': Product.objects.count()},
            {'label': 'Purchases', 'value': PurchaseBatch.objects.count()},
            {'label': 'Sales', 'value': Sale.objects.count()},
            {'label': 'Accounts', 'value': Account.objects.count()},
        ]
    })


def users_index(request):
    users = User.objects.filter(is_active=True).order_by('username').values('id', 'username', 'email')
    return render_inertia(request, 'Users', {'users': list(users)})


def departments_index(request):
    if not _can(request.user, 'view', 'department'):
        return _permission_denied_page(request, 'Departments permission required')

    if request.method == 'POST':
        if not _can(request.user, 'create', 'department'):
            return _permission_denied_page(request, 'Create department permission required')
        department = Department(
            name=request.POST.get('name', '').strip(),
            code=request.POST.get('code', '').strip(),
            description=request.POST.get('description', '').strip(),
        )
        department.set_created_user(request.user)
        department.set_updated_user(request.user)
        department.save()
        return redirect('departments.index')

    return _render_index(request, 'Departments', 'departments', Department.objects.for_user(request.user), ['id', 'name', 'code', 'description'])


def stock_movements_index(request):
    if not _can(request.user, 'view', 'stockmovement'):
        return _permission_denied_page(request, 'Stock movement permission required')

    if request.method == 'POST':
        if not _can(request.user, 'create', 'stockmovement'):
            return _permission_denied_page(request, 'Create stock movement permission required')
        movement = StockMovement(
            product_id=request.POST.get('product'),
            movement_type=request.POST.get('movement_type'),
            quantity=request.POST.get('quantity'),
            from_department_id=request.POST.get('from_department') or None,
            to_department_id=request.POST.get('to_department') or None,
            reference_number=request.POST.get('reference_number', '').strip(),
            reason=request.POST.get('reason', '').strip(),
            note=request.POST.get('note', '').strip(),
        )
        movement.set_created_user(request.user)
        movement.set_updated_user(request.user)
        try:
            movement.save()
        except ValidationError as exc:
            movements = StockMovement.objects.for_user(request.user).select_related('product', 'from_department', 'to_department')
            return render_inertia(request, 'StockMovements', {
                'stockMovements': _stock_movement_rows(movements),
                'options': _common_options(),
                'errors': exc.message_dict if hasattr(exc, 'message_dict') else {'stock': exc.messages},
            })
        return redirect('stock-movements.index')

    movements = StockMovement.objects.for_user(request.user).select_related('product', 'from_department', 'to_department')
    return render_inertia(request, 'StockMovements', {
        'stockMovements': _stock_movement_rows(movements),
        'options': _common_options(),
    })


def _stock_movement_rows(queryset):
    return [
        {
            'id': item.id,
            'product': item.product.name,
            'movement_type': item.movement_type,
            'quantity': item.quantity,
            'from_department': item.from_department.name if item.from_department else '',
            'to_department': item.to_department.name if item.to_department else '',
            'reference_number': item.reference_number,
            'reason': item.reason,
            'movement_date': item.movement_date,
        }
        for item in queryset
    ]


def categories_index(request):
    return _render_index(request, 'Categories', 'categories', Category.objects.order_by('name'), ['id', 'name', 'description'])


def units_index(request):
    return _render_index(request, 'Units', 'units', Unit.objects.order_by('name'), ['id', 'name', 'abbreviation'])


def parties_index(request):
    return _render_index(request, 'Parties', 'parties', Party.objects.order_by('name'), ['id', 'name', 'party_type', 'phone', 'address', 'description'])


def products_index(request):
    return _render_index(request, 'Products', 'products', Product.objects.order_by('name'), ['id', 'name', 'quantity', 'price', 'pack_sale_price', 'unit_sale_price', 'description'])


def purchase_batches_index(request):
    return _render_index(request, 'PurchaseBatches', 'purchaseBatches', PurchaseBatch.objects.order_by('-date', '-id'), ['id', 'batch_number', 'date', 'total', 'reference_number', 'invoice_number', 'note'])


def purchase_items_index(request):
    return _render_index(request, 'PurchaseItems', 'purchaseItems', PurchaseItem.objects.order_by('-id'), ['id', 'quantity', 'piece_or_pack', 'per_pack', 'total_base_unit', 'unit_price', 'total', 'note'])


def purchase_payments_index(request):
    return _render_index(request, 'PurchasePayments', 'purchasePayments', PurchasePayment.objects.order_by('-id'), ['id'])


def sales_index(request):
    return _render_index(request, 'Sales', 'sales', Sale.objects.order_by('-date', '-id'), ['id', 'sale_number', 'date', 'total', 'discount', 'net_total', 'reference_number', 'invoice_number', 'note'])


def sale_items_index(request):
    return _render_index(request, 'SaleItems', 'saleItems', SaleItem.objects.order_by('-id'), ['id', 'quantity', 'pack_or_piece', 'per_pack', 'total_base_unit', 'unit_price', 'total', 'gross_profit', 'profit_margin_percent', 'note'])


def sale_payments_index(request):
    return _render_index(request, 'SalePayments', 'salePayments', SalePayment.objects.order_by('-id'), ['id', 'amount'])


def stock_profit_reports_index(request):
    return _render_index(request, 'StockProfitReports', 'stockProfitReports', StockProfitReport.objects.order_by('-created_at'), ['id', 'report_scope', 'total_sales', 'gross_profit', 'profit_margin_percent', 'remaining_stock_value'])


def currencies_index(request):
    return _render_index(request, 'Currencies', 'currencies', Currency.objects.order_by('code'), ['id', 'code', 'name', 'symbol'])


def accounts_index(request):
    return _render_index(request, 'Accounts', 'accounts', Account.objects.order_by('code'), ['id', 'code', 'name', 'balance'])


def transactions_index(request):
    return _render_index(request, 'Transactions', 'transactions', Transaction.objects.order_by('-created_at'), ['id', 'transaction_type', 'amount', 'description'])


def expense_types_index(request):
    return _render_index(request, 'ExpenseTypes', 'expenseTypes', ExpenseType.objects.order_by('name'), ['id', 'name', 'description'])


def expenses_index(request):
    return _render_index(request, 'Expenses', 'expenses', Expense.objects.order_by('-created_at'), ['id', 'name', 'amount', 'description'])
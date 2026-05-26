from django.contrib.auth import get_user_model
from inertia import render_inertia

from finance.models import Account, Currency, Expense, ExpenseType, Transaction
from .models import (
    Category,
    Party,
    Product,
    PurchaseBatch,
    PurchaseItem,
    PurchasePayment,
    Sale,
    SaleItem,
    SalePayment,
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
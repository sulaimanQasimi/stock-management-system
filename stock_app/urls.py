from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.categories_index, name='categories.index'),
    path('units/', views.units_index, name='units.index'),
    path('parties/', views.parties_index, name='parties.index'),
    path('products/', views.products_index, name='products.index'),
    path('purchase-batches/', views.purchase_batches_index, name='purchase-batches.index'),
    path('purchase-items/', views.purchase_items_index, name='purchase-items.index'),
    path('purchase-payments/', views.purchase_payments_index, name='purchase-payments.index'),
    path('sales/', views.sales_index, name='sales.index'),
    path('sale-items/', views.sale_items_index, name='sale-items.index'),
    path('sale-payments/', views.sale_payments_index, name='sale-payments.index'),
    path('stock-profit-reports/', views.stock_profit_reports_index, name='stock-profit-reports.index'),
    path('currencies/', views.currencies_index, name='currencies.index'),
    path('accounts/', views.accounts_index, name='accounts.index'),
    path('transactions/', views.transactions_index, name='transactions.index'),
    path('expense-types/', views.expense_types_index, name='expense-types.index'),
    path('expenses/', views.expenses_index, name='expenses.index'),
]

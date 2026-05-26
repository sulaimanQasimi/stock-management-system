from django.contrib import admin, messages

from authorization.models import AuthorizationActivityLog

from .models import Account, Currency, Expense, ExpenseType, Transaction


class AuthorizedAdminMixin:
    audit_readonly_fields = (
        'created_by', 'created_at', 'updated_by', 'updated_at',
        'is_trashed', 'trashed_by', 'trashed_at', 'restored_by', 'restored_at',
        'deleted_by', 'deleted_at', 'force_deleted_by', 'force_deleted_at',
    )
    actions = ('trash_selected_records', 'restore_selected_records', 'force_delete_selected_records')

    def get_queryset(self, request):
        manager = getattr(self.model, 'all_objects', None)
        if manager is not None:
            return manager.get_queryset()
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'set_created_user'):
            obj.set_created_user(request.user)
        if hasattr(obj, 'set_updated_user'):
            obj.set_updated_user(request.user)
        super().save_model(request, obj, form, change)
        AuthorizationActivityLog.log(obj, 'update' if change else 'create', request.user)

    @admin.action(description='Trash selected records')
    def trash_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'trash'):
                obj.trash(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) moved to trash.', messages.SUCCESS)

    @admin.action(description='Restore selected records')
    def restore_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'restore'):
                obj.restore(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) restored.', messages.SUCCESS)

    @admin.action(description='Force delete selected records permanently')
    def force_delete_selected_records(self, request, queryset):
        count = 0
        for obj in queryset:
            if hasattr(obj, 'force_delete'):
                obj.force_delete(user=request.user)
                count += 1
        self.message_user(request, f'{count} record(s) permanently deleted.', messages.WARNING)


@admin.register(Currency)
class CurrencyAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('is_trashed',)
    search_fields = ('code', 'name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Account)
class AccountAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'currency', 'balance', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('currency', 'is_trashed')
    search_fields = ('code', 'name')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Transaction)
class TransactionAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'content_type', 'object_id', 'is_trashed', 'created_by')
    list_filter = ('transaction_type', 'account', 'is_trashed')
    search_fields = ('description', 'account__name', 'account__code')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(ExpenseType)
class ExpenseTypeAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('is_trashed',)
    search_fields = ('name',)
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields


@admin.register(Expense)
class ExpenseAdmin(AuthorizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'expense_type', 'amount', 'transaction', 'is_trashed', 'created_by', 'updated_by')
    list_filter = ('expense_type', 'is_trashed')
    search_fields = ('name', 'description')
    readonly_fields = AuthorizedAdminMixin.audit_readonly_fields

from django.apps import AppConfig


class StockAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock_app'

    def ready(self):
        try:
            import stock_app.admin_features  # noqa: F401
            import stock_app.admin_services  # noqa: F401
        except Exception:
            pass

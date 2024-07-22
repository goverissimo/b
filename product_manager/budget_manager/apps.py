from django.apps import AppConfig

class BudgetManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget_manager'

    def ready(self):
        import budget_manager.signals
from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'api'

    def ready(self) -> None:
        """Импортируем сигналы."""

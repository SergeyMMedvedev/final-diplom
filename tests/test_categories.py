import pytest
from django.test import Client

from tests.common import (
    STATUS_ERROR_MSG,
)


class Test03Categories:
    """
    Тестируется возможность просмотра категорий.
    
    Используется:
     - CategoryView
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_get_categories(self, client: Client, categories) -> None:
        """Получить список категорий товаров."""
        response = client.get('/categories')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            response.json().get('results') is not None
        ), "Отсутствует список категорий"
        assert (
            len(response.json().get('results', [])) > 0
        ), "Список категорий пуст"

import pytest
from django.test import Client

from tests.common import (
    STATUS_ERROR_MSG,
)


class Test04Shops:
    @pytest.mark.django_db(transaction=True)
    def test_01_get_shops(self, client: Client, shop) -> None:
        """Получить список магазинов."""
        response = client.get('/shops')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            response.json().get('results') is not None
        ), "Отсутствует список магазинов"
        assert (
            len(response.json().get('results', [])) > 0
        ), "Список магазинов пуст"

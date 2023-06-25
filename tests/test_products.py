import pytest
from django.test import Client

from tests.common import (
    STATUS_ERROR_MSG,
)


class Test05Products:
    """
    Тестируется возможность поиска товаров.

    Используется:
     - ProductInfoView
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_get_products(self, client: Client, productparameter) -> None:
        """Получить список продуктов."""
        response = client.get('/products')

        assert response.status_code == 200, STATUS_ERROR_MSG
        assert len(response.json()) > 0, "Список продуктов пуст"
        response = client.get('/products?shop_id=1')
        shop_ids = [shop["shop"] for shop in response.json()]
        for pk in shop_ids:
            assert pk == 1, "Не работает фильтрация"

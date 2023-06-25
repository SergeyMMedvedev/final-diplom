import pytest

from tests.common import STATUS_ERROR_MSG

products_url = (
    'https://raw.githubusercontent.com/netology-code/'
    'python-final-diplom/master/data/shop1.yaml'
)


class Test10PartnerUpdate:
    """
    Тестирование возможности обновления прайса от поставщика.
    
    Используется:
     - PartnerUpdate
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_update_price(
        self,
        owner_client,
    ) -> None:
        """Владелец может обновить товары."""
        response = owner_client.post(
            '/partner/update', data={"url": products_url}
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        response = owner_client.get('/products')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert len(response.json()) == 4, '4 товара не были добавлены'

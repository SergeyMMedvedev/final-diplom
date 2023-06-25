import pytest

from tests.common import STATUS_ERROR_MSG


class Test09PartnerOrders:
    """
    Тестируется возможность получения заказов поставщиками.

    Используется:
     - PartnerOrders
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_get_order(
        self,
        owner_client,
        productparameter,
        order,
    ) -> None:
        """Владелец может получить созданный клиентом заказ."""
        response = owner_client.get('/partner/orders')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert len(response.json()) > 0, 'Владелец не получил заказ'
        order = response.json()[0]
        assert order.get('state') == 'new', 'Неверный статус заказа'

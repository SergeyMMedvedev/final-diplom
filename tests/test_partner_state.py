import pytest
from django.test import Client

from tests.common import (
    STATUS_ERROR_MSG,
)


class Test06PartnerState:
    """
    Тестируется возможность работы со статусом поставщика.

    Используется:
     - PartnerState
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_get_partner_state(self, owner_client: Client, shop) -> None:
        """Поставщик получает статус."""
        response = owner_client.get('/partner/state')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('state') is True, 'Неверный статус магазина'
        assert (
            response.json().get('name') == shop.name
        ), 'Неправильное имя магазина'

    @pytest.mark.django_db(transaction=True)
    def test_02_update_partner_state(self, owner_client: Client, shop) -> None:
        """Поставщик обновляет статус."""
        data = {"state": False}
        response = owner_client.post('/partner/state', data=data)
        assert response.status_code == 200, STATUS_ERROR_MSG
        response = owner_client.get('/partner/state')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            response.json().get('state') is False
        ), 'Статус магазина не обновился'

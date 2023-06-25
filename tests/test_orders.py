from typing import Callable

import pytest
from django.core import mail
from django.test import Client

from tests.common import STATUS_ERROR_MSG, STATUS_FIELD_ERR


class Test08Orders:
    """
    Тестируется возможность получения и размещения заказов пользователями.

    Используется:
     - OrderView
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_create_order(
        self,
        u_client_with_contacts: Client,
        productparameter,
        create_basket: Callable,
    ) -> None:
        """Клиент может сделать заказ."""
        status = create_basket(u_client_with_contacts)
        assert status == 200, STATUS_ERROR_MSG
        response = u_client_with_contacts.get('/user/contact/')
        assert response.status_code == 200, STATUS_ERROR_MSG
        contact_id = response.json()['results'][0]['id']
        response = u_client_with_contacts.post(
            '/order', data={"contact": contact_id}
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR
        mail_message = mail.outbox[-1].message()
        message = str(mail_message).strip().split('\n')[-1]
        assert (
            message == 'Заказ сформирован'
        ), 'Неправильное содержание письма с подтверждением заказа'
        response = u_client_with_contacts.get('/order')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert len(response.json()) > 0, 'Заказ не появился'

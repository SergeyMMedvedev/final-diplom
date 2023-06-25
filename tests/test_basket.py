import json

import pytest
from django.test import Client

from tests.common import STATUS_ERROR_MSG, STATUS_FIELD_ERR


class Test07Basket:
    """
    Тестируется возможность работы с корзиной пользователя.

    Используется:
     - BasketView
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_create_basket(
        self, user_client: Client, productparameter
    ) -> None:
        """Клиент может положить товары в корзину."""
        response = user_client.get('/products')
        assert response.status_code == 200, STATUS_ERROR_MSG
        order_items = []
        price = 0
        quantity = 2
        for product in response.json()[:2]:
            order_items.append(
                {"product_info": product['id'], "quantity": quantity}
            )
            price += product['price'] * quantity
        response = user_client.post(
            '/basket',
            data=json.dumps(order_items),
            content_type='application/json',
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR
        assert (
            response.json().get('Создано объектов') == 2
        ), 'Неверное значение поля "Создано объектов"'
        response = user_client.get('/basket')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            len(response.json().get('ordered_items', [])) == 2
        ), 'Получено неправильное значение объектов в корзине'
        assert (
            response.json().get('total_sum') == price
        ), 'Получено неправильное значение total_sum'

    def test_02_upd_basket(
        self, user_client: Client, productparameter
    ) -> None:
        """Клиент может обновить корзину."""
        response = user_client.get('/products')
        assert response.status_code == 200, STATUS_ERROR_MSG
        products = response.json()
        order_items = []
        for product in products[:2]:
            order_items.append({"product_info": product['id'], "quantity": 1})
        response = user_client.post(
            '/basket',
            data=json.dumps(order_items),
            content_type='application/json',
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        response = user_client.get('/basket')
        assert response.status_code == 200, STATUS_ERROR_MSG
        total_sum = response.json().get('total_sum')
        ordered_items = response.json().get('ordered_items', [])
        quantity = 10
        upd_ordered_items = []
        for ordered_item in ordered_items[:2]:
            upd_ordered_items.append(
                {"id": ordered_item['id'], "quantity": quantity}
            )
        response = user_client.put(
            '/basket',
            data=json.dumps(upd_ordered_items),
            content_type='application/json',
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR
        assert (
            response.json().get('Обновлено объектов') == 2
        ), 'Неверное значение поля "Обновлено объектов"'
        response = user_client.get('/basket')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            response.json().get('total_sum') == total_sum * quantity
        ), 'Неправильно указана итоговая сумма после обновления корзины'

    def test_03_del_basket(
        self, user_client: Client, productparameter
    ) -> None:
        """Клиент может удалить товары из корзины."""
        response = user_client.get('/products')
        assert response.status_code == 200, STATUS_ERROR_MSG
        order_items = []
        price = 0
        quantity = 2
        for product in response.json()[:2]:
            order_items.append(
                {"product_info": product['id'], "quantity": quantity}
            )
            price += product['price'] * quantity
        response = user_client.post(
            '/basket',
            data=json.dumps(order_items),
            content_type='application/json',
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        response = user_client.get('/basket')
        assert response.status_code == 200, STATUS_ERROR_MSG
        ordered_items = {
            'ordered_items': [
                ordered_item['id']
                for ordered_item in response.json().get('ordered_items')
            ]
        }

        response = user_client.delete(
            '/basket',
            data=json.dumps(ordered_items),
            content_type='application/json',
        )
        print(response.json())
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR
        assert (
            response.json().get('Удалено объектов') == 2
        ), 'Неверное значение поля Удалено объектов"'
        response = user_client.get('/basket')
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert (
            len(response.json().get('ordered_items')) == 0
        ), 'Объекты не были удалены из корзины'

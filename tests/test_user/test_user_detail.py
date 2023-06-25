import pytest
from django.test import Client

from tests.common import (
    STATUS_ERROR_MSG,
    USER_DETAILS_FIELDS,
    login_data,
)


class Test02UserDetail:
    """
    Тестирование получения или изменения пользовательских данных.

    Используется:
     - AccountDetails
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_get_user_detail(self, user_client: Client) -> None:
        """Пользователь получает свои данные."""
        response = user_client.get('/user/details/')
        assert response.status_code == 200, STATUS_ERROR_MSG
        for field in USER_DETAILS_FIELDS:
            assert (
                response.json().get(field) is not None
            ), f"В информации о пользователе отсутствует {field}"

    def test_02_get_user_detail_not_auth(self, client: Client) -> None:
        """Не авторизованный пользователь не может получить свои данные."""
        response = client.get('/user/details/')
        assert response.status_code == 401, STATUS_ERROR_MSG

    def test_03_update_user_detail(
        self, client: Client, user_client: Client
    ) -> None:
        """Пользователь обновил свои данные."""
        new_first_name = "new_fn_user1"
        new_last_name = "new_ln_user1"
        new_email = "newexample@mail.com"
        new_data = {
            "first_name": new_first_name,
            "last_name": new_last_name,
            "email": new_email,
        }
        response = user_client.patch('/user/details/', data=new_data)
        for field in ("first_name", "last_name", "email"):
            assert (
                response.json().get(field) == new_data[field]
            ), f'Поле {field} не обновилось'
        response = client.post(
            '/user/login',
            data={"email": new_email, "password": login_data['password']},
        )
        assert (
            response.status_code == 200
        ), 'Пользователь не смог авторизоваться с новыми данными'

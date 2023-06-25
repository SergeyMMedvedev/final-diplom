import pytest
from django.core import mail
from django.http import HttpResponse
from django.test import Client

from api.models import User
from tests.common import (
    STATUS_ERROR_MSG,
    STATUS_FIELD_ERR,
    login_data,
    user_data,
)


class Test01UserAPI:
    """
    Тестирование регистрации, подтверждения и авторизации пользователя.

    Тестируются позитивные и негативные сценарии. Участвуют:
     - RegisterAccount
     - ConfirmAccount
     - LoginAccount
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_create_user(self, client: Client) -> None:
        """Пользователь регистрируется."""
        response = client.post('/user/register', data=user_data)
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR

    @pytest.mark.django_db(transaction=True)
    def test_02_create_user_without_req_field(self, client: Client) -> None:
        """
        Пользователь без необходимых полей не создается.

        Отсутствуют поля: first_name, last_name, email, password.
        При отправке не валидного запроса, приходит соответствующий ответ.
        Про отсутствие каждого поля выводится соответствующее сообщение.
        """
        response = client.post('/user/register', data={})
        body = response.json()
        errors = body.get('Errors', [])
        assert response.status_code == 400, STATUS_ERROR_MSG
        assert body.get('Status') is False, STATUS_FIELD_ERR
        assert len(errors) > 0, 'Отсутствуют сообщения об обязательных полях'
        for field in ('first_name', 'last_name', 'password', 'email'):
            err_field_msgs = errors.get(field, [])
            assert (
                len(err_field_msgs) > 0
            ), f'Отсутствует сообщение об ошибке поля {field}'

    @pytest.mark.django_db(transaction=True)
    def test_03_create_user_with_bad_password(self, client: Client) -> None:
        """
        Пользователь со слабым паролем не создается.

        При отправке не валидного password выводится соответствующее сообщение.
        """
        user_bad_data = {**user_data}
        user_bad_data['password'] = '1'
        response = client.post('/user/register', data=user_bad_data)
        body = response.json()
        assert response.status_code == 400, STATUS_ERROR_MSG
        assert body.get('Status') is False, STATUS_FIELD_ERR
        pswd_err = body.get('Errors', {}).get('password')
        assert len(pswd_err) > 0, 'Отсутствуют сообщения о невалидном пароле'

    @pytest.mark.django_db(transaction=True)
    def test_04_confirm_user_email(self, client: Client) -> None:
        """
        Пользователь подтверждает регистрацию по ссылке из почты.

        Сценарий:
         - регистрируем пользователя post запросом
         - проверяем, что mail.outbox содержит письмо
         - проверяем успешность get-запроса по ссылке из письма
         - проверяем статус is_active пользователя после подтверждения email
        """
        response = client.post('/user/register', data=user_data)
        assert (
            len(mail.outbox) > 0
        ), 'Письмо с подтверждением не было отправлено!'
        mail_message = mail.outbox[0].message()
        confirm_url = str(mail_message).strip().split('\n')[-1]
        assert confirm_url.startswith(
            'http'
        ), 'не удалось извлечь ссылку на подтверждение почты'
        response = client.get(confirm_url)
        assert response.status_code == 200, STATUS_ERROR_MSG
        body = response.json()
        assert body.get('Status') is True, STATUS_FIELD_ERR

        user = User.objects.filter(email=user_data['email']).first()
        assert user is not None, 'Подтвержденный пользователь не найден'
        assert user.is_active is True, 'Статус пользователя неверный'

    @pytest.mark.django_db(transaction=True)
    def test_05_login_user(
        self, create_and_confirm_user: HttpResponse, client: Client
    ) -> None:
        """Пользователь авторизуется."""
        response = client.post('/user/login', data=login_data)
        assert response.status_code == 200, STATUS_ERROR_MSG
        assert response.json().get('Status') is True, STATUS_FIELD_ERR
        assert (
            bool(response.json().get('Token')) is True
        ), 'При авторизации не получен токен'

    @pytest.mark.django_db(transaction=True)
    def test_07_login_user_without_req_field(
        self, create_and_confirm_user: HttpResponse, client: Client
    ) -> None:
        """
        Пользователь без необходимых полей не авторизуется.

        Отсутствуют поля: email, password.
        При отправке не валидного запроса, приходит соответствующий ответ.
        Про отсутствие каждого поля выводится соответствующее сообщение.
        """
        response = client.post('/user/login', data={})
        body = response.json()
        errors = body.get('Errors', [])
        assert response.status_code == 400, STATUS_ERROR_MSG
        assert body.get('Status') is False, STATUS_FIELD_ERR
        assert len(errors) > 0, 'Отсутствуют сообщения об обязательных полях'
        for field in ('password', 'email'):
            err_field_msgs = errors.get(field, [])
            assert (
                len(err_field_msgs) > 0
            ), f'Отсутствует сообщение об ошибке поля {field}'

    @pytest.mark.django_db(transaction=True)
    def test_08_login_not_created_user(self, client: Client) -> None:
        """Пользователь без регистрации не авторизуется."""
        response = client.post('/user/login', data=login_data)
        assert response.status_code == 400, STATUS_ERROR_MSG
        assert response.json().get('Status') is False, STATUS_FIELD_ERR

    @pytest.mark.django_db(transaction=True)
    def test_09_login_not_confirmed_user(self, client: Client) -> None:
        """Пользователь без подтверждение email не авторизуется."""
        client.post('/user/register', data=user_data)
        response = client.post('/user/login', data=login_data)
        assert response.status_code == 400, STATUS_ERROR_MSG
        assert response.json().get('Status') is False, STATUS_FIELD_ERR

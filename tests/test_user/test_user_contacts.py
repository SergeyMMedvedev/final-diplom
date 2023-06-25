import pytest
from django.test import Client

from tests.common import STATUS_ERROR_MSG, user_contacts


class Test03UserContacts:
    """
    Тестируется возможность работы с контактами покупателей.

    Используется:
     - ContactView
    """
    @pytest.mark.django_db(transaction=True)
    def test_01_create_user_contact(self, user_client: Client) -> None:
        """Пользователь добавил контакт."""
        response = user_client.post('/user/contact/', data=user_contacts)
        assert response.status_code == 201, STATUS_ERROR_MSG

        response = user_client.get('/user/contact/')
        new_contacts = response.json().get('results', [])
        assert len(new_contacts) > 0, 'Новый контакт отсутствует по запросу'
        new_contact = new_contacts[0]
        del new_contact['id']
        for key in new_contacts[0]:
            assert (
                new_contact[key] == user_contacts[key]
            ), f'поле {key} не соответствует отправленным данным'

    @pytest.mark.django_db(transaction=True)
    def test_02_update_user_contact(self, user_client: Client) -> None:
        """Пользователь обновил контакт."""
        response = user_client.post('/user/contact/', data=user_contacts)
        assert response.status_code == 201, STATUS_ERROR_MSG
        response = user_client.get('/user/contact/')
        contact_id = response.json()['results'][0]['id']
        user_contacts['city'] = 'Saint Petersburg'
        response = user_client.patch(
            f'/user/contact/{contact_id}/', data=user_contacts
        )
        assert response.status_code == 200, STATUS_ERROR_MSG
        response = user_client.get('/user/contact/')
        new_contacts = response.json().get('results', [])
        assert len(new_contacts) > 0, 'Новый контакт отсутствует по запросу'
        new_contact = new_contacts[0]
        assert (
            new_contact['city'] == user_contacts['city']
        ), 'Данные не обновились'

    @pytest.mark.django_db(transaction=True)
    def test_03_delete_user_contact(self, user_client: Client) -> None:
        """Пользователь удалил контакт."""
        response = user_client.post('/user/contact/', data=user_contacts)
        assert response.status_code == 201, STATUS_ERROR_MSG
        response = user_client.get('/user/contact/')
        contact_id = response.json()['results'][0]['id']
        response = user_client.delete(f'/user/contact/{contact_id}/')
        assert response.status_code == 204, STATUS_ERROR_MSG
        response = user_client.get('/user/contact/')
        assert (
            len(response.json().get('results', [])) == 0
        ), 'Контакт не удалился'

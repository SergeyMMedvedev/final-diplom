import pytest
from django.core import mail
from django.http import HttpResponse
from django.test import Client
from rest_framework.test import APIClient

from tests.common import login_data, user_data
from api.models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
)


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestUser', **login_data
    )


@pytest.fixture
def create_and_confirm_user(client: Client) -> HttpResponse:
    """Создать пользователя и подтвердить email."""
    client.post('/user/register', data=user_data)
    mail_message = mail.outbox[0].message()
    confirm_url = str(mail_message).strip().split('\n')[-1]
    return client.get(confirm_url)


@pytest.fixture
def user_client(
    admin, client: Client, upd_login_data: dict | None = None
) -> Client:
    """asd."""
    if upd_login_data:
        for k, v in upd_login_data:
            login_data[k] = v
    response = client.post('/user/login', data=login_data)

    user_client = APIClient()
    user_client.credentials(
        HTTP_AUTHORIZATION=f'Token {response.json().get("Token")}',
        HTTP_CONTENT_TYPE="Application/json",
    )
    return user_client


@pytest.fixture
def owner():
    return User.objects.create(
        **{
            "password": "asdQAZ123",
            "is_superuser": False,
            "first_name": "ser2",
            "last_name": "ser2",
            "email": "medvedevsm1989@yandex.ru",
            "company": "asd",
            "position": "1",
            "username": "sdf",
            "is_active": True,
            "type": "shop",
        }
    )


@pytest.fixture
def shop(owner):
    return Shop.objects.create(
        **{"name": "Связной", "user": owner, "state": True}
    )


@pytest.fixture
def categories(shop) -> list[Category]:
    cat1 = Category.objects.create(**{"name": "Смартфоны"})
    cat1.shops.set([shop])
    cat2 = Category.objects.create(**{"name": "Аксессуары"})
    cat2.shops.set([shop])
    cat3 = Category.objects.create(**{"name": "Flash-накопители"})
    cat3.shops.set([shop])
    return [cat1, cat2, cat3]


@pytest.fixture
def products(categories) -> list[Product]:
    p1 = Product.objects.create(
        **{
            "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
            "category": categories[0],
        }
    )
    p2 = Product.objects.create(
        **{
            "name": "Смартфон Apple iPhone XR 256GB (красный)",
            "category": categories[0],
        }
    )
    p3 = Product.objects.create(
        **{
            "name": "Смартфон Apple iPhone XR 256GB (черный)",
            "category": categories[0],
        }
    )
    p4 = Product.objects.create(
        **{
            "name": "Смартфон Apple iPhone XR 128GB (синий)",
            "category": categories[0],
        }
    )
    return [p1, p2, p3, p4]


@pytest.fixture
def products_info(products) -> list[ProductInfo]:
    shop = Shop.objects.filter(id=1).first()
    pi1 = ProductInfo.objects.create(
        **{
            "model": "apple/iphone/xs-max",
            "external_id": 4216292,
            "product": products[0],
            "shop": shop,
            "quantity": 14,
            "price": 110000,
            "price_rrc": 116990,
        }
    )
    pi2 = ProductInfo.objects.create(
        **{
            "model": "apple/iphone/xr",
            "external_id": 4216313,
            "product": products[1],
            "shop": shop,
            "quantity": 9,
            "price": 65000,
            "price_rrc": 69990,
        }
    )
    pi3 = ProductInfo.objects.create(
        **{
            "model": "apple/iphone/xr",
            "external_id": 4216226,
            "product": products[2],
            "shop": shop,
            "quantity": 5,
            "price": 65000,
            "price_rrc": 69990,
        }
    )
    pi4 = ProductInfo.objects.create(
        **{
            "model": "apple/iphone/xr",
            "external_id": 4672670,
            "product": products[3],
            "shop": shop,
            "quantity": 7,
            "price": 60000,
            "price_rrc": 64990,
        }
    )
    return [pi1, pi2, pi3, pi4]


@pytest.fixture
def parameter() -> list[Parameter]:
    param1 = Parameter.objects.create(**{"name": "Диагональ (дюйм)"})
    param2 = Parameter.objects.create(**{"name": "Разрешение (пикс)"})
    param3 = Parameter.objects.create(**{"name": "Встроенная память (Гб)"})
    param4 = Parameter.objects.create(**{"name": "Цвет"})
    return [param1, param2, param3, param4]


@pytest.fixture
def productparameter(products_info, parameter) -> list[ProductParameter]:
    pp1 = ProductParameter.objects.create(
        **{
            "product_info": products_info[0],
            "parameter": parameter[0],
            "value": "6.5",
        }
    )
    pp2 = ProductParameter.objects.create(
        **{
            "product_info": products_info[0],
            "parameter": parameter[1],
            "value": "2688x1242",
        }
    )
    pp3 = ProductParameter.objects.create(
        **{
            "product_info": products_info[0],
            "parameter": parameter[2],
            "value": "512",
        }
    )
    pp4 = ProductParameter.objects.create(
        **{
            "product_info": products_info[0],
            "parameter": parameter[3],
            "value": "золотистый",
        }
    )

    pp5 = ProductParameter.objects.create(
        **{
            "product_info": products_info[1],
            "parameter": parameter[0],
            "value": "6.1",
        }
    )
    pp6 = ProductParameter.objects.create(
        **{
            "product_info": products_info[1],
            "parameter": parameter[1],
            "value": "1792x828",
        }
    )
    pp7 = ProductParameter.objects.create(
        **{
            "product_info": products_info[1],
            "parameter": parameter[2],
            "value": "256",
        }
    )
    pp8 = ProductParameter.objects.create(
        **{
            "product_info": products_info[1],
            "parameter": parameter[3],
            "value": "красный",
        }
    )

    pp9 = ProductParameter.objects.create(
        **{
            "product_info": products_info[2],
            "parameter": parameter[0],
            "value": "6.1",
        }
    )
    pp10 = ProductParameter.objects.create(
        **{
            "product_info": products_info[2],
            "parameter": parameter[1],
            "value": "1792x828",
        }
    )
    pp11 = ProductParameter.objects.create(
        **{
            "product_info": products_info[2],
            "parameter": parameter[2],
            "value": "256",
        }
    )
    pp12 = ProductParameter.objects.create(
        **{
            "product_info": products_info[2],
            "parameter": parameter[3],
            "value": "черный",
        }
    )

    pp13 = ProductParameter.objects.create(
        **{
            "product_info": products_info[3],
            "parameter": parameter[0],
            "value": "6.1",
        }
    )
    pp14 = ProductParameter.objects.create(
        **{
            "product_info": products_info[3],
            "parameter": parameter[1],
            "value": "1792x828",
        }
    )
    pp15 = ProductParameter.objects.create(
        **{
            "product_info": products_info[3],
            "parameter": parameter[2],
            "value": "256",
        }
    )
    pp16 = ProductParameter.objects.create(
        **{
            "product_info": products_info[3],
            "parameter": parameter[3],
            "value": "синий",
        }
    )
    return [
        pp1,
        pp2,
        pp3,
        pp4,
        pp5,
        pp6,
        pp7,
        pp8,
        pp9,
        pp10,
        pp11,
        pp12,
        pp13,
        pp14,
        pp15,
        pp16,
    ]

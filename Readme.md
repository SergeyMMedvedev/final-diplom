# Дипломная работа к профессии Python-разработчик «API Сервис заказа товаров для розничных сетей»

## Описание
Приложение предназначено для автоматизации закупок в розничной сети. Пользователи сервиса — покупатель (менеджер торговой сети, который закупает товары для продажи в магазине) и поставщик товаров.

Клиент (покупатель):

- Менеджер закупок через API делает ежедневные закупки по каталогу, в котором представлены товары от нескольких поставщиков.
- В одном заказе можно указать товары от разных поставщиков — это повлияет на стоимость доставки.
- Пользователь может авторизироваться, регистрироваться и восстанавливать пароль через API.

Поставщик:

- Через API информирует сервис об обновлении прайса.
- Может включать и отключать прием заказов.
- Может получать список оформленных заказов (с товарами из его прайса).

## Начало работы
### Клонировать проект
```
git clone https://github.com/SergeyMMedvedev/final-diplom.git
```
### Настроить переменные окружения
Первый вариант настройки окружения - с использованием тестового почтового сервера "File backend". 
В этом случае сервер записывает электронные письма в файлы.
Этот вариант не предназначен для использования в продакшене — им удобно пользоваться во время разработки.

Команда по созданию файла виртуального окружения:
```
echo "POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
PG_DB=postgres
PG_HOST=postgresql
PG_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
SERVER_HOST=http://localhost/

DJANGO_SUPERUSER_USERNAME=admin77
DJANGO_SUPERUSER_PASSWORD=admin7712345
DJANGO_SUPERUSER_EMAIL=admin77@admin.com" > .env
```

### Запустить контейнеры

```
docker-compose up
```
После выполнения этой команды проект готов к работе.
### Запустить функциональные тесты

Проект покрыт различными тестовыми сценариями.
Для запуска тестов, выполнить команду:
```
docker exec -it orders pytest
```

Все тестовые сценарии описаны [тут](https://github.com/SergeyMMedvedev/final-diplom/blob/main/test_doc.md).

## Примеры

### 1. Создать администратора

```
docker exec orders python manage.py createsuperuser --noinput
```
Администратор по умолчанию создается активированным пользователем, со статусом владельца магазина.

### 2. Выполнить вход 

Пример запроса:
```
POST http://localhost/user/login
Content-Type: application/json

{
    "password":"admin7712345",
    "email":"admin77@admin.com"
}
```
Пример ответа:
```
{
  "Status": true,
  "Token": "f800a9437ea075193d44d44fc365edc728b0a694"
}
```
### 3. Заполнить прайс данными (PartnerUpdate):

Пример запроса:
```
POST http://localhost/partner/update
Content-Type: application/json
Authorization: Token {{token}}

{
    "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
}
```


### 4. Создать пользователя-клиента RegisterAccount

```
POST http://localhost/user/register
Content-Type: application/json

{
    "first_name": "ser2",
    "last_name":"ser2",
    "email":"medvedevsm1989@yandex.ru",
    "password":"asd12322",
    "company":"asd",
    "position":"1"
}
```
Пример ответа:
```
{
  "Status": true
}
```
### 5. Подтвердить пользователя.
Для подтверждения аккаунта, необходимо перейти по ссылке из письма.
Если сервер запущен с тестовым виртуальным окружением, то прочитать письмо можно командой:
```
docker exec orders bash -c 'cat sent_emails/"$(ls sent_emails -t | head -1)"'
```
Пример ответа:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit
Subject: Password Reset Token for medvedevsm1989@yandex.ru
From: medvedevsm1989@yandex.ru
To: medvedevsm1989@yandex.ru
Date: Sun, 25 Jun 2023 18:30:32 -0000
Message-ID: <168771783212.17.16999434538762680123@57187c599b45>

Перейдите по ссылке для подтверждения:
http://localhost/user/register/confirm?token=824585ce2664e8481ca9f7c41d9d6a8926c&email=medvedevsm1989@yandex.ru
```
Необходимо перейти по ссылке для подтверждения аккаунта.
### 6. Выполнить вход

Пример запроса:
```
POST http://localhost/user/login
Content-Type: application/json

{
    "password":"asd12322",
    "email":"medvedevsm1989@yandex.ru"
}
```
Пример ответа:
```
{
  "Status": true,
  "Token": "f800a9437ea075193d44d44fc365edc728b0a694"
}
```
Токен необходимо сохранить и передавать в заголовке:
```
Authorization: Token {{token}}
```
### 7. Посмотреть категории CategoryView
```
GET http://localhost/categories
Content-Type: application/json
```

### 8. Посмотреть магазины ShopView
```
GET http://localhost/shops
Content-Type: application/json
```

### 9. Посмотреть товары
```
GET http://localhost/products
Content-Type: application/json
```

### 10. Добавить контакты

```
POST http://localhost/user/contact/
Content-Type: application/json
Authorization: Token {{token}}

{
    "city":"Moscow",
    "street":"street 1",
    "house":"452",
    "structure":"1",
    "building":"1",
    "apartment":"33",
    "phone": "88005553555"
}
```
### 11. Получить контакты
```
GET http://localhost/user/contact/
Content-Type: application/json
Authorization: Token {{token}}
```

### 12. Создать корзину

```
POST http://localhost/basket
Content-Type: application/json
Authorization: Token {{token}}


[{"product_info":11,"quantity": 1},{"product_info":12,"quantity": 1}]
```

### 13. Создать заказ
```
POST http://localhost/order
Content-Type: application/json
Authorization: Token {{token}}

{
    "contact": 37
}
```

### 14. Просмотр заказа поставщиком
```
POST http://localhost/user/login
Content-Type: application/json

{
    "password":"admin7712345",
    "email":"admin77@admin.com"
}
```

```
GET http://localhost/partner/orders
Content-Type: application/json
Authorization: Token {{token}}
```
---
Также готовые примеры запросов можно посмотреть [в файле client.http](https://github.com/SergeyMMedvedev/final-diplom/blob/main/client.http).

## Пример конфигурации виртуального окружения с использованием реального почтового сервера

Для настройки почтового сервера необходимо указать дополнительные переменные окружения:

- EMAIL_HOST=<smtp сервер>
- EMAIL_PORT=<порт smtp сервера>
- EMAIL_HOST_USER=<ВАША ПОЧТА>
- EMAIL_HOST_PASSWORD=<токен доступа к почте>

Как получить значения этих переменных окружения, можно прочитать [в этой инструкции](https://proghunter.ru/articles/setting-up-the-smtp-mail-service-for-yandex-in-django).

Команда по созданию .env будет выглядеть так:
```
echo "POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
PG_DB=postgres
PG_HOST=postgresql
PG_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=<smtp сервер>
EMAIL_PORT=<порт smtp сервера>
EMAIL_HOST_USER=<ВАША ПОЧТА>
EMAIL_HOST_PASSWORD=<токен доступа к почте, см ниже>
SERVER_HOST=http://localhost/

DJANGO_SUPERUSER_USERNAME=admin77
DJANGO_SUPERUSER_PASSWORD=admin7712345
DJANGO_SUPERUSER_EMAIL=admin77@admin.com" > .env
```
Пример настройки для работы с Яндекс почтой:

```
echo "POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
PG_DB=postgres
PG_HOST=postgresql
PG_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=medvedevsm1989@yandex.ru
EMAIL_HOST_PASSWORD=************
SERVER_HOST=http://localhost/

DJANGO_SUPERUSER_USERNAME=admin77
DJANGO_SUPERUSER_PASSWORD=admin7712345
DJANGO_SUPERUSER_EMAIL=admin77@admin.com" > .env
```





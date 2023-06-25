# tests.test_basket
## Test07Basket

    Тестируется возможность работы с корзиной пользователя.

    Используется:
     - BasketView
    
### test_02_upd_basket
Клиент может обновить корзину.
### test_03_del_basket
Клиент может удалить товары из корзины.
### test_01_create_basket
Клиент может положить товары в корзину.

**Markers:**
- django_db  (transaction=True)
# test_user_detail
## Test02UserDetail

    Тестирование получения или изменения пользовательских данных.

    Используется:
     - AccountDetails
    
### test_03_update_user_detail
Пользователь обновил свои данные.
### test_01_get_user_detail
Пользователь получает свои данные.

**Markers:**
- django_db  (transaction=True)
### test_02_get_user_detail_not_auth
Не авторизованный пользователь не может получить свои данные.
# tests.test_categories
## Test03Categories

    Тестируется возможность просмотра категорий.
    
    Используется:
     - CategoryView
    
### test_01_get_categories
Получить список категорий товаров.

**Markers:**
- django_db  (transaction=True)
# tests.test_orders
## Test08Orders

    Тестируется возможность получения и размещения заказов пользователями.

    Используется:
     - OrderView
    
### test_01_create_order
Клиент может сделать заказ.

**Markers:**
- django_db  (transaction=True)
# tests.test_partner_orders
## Test09PartnerOrders

    Тестируется возможность получения заказов поставщиками.

    Используется:
     - PartnerOrders
    
### test_01_get_order
Владелец может получить созданный клиентом заказ.

**Markers:**
- django_db  (transaction=True)
# tests.test_partner_state
## Test06PartnerState

    Тестируется возможность работы со статусом поставщика.

    Используется:
     - PartnerState
    
### test_01_get_partner_state
Поставщик получает статус.

**Markers:**
- django_db  (transaction=True)
### test_02_update_partner_state
Поставщик обновляет статус.

**Markers:**
- django_db  (transaction=True)
# tests.test_partner_update
## Test10PartnerUpdate

    Тестирование возможности обновления прайса от поставщика.
    
    Используется:
     - PartnerUpdate
    
### test_01_update_price
Владелец может обновить товары.

**Markers:**
- django_db  (transaction=True)
# tests.test_products
## Test05Products

    Тестируется возможность поиска товаров.

    Используется:
     - ProductInfoView
    
### test_01_get_products
Получить список продуктов.

**Markers:**
- django_db  (transaction=True)
# tests.test_shops
## Test04Shops

    Тестируется возможность просмотра списка магазинов.

    Используется:
     - ShopView
    
### test_01_get_shops
Получить список магазинов.

**Markers:**
- django_db  (transaction=True)
# test_user_auth
## Test01UserAPI

    Тестирование регистрации, подтверждения и авторизации пользователя.

    Тестируются позитивные и негативные сценарии. Участвуют:
     - RegisterAccount
     - ConfirmAccount
     - LoginAccount
    
### test_01_create_user
Пользователь регистрируется.

**Markers:**
- django_db  (transaction=True)
### test_02_create_user_without_req_field

        Пользователь без необходимых полей не создается.

        Отсутствуют поля: first_name, last_name, email, password.
        При отправке не валидного запроса, приходит соответствующий ответ.
        Про отсутствие каждого поля выводится соответствующее сообщение.
        

**Markers:**
- django_db  (transaction=True)
### test_03_create_user_with_bad_password

        Пользователь со слабым паролем не создается.

        При отправке не валидного password выводится соответствующее сообщение.
        

**Markers:**
- django_db  (transaction=True)
### test_04_confirm_user_email

        Пользователь подтверждает регистрацию по ссылке из почты.

        Сценарий:
         - регистрируем пользователя post запросом
         - проверяем, что mail.outbox содержит письмо
         - проверяем успешность get-запроса по ссылке из письма
         - проверяем статус is_active пользователя после подтверждения email
        

**Markers:**
- django_db  (transaction=True)
### test_05_login_user
Пользователь авторизуется.

**Markers:**
- django_db  (transaction=True)
### test_07_login_user_without_req_field

        Пользователь без необходимых полей не авторизуется.

        Отсутствуют поля: email, password.
        При отправке не валидного запроса, приходит соответствующий ответ.
        Про отсутствие каждого поля выводится соответствующее сообщение.
        

**Markers:**
- django_db  (transaction=True)
### test_08_login_not_created_user
Пользователь без регистрации не авторизуется.

**Markers:**
- django_db  (transaction=True)
### test_09_login_not_confirmed_user
Пользователь без подтверждение email не авторизуется.

**Markers:**
- django_db  (transaction=True)
# test_user_contacts
## Test03UserContacts

    Тестируется возможность работы с контактами покупателей.

    Используется:
     - ContactView
    
### test_01_create_user_contact
Пользователь добавил контакт.

**Markers:**
- django_db  (transaction=True)
### test_02_update_user_contact
Пользователь обновил контакт.

**Markers:**
- django_db  (transaction=True)
### test_03_delete_user_contact
Пользователь удалил контакт.

**Markers:**
- django_db  (transaction=True)

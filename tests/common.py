login_data = {
    'email': 'example@mail.com',
    'password': 'asd12322',
}
user_contacts = {
    "city": "Moscow",
    "street": "street 1",
    "house": "1",
    "structure": "1",
    "building": "1",
    "apartment": "1",
    "phone": "88005553555",
}
user_data = {'first_name': 'user1', 'last_name': 'user1', **login_data}
owner_login_data = {
    "email": "example2@mail.com",
    "password": "asdQAZ123",
}
owner_data = {
    "is_superuser": False,
    "first_name": "user2",
    "last_name": "user2",
    "company": "asd",
    "position": "1",
    "username": "sdf",
    "is_active": True,
    "type": "shop",
    **owner_login_data
}

STATUS_ERROR_MSG = 'Неправильный http код ответа'
STATUS_FIELD_ERR = 'Неправильное значение поля Status'
USER_DETAILS_FIELDS = [
    "id",
    "first_name",
    "last_name",
    "email",
    "company",
    "position",
    "contacts",
]


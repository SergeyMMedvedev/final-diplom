login_data = {
    'email': 'example@mail.com',
    'password': 'asd12322',
}

user_data = {'first_name': 'user1', 'last_name': 'user1', **login_data}
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

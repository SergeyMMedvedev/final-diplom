1. Этап 1. Создание и настройка проекта
python -m venv venv
source venv/Scripts/activate
python -m pip install -r requirements.txt

django-admin startproject orders .

python manage.py startapp api
python manage.py makemigrations

python manage.py migrate
python manage.py runserver

2. Этап 2. Проработка моделей данных

python manage.py startapp api
createdb -U postgres orders_db

settings.py
AUTH_USER_MODEL = "api.User"

3. Этап 3. Реализация импорта товаров

Созданы функции загрузки товаров из приложенных файлов в модели Django.
Загружены товары из всех файлов для импорта.

Пользователь должен быть type shop
Для того чтобы это сделать, нужно зайти в админку.
Чтобы зайти в админку, нужно сделать суперпользователя. Чтобы его сделать
мало:
python manage.py createsuperuser
Надо его еще активировать в базе данных

Url может меняться



docker-compose up
docker exec -it orders pytest

For more information, see the [contributor guide index](https://github.com/SergeyMMedvedev/final-diplom/test_doc.md).
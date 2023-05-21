1. Этап 1. Создание и настройка проекта
python -m venv venv
source venv/Scripts/activate
python -m pip install -r requirements.txt

django-admin startproject orders .

python manage.py startapp api
python manage.py makemigrations


python manage.py runserver

2. Этап 2. Проработка моделей данных

python manage.py startapp api
createdb -U postgres orders_db

settings.py
AUTH_USER_MODEL = "api.User"











FROM python:3.11

WORKDIR /code
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000

CMD python3 manage.py collectstatic --noinput && \
    python3 manage.py makemigrations && \
    python3 manage.py migrate --run-syncdb && \
    gunicorn orders.wsgi:application --bind 0.0.0.0:8000

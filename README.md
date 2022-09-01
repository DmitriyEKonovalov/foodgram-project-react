![example event parameter](https://github.com/DmitriyEKonovalov/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

# Сайт Foodgram. Сборник рецептов и продуктовый помощник. 
Реализация модели, API и деплой в рамках дипломного задания Яндекс.Практикум.

#### Автор: Дмитрий Коновалов

## Функциональность:
- Аутентификация пользователей
- Добавление и редактирование рецептов
- работа с ингредиентами и тэгами рецептов
- подписка на авторов рецептов
- добавление рецептов в корзину и в список избранного
- выгрузка ингредиентов по списку из рецептов в корзине
- 
- Позволяет пользователям добавлять рецепты 

## Технологии
- Python / Django / Django ORM / Django Rest Framework
- PostgreSQL
- gunicorn
- nginx

## Установка
1. **Клонируйте репозиторий:**
```sh
https://github.com/DmitriyEKonovalov/foodgram-project-react.git

```

2. **Создать файл .env в папку infra по шаблону**
```sh
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=
# указываем, что работаем с postgresql
DB_ENGINE=django.db.backends.postgresql

# имя базы данных
DB_NAME=postgres

# логин для подключения к базе данных
POSTGRES_USER=postgres

# пароль для подключения к БД (установите свой)
POSTGRES_PASSWORD=postgres

# название сервиса (контейнера)
DB_HOST=db

# порт для подключения к БД
DB_PORT=5432

# для создания админа
DJANGO_SUPERUSER_USERNAME="username"
DJANGO_SUPERUSER_PASSWORD="password"
DJANGO_SUPERUSER_EMAIL="email"
```
**Запустите создание образов и развертывание контейнеров:**
```sh
sudo docker-compose up -d
```
**Миграции и сбор статики:**
```sh
sudo docker-compose exec web python manage.py makemigrations --no-input
sudo docker-compose exec web python manage.py migrate --no-input

sudo docker-compose exec web python manage.py collectstatic --no-input
```

**При необходимости заполните тестовыми данными**
```sh
# создать суперпользователя 
sudo docker-compose exec backend python manage.py createsuperuser
# или создать сразу несколько тестовых пользователей с использованием данных из .env
sudo docker-compose exec web python manage.py create_users

# заполнить базу тестовыми данными
sudo docker-compose exec web python manage.py load_csv
```

# yatube_project
***Социальная сеть блогеров***

**Технологии**

Python 3.9 Django 2.2.19

**Запуск проекта в dev-режиме**

- Установите и активируйте виртуальное окружение:
```sh
python -m venv venv
. venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt:
```sh
pip install -r requirements.txt
```
- Для запуска проекта необходимо сгенерировать SECRET_KEY, перейдите в папку с файлом manage.py выполните:
```sh
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()
YOUR_KEY
>>> quit()
скопировать полученное значение в settings.py SECRET_KEY = 'YOUR_KEY'
```
- Создание таблиц в базе данных:
```sh
python manage.py migrate
```
- После получения и вставки SECRET_KEY, запустить проект:
```sh
python manage.py runserver
Сtrl + C   -> остановить
```
- Наполнение базы данных без файлов media:
```sh
python manage.py shell  
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()
python manage.py loaddata dump.json
```

**Функционал:**

- На сайте можно создать свою страницу.
- После регистрации пользователь получает свой профайл(страницу).
- На сайте есть форма для создания поста и вставки картинки.
- Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи.

***Превью***

![PyDj](/yatube/static/img/final_version.jpg =600x340)
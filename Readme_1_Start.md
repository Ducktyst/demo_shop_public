## Команды создания проекта

В зависимости от операционной системы команды могут отличаться.

Инициализация виртуального окружения

```shell
python -m venv .vemv
```

В Windows
```shell 
source .venv/Scripts/activate
```


В Linux (Unix-систмы)
```shell 
source .venv/bin/activate
```

Установка Django
```shell
python -m pip install Django==4.2
```

Создание проекта 'demoproject' в manage.py в корневой директории.  
Инициализация приложения 'shop'
```shell
django-admin startproject demoproject .  
django-admin startapp shop 
``` 

Применить миграции Django
```shell
python manage.py migrate
```

В settings.py добавить директорию для статики:  
```
STATIC_ROOT = BASE_DIR / 'static
```

Собрать статику Django-админки
```shell
python manage.py collectstatic
```

Запуск Django-сервера
```shell
python manage.py runserver
```

Чтобы Django был на русском, изменить в `settings.py` настройку `LANGUAGE_CODE` на `ru-ru`
```
LANGUAGE_CODE = 'ru-ru'
```


Создать аккаунт администратора
```shell
python manage.py createsuperuser
```

Админ-панель Django будет доступна по адресу:
http://127.0.0.1:8000/admin/

### Ссылки:

1. Инициализация приложения Django с объяснением команд.
В туториале выполняем все шаги до публикации в интернет (Публиковать никуда не нужно, работаем локально).  
Команды из туториала выполнять в зависимости от операционной системы (Windows/Lunux).
[Туториал создание блога на Django (DjangoGirls)](https://tutorial.djangogirls.org/ru/)

### Примечание:
В данном репозитории могут находиться директории `static` `.venv` и файлы бд, например `db.sqlite3`
В продакшн-приложениях они не должны находиться в репозии. В данном случае, они здесь для упрощения работы.

Доступы к бд и прочие чувствительные данные так же не должны храниться в репозитории.

# budget backend

### Зависимости

- Python3.6
- Postgresql 10
- Django 2.2
- Django rest framework
- Redis

#### Настраиваем бд для дева

```sql
CREATE DATABASE budget;
CREATE USER budget WITH password 'budget';
GRANT ALL PRIVILEGES ON DATABASE budget TO budget;
```

### Порядок инициализации приложения

#####1. Установка переменных окружения:

```bash
#export RUNTIME_ENV='dev'
export RUNTIME_ENV='prod'
```

#####2. Применене миграций к базе

```bash
python manage.py migrate
```


#####3. Компилируем словари переводов
```bash
python manage.py compilemessages
```

#####4. Создаем суперюзера для работы

```bash
python manage.py createsuperuser
```



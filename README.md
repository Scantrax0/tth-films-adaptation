# tth-films-adaptation
## Установка
Используется python 3.9.16.

Установить необходимые пакеты:
```
pip install -r requirements.txt
```
Для Linux требуется библиотека lib.gl1. На Cent OS устанавливается так:
```
yum install mesa-libGL
```
Далее необходимо провести миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Создать суперюзера, который будет использоваться для входа в панель администратора:
```
python manage.py createsuperuser
```
## Запуск приложения

Для запуска приложения нужно запустить два процесса - сервер и очередь задач.

Запуск сервера
```
python manage.py runserver
```
Запуск контроллера очереди задач
```
python manage.py process_tasks
```

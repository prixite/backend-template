#!/usr/bin/env bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn -w $1 --worker-tmp-dir /dev/shm app.wsgi:application --bind unix:/dev/shm/gunicorn.sock

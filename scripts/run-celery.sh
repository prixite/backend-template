#!/usr/bin/env bash
celery -A app.celery worker -l INFO -Q 2 -Q default

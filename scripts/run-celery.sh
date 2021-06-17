#!/usr/bin/env bash
celery -A soccer.celery worker -l INFO -Q 2 -Q default

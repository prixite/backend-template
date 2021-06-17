#!/usr/bin/env bash
set -e
coverage run ./manage.py test -v 2 --keepdb "${@:1}"
coverage html
coverage report

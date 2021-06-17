#!/usr/bin/env bash
./manage.py test --keepdb "${@:1}"

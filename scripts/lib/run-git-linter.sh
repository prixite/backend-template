#!/usr/bin/env bash
set -e

# The rules can be found in /.gitlint

range=origin/master..

export LANG=C.UTF-8
gitlint --commits $range

#!/usr/bin/env bash
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR/alembic
alembic revision --autogenerate -m "$1"

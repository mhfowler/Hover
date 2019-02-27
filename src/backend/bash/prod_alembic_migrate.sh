#!/usr/bin/env bash
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR/alembic
SK_FORCE_USE_ENVIRON=PROD alembic upgrade head

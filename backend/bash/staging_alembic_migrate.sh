#!/usr/bin/env bash
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
export PYTHONPATH=$BASEDIR:$PYTHONPATH
cd $BASEDIR/alembic
SK_FORCE_USE_ENVIRON=STAGING alembic upgrade head

#!/usr/bin/env bash
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR
export PYTHONPATH=$BASEDIR:$PYTHONPATH
HELLO_FORCE_USE_ENVIRON=TEST python $BASEDIR/hello_tests/api_tests.py
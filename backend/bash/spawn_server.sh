#!/usr/bin/env bash
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR
export PYTHONPATH=$BASEDIR:$PYTHONPATH
cd $BASEDIR/devops
touch $BASEDIR/devops/hosts
python spawn_server.py
sleep 5
#ansible-playbook -i hosts setup_server.yml
#ansible-playbook -i hosts deploy.yml

#!/usr/bin/env bash
set -e
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR/../frontend
BUILD_ENV=production npm run build
cd $BASEDIR/devops
ansible-playbook -i hosts prod_deploy.yml
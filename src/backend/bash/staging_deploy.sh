#!/usr/bin/env bash
set -e
BASEDIR=$(dirname $( cd $(dirname $0) ; pwd -P ))
cd $BASEDIR
./bash/test.sh
cd $BASEDIR/../frontend
BUILD_ENV=staging npm run build
cd $BASEDIR/devops
ansible-playbook -i hosts staging_deploy.yml
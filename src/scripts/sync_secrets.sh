#!/usr/bin/env bash
set -e
BASEDIR=$( cd $(dirname $0)/.. ; pwd -P )
SECRETDIR=/Users/maxfowler/Dropbox/Hover-Secrets

# Hover_api
rm -r $BASEDIR/Hover_api/devops/secret_files
cp -r $SECRETDIR/Hover_api_secret_files $BASEDIR/Hover_api/devops/secret_files

# msl
rm -r $BASEDIR/message_sending_layer/devops/secret_files
cp -r $SECRETDIR/message_sending_layer_secret_files $BASEDIR/message_sending_layer/devops/secret_files

# dashboard
rm -r $BASEDIR/dashboard/devops/secret_files
cp -r $SECRETDIR/dashboard_secret_files $BASEDIR/dashboard/devops/secret_files
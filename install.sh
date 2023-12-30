#!/bin/bash

read -p "JIRA user name: " USER_NAME
read -p "JIRA api token: " API_TOKEN
read -p "Enter ticket filter string [iOS]: " TICKET_FILTER
TICKET_FILTER=${TICKET_FILTER:-iOS}

echo "USER_NAME=\"$USER_NAME\"" > rt_check/.env
echo "API_TOKEN=\"$API_TOKEN\"" >> rt_check/.env
echo "TICKET_FILTER=\"$TICKET_FILTER\"" >> rt_check/.env
echo "GIT_REPO_PATH=\".\"" >> rt_check/.env

ROOT_PATH=$(cd `dirname $0`/rt_check && pwd)
pushd $ROOT_PATH

poetry install

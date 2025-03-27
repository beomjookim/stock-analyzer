#!/bin/bash

airflow db upgrade

# admin 유저가 없으면 생성
airflow users list | grep admin > /dev/null
if [ $? -ne 0 ]; then
  echo "Creating admin user..."
  airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
else
  echo "Admin user already exists. Skipping creation."
fi

# 웹서버 실행
airflow webserver

#!/bin/bash

until mongo --host mongodb --eval "print(\"Waiting for mongodb to start\")"
do
    sleep 1
done

mongo --host mongodb --eval  "db.getSiblingDB('$DB_NAME').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'$DB_NAME'}]});"


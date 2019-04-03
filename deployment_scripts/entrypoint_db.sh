#!/bin/bash

until mongo --host mongodb --eval "print(\"Waiting for mongodb to start\")"
do
    sleep 1
done

mongo --host mongodb --eval  "db.getSiblingDB('test_db').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'test_db'}]});"
mongo --host mongodb --eval  "db.getSiblingDB('dev_db').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'dev_db'}]});"


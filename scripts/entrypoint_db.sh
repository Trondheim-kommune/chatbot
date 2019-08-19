#!/bin/bash

until mongo --host mongodb --eval "print(\"Waiting for mongodb to start\")"
do
    sleep 1
done


# Check if the users exists already before attempting to create them
DB_DEV_USER_CNT=$(mongo --host mongodb --eval "db.getSiblingDB('dev_chatbot').system.users.find({user:'vegardev'}).count()" | sed -n 5p)
DB_PROD_USER_CNT=$(mongo --host mongodb --eval "db.getSiblingDB('prod_chatbot').system.users.find({user:'vegardev'}).count()" | sed -n 5p)

if [ "$DB_DEV_USER_CNT" -gt 0 ]; then
	mongo --host mongodb --eval "db.getSiblingDB('dev_chatbot').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'dev_chatbot'}]});"
fi
if [ "$DB_PROD_USER_CNT" -gt 0 ]; then
	mongo --host mongodb --eval "db.getSiblingDB('prod_chatbot').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'prod_chatbot'}]});"
fi

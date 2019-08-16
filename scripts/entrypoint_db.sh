#!/bin/bash

until mongo --host mongodb --eval "print(\"Waiting for mongodb to start\")"
do
    sleep 1
done

mongo --host mongodb --eval
"db.getSiblingDB('dev_chatbot').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'dev_chatbot'}]});"
mongo --host mongodb --eval
"db.getSiblingDB('prod_chatbot').createUser({user:'$DB_USER', pwd:'$DB_PWD', roles:[{role:'readWrite',db:'prod_chatbot'}]});"


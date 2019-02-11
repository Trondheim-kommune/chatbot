rsync . agent25@agent25.tinusf.com:/home/agent25/agent-25/api/flask/ -r
rsync ../../model/MongoDBControllerWebhook.py agent25@agent25.tinusf.com:/home/agent25/agent-25/model/MongoDBControllerWebhook.py
ssh agent25@agent25.tinusf.com 'cd /home/agent25/agent-25/api/flask/ && ./start_server_screen.sh'

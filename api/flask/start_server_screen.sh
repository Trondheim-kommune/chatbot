cd /home/agent25/agent-25 && source /home/agent25/agent-25/venv/bin/activate && make
cd /home/agent25/agent-25/api/flask
screen -S flask_dev_serv -X quit
screen -S flask_dev_serv -d -m api/flask/start_server.sh

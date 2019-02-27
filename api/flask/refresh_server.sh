rsync api/flask agent25@agent25.tinusf.com:/home/agent25/agent-25/api/flask/ -r
rsync model/ agent25@agent25.tinusf.com:/home/agent25/agent-25/model/ -r
rsync scraper/ agent25@agent25.tinusf.com:/home/agent25/agent-25/scraper/ -r
ssh agent25@agent25.tinusf.com 'cd /home/agent25/agent-25/api/flask/ && ./start_server_screen.sh'

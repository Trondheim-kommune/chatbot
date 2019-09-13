FROM python:3 as build-deps

# Path to workspace in container
WORKDIR /usr/src/app

# Docker pythonpath having trouble resolving some packages, easy fix
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/chatbot/scraper"

# Install dependencies
RUN apt-get update
RUN apt-get install libssl-dev musl-dev libffi-dev libxslt-dev libstdc++6 -y
RUN apt-get install nginx gcc g++ bash -y cron

# Add requirements
COPY ./requirements.txt .

# Install python packages step
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# Copy all code
COPY . .

# Setup log file
RUN mkdir -p /usr/src/app/logs && touch /usr/src/app/logs/chatbot.log

# Copy cron-job script to the cron.d dir
COPY scripts/crontab /etc/cron.d/chatbot

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/chatbot

# Apply cron job
RUN crontab /etc/cron.d/chatbot

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Setup NGINX config
COPY chatbot/api/nginx.conf /etc/nginx

# Give NGINX access to the uwsgi web socket
RUN chmod 777 -R /tmp && chmod o+t -R /tmp

# Set correct timezone for logging
RUN ln -snf /usr/share/zoneinfo/Europe/Oslo /etc/localtime && echo Europe/Oslo > /etc/timezone

# Install extra package
RUN ["pip", "install", "."]

# Install pakcage
RUN ["python3", "setup.py", "develop"]

CMD ["cron"]

CMD ["./scripts/start_chatbot_docker.sh"]

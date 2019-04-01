FROM python:3

# Path to workspace in container
WORKDIR /usr/src/app

# Docker pythonpath having trouble resolving some packages, easy fix
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/scraper"

# Install dependencies
RUN apt-get update
RUN apt-get install libssl-dev musl-dev libffi-dev libxslt-dev libstdc++ -y
RUN apt-get install gcc g++ bash libstdc++ -y cron

# Add requirements
COPY ./requirements.txt .

# Install python packages step
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# Copy all code
COPY . .

# Add crontab file in the cron directory
ADD deployment_scripts/crontab /etc/cron.d/crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Show which port to expose to the outside
EXPOSE 8080

# Install extra package
RUN ["pip", "install", "."]

# Install pakcage
RUN ["python3", "setup.py", "develop"]

# Start server
CMD ["./start_server_docker.sh"]

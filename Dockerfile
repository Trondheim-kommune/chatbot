FROM python:3

# Path to workspace in container
WORKDIR /usr/src/app

# Docker pythonpath having trouble resolving some packages, easy fix
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/scraper"

# Install dependencies
RUN apt-get update
RUN apt-get install libssl-dev musl-dev libffi-dev libxslt-dev libstdc++ -y
RUN apt-get install gcc g++ bash libstdc++ -y nginx

# Add requirements
COPY ./requirements.txt .

# Install python packages step
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# Copy all code
COPY . .

# Show which port to expose to the outside
EXPOSE 8080

# Install extra package
RUN ["pip3", "install", "-e", "."]

RUN ["python3", "setup.py", "develop"]

COPY nginx.conf /etc/nginx
CMD ["./start_server_docker.sh"]

# Start server
#cmd ["./api/flask/start_server.sh"]

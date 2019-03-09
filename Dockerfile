FROM alpine:3.7

# Path to workspace in container
WORKDIR /usr/src/app

# Install dependencies
RUN apk update && \
 apk add python3 libressl-dev musl-dev libffi-dev libxslt-dev libstdc++ && \
 apk add --virtual .build-deps gcc g++ python3-dev bash libstdc++

# Add requirements
COPY ./requirements.txt .

# Install python packages step
RUN python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# Copy all code
COPY . .

# Show which port to expose to the outside
EXPOSE 8080

# Install extra package
RUN ["pip3", "install", "."]

# Start server
cmd ["./start_server_docker.sh"]

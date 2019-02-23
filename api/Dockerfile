FROM alpine:3.7

# Path to workspace in container
WORKDIR /usr/src/app

# Add requirements
COPY ./requirements.txt .

# Install dependencies
RUN apk update && \
 apk add python3 libressl-dev musl-dev libffi-dev libxslt-dev && \
 apk add --virtual .build-deps gcc g++ python3-dev bash

# Install python packages step
RUN python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# Copy all code
COPY . .

# Run crawler
CMD ["scrapy", "crawl" "trondheim", "-o", "test.csv", "-t", "csv"]
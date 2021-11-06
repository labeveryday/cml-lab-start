FROM python:3.7.12-alpine3.14
LABEL maintainer="Duan Lightfoot <duanl@labeveryday.com>"

EXPOSE 5000

# Install basic utilities
RUN apk add -U \
        python3 \
        py-pip \
        ca-certificates \
        && rm -rf /var/cache/apk/* \
        && pip install --no-cache-dir \
        setuptools \
        wheel

# Copy pip requirements file to app/ of the container
COPY requirements.txt /app/
WORKDIR /app
# Install python dependencies
RUN pip install -r requirements.txt

# Copy all current ./ files app to the /app in the container
COPY . /app

CMD [ "python", "./app/cml_app.py" ]

# Build the container
# docker build -t python:cml_app .

# Run the container
# docker run -it -p 5000:5000 python:cml_app

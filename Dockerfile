FROM python:3.6.8-slim-stretch
WORKDIR /app
COPY . /app
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "cron"]
RUN ["apt-get", "install", "-y", "nano"]
RUN ["apt-get", "install", "-y", "procps"]
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000

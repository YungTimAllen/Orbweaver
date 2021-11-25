# syntax=docker/dockerfile:1
FROM python:3.9.5-slim-buster

COPY . /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "python3", "app.py"]
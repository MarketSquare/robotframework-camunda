FROM python:3-buster as runtime

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade --requirement requirements.txt

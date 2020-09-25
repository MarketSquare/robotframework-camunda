FROM nexus.dpag.io:18078/python:3-buster as runtime

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade --requirement requirements.txt -i https://nexus.dpag.io:8443/nexus/repository/pypi-all/simple

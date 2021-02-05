# Dockerfile for AWS
FROM amazonlinux:2.0.20191016.0

RUN yum install -y python37 && \
    yum install -y python3-pip && \
    yum install -y zip && \
    yum clean all

RUN python3.7 -m pip install --upgrade pip && \
    python3.7 -m pip install virtualenv

COPY aws_requirements.txt /app/

RUN python3.7 -m venv /app/venv

RUN /app/venv/bin/python -m pip install --target /app/python/python -r /app/aws_requirements.txt

RUN cd /app/python && \
    zip -r /app/aws.zip .

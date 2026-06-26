FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

# Install pip and gunicorn web server
RUN pip install --no-cache-dir --upgrade pip
RUN pip install gunicorn==20.1.0

# Install requirements.txt
COPY requirements.txt /

#RUN useradd -m -r appuser && \
#   mkdir /app && \
#   chown -R appuser /app
#USER appuser
RUN pip install --no-cache-dir -r /requirements.txt --only-binary Pillow --only-binary psycopg2-binary

# application files - copied into container
WORKDIR /app

COPY ./camelot /app/camelot
COPY ./projectcamelot /app/projectcamelot
COPY ./static /app/static
COPY LICENSE /app
COPY manage.py /app

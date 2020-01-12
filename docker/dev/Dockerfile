FROM python:3.8.1-buster

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="BusyBeaver -- Development image"

WORKDIR /app

COPY requirements.txt requirements_dev.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements_dev.txt

RUN groupadd -g 901 -r sivdev \
    && useradd -g sivdev -r -u 901 sivdev_user \
    && mkdir /app/logs /home/sivdev_user \
    && chmod -R 777 /app/logs /home/sivdev_user

EXPOSE 5000

# Switch from root user for security
USER sivdev_user

COPY ./ /app

ENTRYPOINT [ "scripts/entrypoint.sh" ]

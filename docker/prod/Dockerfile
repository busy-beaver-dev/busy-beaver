FROM python:3.8.1-buster

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="BusyBeaver -- Production image"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN groupadd -g 901 -r busybeaverdev \
    && useradd -g busybeaverdev -r -u 901 busybeaver_user \
    && mkdir /app/logs /home/busybeaver_user \
    && chmod -R 777 /app/logs /home/busybeaver_user

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 5000

COPY ./ /app

# Switch from root user for security
USER busybeaver_user

ENTRYPOINT [ "scripts/entrypoint.sh" ]

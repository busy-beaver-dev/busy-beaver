FROM python:3.9.0-buster

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="BusyBeaver -- Development image"

ENV PYTHONUNBUFFERED 1
ENV PYTHONASYNCIODEBUG 1
ENV PYTHONTRACEMALLOC 1

WORKDIR /app

COPY requirements.txt requirements_dev.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements_dev.txt

EXPOSE 5000

COPY ./ /app

# Switch from root user for security
RUN groupadd -g 901 -r busybeaverdev \
    && useradd -g busybeaverdev -r -u 901 busybeaver_user \
    && mkdir /home/busybeaver_user \
    && chmod -R 755 /home/busybeaver_user
USER busybeaver_user

ENTRYPOINT [ "scripts/entrypoint.sh" ]

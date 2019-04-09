FROM python:3.7.1-stretch

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="BusyBeaver -- Production image"

WORKDIR /app

COPY requirements.txt /tmp/

RUN groupadd -g 901 -r sivdev \
    && useradd -g sivdev -r -u 901 sivdev_user \
    && pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 5000

# Switch from root user for security
# USER sivdev_user
# TODO: as we are writing logs, we need to be root. find a better solution
COPY ./ /app

ENTRYPOINT [ "scripts/entrypoint.sh" ]

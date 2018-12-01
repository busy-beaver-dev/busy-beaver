FROM python:3.7.1-stretch

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="Image for BusyBeaver"

# Install libyaml
RUN git clone https://github.com/yaml/pyyaml.git /tmp/pyyaml \
    && cd /tmp/pyyaml \
    && python setup.py --without-libyaml install \
    && cd ../../ \
    && rm -rf /tmp/pyyaml

WORKDIR /app

COPY requirements.txt requirements_dev.txt /tmp/
COPY ./ /app

RUN groupadd -g 901 -r sivdev && \
    useradd -g sivdev -r -u 901 sivdev_user && \
    pip install --no-cache-dir -r /tmp/requirements_dev.txt

EXPOSE 5100

# Switch from root user for security
USER sivdev_user

CMD ["uvicorn", "busy_beaver.backend:api", "--host", "0.0.0.0", "--port", "5100"]

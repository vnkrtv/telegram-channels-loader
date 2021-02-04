FROM snakepacker/python:all as builder
MAINTAINER vnkrtv

COPY requirements.txt /mnt/
RUN python3.7 -m venv /usr/share/python3/venv \
 && /usr/share/python3/venv/bin/pip install -U pip \
 && /usr/share/python3/venv/bin/pip install -Ur /mnt/requirements.txt

FROM snakepacker/python:3.7 as base

COPY --from=builder /usr/share/python3/venv /usr/share/python3/venv
COPY . /usr/share/python3/

CMD ["/usr/share/python3/venv/bin/python3.7", "/usr/share/python3/deploy/register_client.py"]
ENTRYPOINT ["/usr/share/python3/venv/bin/python3.7", "/usr/share/python3/main.py"]
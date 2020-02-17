FROM python:3.7-slim
LABEL maintainer="Anton Lebedev <mailbox@lebster.me>"
WORKDIR /updater
RUN apt-get update && apt-get install -y wget curl zip cron rsyslog procps
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /updater
COPY crontab /tmp/crontab
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
# Start cron in the foreground.
CMD [ "cron", "-f" ]

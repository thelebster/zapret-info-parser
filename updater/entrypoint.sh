#!/bin/bash

printenv

touch /etc/cron.d/crontab \
    && echo DESTINATION_DIR=$DESTINATION_DIR >> /etc/cron.d/crontab \
    && echo MONGODB_URI=$MONGODB_URI >> /etc/cron.d/crontab \
    && cat /tmp/crontab >> /etc/cron.d/crontab \
    && cat /etc/cron.d/crontab

chown -R root /etc/cron.d/crontab \
    && chmod 0644 /etc/cron.d/crontab \
    && crontab /etc/cron.d/crontab

exec "$@"

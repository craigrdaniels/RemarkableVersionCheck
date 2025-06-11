FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y cron

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

COPY cron_job /etc/cron.d/remarkable-cron-job
RUN chmod 0644 /etc/cron.d/remarkable-cron-job
RUN chmod a+x /etc/cron.d/remarkable-cron-job
RUN crontab /etc/cron.d/remarkable-cron-job

RUN touch /var/log/cron.log

CMD ["sh", "-c", "cron -f & tail -f /var/log/cron.log"]


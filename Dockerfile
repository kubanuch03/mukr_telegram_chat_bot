FROM python:3.10

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY . /app/

RUN apt-get update
RUN apt-get update && \
    apt-get install -y gettext && \
    apt-get clean && \
    pip install -r requirements.txt

CMD ["bash", "entrypoint.sh"]
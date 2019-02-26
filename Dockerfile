FROM python:3.7-alpine

RUN adduser -D viaauser
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget linux-headers 
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base && pip install --upgrade pip

WORKDIR /home/viaauser
COPY . /home/viaauser/

RUN pip install .

RUN chown -R viaauser:viaauser ./
USER viaauser

EXPOSE 8080

ENTRYPOINT ["uwsgi", "--http", ":8080", "--wsgi-file", "src/server/wsgi.py", "--callable", "application", "--processes", "4", "--threads", "2", "--stats", ":9191" ]

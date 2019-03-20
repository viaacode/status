FROM python:3.7-alpine


RUN apk add --no-cache uwsgi-python3
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /home/viaauser
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/viaauser/

RUN adduser -D viaauser
RUN chown -R viaauser:viaauser ./
USER viaauser

EXPOSE 8080

ENTRYPOINT ["uwsgi", "--http", ":8080", "--wsgi-file", "src/viaastatus/server/wsgi.py", "--callable", "application", "--processes", "4", "--threads", "2", "--stats", ":9191" ]

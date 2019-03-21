FROM python:3.7-alpine

RUN apk --update add --virtual build-dependencies build-base linux-headers
RUN apk --update add pcre-dev
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /home/viaauser
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apk del build-dependencies
RUN rm -fr /var/cache/apk/*

COPY . /home/viaauser/

RUN pip install --no-cache-dir -e .
RUN adduser -D viaauser
RUN chown -R viaauser:viaauser ./
USER viaauser

EXPOSE 8080

ENTRYPOINT [ "./run.sh" ]

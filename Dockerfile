FROM python:3.7-alpine

RUN apk --update add --virtual build-dependencies build-base linux-headers
RUN apk --update add pcre-dev
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir uwsgi
RUN apk --update add nginx
RUN apk --update add supervisor

WORKDIR /home/app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apk del build-dependencies
RUN rm -fr /var/cache/apk/*

COPY . /home/app/

COPY ./docker/nginx-main.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
RUN chown -R nginx:nginx /etc/nginx/nginx.conf

COPY ./docker/uwsgi.ini /home/app/uwsgi.ini
COPY ./docker/run.sh /home/app/run.sh
COPY ./docker/supervisord.conf /etc/supervisord.conf

RUN pip install --no-cache-dir -e .

RUN mkdir /run/nginx
RUN chown -R nginx:nginx ./

# if certificates available, copy ssl configs, else copy plain http configs
RUN test -d /home/app/certs && cp /home/app/docker/nginx-ssl.*.conf /etc/nginx/conf.d/ || cp /home/app/docker/nginx.*.conf /etc/nginx/conf.d/

EXPOSE 8080 8443

CMD ["/usr/bin/supervisord"]

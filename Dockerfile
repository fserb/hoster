FROM debian:buster

RUN apt-get update && \
  apt-get install -y --no-install-suggests --no-install-recommends \
    bash mime-support procps wget python3 python3-pip emacs-nox gnupg less \
    supervisor libmagic1 nginx php php-fpm bzip2 file geoip-database \
    libnginx-mod-http-echo libnginx-mod-http-fancyindex libnginx-mod-http-geoip \
    libnginx-mod-http-uploadprogress \
    php-bz2 php-curl php-dom php-exif php-gd php-iconv php-intl php-memcached \
    php-posix php-soap php-sockets php-sqlite3 php-tokenizer php-xml \
    php-xmlreader php-xmlrpc php-zip && \
  rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir flask Flask-RESTful waitress python-magic

VOLUME /data
VOLUME /www
VOLUME /config

# Nginx
EXPOSE 5000

WORKDIR /app/

RUN groupadd -r www && useradd -r -g www www

RUN rm -f /etc/nginx/conf.d/default.conf

ENV SERVER_PATH "/www"

COPY /app /app/

RUN chmod 777 docker-entrypoint.sh server.py

CMD ["./docker-entrypoint.sh"]

FROM debian:buster

RUN apt-get update && \
  apt-get install -y --no-install-suggests --no-install-recommends \
    nodejs bash mime-support procps wget python3 python3-pip vim gnupg \
    supervisor npm libmagic1 nginx php php-fpm bzip2 file geoip-database \
    libnginx-mod-http-echo libnginx-mod-http-fancyindex libnginx-mod-http-geoip \
    libnginx-mod-http-uploadprogress php-bz2 php-curl php-dom php-exif \
    php-gd php-iconv php-intl php-memcached php-posix php-soap php-sockets \
    php-sqlite3 php-tokenizer php-xml php-xmlreader php-xmlrpc php-zip && \
  npm install -g npm@latest && \
  rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add - && \
  echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list && \
  apt-get update && \
  apt-get install -y mongodb-org && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/lib/mongodb && \
  mv /etc/mongod.conf /etc/mongod.conf.orig

RUN pip3 install --no-cache-dir flask PyMongo Flask-PyMongo Flask-RESTful waitress python-magic

RUN npm install -g -loglevel info --production mongo-express

VOLUME /data
VOLUME /www
VOLUME /config

# Port for MongoDB
EXPOSE 27017

# Port for server.py
EXPOSE 5000

# Nginx
EXPOSE 80

WORKDIR /app/

RUN groupadd -r www && useradd -r -g www www

RUN rm -f /etc/nginx/conf.d/default.conf

ENV SERVER_PATH "/www"

COPY /app /app/

RUN chmod 777 docker-entrypoint.sh server.py

CMD ["./docker-entrypoint.sh"]

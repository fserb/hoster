FROM debian:buster

VOLUME /data
VOLUME /www

RUN groupadd -r mongodb && useradd -r -g mongodb mongodb

RUN apt-get update && \
  apt-get install -y --no-install-suggests --no-install-recommends \
    nodejs bash mime-support procps wget python3 python3-pip vim gnupg \
    supervisor npm && \
  npm install -g npm@latest && \
  rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add - && \
  echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list && \
  apt-get update && \
  apt-get install -y mongodb-org && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/lib/mongodb && \
  mv /etc/mongod.conf /etc/mongod.conf.orig

RUN pip3 install --no-cache-dir flask PyMongo Flask-PyMongo Flask-RESTful waitress

RUN npm install -g -loglevel info --production mongo-express

ENV SERVER_PATH "/www"

COPY docker-entrypoint.sh supervisord.conf server.py /app/

WORKDIR /app/

RUN chmod 777 docker-entrypoint.sh server.py

# Port for MongoDB
EXPOSE 27017

# Port for mongo-express
EXPOSE 8081

# Port for server.py
EXPOSE 5000

CMD ["./docker-entrypoint.sh"]

FROM debian:buster

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
  apt-get install -y --no-install-suggests --no-install-recommends \
    bash mime-support procps wget python3 python3-pip emacs-nox gnupg less \
    libmagic1 nginx bzip2 file geoip-database python3-pygit2 git \
    libnginx-mod-http-echo libnginx-mod-http-fancyindex libnginx-mod-http-geoip \
    libnginx-mod-http-uploadprogress && \
  rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir setuptools supervisor flask Flask-RESTful waitress python-magic

VOLUME /repo
VOLUME /www
VOLUME /config

# Nginx
EXPOSE 5000

WORKDIR /app/

RUN groupadd -r www && useradd -r -g www www

RUN rm -f /etc/nginx/conf.d/default.conf

ENV SERVER_PATH "/www"
ENV SERVER_REPO_PATH "/repo"

COPY /app /app/

RUN chmod 777 docker-entrypoint.sh server.py

CMD ["./docker-entrypoint.sh"]

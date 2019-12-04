FROM debian:bullseye-slim
LABEL maintainer "Fernando Serboncini <fserb@fserb.com>"

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update && \
  apt-get install -y --no-install-suggests --no-install-recommends \
    mime-support python3 python3-pip gnupg \
    libmagic1 nginx bzip2 file python3-pygit2 fcgiwrap \
    libnginx-mod-http-fancyindex && \
  rm -f /etc/nginx/conf.d/default.conf && \
  rm -rf /usr/share/doc && \
  rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir setuptools supervisor flask Flask-RESTful waitress python-magic

ARG BUILD_ENV
RUN if [ "${BUILD_ENV}" = "dev" ]; then apt-get update && \
  apt-get install -y bash procps wget emacs-nox less git ; fi

# Path that will contain git repositories
VOLUME /repo
# Path statically served
VOLUME /www
# Persistent config (nginx)
VOLUME /config

# Nginx
EXPOSE 5000

WORKDIR /app/

ENV SERVER_PATH "/www"
ENV SERVER_REPO_PATH "/repo"

COPY /app /app/

RUN chmod 777 docker-entrypoint.sh server.py

CMD ["./docker-entrypoint.sh"]

FROM postgres
RUN apt-get update && \
    apt-get install -y postgresql-contrib postgresql-postgis && \
    apt-get autoremove -y -qq && \
    rm -rf /var/lib/apt/lists/*

ADD createExtensions.sh /docker-entrypoint-initdb.d/
RUN chmod 755 /docker-entrypoint-initdb.d/createExtensions.sh

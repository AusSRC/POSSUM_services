FROM library/postgres:16.0
RUN apt-get update && apt-get upgrade -y && apt-get install -y postgresql-contrib vim
RUN apt-get install -y postgresql-16-postgis-3
RUN apt-get install -y postgresql-16-pgsphere
COPY *.sql /docker-entrypoint-initdb.d/
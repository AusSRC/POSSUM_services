# POSSUM services

A collection of web services for managing the state of the POSSUM survey. The portal tracks the changes to the database and presents that to the user through a web portal.

## Database

We have a PostgreSQL database to store the state information required for the survey. First you will need to create the postgres user by creating a file `psql.env` in the `db` directory

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

Then you can build the images and deploy the container, which will be required for the web services.

```
docker-compose up --build -d
```

## Web

The web interface uses Django to present an interactive portal to view and manipulate the contents of the database. This relies on having the database service already up and running. In order for the application to be accessible via web you will also need to create and run the `nginx` reverse proxy.

### Static files

To collect static files for the Django application you will need to run a command before building the web service. Create a Python environment, install all of the dependencies (`/possum/requirements.txt`) and then run

```
python3 manage.py collectstatic
```

This should create a bunch of files under `possum/static`. This volume is mounted to the static folder directory that is mounted to nginx so that static files can be accessible to users of the application.

The static volume is mounted to `/opt/services/possum_web/src/static/` inside of the containers. So an alternative for creating the static folders is to run the `collectstatic` command from inside the `possum_web` container and copy the files to the static volume directory.

### Build

This command will build both the `nginx` reverse proxy and the Django `web` services.

```
docker-compose up --build -d
```

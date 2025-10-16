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

The web interface uses Django to present an interactive portal to view and manipulate the contents of the database. This relies on having the database service already up and running (see steps above). In order for the application to be accessible via web you will also need to create and run the `nginx` reverse proxy.

### Build

We use environment variables to set some of the Django settings. To build the application you will need to create a `.env` file and place it under `/possum/possum` with the following variables set:

```
LOCAL = True
DEBUG = True
DJANGO_SECRET_KEY =
ALLOWED_HOSTS =

DATABASE_HOST = possum_db
DATABASE_PORT = 5432
DATABASE_NAME = possum
DATABASE_USER = postgres
DATABASE_PASSWORD = password
SEARCH_PATH = public,possum

EMAIL_HOST_USER =
EMAIL_HOST_PASSORD =
```

Where the Django secret key can be generated with various tools (e.g. https://djecrety.ir/). The second set of database environment variables are for connection to the database, so you will fill these out based on the settings of the deployment of the service above. The third set is for sending user password reset emails (accessed by /password_reset URL). Currently this is generated with gmail app password. To enable a new user to login to Django, you must tick the "staff member" checkbox during registration.

This command will build both the `nginx` reverse proxy and the Django `web` services.

```
docker-compose up --build -d
```

You can find more information about Django settings here: https://docs.djangoproject.com/en/5.1/topics/settings/

### Static files

To collect static files for the Django application you will need to run a command before building the web service. Create a Python environment, install all of the dependencies (`/possum/requirements.txt`) and then run

```
python3 manage.py collectstatic
```

This should create a bunch of files under `possum/static`. This volume is mounted to the static folder directory that is mounted to nginx so that static files can be accessible to users of the application.

The static volume is mounted to `/opt/services/possum_web/src/static/` inside of the containers. So an alternative for creating the static folders is to run the `collectstatic` command from inside the `possum_web` container and copy the files to the static volume directory.


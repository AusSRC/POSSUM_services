# API

TBA

## Tests

We have written a suite of unit tests that can be used to verify a deployment was successful. To run this you will need to deploy:

* possum_db
* possum_web

services at a minimum in a development environment. This has been tested with these services deployed locally.

**NOTE**: this set of tests are not intended to run in a production environment. Please deploy a dev or local copy. They will update the state of the database.

### Setup

Create a `pytest.ini` file in the `possum` directory. It should contain the following content:

```
[pytest]
DJANGO_SETTINGS_MODULE = possum.settings
python_files = tests.py test_*.py *_tests.py
pythonpath = . possum
```

### Running

Run the tests with `pytest` command inside the `possum` directory.

### Known errors

I encountered an error while attempting to run the test locally:

```
django.db.utils.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: could not initiate GSSAPI security context: Unspecified GSS failure
```

To fix this, update the Django settings file `possum/possum/settings.py` at `DATABASES` to include the option to disable GSSAPI.

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': f'-c search_path={SEARCH_PATH}'
        },
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'OPTIONS': {
            'gssencmode': 'disable',  # <-- Add this line
        },
    },
}
```

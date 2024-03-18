# POSSUM services

### Trigger

Long running subscriber background process to manage events (CASDA + internal state changes)

Template `config.ini` file

```
[Database]
host = 127.0.0.1
database = possum
user = admin
password = admin
port = 5432

[RabbitMQ]
dsn =

[Pipeline]
main =
mfs =
mosaic =
username =
```

To run:

```
python3 -m possum
```
CREATE USER "admin";
ALTER USER "admin" WITH PASSWORD 'admin';
ALTER USER "admin" WITH SUPERUSER;
CREATE DATABASE possum WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
ALTER DATABASE possum OWNER TO "admin";
CREATE USER "gavo";
ALTER USER "gavo" WITH PASSWORD 'gavo';
CREATE USER "gavoadmin";
ALTER USER "gavoadmin" WITH PASSWORD 'gavoadmin';
CREATE USER "untrusted";
ALTER USER "untrusted" WITH PASSWORD 'untrusted';
\c possum
CREATE SCHEMA possum;
ALTER SCHEMA possum OWNER TO admin;
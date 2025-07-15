-- Enable dblink extension
CREATE EXTENSION IF NOT EXISTS dblink;

-- Create admin user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin') THEN
        CREATE USER "admin" WITH PASSWORD 'admin';
        ALTER USER "admin" WITH SUPERUSER;
    END IF;
END $$;

-- Create possum database if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'possum') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE possum WITH TEMPLATE = template0 ENCODING = ''UTF8'' LC_COLLATE = ''en_US.utf8'' LC_CTYPE = ''en_US.utf8''');
        PERFORM dblink_exec('dbname=postgres', 'ALTER DATABASE possum OWNER TO "admin"');
    END IF;
END $$;

-- Create gavo user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gavo') THEN
        CREATE USER "gavo" WITH PASSWORD 'gavo';
    END IF;
END $$;

-- Create gavo user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'possum_user') THEN
        CREATE USER "possum_user" WITH PASSWORD 'possum_user';
    END IF;
END $$;

-- Create gavoadmin user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gavoadmin') THEN
        CREATE USER "gavoadmin" WITH PASSWORD 'gavoadmin';
    END IF;
END $$;

-- Create untrusted user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'untrusted') THEN
        CREATE USER "untrusted" WITH PASSWORD 'untrusted';
    END IF;
END $$;

-- Connect to possum database
\c possum

-- Create possum schema if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'possum') THEN
        CREATE SCHEMA possum;
        ALTER SCHEMA possum OWNER TO admin;
    END IF;
END $$;
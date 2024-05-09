#!/bin/bash
set -e

# PostgreSQL user, database, and extension setup as superuser
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER tritsk WITH PASSWORD '0000';
    CREATE DATABASE tritsk;
    GRANT ALL PRIVILEGES ON DATABASE tritsk TO tritsk;
    ALTER DATABASE tritsk OWNER TO tritsk;
EOSQL

# Connect to the 'tritsk' database to set up schema and extensions
psql -v ON_ERROR_STOP=1 --username "tritsk" --dbname "tritsk" <<-EOSQL
    -- Ensure the extension is available
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    -- Make 'tritsk' the owner of the public schema
    ALTER SCHEMA public OWNER TO tritsk;
EOSQL

# Execute a SQL file to set up the database schema and initial data
psql -v ON_ERROR_STOP=1 --username "tritsk" --dbname "tritsk" -f /docker-entrypoint-initdb.d/setup.sql

#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# This script will be executed by the PostgreSQL container on startup.
# It connects to the database specified by POSTGRES_DB, POSTGRES_USER
# and creates the pgvector extension.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
    -- You can add your table creation statements here as well if you like
    -- For example:
    /*
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL UNIQUE,
        overview TEXT,
        genres TEXT[],
        release_year INTEGER,
        poster_url TEXT,
        rating FLOAT,
        popularity FLOAT,
        embedding VECTOR(384) -- Adjust dimension as needed
    );

    -- Example index (create AFTER data is loaded for IVFFlat, or anytime for HNSW)
    -- CREATE INDEX ON movies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    -- CREATE INDEX ON movies USING hnsw (embedding vector_cosine_ops);
    */
EOSQL

echo "pgvector extension created (if it didn't exist)."
# You can add more SQL files to this directory (e.g., 02_create_tables.sql)
# and they will be executed in alphabetical order.
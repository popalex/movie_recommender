# movie_recommender/data_ingestion/populate_db.py

import psycopg2
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
# numpy is often a dependency of sentence-transformers, but not directly used here for SQL conversion
# psycopg2 can handle Python lists of floats for vector types if pgvector is set up.

# --- Configuration ---
# Load environment variables from .env file at the project root
# Adjust the path if your script is in a different subdirectory level
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DB_HOST = os.getenv("DB_HOST", "localhost") # Use a specific var or default to localhost for direct run
DB_PORT = os.getenv("DB_PORT", "5433")      # The host port mapped in docker-compose.yml
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Sentence Transformer model
MODEL_NAME = 'all-MiniLM-L6-v2' # Good balance of performance and size
EMBEDDING_DIM = 384 # This model outputs 384-dimensional embeddings

# Sample movie data
SAMPLE_MOVIES = [
    {
        "title": "Inception",
        "overview": "A thief who steals information by entering people's dreams is offered a chance to have his criminal history erased as payment for a task considered to be impossible: 'inception', the implantation of another person's idea into a target's subconscious.",
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "release_year": 2010,
        "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkWTjdSJpzKueLQo.jpg",
        "rating": 8.8,
        "popularity": 150.0
    },
    {
        "title": "The Shawshank Redemption",
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "genres": ["Drama", "Crime"],
        "release_year": 1994,
        "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "rating": 9.3,
        "popularity": 120.0
    },
    {
        "title": "The Dark Knight",
        "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "genres": ["Action", "Crime", "Drama"],
        "release_year": 2008,
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6oLPYkXc2Yb.jpg",
        "rating": 9.0,
        "popularity": 180.0
    },
    {
        "title": "Pulp Fiction",
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "genres": ["Thriller", "Crime"],
        "release_year": 1994,
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "rating": 8.9,
        "popularity": 140.0
    },
    {
        "title": "Forrest Gump",
        "overview": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
        "genres": ["Comedy", "Drama", "Romance"],
        "release_year": 1994,
        "poster_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "rating": 8.8,
        "popularity": 130.0
    },
    {
        "title": "The Matrix",
        "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "genres": ["Action", "Sci-Fi"],
        "release_year": 1999,
        "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "rating": 8.7,
        "popularity": 160.0
    },
    {
        "title": "Interstellar",
        "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "genres": ["Adventure", "Drama", "Sci-Fi"],
        "release_year": 2014,
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "rating": 8.6,
        "popularity": 200.0
    },
    # TV Series examples
    {
        "title": "Breaking Bad",
        "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future.",
        "genres": ["Crime", "Drama", "Thriller"],
        "release_year": 2008, # Year first aired
        "poster_url": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
        "rating": 9.5,
        "popularity": 250.0
    },
    {
        "title": "Stranger Things",
        "overview": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces, and one strange little girl.",
        "genres": ["Drama", "Fantasy", "Horror", "Mystery", "Sci-Fi", "Thriller"],
        "release_year": 2016,
        "poster_url": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
        "rating": 8.6,
        "popularity": 300.0
    },
    {
        "title": "The Office (US)",
        "overview": "A mockumentary on a group of typical office workers, where the workday consists of ego clashes, inappropriate behavior, and tedium.",
        "genres": ["Comedy"],
        "release_year": 2005,
        "poster_url": "https://image.tmdb.org/t/p/w500/qWnJzyZhyy74gjpSjIXH4Hfort7.jpg",
        "rating": 8.5,
        "popularity": 100.0
    }
]

def get_db_connection():
    """Establishes connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Database connection successful.")
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print(f"Connection parameters: host={DB_HOST}, port={DB_PORT}, dbname={POSTGRES_DB}, user={POSTGRES_USER}")
        raise
    return conn

def create_movies_table_if_not_exists(conn):
    """Creates the movies table if it doesn't already exist."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        overview TEXT,
        genres TEXT[],
        release_year INTEGER,
        poster_url TEXT,
        rating FLOAT,
        popularity FLOAT,
        embedding VECTOR({EMBEDDING_DIM}),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT unique_movie_title UNIQUE (title) -- Ensures titles are unique for ON CONFLICT
    );
    """
    # Index for faster similarity search (can be created after data is loaded)
    # Choose one: IVFFlat is faster to build but might have lower recall for exact KNN. HNSW is often preferred.
    # create_index_query_ivfflat = "CREATE INDEX IF NOT EXISTS movies_embedding_ivfflat_idx ON movies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
    create_index_query_hnsw = f"CREATE INDEX IF NOT EXISTS movies_embedding_hnsw_idx ON movies USING hnsw (embedding vector_cosine_ops);"

    # Trigger to update updated_at timestamp
    create_trigger_function_query = """
    CREATE OR REPLACE FUNCTION trigger_set_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    create_trigger_query = """
    DROP TRIGGER IF EXISTS set_timestamp_movies ON movies;
    CREATE TRIGGER set_timestamp_movies
    BEFORE UPDATE ON movies
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();
    """

    with conn.cursor() as cur:
        print("Creating movies table (if it doesn't exist)...")
        cur.execute(create_table_query)
        print("Creating HNSW index for embeddings (if it doesn't exist)...")
        cur.execute(create_index_query_hnsw) # Or IVFFlat
        print("Creating/Updating timestamp trigger function and trigger...")
        cur.execute(create_trigger_function_query)
        cur.execute(create_trigger_query)
        conn.commit()
        print("Table and index setup complete.")

def populate_data():
    """Fetches sample movies, generates embeddings, and upserts them into the database."""
    conn = None
    try:
        conn = get_db_connection()
        create_movies_table_if_not_exists(conn) # Ensure table and index exist

        print(f"Loading sentence transformer model: {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        print("Model loaded.")

        with conn.cursor() as cur:
            for movie in SAMPLE_MOVIES:
                title = movie["title"]
                overview = movie.get("overview", "")
                genres = ", ".join(movie.get("genres", [])) # Comma-separated string for embedding

                # Create a comprehensive text string for embedding
                text_to_embed = f"Title: {title}. Overview: {overview}. Genres: {genres}."

                print(f"Generating embedding for: {title}")
                embedding = model.encode(text_to_embed).tolist() # Encode and convert to Python list

                # Upsert logic: Insert if title doesn't exist, update if it does
                # The unique_movie_title constraint on `title` is used for ON CONFLICT
                upsert_query = f"""
                INSERT INTO movies (title, overview, genres, release_year, poster_url, rating, popularity, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::VECTOR({EMBEDDING_DIM}))
                ON CONFLICT (title) DO UPDATE SET
                    overview = EXCLUDED.overview,
                    genres = EXCLUDED.genres,
                    release_year = EXCLUDED.release_year,
                    poster_url = EXCLUDED.poster_url,
                    rating = EXCLUDED.rating,
                    popularity = EXCLUDED.popularity,
                    embedding = EXCLUDED.embedding,
                    updated_at = NOW();
                """
                cur.execute(upsert_query, (
                    title,
                    movie.get("overview"),
                    movie.get("genres"),
                    movie.get("release_year"),
                    movie.get("poster_url"),
                    movie.get("rating"),
                    movie.get("popularity"),
                    embedding # Pass as list, PostgreSQL with pgvector handles conversion
                ))
                print(f"Upserted: {title}")

            conn.commit()
            print("All sample movies have been processed and upserted.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while populating data: {error}")
        if conn:
            conn.rollback() # Rollback changes on error
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting database population script...")
    populate_data()
    print("Database population script finished.")
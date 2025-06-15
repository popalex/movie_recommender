from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # For React frontend
import psycopg2
import numpy as np
import os
import random
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector # Import the registration function

# Load environment variables from .env file
load_dotenv(dotenv_path="../../.env") # Adjust path if .env is elsewhere relative to main.py

app = FastAPI()

# --- CORS ---
# Allow your React frontend to communicate (adjust origins as needed)
origins = [
    "http://localhost:3000", # Default React dev port
    "http://127.0.0.1:3000",
    "http://localhost:5173", # React Vite dev port
    # Add your deployed frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],       # TEMPORARY DEBUG: DO NOT USE IN PROD !!!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END CORS ---


# Database connection details from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        register_vector(conn)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        # In a real app, you might want a more robust retry or error handling
        raise HTTPException(status_code=503, detail="Database connection error")


@app.on_event("startup")
async def startup_event():
    # You can add a check here to ensure DB is accessible or tables exist
    print("Application startup: Attempting to connect to database...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;") # Simple query to test connection
        print("Database connection successful.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to connect to database on startup: {e}")
        # Decide if the app should fail to start or continue with degraded functionality

@app.post("/recommend")
async def recommend_movies(titles: list[str]):
    # Validate input length
    if len(titles) != 3:
        raise HTTPException(status_code=400, detail="Please provide exactly 3 movie/TV titles.")
    # Validate that no title is empty or blank
    for title in titles:
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(status_code=400, detail="Input titles must be non-empty strings")

    conn = get_db_connection()
    cursor = conn.cursor()

    embeddings = []
    input_movie_ids = []

    for title_input in titles:
        # Use ILIKE for case-insensitive search and exact match on title (or fuzzy match)
        # You might need more sophisticated title matching in a real app
        cursor.execute(
            "SELECT id, embedding FROM movies WHERE lower(title) = lower(%s) LIMIT 1",
            (title_input.strip(),)
        )
        result = cursor.fetchone()
        if result:
            input_movie_ids.append(result[0])
            embeddings.append(np.array(result[1]))
        else:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Movie '{title_input}' not found.")

    if not embeddings:
        cursor.close()
        conn.close()
        # This case should ideally be caught by the loop above
        raise HTTPException(status_code=404, detail="None of the input movies were found.")

    profile_vector = np.mean(embeddings, axis=0)
    profile_vector_str = "[" + ",".join(map(str, profile_vector)) + "]"

    placeholders = ','.join(['%s'] * len(input_movie_ids))
    query = f"""
        SELECT id, title, overview, poster_url, release_year
        FROM movies
        WHERE id NOT IN ({placeholders})
        ORDER BY embedding <=> %s::vector
        LIMIT 10;
    """
    params = list(input_movie_ids) + [profile_vector_str]
    cursor.execute(query, tuple(params))
    recommendations_raw = cursor.fetchall()
    cursor.close()
    conn.close()

    recommendations = [
        {"id": r[0], "title": r[1], "overview": r[2], "poster_url": r[3], "release_year": r[4]}
        for r in recommendations_raw[:3]
    ]
    return {"recommendations": recommendations}

@app.get("/surprise")
async def surprise_me():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, overview, poster_url, release_year
        FROM movies
        WHERE rating IS NOT NULL AND popularity IS NOT NULL AND rating > 7.0 AND popularity > 100 -- Adjust as needed
        ORDER BY RANDOM()
        LIMIT 3;
    """)
    surprises_raw = cursor.fetchall()
    cursor.close()
    conn.close()

    if not surprises_raw:
        raise HTTPException(status_code=404, detail="Could not find surprise movies. DB might be empty or criteria too strict.")

    surprises = [
        {"id": r[0], "title": r[1], "overview": r[2], "poster_url": r[3], "release_year": r[4]}
        for r in surprises_raw
    ]
    return {"surprises": surprises}

# To run locally using uvicorn directly (outside Docker for quick tests):
# cd movie_recommender/backend
# uvicorn app.main:app --reload --port 8000
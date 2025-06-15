import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root (parent of 'tests' and 'backend') to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
# Add the backend directory to sys.path
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

# Import your FastAPI app instance and the module it resides in
try:
    from app.main import app  # Your FastAPI application instance
    import app.main as app_main_module # The module itself for patching
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import FastAPI app or module from app.main.")
    print(f"ImportError: {e}")
    print(f"Current sys.path: {sys.path}")
    print("Please ensure:")
    print(f"1. The 'backend' directory is at: {os.path.join(PROJECT_ROOT, 'backend')}")
    print(f"2. Your FastAPI instance in 'backend/app/main.py' is named 'app'.")
    print(f"3. There are no syntax errors in 'backend/app/main.py' preventing its import.")
    raise # Re-raise the error to stop test collection if app can't be imported

# Ensure 'app.main.psycopg2' exists or adjust the patch target.
# This means 'app/main.py' should have 'import psycopg2'
@patch('app.main.psycopg2.connect') # Patch where 'connect' is used
async def test_get_db_connection_internal_error_handling(mock_psycopg2_connect, client: AsyncClient):
    """
    Tests if the actual get_db_connection function in app.main
    correctly handles psycopg2.OperationalError from psycopg2.connect
    and raises an HTTPException(503).
    """
    mock_psycopg2_connect.side_effect = psycopg2.OperationalError("Simulated actual connect failure")

    # We are not using the mock_db_connection fixture here because we want
    # the *real* get_db_connection to run, with only psycopg2.connect mocked.

    response = await client.get("/surprise") # This will trigger a call to the real get_db_connection

    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "Database connection error"
    mock_psycopg2_connect.assert_called_once()

@pytest_asyncio.fixture(scope="session")
async def client():
    """
    An asynchronous test client for the FastAPI app.
    Uses ASGITransport for direct in-memory testing.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def mock_db_connection():
    """
    Mocks the database connection and cursor.
    Always yields (mock_get_conn, mock_cursor).
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Default behavior for cursor methods (can be overridden in individual tests)
    mock_cursor.fetchone.return_value = None # Default to "not found"
    mock_cursor.fetchall.return_value = []   # Default to empty list

    # Patch 'get_db_connection' in the module where it's defined (app_main_module)
    # This assumes get_db_connection is a top-level function in app.main
    with patch.object(app_main_module, 'get_db_connection', return_value=mock_conn) as mock_get_conn:
        yield mock_get_conn, mock_cursor

# --- Sample Data for Mocking ---
# These can be used by tests to configure mock return values.
# Dimensions for embeddings (e.g., 384 for all-MiniLM-L6-v2)
EMBEDDING_DIM = 384

SAMPLE_MOVIE_EMBEDDINGS = {
    # title: (id, embedding_list)
    "Inception": (1, [0.1] * EMBEDDING_DIM),
    "The Dark Knight": (2, [0.2] * EMBEDDING_DIM),
    "Interstellar": (3, [0.3] * EMBEDDING_DIM),
    "Pulp Fiction": (4, [0.4] * EMBEDDING_DIM),
    "Breaking Bad": (5, [0.5] * EMBEDDING_DIM), # TV Series example
}

# Sample movie details that would be returned by a recommendation or surprise query
# (id, title, overview, poster_url, release_year)
SAMPLE_RECOMMENDATION_DETAILS = [
    (101, "Recommended Movie 1", "Overview for Recommended Movie 1", "/poster1.jpg", 2020),
    (102, "Recommended Movie 2", "Overview for Recommended Movie 2", "/poster2.jpg", 2021),
    (103, "Recommended Movie 3", "Overview for Recommended Movie 3", "/poster3.jpg", 2022),
    (104, "Recommended Movie 4", "Overview for Recommended Movie 4", "/poster4.jpg", 2023), # Extra for fetching more
]

SAMPLE_SURPRISE_DETAILS = [
    (201, "Surprise Movie Alpha", "Overview for Surprise Movie Alpha", "/posterA.jpg", 2018),
    (202, "Surprise Movie Beta", "Overview for Surprise Movie Beta", "/posterB.jpg", 2019),
    (203, "Surprise Movie Gamma", "Overview for Surprise Movie Gamma", "/posterC.jpg", 2017),
]
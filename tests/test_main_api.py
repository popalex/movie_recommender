from unittest.mock import patch
import pytest
from httpx import AsyncClient
import psycopg2 # For psycopg2.OperationalError

# Import sample data from conftest
from tests.conftest import (
    SAMPLE_MOVIE_EMBEDDINGS,
    SAMPLE_RECOMMENDATION_DETAILS,
    SAMPLE_SURPRISE_DETAILS
)

# Mark all tests in this module to use pytest-asyncio for async functions
pytestmark = pytest.mark.asyncio


async def test_api_docs_accessible(client: AsyncClient):
    """
    Test if the FastAPI auto-generated /docs endpoint is available.
    """
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text # Basic check for Swagger page content

async def test_recommend_movies_success(client: AsyncClient, mock_db_connection):
    """Test successful movie recommendation when all input movies are found."""
    mock_get_conn, mock_cursor = mock_db_connection
    input_titles = ["Inception", "The Dark Knight", "Interstellar"]

    # --- Revised Mocking for fetchone ---
    # We'll create a list of expected results for the fetchone calls
    # in the order they will be made.
    expected_fetchone_results = []
    for title_input in input_titles:
        found = False
        for movie_key, (movie_id, emb_vector) in SAMPLE_MOVIE_EMBEDDINGS.items():
            if movie_key.lower() == title_input.lower():
                expected_fetchone_results.append((movie_id, emb_vector))
                found = True
                break
        if not found:
            expected_fetchone_results.append(None) # Should not happen in this success test

    # Make mock_cursor.fetchone.side_effect an iterator or a callable that pops from this list
    call_count_fetchone = 0
    def fetchone_side_effect_handler():
        nonlocal call_count_fetchone
        if call_count_fetchone < len(expected_fetchone_results):
            result = expected_fetchone_results[call_count_fetchone]
            call_count_fetchone += 1
            return result
        return None # Should not be reached if logic is correct

    mock_cursor.fetchone.side_effect = fetchone_side_effect_handler
    # --- End Revised Mocking for fetchone ---

    mock_cursor.fetchall.return_value = SAMPLE_RECOMMENDATION_DETAILS[:3]

    response = await client.post("/recommend", json=input_titles)

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 3
    # ... (rest of assertions)
    mock_get_conn.assert_called_once()
    assert mock_cursor.execute.call_count == 4 # 3 for input, 1 for recommendation
    assert call_count_fetchone == 3 # Ensure fetchone was called 3 times


async def test_recommend_movies_one_input_not_found(client: AsyncClient, mock_db_connection):
    """Test recommendation fails if one input movie is not found."""
    mock_get_conn, mock_cursor = mock_db_connection
    input_titles = ["Inception", "This Movie Does Not Exist In DB", "Interstellar"]

    # --- Revised Mocking for fetchone ---
    expected_fetchone_results = []
    for title_input in input_titles:
        found = False
        title_to_check = title_input.lower()
        if title_to_check == "this movie does not exist in db":
            expected_fetchone_results.append(None) # Simulate not found
            found = True
        else:
            for movie_key, (movie_id, emb_vector) in SAMPLE_MOVIE_EMBEDDINGS.items():
                if movie_key.lower() == title_to_check:
                    expected_fetchone_results.append((movie_id, emb_vector))
                    found = True
                    break
        if not found and title_to_check != "this movie does not exist in db": # Should not happen for existing titles
            expected_fetchone_results.append(None)

    call_count_fetchone = 0
    def fetchone_side_effect_handler():
        nonlocal call_count_fetchone
        if call_count_fetchone < len(expected_fetchone_results):
            result = expected_fetchone_results[call_count_fetchone]
            call_count_fetchone += 1
            return result
        # This might be called if your app logic tries to fetchone more than expected
        # or if the list wasn't populated correctly.
        # For this test, it might indicate an issue if called more than 3 times.
        pytest.fail(f"fetchone called too many times. Expected {len(expected_fetchone_results)}, called {call_count_fetchone + 1}")
        return None

    mock_cursor.fetchone.side_effect = fetchone_side_effect_handler
    # --- End Revised Mocking for fetchone ---

    response = await client.post("/recommend", json=input_titles)

    assert response.status_code == 404
    data = response.json()
    assert "Movie 'This Movie Does Not Exist In DB' not found" in data["detail"]
    mock_get_conn.assert_called_once()
    # `execute` would be called twice before the error (for Inception, then for the non-existent one)
    # The exact number of execute calls before failure depends on where the loop breaks in your app.main.py
    # If it breaks immediately on first not found:
    assert mock_cursor.execute.call_count >= 1 and mock_cursor.execute.call_count <= 2
    assert call_count_fetchone >= 1 and call_count_fetchone <= 2


async def test_recommend_movies_incorrect_input_count(client: AsyncClient):
    """Test recommendation fails if not exactly 3 movies are provided."""
    # Test with 2 movies
    response_two = await client.post("/recommend", json=["Inception", "The Dark Knight"])
    assert response_two.status_code == 400 # Or 422 if using Pydantic model validation for list length
    data_two = response_two.json()
    assert "Please provide exactly 3 movie/TV titles" in data_two["detail"]

    # Test with 4 movies
    response_four = await client.post("/recommend", json=["Inception", "The Dark Knight", "Interstellar", "Pulp Fiction"])
    assert response_four.status_code == 400
    data_four = response_four.json()
    assert "Please provide exactly 3 movie/TV titles" in data_four["detail"]


async def test_surprise_me_success(client: AsyncClient, mock_db_connection):
    """Test successful /surprise endpoint."""
    mock_get_conn, mock_cursor = mock_db_connection

    # Configure mock_cursor.fetchall for the surprise movie lookup
    mock_cursor.fetchall.return_value = SAMPLE_SURPRISE_DETAILS # Return 3 surprise movies

    response = await client.get("/surprise")

    assert response.status_code == 200
    data = response.json()
    assert "surprises" in data
    assert len(data["surprises"]) == 3
    assert data["surprises"][0]["title"] == SAMPLE_SURPRISE_DETAILS[0][1]
    assert data["surprises"][1]["id"] == SAMPLE_SURPRISE_DETAILS[1][0]

    mock_get_conn.assert_called_once()
    mock_cursor.execute.assert_called_once() # Expect one SQL query for surprise
    # Optional: Inspect the surprise query
    query_sql = mock_cursor.execute.call_args[0][0]
    assert "ORDER BY RANDOM()" in query_sql # Check if random ordering is part of the query


async def test_surprise_me_no_movies_found_in_db(client: AsyncClient, mock_db_connection):
    """Test /surprise endpoint when the database returns no movies matching criteria."""
    mock_get_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [] # Simulate database returning no movies

    response = await client.get("/surprise")

    assert response.status_code == 404
    data = response.json()
    assert "Could not find surprise movies" in data["detail"] # Match your API's error message
    mock_get_conn.assert_called_once()


# This test will NOT use the mock_db_connection fixture
# because we want the real get_db_connection to run.
@patch('app.main.psycopg2.connect') # Patch where 'psycopg2.connect' is called (in app.main)
async def test_database_connection_error_scenario(mock_psycopg2_connect_call, client: AsyncClient):
    """
    Tests if the *actual* get_db_connection function in app.main
    correctly handles psycopg2.OperationalError from psycopg2.connect
    and converts it to an HTTPException(503).
    """
    # Configure the mock for psycopg2.connect to raise OperationalError
    mock_psycopg2_connect_call.side_effect = psycopg2.OperationalError(
        "Simulated DB connection error from psycopg2.connect"
    )

    # Make a request to an endpoint that calls the real get_db_connection
    response = await client.get("/surprise") 

    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "Database connection error"

    # Assert that psycopg2.connect was actually called
    mock_psycopg2_connect_call.assert_called_once()
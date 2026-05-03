import requests
import psycopg2
import pytest  



def test_youtube_api_response(airflow_variable):
    api_key = airflow_variable("api_key")
    channel_handle = airflow_variable("channel_handle")

    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&forUsername={channel_handle}&key={api_key}"
    
    
    try: 
        response =requests.get(url)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    except Exception as e:
        pytest.fail(f"API request failed: {e}")
    

def test_real_postgres_connection(real_postgres_conn):
    cursor = None
    
    try:
        cursor = real_postgres_conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        assert result[0] == 1
    
    except Exception as e:
        pytest.fail(f"Database query failed: {e}")
    
    finally:
        if cursor is not None:
            cursor.close()
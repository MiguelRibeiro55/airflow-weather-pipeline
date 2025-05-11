from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging
import os




logger = logging.getLogger("airflow")

def create_table_if_not_exists():
    pg_hook = PostgresHook(postgres_conn_id='postgres_weather')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Create the table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        temperature REAL NOT NULL,
        description VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Table weather_data is ready.")

def fetch_weather_data(**kwargs):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    
    if not api_key:
        logger.error("API key is not set. Please check environment variables.")
        raise ValueError("Missing API key.")
    
    city = "Amsterdam"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    
    response = requests.get(url)
    weather_data = response.json()
    
    if response.status_code == 200:
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        timestamp = datetime.now().isoformat()  # Timestamp for when the data was fetched
        
        # Pass the data and timestamp for further processing
        kwargs['ti'].xcom_push(key='weather_data', value={'timestamp': timestamp, 'temp': temp, 'description': description})
        
        logger.info(f"Current weather in {city}: {temp}ºC, {description} at {timestamp}")
    else:
        logger.error(f"Failed to fetch weather data: {weather_data.get('message')}")
        raise ValueError(f"Failed to fetch weather data: {weather_data.get('message')}")

def append_to_database(**kwargs):
    
    weather_data = kwargs['ti'].xcom_pull(task_ids='fetch_weather_data', key='weather_data')
    
    if not weather_data:
        logger.warning("No weather data to insert.")
        return
    
    pg_hook = PostgresHook(postgres_conn_id='postgres_weather')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM weather_data WHERE timestamp = %s", (weather_data['timestamp'],))
    
    if cursor.fetchone()[0] == 0:
        
        query = """
        INSERT INTO weather_data (timestamp, temperature, description)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(query, (weather_data['timestamp'], weather_data['temp'], weather_data['description']))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Weather data inserted into database.")
    
    else:
        logger.info("Duplicate timestamp. Skipping insert.")

    
    
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 10),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=10),
}

dag = DAG(
    'weather_data',
    default_args=default_args,
    schedule_interval='@daily',  # Runs once a day
    catchup=False,
)

# Create the table if it doesn't exist
create_table_task = PythonOperator(
    task_id='create_table',
    python_callable=create_table_if_not_exists,
    dag=dag
)

fetch_task = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    provide_context=True,
    dag=dag
)

append_task = PythonOperator(
    task_id='append_to_database',
    python_callable=append_to_database,
    provide_context=True,
    dag=dag
)

# Set the task dependencies
create_table_task >> fetch_task >> append_task

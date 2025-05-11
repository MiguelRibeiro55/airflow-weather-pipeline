# 🌤️ Weather Data Pipeline with Apache Airflow

This project is an end-to-end data pipeline built using **Apache Airflow** that collects daily weather data for **Amsterdam** from the **OpenWeatherMap API**, and stores it in a **PostgreSQL** database.

## 📦 Features

- 🕒 **Scheduled ETL**: Runs daily via Airflow DAGs.
- 🔍 **Deduplication**: Avoids inserting the same data twice using timestamp checks.
- 🌐 **API Integration**: Fetches real-time weather data (temperature, description).
- 🗄️ **PostgreSQL Storage**: Persists weather data with schema validation.

## 📁 Project Structure

```
.
├── dags/
│   └── weather_pipeline.py      # Airflow DAG definition
├── docker-compose.yml           # Docker setup for Airflow and PostgreSQL
├── .env                         # Environment variables (e.g., OpenWeatherMap API key)
└── README.md                    # Project documentation
```

## ⚙️ Technologies

- Apache Airflow 2.8.1 (Python 3.10)
- PostgreSQL 13
- Docker & Docker Compose
- OpenWeatherMap API

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-data-pipeline.git
cd weather-data-pipeline
```

### 2. Set your OpenWeatherMap API Key

Create a `.env` file in the root of your project and add your API key:

```
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Start the services

```bash
docker-compose up --build
```

Visit Airflow UI at `http://localhost:8080`  
Default credentials: `airflow` / `airflow`

### 4. Add Airflow Connection

- Go to **Admin > Connections**.
- Add a new connection:
  - Conn ID: `postgres_weather`
  - Conn Type: `Postgres`
  - Host: `postgres`
  - Schema: `airflow`
  - Login: `airflow`
  - Password: `airflow`
  - Port: `5432`

### 5. Enable the DAG

In the Airflow UI, unpause the `weather_data` DAG to start scheduling.

## 🧠 What You Learn

- Building a reliable and maintainable ETL pipeline.
- Using XComs for task-to-task communication in Airflow.
- Handling API data and persisting it with deduplication logic.
- Deploying workflows with Docker for reproducibility.

## 📊 Sample Table Schema

```sql
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature REAL NOT NULL,
    description VARCHAR(255) NOT NULL
);
```

## 📌 Author

Made by a future Data Engineer 🚀

---

Happy Data-ing! 🧬

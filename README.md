# Data Analysis Microservice

A Flask-based API that reads movie data from a CSV file, filters movies by genre, and records API queries in PostgreSQL. The application and database run in separate Docker containers using Docker Compose.

## Technologies Used

- Python and Flask
- Pandas
- PostgreSQL
- Docker and Docker Compose

## Project Structure

```text
data-analysis-service/
├── data/
│   └── movies.csv
├── app.py
├── Dockerfile.base
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

## API Endpoints

### Health Check

`GET /health`

Returns the API health status.

### Query Movies

`GET /query`

Returns all movies.

`GET /query?genre=Drama`

Returns movies matching the requested genre. Genre filtering is case-insensitive.

Every query request is recorded in PostgreSQL.

## Configuration

Create a `.env` file using `.env.example` as a template. Set the database name, username, password, host, and port.

Do not commit `.env` to version control.

## Build and Run

Build the reusable Python base image:

```powershell
docker build -f Dockerfile.base -t data-analysis-base:1.0 .
```

Start the application and database:

```powershell
docker compose up --build -d
```

Check running services:

```powershell
docker compose ps
```

## Testing

Test the health endpoint:

```powershell
curl.exe http://localhost:5000/health
```

Test genre filtering:

```powershell
curl.exe "http://localhost:5000/query?genre=Drama"
```

View query logs in PostgreSQL:

Connect to the PostgreSQL container using the username and database name configured in your .env file: 

docker compose exec db psql -U <your_db_user> -d <your_db_name> 

At the psql prompt, run: 

SELECT query_id, query_params, timestamp FROM queries_log ORDER BY query_id; 

Confirm that each request to /query created a log entry. The /health endpoint does not need to be logged

## Database Persistence

PostgreSQL data is stored in the named Docker volume `postgres_data`. The data remains available after containers are removed and recreated, provided the volume is not deleted.

## Stop the Services

```powershell
docker compose down
```

The named database volume is retained when `docker compose down` is run without the `-v` option.

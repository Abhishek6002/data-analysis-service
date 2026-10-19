
from flask import Flask, request, jsonify
import pandas as pd
import os
import time
import psycopg2

app = Flask(__name__)

CSV_PATH = "data/movies.csv"


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "moviesdb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123")
    )


def initialize_database():
    # Retry because PostgreSQL may take time to start
    for attempt in range(10):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS queries_log (
                    query_id SERIAL PRIMARY KEY,
                    query_params TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("Database table is ready.")
            return

        except psycopg2.OperationalError as e:
            print(f"Database not ready (attempt {attempt + 1}/10): {e}")
            time.sleep(3)

    print("Warning: Database unavailable at startup.")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/query", methods=["GET"])
def query_movies():
    genre = request.args.get("genre")

    # Log the request to PostgreSQL
    query_params = f"genre={genre}" if genre else "all"

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO queries_log (query_params) VALUES (%s)",
            (query_params,)
        )

        conn.commit()
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        app.logger.error("Failed to log query: %s", e)
        return jsonify({"error": "Database logging failed"}), 503

    # Read and filter the movie dataset
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = df.columns.str.strip()

        if genre:
            df = df[df["genre"].str.lower() == genre.strip().lower()]

        movies = df.to_dict(orient="records")
        return jsonify(movies), 200

    except (OSError, pd.errors.ParserError, ValueError, KeyError) as e:
        app.logger.error("Failed to read movie dataset: %s", e)
        return jsonify({"error": "Unable to read movie dataset"}), 500


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)

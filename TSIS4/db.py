# db.py – Database access layer (psycopg2 + PostgreSQL)
#
# Schema (run once to initialise):
#   CREATE TABLE players (
#       id       SERIAL PRIMARY KEY,
#       username VARCHAR(50) UNIQUE NOT NULL
#   );
#   CREATE TABLE game_sessions (
#       id            SERIAL PRIMARY KEY,
#       player_id     INTEGER REFERENCES players(id),
#       score         INTEGER   NOT NULL,
#       level_reached INTEGER   NOT NULL,
#       played_at     TIMESTAMP DEFAULT NOW()
#   );

import psycopg2
from psycopg2 import sql

# ── Connection settings – edit to match your PostgreSQL instance ──────────────
DB_CONFIG = {
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "1234",
    "host":     "localhost",
    "port":     5432,
}

def _connect():
    """Open and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    Create tables if they do not already exist.
    Call once at application startup.
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER   NOT NULL,
                    level_reached INTEGER   NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()


def get_or_create_player(username: str) -> int:
    """
    Return the player's id, creating a row if the username is new.
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            player_id = cur.fetchone()[0]
        conn.commit()
    return player_id


def save_session(player_id: int, score: int, level_reached: int):
    """Insert a completed game session into game_sessions."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions (player_id, score, level_reached)
                VALUES (%s, %s, %s)
                """,
                (player_id, score, level_reached)
            )
        conn.commit()


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever, or 0 if none."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,)
            )
            return cur.fetchone()[0]


def get_leaderboard(limit: int = 10) -> list[tuple]:
    """
    Return the top `limit` scores as a list of tuples:
      (rank, username, score, level_reached, played_at)
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at::date
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s
                """,
                (limit,)
            )
            return cur.fetchall()
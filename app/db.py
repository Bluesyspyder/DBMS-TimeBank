"""
TimeBank - Database Connection Module
Handles PostgreSQL connection using psycopg2 and python-dotenv.
All database logic remains in SQL (procedures, triggers, transactions).
"""

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connection pool for efficient connection management
_connection_pool = None


def get_connection_pool():
    """Create or return the existing connection pool."""
    global _connection_pool
    if _connection_pool is None or _connection_pool.closed:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "timebank"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
    return _connection_pool


def get_connection():
    """Get a connection from the pool."""
    pool = get_connection_pool()
    return pool.getconn()


def release_connection(conn):
    """Return a connection to the pool."""
    pool = get_connection_pool()
    pool.putconn(conn)


def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query and optionally fetch results.

    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch: If True, fetch and return results

    Returns:
        List of tuples if fetch=True, else None
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def execute_procedure(proc_name, params=None):
    """
    Call a stored procedure.

    Args:
        proc_name: Name of the stored procedure
        params: Parameters as a tuple

    Returns:
        None (procedures commit internally or via CALL)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if params:
                placeholders = ", ".join(["%s"] * len(params))
                cur.execute(f"CALL {proc_name}({placeholders})", params)
            else:
                cur.execute(f"CALL {proc_name}()")
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def execute_function(func_name, params=None):
    """
    Call a stored function and return the result.

    Args:
        func_name: Name of the function
        params: Parameters as a tuple

    Returns:
        The function result
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if params:
                placeholders = ", ".join(["%s"] * len(params))
                cur.execute(f"SELECT {func_name}({placeholders})", params)
            else:
                cur.execute(f"SELECT {func_name}()")
            result = cur.fetchone()
            return result[0] if result else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def close_pool():
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool and not _connection_pool.closed:
        _connection_pool.closeall()
        _connection_pool = None

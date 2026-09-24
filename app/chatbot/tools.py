import sqlite3
from langchain_core.tools import tool
from app.config import settings

def get_connection():
    path = settings.SQLITE_URL.replace("sqlite:///", "")
    return sqlite3.connect(path)

@tool
def get_db_schema() -> str:
    """Returns the schema of the students table to help write valid SQL queries."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students';")
        schema = cursor.fetchone()
        return schema[0] if schema else "Table 'students' does not exist."

@tool
def run_sqlite_query(query: str) -> str:
    """Executes a strictly READ-ONLY SQL query on SQLite and returns the results.
    Do not run DROP, INSERT, UPDATE, DELETE, or ALTER queries."""
    sanitized = query.strip().upper()
    if not sanitized.startswith("SELECT"):
        return "Security error: Only SELECT queries are permitted."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description] if cursor.description else []
            return f"Columns: {headers}\nRows: {rows}"
    except Exception as e:
        return f"Database query execution error: {str(e)}"

tools = [get_db_schema, run_sqlite_query]
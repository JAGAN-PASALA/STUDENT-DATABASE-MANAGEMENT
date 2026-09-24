import os
import sqlite3
import traceback
from google import genai
from google.genai import types
from app.config import settings

def get_connection():
    path = settings.SQLITE_URL.replace("sqlite:///", "")
    return sqlite3.connect(path)

def get_db_schema() -> str:
    """Returns the schema of the students table to write valid SQL SELECT queries."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students';")
            row = cursor.fetchone()
            return row[0] if row else "Table 'students' does not exist."
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"

def run_sqlite_query(query: str) -> str:
    """Executes a strictly READ-ONLY SQL query on the SQLite database and returns the rows.
    Do NOT execute DROP, INSERT, UPDATE, or DELETE queries."""
    sanitized = query.strip()
    if not sanitized.upper().startswith("SELECT"):
        return "Security error: Only SELECT queries are permitted."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sanitized)
            rows = cursor.fetchall()
            headers = [d[0] for d in cursor.description] if cursor.description else []
            if not rows:
                return "Query executed successfully, but returned 0 rows."
            return f"Columns: {headers}\nRows: {rows}"
    except Exception as e:
        return f"Database error: {str(e)}"

SYSTEM_PROMPT = """You are an intelligent database assistant for a Student Management System.
You have access to tools that check table schemas and run read-only SQL queries on the SQLite database.
Always inspect the schema first if you do not know the columns.
Translate user questions into accurate SQL SELECT queries, call the run_sqlite_query tool, and synthesize the result into a concise, friendly response.
Do NOT attempt to write or mutate data."""

def ask_agent(user_query: str) -> str:
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    # Models to try sequentially if one is rate limited, overloaded, or not found
    available_models = [
        "gemini-2.5-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.8-flash"
    ]

    last_err = None

    for model_name in available_models:
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[get_db_schema, run_sqlite_query],
                temperature=0.0
            )

            chat = client.chats.create(model=model_name, config=config)
            response = chat.send_message(user_query)

            if response and response.text:
                return response.text.strip()
            
            return "The model executed the database query, but no summary text was produced."

        except Exception as e:
            err_str = str(e)
            last_err = e

            # Failover on:
            # 404 / NOT_FOUND (Model endpoint missing)
            # 429 / RESOURCE_EXHAUSTED (Quota rate limit)
            # 503 / UNAVAILABLE (High demand / server overload)
            retryable_codes = ["404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]
            if any(code in err_str for code in retryable_codes):
                print(f"Model {model_name} unavailable ({err_str[:60]}...). Failing over to next model...")
                continue
            
            print(f"Unexpected error executing on {model_name}: {e}")
            traceback.print_exc()
            raise e

    # If all models failed to respond
    if "503" in str(last_err) or "UNAVAILABLE" in str(last_err):
        return "⚠️ Google AI servers are experiencing temporary high demand across all endpoints. Please retry your question in a moment."
    if "429" in str(last_err) or "RESOURCE_EXHAUSTED" in str(last_err):
        return "⚠️ All free-tier Gemini model quotas are temporarily exhausted. Please wait 60 seconds or use a fresh API key."

    raise last_err
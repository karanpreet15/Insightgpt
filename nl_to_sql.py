"""
Converts a natural-language question into a DuckDB-compatible SQL query
using a local Ollama model.
"""

import re
from .llm import ask_llm

SYSTEM_PROMPT = """
You are a SQL generation engine for a business analytics tool.

You write DuckDB-compatible SQL SELECT queries based on a user's
natural-language question and database schema.

Rules:

- Only generate SELECT or WITH...SELECT queries.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE.
- Use only tables and columns present in the schema.
- Always alias aggregates clearly.
- For top-N questions use ORDER BY + LIMIT.
- If user doesn't specify N, use LIMIT 10.
- Return ONLY SQL.
- No explanations.
- No markdown.
"""


class SQLGenerationError(Exception):
    pass


def _extract_sql(text: str) -> str:

    text = text.strip()

    text = re.sub(
        r"^```sql\s*|^```\s*|```$",
        "",
        text,
        flags=re.MULTILINE
    ).strip()

    return text.rstrip(";").strip()


def _is_safe_select(sql: str) -> bool:

    forbidden = (
        r"\b(insert|update|delete|drop|alter|create|truncate|attach|detach|"
        r"copy|pragma|grant|replace|call|export|import)\b"
    )

    if re.search(
        forbidden,
        sql,
        flags=re.IGNORECASE
    ):
        return False

    return bool(
        re.match(
            r"^\s*(select|with)\b",
            sql,
            flags=re.IGNORECASE
        )
    )


def generate_sql(
    question: str,
    schema_description: str,
    previous_error: str = None,
    previous_sql: str = None
) -> str:

    prompt = f"""
{SYSTEM_PROMPT}

Schema:
{schema_description}

Question:
{question}
"""

    if previous_error and previous_sql:

        prompt += f"""

Previous SQL:
{previous_sql}

Error:
{previous_error}

Fix the query and return only corrected SQL.
"""

    raw = ask_llm(prompt)

    sql = _extract_sql(raw)

    if not _is_safe_select(sql):
        raise SQLGenerationError(
            f"Generated query was rejected: {sql}"
        )

    return sql
"""
Glue layer:
Question -> SQL Generation -> DuckDB Execution

Automatically retries once if generated SQL fails.
"""

from .nl_to_sql import generate_sql


def run_question(
    question: str,
    datastore,
    max_retries: int = 1
) -> dict:

    schema = datastore.schema_description()

    sql = generate_sql(
        question,
        schema
    )

    attempt = 0

    while True:

        try:

            df = datastore.con.execute(sql).fetchdf()

            return {
                "sql": sql,
                "dataframe": df,
                "error": None
            }

        except Exception as e:

            attempt += 1

            if attempt > max_retries:

                return {
                    "sql": sql,
                    "dataframe": None,
                    "error": str(e)
                }

            sql = generate_sql(
                question,
                schema,
                previous_error=str(e),
                previous_sql=sql
            )
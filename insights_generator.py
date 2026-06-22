"""
Generates business insights from query results using a local Ollama model.
"""

from .llm import ask_llm

SYSTEM_PROMPT = """
You are a senior business analyst writing for a non-technical executive.

Rules:
- Write 3 to 5 concise business insights.
- Use actual numbers from the data.
- Highlight trends, top performers, outliers, and risks.
- Avoid technical SQL language.
- End with one actionable recommendation.
- No generic statements.
"""


def generate_insights(
    question: str,
    sql: str,
    df
) -> str:

    if df is None or df.empty:
        return "No data returned from the query."

    sample = df.head(30).to_markdown(index=False)

    prompt = f"""
{SYSTEM_PROMPT}

Question:
{question}

SQL Used:
{sql}

Result Data:
{sample}

Generate business insights.
"""

    return ask_llm(prompt)
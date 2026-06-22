import tempfile

import streamlit as st

from core.data_loader import DataStore
from core.sql_engine import run_question
from core.chart_generator import auto_chart
from core.insights_generator import generate_insights
from core.pdf_report import build_pdf_report

st.set_page_config(
    page_title="InsightGPT",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------

if "datastore" not in st.session_state:
    st.session_state.datastore = DataStore()

if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("📊 InsightGPT — AI-Powered Analytics Assistant")

st.success(
    "🚀 Running Locally with Ollama + Qwen2.5-Coder 7B"
)

st.caption(
    "Upload your data. Ask questions in plain English. "
    "Get SQL, charts, and business insights automatically."
)

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.success("✅ Local AI Model")
    st.caption("Qwen2.5-Coder 7B via Ollama")

    st.header("1. Upload Data")

    uploaded_files = st.file_uploader(
        "Upload CSV file(s)",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:

        existing_sources = [
            m["source_file"]
            for m in st.session_state.datastore.tables.values()
        ]

        for f in uploaded_files:

            if f.name not in existing_sources:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".csv"
                ) as tmp:

                    tmp.write(f.getvalue())
                    tmp_path = tmp.name

                table_name = (
                    st.session_state.datastore.load_csv(
                        tmp_path,
                        filename=f.name
                    )
                )

                st.success(
                    f"Loaded `{f.name}` → table `{table_name}`"
                )

    if st.session_state.datastore.tables:

        st.header("2. Loaded Tables")

        for tname, meta in (
            st.session_state.datastore.tables.items()
        ):

            with st.expander(
                f"{tname} ({meta['row_count']} rows)"
            ):

                st.write(
                    ", ".join(meta["columns"])
                )

    if st.session_state.history:

        st.header("3. Export")

        if st.button(
            "📄 Generate PDF Report",
            use_container_width=True
        ):

            output_path = (
                tempfile.gettempdir()
                + "/insightgpt_report.pdf"
            )

            build_pdf_report(
                st.session_state.history,
                output_path
            )

            with open(output_path, "rb") as f:

                st.download_button(
                    "⬇️ Download PDF Report",
                    f,
                    file_name="insightgpt_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ------------------------------------------------------------
# Main Body
# ------------------------------------------------------------

if not st.session_state.datastore.tables:

    st.info(
        "👈 Upload a CSV file from the sidebar to get started."
    )

    st.stop()

st.header("Ask a Question About Your Data")

example_qs = [
    "What are my top 5 selling products by revenue?",
    "Which customers generated the most revenue?",
    "Show total sales by month"
]

clicked_example = None

cols = st.columns(len(example_qs))

for c, q in zip(cols, example_qs):

    if c.button(q, use_container_width=True):
        clicked_example = q

question = st.text_input(
    "Your Question",
    value=clicked_example or "",
    placeholder="e.g. What are my top-selling products?"
)

ask = st.button(
    "Ask InsightGPT",
    type="primary"
)

# ------------------------------------------------------------
# Query Execution
# ------------------------------------------------------------

if ask and question.strip():

    with st.spinner("Generating SQL..."):

        try:

            result = run_question(
                question,
                st.session_state.datastore
            )

        except Exception as e:

            st.error(
                f"Something went wrong generating SQL: {e}"
            )

            st.stop()

    if result["error"]:

        st.error(
            "Couldn't execute the generated query."
        )

        st.code(
            result["sql"],
            language="sql"
        )

        st.caption(
            f"Error: {result['error']}"
        )

    else:

        df = result["dataframe"]
        sql = result["sql"]

        st.subheader("Generated SQL")

        st.code(
            sql,
            language="sql"
        )

        st.subheader("Results")

        st.dataframe(
            df,
            use_container_width=True
        )

        fig, chart_type = auto_chart(
            df,
            question
        )

        if fig is not None:

            st.subheader("Chart")

            st.plotly_chart(

                fig,
                use_container_width=True,
                key="main_chart"
)

        with st.spinner(
            "Generating business insights..."
        ):

            try:

                insights = generate_insights(
                    question,
                    sql,
                    df
                )

            except Exception as e:

                insights = (
                    f"_Could not generate insights: {e}_"
                )

        st.subheader(
            "Business Insights"
        )

        st.markdown(
            insights
        )
        if (
    not st.session_state.history
    or st.session_state.history[-1]["question"] != question
):
            

            st.session_state.history.append(
                {
                    "question": question,
                    "sql": sql,
                    "dataframe": df,
                    "chart_fig": fig,
                    "insights": insights,
                    }
            )

        



# ------------------------------------------------------------
# History
# ------------------------------------------------------------

# ------------------------------------------------------------
# History
# ------------------------------------------------------------

if st.session_state.history:

    st.divider()

    st.subheader(
        "Query History (This Session)"
    )

    for idx, entry in enumerate(
        reversed(st.session_state.history)
    ):

        with st.expander(
            f"Q: {entry['question']}"
        ):

            st.code(
                entry["sql"],
                language="sql"
            )

            st.dataframe(
                entry["dataframe"],
                use_container_width=True
            )

            if entry["chart_fig"] is not None:

                st.plotly_chart(
                    entry["chart_fig"],
                    use_container_width=True,
                    key=f"history_chart_{idx}"
                )

            st.markdown(
                entry["insights"]
            )
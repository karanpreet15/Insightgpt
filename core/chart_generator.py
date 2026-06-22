"""
Looks at the shape/types of a query result and picks a sensible chart automatically:
- single value            -> KPI indicator
- date column + numeric   -> line chart (trend over time)
- category + numeric      -> bar chart (or pie if it's a small set of proportions)
- two numeric columns     -> scatter
- anything else           -> no chart, table only
"""
import re
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _looks_like_datetime(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    try:
        sample = series.dropna().astype(str).head(5)
        if sample.empty:
            return False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pd.to_datetime(sample)
        return True
    except Exception:
        return False


def auto_chart(df: pd.DataFrame, question: str = ""):
    """Returns (plotly_figure_or_None, chart_type_string)."""
    if df is None or df.empty:
        return None, "no_data"

    df = df.copy()
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    other_cols = [c for c in df.columns if c not in numeric_cols]

    # Single scalar result -> KPI card
    if df.shape[0] == 1 and len(numeric_cols) == 1 and df.shape[1] <= 2:
        value = df[numeric_cols[0]].iloc[0]
        fig = go.Figure(go.Indicator(
            mode="number",
            value=float(value),
            title={"text": numeric_cols[0].replace("_", " ").title()},
        ))
        fig.update_layout(height=250)
        return fig, "kpi"

    date_col = next((c for c in other_cols if _looks_like_datetime(df[c])), None)

    # Time series
    if date_col and numeric_cols:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        fig = px.line(
            df, x=date_col, y=numeric_cols[0], markers=True,
            title=f"{numeric_cols[0].replace('_', ' ').title()} over time",
        )
        return fig, "line"

    # Category vs numeric
    if other_cols and numeric_cols:
        cat_col, val_col = other_cols[0], numeric_cols[0]
        wants_proportion = bool(re.search(
            r"share|proportion|percentage|percent|split|distribution|breakdown|mix",
            question, flags=re.IGNORECASE,
        ))
        if wants_proportion and df[cat_col].nunique() <= 8:
            fig = px.pie(
                df, names=cat_col, values=val_col,
                title=f"{val_col.replace('_', ' ').title()} share by {cat_col.replace('_', ' ').title()}",
            )
            return fig, "pie"
        df_sorted = df.sort_values(val_col, ascending=False).head(20)
        fig = px.bar(
            df_sorted, x=cat_col, y=val_col,
            title=f"{val_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
        )
        fig.update_layout(xaxis_tickangle=-30)
        return fig, "bar"

    # Two numeric columns -> scatter
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1],
            title=f"{numeric_cols[1].replace('_', ' ').title()} vs {numeric_cols[0].replace('_', ' ').title()}",
        )
        return fig, "scatter"

    return None, "table_only"

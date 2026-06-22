"""
Loads uploaded CSVs into an in-memory DuckDB instance and keeps track of
schema metadata so we can describe the data to Claude for NL -> SQL generation.
"""
import re
import duckdb
import pandas as pd


def sanitize_name(name: str) -> str:
    """Turn an arbitrary filename/column name into a safe SQL identifier."""
    name = re.sub(r"\.[^.]+$", "", name)          # strip file extension
    name = re.sub(r"[^0-9a-zA-Z_]", "_", name)     # replace invalid chars
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "col"
    if re.match(r"^[0-9]", name):
        name = f"t_{name}"
    return name.lower()


class DataStore:
    """Holds the DuckDB connection + metadata for every table the user has uploaded."""

    def __init__(self):
        self.con = duckdb.connect(database=":memory:")
        self.tables = {}  # table_name -> metadata dict

    def load_csv(self, file_path: str, filename: str = None) -> str:
        filename = filename or file_path.split("/")[-1]
        base_name = sanitize_name(filename)
        table_name = base_name
        i = 1
        while table_name in self.tables:
            table_name = f"{base_name}_{i}"
            i += 1

        df = pd.read_csv(file_path)

        # sanitize + dedupe column names
        new_cols, seen = [], {}
        for idx, c in enumerate(df.columns):
            clean = sanitize_name(str(c)) or f"col_{idx}"
            if clean in seen:
                seen[clean] += 1
                clean = f"{clean}_{seen[clean]}"
            else:
                seen[clean] = 0
            new_cols.append(clean)
        df.columns = new_cols

        # try to parse obvious date columns so charting/sorting works later
        # (pandas >= 3.0 uses a "str" dtype for text columns instead of "object")
        for col in df.columns:
            is_text_col = df[col].dtype == object or str(df[col].dtype) == "str"
            if is_text_col and re.search(r"date|time|month|year", col):
                try:
                    df[col] = pd.to_datetime(df[col], errors="raise")
                except Exception:
                    pass

        self.con.register(table_name, df)
        self.tables[table_name] = {
            "df": df,
            "columns": list(df.columns),
            "dtypes": {c: str(df[c].dtype) for c in df.columns},
            "source_file": filename,
            "row_count": len(df),
        }
        return table_name

    def schema_description(self) -> str:
        """Plain-text schema (+ sample rows) fed to Claude so it can write valid SQL."""
        lines = []
        for tname, meta in self.tables.items():
            lines.append(f"TABLE {tname} ({meta['row_count']} rows)")
            for col in meta["columns"]:
                lines.append(f"  - {col}: {meta['dtypes'][col]}")
            sample = meta["df"].head(3).to_dict(orient="records")
            lines.append(f"  sample_rows: {sample}")
            lines.append("")
        return "\n".join(lines)

    def get_table_names(self):
        return list(self.tables.keys())

import os
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from dotenv import load_dotenv

# LLM only for parsing user query → search_data + comparison operators
from llm_models import deepseek_model,llama_model
from parser_and_prompts import (
    search_prompt_template,
    filter_prompt_template,
    search_parser,
    filter_column_parser,
)

load_dotenv()
local_path = os.getenv("LOCAL_PATH")


# =========================
# Parsers from LLM (unchanged)
# =========================

def get_filter_for_columns(user_query: str):
    """
    Returns an ApplyFilterToColumn pydantic model (or equivalent) with
    fields set to 'Greater than' / 'Lesser than' or None.
    """
    filter_chain = filter_prompt_template |llama_model | filter_column_parser
    result = filter_chain.invoke({'user_query': user_query})
    return result  # keep pydantic model; we handle model_dump later


def get_search_data(user_query: str) -> Dict[str, Any]:
    """
    Returns a dict of extracted search values based on the user's query.
    Values may be singular or lists (for ranges).
    """
    search_chain = search_prompt_template |llama_model| search_parser
    result = search_chain.invoke(user_query)
    return result.model_dump(exclude_none=True)


# =========================
# Manual deterministic filtering
# =========================

NUMERIC_COLS = {
    "Price_in_Crore",
    "Rate_rs_sqft",
    "Area_in_sq_meter",
    "bedRoom",
    "bathroom",
    "balcony",
    "floorNum",
    "Totalfloor",
}

ENUM_COLS = {
    "AreaType",        # AreaTypeEnum values like "Carpet", "Built Up", "Super Built up"
    "facing",          # FacingDirection enum values
    "additionalRoom",  # AdditionalRoomType strings / combos
}

TEXT_COLS = {
    "colony_or_sector",
    "City",
    "Country",
    # Add 'society' here if present in your CSV
}


def _normalize_series_str(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.casefold()


def _normalize_value_str(v: Any) -> str:
    return str(v).strip().casefold()


def _ensure_list(v: Any) -> List[Any]:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _apply_numeric_filter(
    df: pd.DataFrame,
    col: str,
    value: Optional[Union[int, float, List[Union[int, float]]]],
    comparator: Optional[str],  # "Greater than" | "Lesser than" | None
) -> pd.DataFrame:
    if value is None or col not in df.columns:
        return df

    if isinstance(value, list):
        vals = [x for x in value if x is not None]
        if len(vals) == 0:
            return df
        if len(vals) >= 2 and comparator is None:
            lo, hi = min(vals), max(vals)
            return df[df[col].between(lo, hi)]
        # fall through with single value
        value = vals[0]

    # Single numeric value
    try:
        series = pd.to_numeric(df[col], errors="coerce")
    except Exception:
        series = df[col]

    if comparator == "Greater than":
        return df[series >= value]
    elif comparator == "Lesser than":
        return df[series <= value]
    else:
        return df[series == value]


def _apply_categorical_filter(
    df: pd.DataFrame,
    col: str,
    value: Optional[Union[str, List[str]]],
) -> pd.DataFrame:
    if value is None or col not in df.columns:
        return df

    series_norm = _normalize_series_str(df[col])
    values = _ensure_list(value)
    if len(values) == 0:
        return df

    norm_values = {_normalize_value_str(v) for v in values}
    mask = series_norm.isin(norm_values)
    return df[mask]


def _apply_enum_filter(
    df: pd.DataFrame,
    col: str,
    value: Optional[Union[str, List[str]]],
) -> pd.DataFrame:
    # Enums typically stored as strings in the CSV
    return _apply_categorical_filter(df, col, value)


def filter_dataframe_manual(
    df: pd.DataFrame,
    fields: Dict[str, bool],
    search_data: Dict[str, Any],
    filter_on_columns_model: Any,  # ApplyFilterToColumn pydantic model or dict
) -> pd.DataFrame:
    """
    Deterministically filter `df` using:
      - `fields`: which columns the user cares about (bool flags, including optional 'top_floor')
      - `search_data`: values to filter on (single or list/range)
      - `filter_on_columns_model`: per-column comparator ('Greater than' / 'Lesser than') for numeric fields
    """
    df_filtered = df.copy()

    # Convert pydantic model -> dict if needed
    if hasattr(filter_on_columns_model, "model_dump"):
        filter_on_columns = filter_on_columns_model.model_dump(exclude_none=True)
    elif isinstance(filter_on_columns_model, dict):
        filter_on_columns = {k: v for k, v in filter_on_columns_model.items() if v is not None}
    else:
        filter_on_columns = {}

    # 1) Handle top-floor first if requested
    if fields.get("top_floor", False):
        if "Totalfloor" in df_filtered.columns and "floorNum" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["Totalfloor"] == df_filtered["floorNum"]]

    # 2) Apply filters only for fields explicitly marked True (except top_floor handled above)
    for key, enabled in fields.items():
        if not enabled or key == "top_floor":
            continue

        value = search_data.get(key, None)
        comparator = filter_on_columns.get(key, None)

        if key in NUMERIC_COLS and key in df_filtered.columns:
            df_filtered = _apply_numeric_filter(df_filtered, key, value, comparator)

        elif key in ENUM_COLS and key in df_filtered.columns:
            df_filtered = _apply_enum_filter(df_filtered, key, value)

        elif key in TEXT_COLS and key in df_filtered.columns:
            df_filtered = _apply_categorical_filter(df_filtered, key, value)

        # Early exit if empty
        if df_filtered.empty:
            break

    return df_filtered


def run_csv_agent(
    fields: Dict[str, bool],
    df: pd.DataFrame,
    search_data: Dict[str, Any],
    filter_on_columns: Any,
) -> pd.DataFrame:
    """
    Manual, deterministic filtering. No LLM query generation/eval.
    `df` is a pandas DataFrame already loaded by the caller.
    """
    result = filter_dataframe_manual(df, fields, search_data, filter_on_columns)
    return result

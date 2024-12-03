import logging
import re

import pandas as pd


def drop_na_columns(table_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that have zero instances or all columns are "--"
    """
    original_columns = table_df.columns
    for column in table_df.columns:
        column_data = [d for d in table_df[column] if pd.notna(d) and d != "--"]

        if len(column_data) <= 1:
            table_df = table_df.drop(column, axis=1)
            continue

        # TODO: why use "Unnamed:"
        if "Unnamed:" in column:
            table_df = table_df.drop(column, axis=1)
            continue

    remove_columns = list(set(original_columns) - set(table_df.columns))
    if len(remove_columns) > 0:
        logging.info(f"Removed columns: {remove_columns}")

    return table_df


def normalize_and_flatten_text(text: str) -> str:
    """Normalizes and flattens the input text.

    Returns:
        str: lowercased, replace whitespace, line break, "." to " "
    """
    text = text.lower()
    text = re.split(r'[\s\_\.]', text)
    text = " ".join(text).strip()

    return text

import logging
import re

import pandas as pd


def drop_na_columns(table_df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns that have zero instances or all columns are "--".
    """
    original_columns = table_df.columns
    for column in original_columns:
        column_data = table_df[column].replace("--", pd.NA).dropna()

        # seems dataframe default column name
        if len(column_data) < 1 or column.startswith("Unnamed:"):
            table_df = table_df.drop(column, axis=1)

    remove_columns = list(set(original_columns) - set(table_df.columns))
    if remove_columns:
        logging.info(f"Removed columns: {remove_columns}")

    return table_df


def normalize_and_flatten_text(raw_text: str) -> str:
    """Normalizes and flattens the input text.

    Returns:
        str: lowercased, replace whitespace, line break, "." to " "
    """
    raw_text = raw_text.lower()
    texts = re.split(r'[\s\_\.]', raw_text)
    text = " ".join(texts).strip()

    return text

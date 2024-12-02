import logging

import pandas as pd


def drop_na_columns(table_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that have zero instances or all columns are "--"
    """
    original_columns = table_df.columns
    for column in table_df.columns:
        column_data = [d for d in list(table_df[column]) if d == d and d != "--"]

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

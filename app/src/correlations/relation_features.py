import random
import re
from itertools import product

import numpy as np
import pandas as pd
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction
from numpy.linalg import norm
from sentence_transformers import util
from strsimpy.damerau import Damerau
from strsimpy.metric_lcs import MetricLCS

from app.src.correlations.model import SentenceTransformer
from app.src.correlations.self_features import make_self_features_from

SMOOTHIE = SmoothingFunction().method4
METRIC_LCS = MetricLCS()
DAMERAU = Damerau()
SEED = 200
random.seed(SEED)


class Constants:
    TRAIN_LABEL_RATIO = 0.1

    # EXPERIMENTAL
    ADDITIONAL_FEATURE_DIMENSION = 6  # not sure
    DEEP_EMBEDDING_FEATURES_DIMENSION = 768
    EPSILON = 1e-8  # prevent div by zero


def preprocess_text(text: str) -> str:
    """

    Returns:
        str: lowercased, replace whitespace, line break, "." to " "
    """
    text = text.lower()

    text = re.split(r'[\s\_\.]', text)
    text = " ".join(text).strip()

    return text


def get_col_names_features(
        l_col_name: str,
        r_col_name: str,
        l_col_name_embedding: np.ndarray,
        r_col_name_embedding: np.ndarray,
) -> np.ndarray:
    """

    Returns:
         np.ndarray:
         bleu_score: used SmoothingFunction().method4
         edit_distance: Damerau Distance
         lcs: MetricLCS Distance
         transformer_score: cosine similarity
         one_in_one: 포함 관계 일 경우 1, 아니면 0
    """
    bleu_score = bleu([l_col_name], r_col_name, smoothing_function=SMOOTHIE)
    edit_distance = DAMERAU.distance(l_col_name, r_col_name)
    lcs = METRIC_LCS.distance(l_col_name, r_col_name)
    transformer_score = util.cos_sim(l_col_name_embedding, r_col_name_embedding)
    one_in_one = l_col_name in r_col_name or r_col_name in l_col_name

    col_names_features = np.array(
        [bleu_score, edit_distance, lcs, transformer_score, one_in_one],
        dtype=np.float32
    )

    return col_names_features


def calculate_embedding_cosine_similarity(embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
    """

    Returns:
         np.ndarray: cosine similarity between two sentences embeddings.
    """
    cosine_similarity = np.inner(embeddings1, embeddings2) / (norm(embeddings1) * norm(embeddings2))
    return np.array([cosine_similarity])


def get_output_feature_from_row(
        l_col_name: str,
        l_feature: np.ndarray,
        l_col_name_embedding: np.ndarray,
        r_col_name: str,
        r_feature: np.ndarray,
        r_col_name_embedding: np.ndarray
) -> np.ndarray:
    # (feature 의 차의 abs) / (feature 의 합 + EPSILON)
    difference_features_percent = np.abs(l_feature - r_feature) / (l_feature + r_feature + Constants.EPSILON)
    # TODO: 정확히 무슨 계산인지?

    # for col_name additional features
    col_names_features = get_col_names_features(l_col_name, r_col_name, l_col_name_embedding, r_col_name_embedding)

    # select only DEEP_EMBEDDING_FEATURES to calculate embedding_cos_sim
    embedding_cos_sim = calculate_embedding_cosine_similarity(
        l_feature[-Constants.DEEP_EMBEDDING_FEATURES_DIMENSION:],
        r_feature[-Constants.DEEP_EMBEDDING_FEATURES_DIMENSION:]
    )

    output_feature = np.concatenate((
        difference_features_percent[:-Constants.DEEP_EMBEDDING_FEATURES_DIMENSION],
        col_names_features,
        embedding_cos_sim
    ))

    return output_feature


def create_feature_matrix_inference(l_df: pd.DataFrame, r_df: pd.DataFrame) -> np.ndarray:
    """

    Notes:
        Read data from 2 table dataframe, mapping file path and make relational features and labels as a matrix.
    """

    l_table_features = make_self_features_from(l_df)
    # np.savetxt("l_table_features.csv", l_table_features, fmt="%s", delimiter=",")

    r_table_features = make_self_features_from(r_df)
    # np.savetxt("r_table_features.csv", r_table_features, fmt="%s", delimiter=",")

    l_columns = [preprocess_text(c) for c in l_df.columns]
    r_columns = [preprocess_text(c) for c in r_df.columns]

    combinations = list(product(range(len(l_columns)), range(len(r_columns))))

    # TODO: Model Depends, or Logic
    model = SentenceTransformer.get()

    column_name_embeddings: dict[str, any] = {c: model.encode(c) for c in l_columns + r_columns}
    # END OF MODEL LOGIC

    NON_EMBEDDED_DIMENSION = l_table_features.shape[1] - Constants.DEEP_EMBEDDING_FEATURES_DIMENSION

    # TODO: Matrix values, row size are ignored
    output_feature_table = np.zeros(
        (
            # combinations_label len = l_columns * r_columns
            len(combinations),
            # NON_EMBEDDED_DIMENSION + ADDITIONAL_FEATURE_DIMENSION
            NON_EMBEDDED_DIMENSION + Constants.ADDITIONAL_FEATURE_DIMENSION
        ),
        dtype=np.float32
    )

    for i, (l_col, r_col) in enumerate(combinations):
        l_col_name = l_columns[l_col]
        r_col_name = r_columns[r_col]

        output_feature_table[i, :] = get_output_feature_from_row(
            l_col_name,
            l_table_features[l_col],
            column_name_embeddings[l_col_name],
            r_col_name,
            r_table_features[r_col],
            column_name_embeddings[r_col_name]
        )

    return output_feature_table

import random
from itertools import product
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from nltk.translate import bleu  # type: ignore
from nltk.translate.bleu_score import SmoothingFunction  # type: ignore
from numpy.linalg import norm
from numpy.typing import NDArray
from sentence_transformers import util
from strsimpy.damerau import Damerau  # type: ignore
from strsimpy.metric_lcs import MetricLCS  # type: ignore

from app.src.correlations.constants import constants
from app.src.correlations.data_cleaner import normalize_and_flatten_text
from app.src.correlations.model import SentenceTransformer
from app.src.correlations.self_features import make_self_features_from

SMOOTHIE = SmoothingFunction().method4
METRIC_LCS = MetricLCS()
DAMERAU = Damerau()
SEED = 200
random.seed(SEED)

TRAIN_LABEL_RATIO = 0.1
EPSILON = 1e-8  # prevent div by zero


def get_col_names_features(
        l_col_name: str,
        r_col_name: str,
        l_col_name_embedding: NDArray[Any],
        r_col_name_embedding: NDArray[Any],
) -> NDArray[Any]:
    """Get features from column names.

    Returns:
         NDArray[Any]:
         bleu_score: used SmoothingFunction().method4
         edit_distance: Damerau Distance
         lcs: MetricLCS Distance
         transformer_score: cosine similarity
         one_in_one: 포함 관계 일 경우 1, 아니면 0
    """
    bleu_score = bleu([l_col_name], r_col_name, smoothing_function=SMOOTHIE)
    edit_distance = DAMERAU.distance(l_col_name, r_col_name)
    lcs = METRIC_LCS.distance(l_col_name, r_col_name)
    transformer_score = util.cos_sim(l_col_name_embedding, r_col_name_embedding).item()
    one_in_one = int(l_col_name in r_col_name or r_col_name in l_col_name)

    col_names_features = np.array(
        [bleu_score, edit_distance, lcs, transformer_score, one_in_one],
        dtype=np.float32
    )

    return col_names_features


def calculate_embedding_cosine_similarity(embeddings1: NDArray[Any], embeddings2: NDArray[Any]) -> NDArray[Any]:
    """Calculate cosine similarity between embeddings.

    Returns:
         NDArray[Any]: cosine similarity between two sentences embeddings.
    """
    cosine_similarity = np.inner(embeddings1, embeddings2) / (norm(embeddings1) * norm(embeddings2))
    return np.array([cosine_similarity])


def get_output_feature_from_row(
        l_col_name: str,
        l_feature: NDArray[Any],
        l_col_name_embedding: NDArray[Any],
        r_col_name: str,
        r_feature: NDArray[Any],
        r_col_name_embedding: NDArray[Any]
) -> NDArray[Any]:
    """Get output features for a pair of columns.

    Args:
        l_col_name: Left column name.
        l_feature: Left column features.
        l_col_name_embedding: Left column name embedding.
        r_col_name: Right column name.
        r_feature: Right column features.
        r_col_name_embedding: Right column name embedding.

    Returns:
        NDArray[Any]: Combined feature vector.
    """
    l_non_embed_feature, l_embed_feature = np.split(l_feature, [-constants.DEEP_EMBEDDING_FEATURES_DIMENSION])
    r_non_embed_feature, r_embed_feature = np.split(r_feature, [-constants.DEEP_EMBEDDING_FEATURES_DIMENSION])

    # TODO: 정확히 무슨 계산인지?
    # (non_embed_feature 의 차의 abs) / (non_embed_feature 의 합 + EPSILON)
    difference_features_percent = (np.abs(l_non_embed_feature - r_non_embed_feature)
                                   / (l_non_embed_feature + r_non_embed_feature + EPSILON))

    # for col_name additional features
    col_names_features = get_col_names_features(l_col_name, r_col_name, l_col_name_embedding, r_col_name_embedding)

    # select only DEEP_EMBEDDING_FEATURES to calculate embedding_cos_sim
    embedding_cos_sim = calculate_embedding_cosine_similarity(l_embed_feature, r_embed_feature)

    # non_embed(24) + col_name(5) + cos_sim(1) = 30 features
    output_feature = np.concatenate((difference_features_percent, col_names_features, embedding_cos_sim))

    return output_feature


def create_feature_matrix_inference(l_df: pd.DataFrame, r_df: pd.DataFrame) -> Tuple[NDArray[Any], Dict[str, str], Dict[str, str]]:
    """Create feature matrix for inference.

    Notes:
        Read data from 2 table dataframe, mapping file path and make relational features and labels as a matrix.

    Returns:
        Tuple[NDArray[Any], Dict[str, str], Dict[str, str]]: Feature matrix and column classifications.
    """
    l_table_features, l_column_types = make_self_features_from(l_df)
    # np.savetxt("l_table_features.csv", l_table_features, fmt="%s", delimiter=",")

    r_table_features, r_column_types = make_self_features_from(r_df)
    # np.savetxt("r_table_features.csv", r_table_features, fmt="%s", delimiter=",")

    l_columns = [normalize_and_flatten_text(c) for c in l_df.columns.to_list()]
    r_columns = [normalize_and_flatten_text(c) for c in r_df.columns.to_list()]

    combinations = list(product(range(len(l_columns)), range(len(r_columns))))

    # TODO: Model Depends, or Logic
    model = SentenceTransformer.get()

    column_name_embeddings: Dict[str, Any] = {c: model.encode(c) for c in l_columns + r_columns}
    # END OF MODEL LOGIC

    non_embedded_dimension = l_table_features.shape[1] - constants.DEEP_EMBEDDING_FEATURES_DIMENSION

    # TODO: Matrix values, row size are ignored
    output_feature_table = np.zeros(
        (
            # combinations_label len = l_columns * r_columns
            len(combinations),
            # non_embedded_dimension + ADDITIONAL_FEATURE_DIMENSION
            non_embedded_dimension + constants.ADDITIONAL_FEATURE_DIMENSION
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

    return output_feature_table, l_column_types, r_column_types

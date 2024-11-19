import logging
import os
import random
import re
from typing import Optional

import numpy as np
import pandas as pd
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction
from numpy.linalg import norm
from sentence_transformers import util
from strsimpy.damerau import Damerau
from strsimpy.metric_lcs import MetricLCS
from torch import Tensor

from app.src.correlations.enums import CombinationType
from app.src.correlations.model import SentenceTransformer
from app.src.correlations.self_features import make_self_features_from

SMOOTHIE = SmoothingFunction().method4
METRIC_LCS = MetricLCS()
DAMERAU = Damerau()
SEED = 200
random.seed(SEED)


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.split(r'[\s\_\.]', text)
    text = " ".join(text).strip()
    return text


def transformer_similarity(sentence1: str, sentence2: str) -> Tensor:
    """
    @return Use sentence transformer to calculate similarity between two sentences.
    """
    # TODO: Depends
    model = SentenceTransformer.get()

    embeddings1 = model.encode(sentence1)
    embeddings2 = model.encode(sentence2)
    cosine_similarity = util.cos_sim(embeddings1, embeddings2)
    return cosine_similarity


def read_mapping(mapping_file: Optional[str] = None) -> set:
    """
    Read mapping file and return a set.
    Params: mapping_file
    Returns: set
    """

    if mapping_file is None or not os.path.exists(mapping_file):
        logging.debug(f"[Mapping file: {mapping_file}] not found, Returns Empty Set")
        return set()

    with open(mapping_file, 'r') as f:
        mapped_data = f.readlines()

    mapped_data = [x.strip() for x in mapped_data]
    mapping = set()
    for m in mapped_data:
        m = m.split(",")
        m = [m.strip("< >") for m in m]
        mapping.add(tuple(m))
    return mapping


def make_combinations_labels(
        l_columns: list[pd.Index],
        r_columns: list[pd.Index],
        mapping: set,
        combination_type: CombinationType = CombinationType.TRAIN
):
    """
    Make combinations from columns1 list and columns2 list. Label them using mapping.
    """
    labels = {}
    for i, c1 in enumerate(l_columns):
        for j, c2 in enumerate(r_columns):
            labels[(i, j)] = int((c1, c2) in mapping or (c2, c1) in mapping)

    # sample negative labels
    if combination_type == CombinationType.TRAIN:
        combinations_count = len(labels)
        for i in range(combinations_count * 2):
            if sum(labels.values()) >= 0.1 * len(labels):
                break
            c1 = random.choice(range(len(l_columns)))
            c2 = random.choice(range(len(r_columns)))
            if (c1, c2) in labels and labels[c1, c2] == 0:
                del labels[(c1, c2)]

    return labels


def get_colnames_features(text1: str, text2: str, column_name_embeddings: dict[str, any]):
    """
    @return Use BLEU, edit distance and word2vec to calculate features.
    """
    bleu_score = bleu([text1], text2, smoothing_function=SMOOTHIE)
    edit_distance = DAMERAU.distance(text1, text2)
    lcs = METRIC_LCS.distance(text1, text2)
    transformer_score = util.cos_sim(column_name_embeddings[text1], column_name_embeddings[text2])
    one_in_one = text1 in text2 or text2 in text1
    colnames_features = np.array([bleu_score, edit_distance, lcs, transformer_score, one_in_one])
    return colnames_features


# TODO: embedding types
def get_instance_similarity(embeddings1, embeddings2) -> np.ndarray:
    """
    @return cosine similarity between two sentences.
    """
    cosine_similarity = np.inner(embeddings1, embeddings2) / (norm(embeddings1) * norm(embeddings2))
    return np.array([cosine_similarity])


def create_feature_matrix(
        l_df: pd.DataFrame,
        r_df: pd.DataFrame,
        mapping_file: Optional[str] = None,
        combination_type: CombinationType = CombinationType.TRAIN
):
    """
    Read data from 2 table dataframe, mapping file path and make relational features and labels as a matrix.
    """
    mapping = read_mapping(mapping_file)
    l_columns = list(l_df.columns)
    r_columns = list(r_df.columns)

    combinations_labels = make_combinations_labels(l_columns, r_columns, mapping, combination_type)

    l_table_features = make_self_features_from(l_df)
    r_table_features = make_self_features_from(r_df)

    # TODO: Depends
    model = SentenceTransformer.get()

    column_name_embeddings: dict[str, any] = {preprocess_text(k): model.encode(preprocess_text(k)) for k in
                                              l_columns + r_columns}

    # 6?
    additional_feature_num = 6

    # 768?
    output_feature_table = np.zeros(
        (len(combinations_labels), l_table_features.shape[1] - 768 + additional_feature_num),
        dtype=np.float32)
    output_labels = np.zeros(len(combinations_labels), dtype=np.int32)
    for i, (combination, label) in enumerate(combinations_labels.items()):
        c1, c2 = combination
        c1_name = preprocess_text(l_columns[c1])
        c2_name = preprocess_text(r_columns[c2])

        difference_features_percent = np.abs(l_table_features[c1] - r_table_features[c2]) / (
                l_table_features[c1] + r_table_features[c2] + 1e-8)

        colnames_features = get_colnames_features(c1_name, c2_name, column_name_embeddings)
        instance_similarity = get_instance_similarity(l_table_features[c1][-768:], r_table_features[c2][-768:])
        output_feature_table[i, :] = np.concatenate(
            (difference_features_percent[:-768], colnames_features, instance_similarity))
        output_labels[i] = label

        # add column names mask for training data
        if combination_type == CombinationType.TRAIN and i % 5 == 0:
            colnames_features = np.array([0, 12, 0, 0.2, 0])
            added_features = np.concatenate(
                (difference_features_percent[:-768], colnames_features, instance_similarity))
            added_features = added_features.reshape((1, added_features.shape[0]))
            output_feature_table = np.concatenate((output_feature_table, added_features), axis=0)
            output_labels = np.concatenate((output_labels, np.array([label])))

    return output_feature_table, output_labels

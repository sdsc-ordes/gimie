import json
from typing import List

import numpy as np
import pytest

from gimie.utils.text_processing import TfidfConfig, TfidfVectorizer

CORPUS = [
    "This is my test document.",
    "This is another test document.",
]


@pytest.fixture
def tfidf_vectorizer() -> TfidfVectorizer:
    """Fixture for a TfidfVectorizer instance."""
    config = TfidfConfig(norm="l2", sublinear_tf=True)
    return TfidfVectorizer(config=config)


def test_tfidf_serde(tfidf_vectorizer: TfidfVectorizer):
    """Test json serialization and deserialization of TfidfVectorizer."""
    json_str = tfidf_vectorizer.model_dump_json(indent=2)
    json.loads(json_str)
    print(TfidfVectorizer.model_validate_json(json_str))


def test_tfidf_fit_transform(tfidf_vectorizer: TfidfVectorizer):
    """Test correctness of tfidf fit."""
    _ = tfidf_vectorizer.fit_transform(CORPUS)
    # targets computed using sklearn 1.2.2
    target_voc = {
        "another": 0,
        "document": 1,
        "is": 2,
        "my": 3,
        "test": 4,
        "this": 5,
    }
    target_idf = np.array(
        [1.4054651081081644, 1.0, 1.0, 1.4054651081081644, 1.0, 1.0]
    )
    assert all(
        [v == target_voc[t] for t, v in tfidf_vectorizer.vocabulary.items()]
    )
    pred_idf: List[float] = tfidf_vectorizer.idf_vector
    assert all([pred == target for pred, target in zip(pred_idf, target_idf)])


# Test fitting different configurations
@pytest.mark.parametrize(
    "config",
    [
        TfidfConfig(),
        TfidfConfig(max_features=10),
        TfidfConfig(ngram_range=(1, 2)),
        TfidfConfig(ngram_range=(2, 2)),
        TfidfConfig(smooth_idf=False),
        TfidfConfig(norm="l1"),
        TfidfConfig(norm="l2"),
        TfidfConfig(sublinear_tf=True),
        TfidfConfig(vocabulary={"this": 0, "is": 1, "test": 2}),
    ],
)
def test_tfidf_configs(config):
    """Test fitting different configurations."""
    vectorizer = TfidfVectorizer(config=config)
    _ = vectorizer.fit_transform(CORPUS)

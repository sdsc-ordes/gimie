from collections import Counter
from functools import reduce
import re
from typing import (
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
)

import numpy as np
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
import scipy.sparse as sp


def tokenize(text: str, sep: str = " ") -> List[str]:
    """Basic tokenizer. Removes punctuation, but not stop words.

    Parameters
    ----------
    text:
        Text to tokenize.
    sep:
        Token separator.

    Examples
    --------
    >>> tokenize("Is this a test? Yes it is.")
    ['is', 'this', 'a', 'test', 'yes', 'it', 'is']
    """
    text = text.lower()
    text = re.sub(r"[\.|,|;|:|!|?|\n]", "", text)
    return text.split(sep)


def extract_ngrams(tokens: List[str], size: int = 1) -> List[str]:
    """Extract ngrams from a list of tokens.

    Parameters
    ----------
    tokens:
        List of tokens.
    size:
        Size of ngrams to extract.

    Examples
    --------
    >>> extract_ngrams(["this", "is", "a", "test"], size=2)
    ['this is', 'is a', 'a test']
    """
    return [
        " ".join(tokens[i : i + size])
        for i in range(0, len(tokens) - size + 1)
    ]


def get_ngram_counts(
    doc: str, ngram_range: Tuple[int, int] = (1, 1)
) -> Counter[str]:
    """Get ngram counts for a document. The ngram range is inclusive.

    Parameters
    ----------
    doc:
        Document to extract ngrams from.
    ngram_range:
        Inclusive range of ngram sizes to extract.

    Examples
    --------
    >>> get_ngram_counts("Red roses red.", ngram_range=(1, 2))
    Counter({'red': 2, 'roses': 1, 'red roses': 1, 'roses red': 1})
    """
    ngram_counts: Counter[str] = Counter()
    tokens = tokenize(doc)
    for size in range(ngram_range[0], ngram_range[1] + 1):
        ngram_counts += Counter(extract_ngrams(tokens, size))
    return ngram_counts


def normalize_csr_rows(X: sp.csr_matrix, norm: str = "l1") -> sp.csr_matrix:
    """Normalize rows of a CSR matrix in place.

    Parameters
    ----------
    X:
        CSR matrix to normalize.
    norm:
        Norm to use for normalization. Either "l1" or "l2".

    Examples
    --------
    >>> X = sp.csr_matrix([[1, 2], [3, 4]], dtype=np.float64)
    >>> normalize_csr_rows(X, norm="l1").toarray()
    array([[0.33333333, 0.66666667],
           [0.42857143, 0.57142857]])
    >>> normalize_csr_rows(X, norm="l2").toarray()
    array([[0.4472136 , 0.89442719],
           [0.6       , 0.8       ]])
    """
    norm_func = {
        "l1": lambda x: np.abs(x).sum(),
        "l2": lambda x: np.sqrt((x**2).sum()),
    }[norm]

    for i in range(X.shape[0]):
        if X[i].sum() == 0.0:
            continue

        X[i, :] /= norm_func(X[i].data)
    return X


@dataclass
class TfidfConfig:
    """Configuration for TfidfVectorizer.

    For more information on tf-idf, see https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html

    Parameters
    ----------
    max_features:
        Maximum number of features to keep. If None, all features are kept.
    ngram_range:
        Inclusive range of ngram sizes to extract.
    smooth_idf:
        Smooth idf weights by adding a constant 1 to the numerator and denominator
        of the idf as if an extra document was seen containing every term once,
        preventing zero divisions.
    vocabulary:
        Vocabulary to use. If None, the vocabulary is inferred from the data.
    norm:
        Normalization to use for the tfidf matrix. Either "l1" or "l2".
    sublinear_tf:
        Apply sublinear tf scaling, i.e. replace tf with 1 + log(tf).
    """

    max_features: Optional[int] = None
    ngram_range: Tuple[int, int] = (1, 1)
    smooth_idf: bool = True
    vocabulary: Optional[Dict[str, int]] = None
    norm: Optional[Literal["l1", "l2"]] = None
    sublinear_tf: bool = False


class TfidfVectorizer(BaseModel):
    r"""A simple term frequency-inverse document frequency (tf-idf) vectorizer
    that can be loaded from and serialized to JSON.

    This implementation replicates the behavior of scikit-learn's (as of 1.3.2),
    but only supports a subset of its parameters.

    For more information on tf-idf, see https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html

    Parameters
    ----------
    config:
        Configuration for the vectorizer.
    idf_vector:
        Precomputed idf vector. If None, it is computed from the data.
    vocabulary:
        Vocabulary to use. If None, the vocabulary is inferred from the data.

    Examples
    --------
    >>> docs = ["The quick brown fox", "jumps over", "the lazy dog."]
    >>> vectorizer = TfidfVectorizer(config=TfidfConfig())
    >>> tfidf = vectorizer.fit_transform(docs)
    >>> tfidf.shape
    (3, 8)
    """

    config: TfidfConfig
    idf_vector: List[float] = list()
    vocabulary: Dict[str, int] = Field(default_factory=dict)

    def _get_idf_vector(
        self, ngram_counts: List[Counter[str]], vocab: Dict[str, int]
    ) -> List[float]:
        """Compute the idf vector for the whole corpus from a list of
        ngram counts from each document.

        Parameters
        ----------
        ngram_counts:
            List of ngram counts for each document.
        vocab:
            Vocabulary to use. Each ngram key has an integer value used as the
            column index of the output matrix.
        """
        idf_vector = np.zeros(len(vocab), dtype=np.float64)
        for record in ngram_counts:
            idf_vector[[vocab[t] for t in record.keys() if t in vocab]] += 1
        n_docs = len(ngram_counts) + int(self.config.smooth_idf)
        idf_vector += int(self.config.smooth_idf)
        idf_vector = 1 + np.log(n_docs / (idf_vector))
        return list(idf_vector)

    def _get_tf_matrix(
        self, ngram_counts: List[Counter[str]], vocab: Dict[str, int]
    ) -> sp.csr_matrix:
        """Compute the term frequency matrix for the whole corpus from a
        list of ngram counts from each document.

        Parameters
        ----------
        ngram_counts:
            List of ngram counts for each document (rows of the output matrix).
        vocab:
            Vocabulary to use. Each ngram key has an integer value used as the
            column index of the output matrix.
        """
        tf_matrix = sp.lil_matrix(
            (len(ngram_counts), len(vocab)), dtype=np.float64
        )
        for idx, record in enumerate(ngram_counts):
            pairs = record.items()
            counts = [v for _, v in pairs]
            tf_matrix[idx, [vocab[t] for t, _ in pairs]] = [c for c in counts]
        tf_matrix = tf_matrix.tocsr()
        if self.config.sublinear_tf:
            # applies log in place
            np.log(tf_matrix.data, tf_matrix.data)  # type: ignore
            tf_matrix.data += 1  # type: ignore
        return tf_matrix

    def _get_tfidf(
        self, ngram_counts: List[Counter[str]], vocab: Dict[str, int]
    ) -> sp.csr_matrix:
        """Compute the tfidf matrix over the whole corpus from a list of
        ngram counts from each document.

        Parameters
        ----------
        ngram_counts:
            List of ngram counts for each document.
        vocab:
            Vocabulary to use. Each ngram key has an integer value used as the
            column index of the output matrix.
        """
        tf_matrix: sp.csr_matrix = self._get_tf_matrix(
            ngram_counts, vocab=vocab
        )

        tfidf_matrix = tf_matrix.multiply(np.array(self.idf_vector))  # type: ignore
        return tfidf_matrix.tocsr()  # type: ignore

    def _get_vocabulary(
        self, ngram_counts: Iterable[Counter[str]]
    ) -> dict[str, int]:
        """Get the vocabulary from a list of ngram counts. The vocabulary
        is a mapping from ngrams to integer used as column indices in the
        tfidf matrix.

        Parameters
        ----------
        ngram_counts:
            List of ngram counts for each document.
        """
        counts_corpus = reduce(lambda x, y: x | y, ngram_counts).most_common()
        if self.config.max_features is not None:
            counts_corpus = counts_corpus[: self.config.max_features]
        return {
            t[0]: i
            for i, t in enumerate(sorted(counts_corpus, key=lambda x: x[0]))
        }

    def fit(self, data: Iterable[str]):
        """Fit the vectorizer to a list of documents.

        Parameters
        ----------
        data:
            List of documents contents to fit the vectorizer to."""
        counts_records: List[Counter[str]] = [
            get_ngram_counts(doc, self.config.ngram_range) for doc in data
        ]
        vocab = self.config.vocabulary or self._get_vocabulary(counts_records)
        self.idf_vector = self._get_idf_vector(counts_records, vocab=vocab)
        self.vocabulary = vocab

    def transform(self, data: Iterable[str]) -> sp.csr_matrix:
        """Transform a list of documents into a tfidf matrix.
        The model must be fit before calling this method.

        Parameters
        ----------
        data:
            List of documents contents to transform.
        """
        if not self.vocabulary:
            raise ValueError("Vocabulary is empty. Call `fit` first.")
        counts_records = [
            get_ngram_counts(doc, self.config.ngram_range) for doc in data
        ]
        counts_records = [
            Counter({k: v for k, v in doc.items() if k in self.vocabulary})
            for doc in counts_records
        ]
        tfidf = self._get_tfidf(counts_records, vocab=self.vocabulary)
        if self.config.norm is not None:
            return normalize_csr_rows(tfidf, norm=self.config.norm)
        return tfidf

    def fit_transform(self, data: Iterable[str]) -> sp.csr_matrix:
        """Fit the vectorizer to a list of documents and transform them
        into a tfidf matrix.

        Parameters
        ----------
        data:
            List of documents contents to fit the vectorizer to and transform.
        """
        self.fit(list(data))
        return self.transform(data)

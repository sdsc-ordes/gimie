#!/usr/bin/env python3
"""Download all SPDX licenses and fit a tf-idf vectorizer to them.
The tf-idf matrix, vectorizer and license list are then saved to disk."""

import json
from pathlib import Path
from typing import List, NamedTuple

import scipy.sparse as sp
import requests

from gimie.utils.text import TfidfConfig, TfidfVectorizer

OUT_DIR = Path("gimie") / "parsers" / "license" / "data"

# Download all licenses metadata from SPDX
SPDX_LIST_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
all_licenses = requests.get(SPDX_LIST_URL).json()

# Assemble corpus of license texts (this takes a while)
class License(NamedTuple):
    license_id: str
    text: str


corpus: List[License] = []

for idx, license in enumerate(all_licenses["licenses"]):
    resp = requests.get(license["detailsUrl"])
    if not resp.ok:
        continue
    text = resp.json()["licenseText"]
    corpus.append(License(license["licenseId"], text))

# Fit tfidf vectorizer to corpus
texts = [l.text for l in corpus]
vectorizer = TfidfVectorizer(
    config=TfidfConfig(
        max_features=700, ngram_range=(1, 2), sublinear_tf=True, norm="l2"
    )
)
tfidf = vectorizer.fit_transform(texts)

# Save vectorizer and tfidf matrix
with open(OUT_DIR / "tfidf_vectorizer.json", "w") as fp:
    fp.write(vectorizer.model_dump_json())
sp.save_npz(OUT_DIR / "tfidf_matrix.npz", tfidf)
with open(OUT_DIR / "spdx_licenses.csv", "w") as fp:
    for l in corpus:
        fp.write(f"{l.license_id},{len(l.text)}\n")

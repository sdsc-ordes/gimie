#!/usr/bin/env python3
"""Download all SPDX licenses and fit a tf-idf vectorizer to them.
The tf-idf matrix, vectorizer and license list are then saved to disk."""

import json
from pathlib import Path
from typing import List, NamedTuple

import numpy as np
import requests
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
import skops.io as sio
from zipfile import ZIP_DEFLATED

OUT_DIR = Path("gimie") / "parsers" / "license" / "data"

# Retrieve metadata for all OSI approved and valid licenses from SPDX
SPDX_LIST_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
all_licenses = requests.get(SPDX_LIST_URL).json()["licenses"]
licenses = filter(lambda l: l["isOsiApproved"], all_licenses)
licenses = filter(lambda l: not l["isDeprecatedLicenseId"], licenses)
licenses = list(licenses)

# Assemble corpus of license texts (this takes a while)
class License(NamedTuple):
    license_id: str
    text: str


corpus: List[License] = []

for idx, license in enumerate(licenses):
    resp = requests.get(license["detailsUrl"])
    if not resp.ok:
        continue
    text = resp.json()["licenseText"]
    corpus.append(License(license["licenseId"], text))

# Fit tfidf vectorizer to corpus
texts = [l.text for l in corpus]
vectorizer = TfidfVectorizer(
    max_features=700, ngram_range=(1, 2), sublinear_tf=True, norm="l2"
)
tfidf = vectorizer.fit_transform(texts)

# Save vectorizer and tfidf matrix
obj = sio.dump(
    vectorizer,
    OUT_DIR / "tfidf_vectorizer.skops",
    compression=ZIP_DEFLATED,
    compresslevel=9,
)
# Prune precision to reduce size
tfidf.data = tfidf.data.astype(np.float16)
sp.save_npz(OUT_DIR / "tfidf_matrix.npz", tfidf)
with open(OUT_DIR / "spdx_licenses.csv", "w") as fp:
    for l in corpus:
        fp.write(f"{l.license_id},{len(l.text)}\n")

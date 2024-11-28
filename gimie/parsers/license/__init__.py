# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import csv
from io import BytesIO
import pkgutil
import re
from typing import List, Optional, Set

import numpy as np
import scipy.sparse as sp
from rdflib.term import URIRef
from rdflib import Graph
from gimie.graph.namespaces import SDO
from gimie.parsers.abstract import Parser, Property
from gimie.utils.text_processing import TfidfVectorizer


class LicenseParser(Parser):
    """Parse LICENSE body into schema:license <spdx-url>.
    Uses tf-idf-based matching."""

    def __init__(self, subject: str):
        super().__init__(subject)

    def parse(self, data: bytes) -> Graph:
        """Extracts an spdx URL from a license file and returns a
        graph with a single triple <url> <schema:license> <spdx_url>.
        If no matching URL is found, an empty graph is returned.
        """
        license_facts = Graph()
        license_url = match_license(data)

        if license_url:
            license_facts.add((self.subject, SDO.license, URIRef(license_url)))
        return license_facts


def match_license(data: bytes, min_similarity: float = 0.9) -> Optional[str]:
    """Given a license file, returns the url of the most similar spdx license.
    This is done using TF-IDF on the license text and getting the
    closest match in the SPDX license corpus based on cosine similarity.

    Parameters
    ----------
    data:
        The license body as bytes.

    Examples
    --------
    >>> match_license(open('LICENSE', 'rb').read())
    'https://spdx.org/licenses/Apache-2.0.html'
    """
    # Compute tfidf vector for input license
    vectorizer = load_tfidf_vectorizer()
    input_vec = vectorizer.transform([data.decode()])

    # Load ids and tfidf vectors for spdx licenses
    spdx_licenses = load_spdx_ids()
    spdx_vecs = load_tfidf_matrix()
    # Compute cosine similarity between input_vec and spdx vectors
    sim: np.ndarray = (input_vec * spdx_vecs.T).todense()
    # Pick the most similar spdx vector
    closest_idx = np.argmax(sim)
    # If similarity is below threshold, return None
    if sim[0, closest_idx] < min_similarity:
        return None
    closest_id = spdx_licenses[closest_idx]
    return f"https://spdx.org/licenses/{closest_id}.html"


def load_tfidf_vectorizer() -> TfidfVectorizer:
    """Load tfidf matrix and vectorizer from disk."""

    data = pkgutil.get_data(__name__, "data/tfidf_vectorizer.json")
    if data is None:
        raise FileNotFoundError("Could not find tfidf_vectorizer.json")
    return TfidfVectorizer.model_validate_json(data)


def load_spdx_ids() -> List[str]:
    """Load spdx licenses from disk."""
    data = pkgutil.get_data(__name__, "data/spdx_licenses.csv")
    if data is None:
        raise FileNotFoundError("Could not find spdx_licenses.csv")
    reader = csv.reader(data.decode().split("\n"))
    return [l[0] for l in reader if l]


def load_tfidf_matrix() -> sp.csr_matrix:
    """Load pre-computed tfidf matrix of spdx licenses from disk.
    Matrix has dimensions (n_licenses, n_features)."""
    data = pkgutil.get_data(__name__, "data/tfidf_matrix.npz")
    if data is None:
        raise FileNotFoundError("Could not find tfidf_matrix.npz")
    return sp.load_npz(BytesIO(data))


def is_license_filename(filename: str) -> bool:
    """Given an input filename, returns a boolean indicating whether the filename path looks like a license.

    Parameters
    ----------
    filename:
        A filename to check.

    Examples
    --------
    >>> is_license_filename('LICENSE-APACHE')
    True
    >>> is_license_filename('README.md')
    False
    """
    if filename.startswith("."):
        return False
    pattern = r".*(license(s)?.*|lizenz|reus(e|ing).*|copy(ing)?.*)(\.(txt|md|rst))?$"
    if re.match(pattern, filename, flags=re.IGNORECASE):
        return True
    return False

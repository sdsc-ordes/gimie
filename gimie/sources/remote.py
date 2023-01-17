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
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import requests
from typing import List, Optional
from urllib.parse import urlparse

from calamus import fields
from calamus.schema import JsonLDSchema
from rdflib import Graph

from gimie.sources.abstract import Extractor
from gimie.models import Person, PersonSchema
from gimie.namespaces import SDO

GH_API = "https://api.github.com"


@dataclass
class GithubExtractor(Extractor):
    path: str
    name: Optional[str] = None
    author: Optional[Person] = None
    contributors: Optional[List[Person]] = None
    prog_language: Optional[str] = None
    download_url: Optional[str] = None
    description: Optional[str] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    license: Optional[str] = None

    def extract(self):
        self._id = self.path
        self.name = urlparse(self.path).path.strip("/")

        resp = requests.get(f"{GH_API}/repos/{self.name}")
        if resp.status_code != 200:
            raise ConnectionError(resp.json()["message"])
        data = resp.json()

        self.author = self.get_user(data["owner"]["login"])
        self.contributors = self.get_contributors()
        self.download_url = (
            data["archive_url"][:-6]
            .removesuffix("{/ref}")
            .format(archive_format="tarball")
        )
        self.description = data["description"]
        self.date_created = datetime.fromisoformat(data["created_at"][:-1])
        self.date_modified = datetime.fromisoformat(data["updated_at"][:-1])
        self.license = data["license"]["url"]

    def get_user(self, name: str) -> Person:
        """Specialized API query to get user details."""
        resp = requests.get(f"{GH_API}/users/{name}").json()
        return Person.from_github(**resp)

    def get_contributors(self) -> List[Person]:
        """Specialized API query to get list of contributors names."""
        conts = requests.get(f"{GH_API}/repos/{self.name}/contributors").json()
        return [self.get_user(cont["login"]) for cont in conts]

    def to_graph(self) -> Graph:
        jd = GithubExtractorSchema().dumps(self)
        g: Graph = Graph().parse(format="json-ld", data=str(jd))
        g.bind("schema", SDO)
        return g


class GithubExtractorSchema(JsonLDSchema):
    """This defines the schema used for json-ld serialization."""

    _id = fields.Id()
    name = fields.String(SDO.name)
    author = fields.Nested(SDO.author, PersonSchema)
    contributors = fields.List(SDO.contributor, fields.String)
    prog_language = fields.String(SDO.programmingLanguage)
    download_url = fields.IRI(SDO.downloadUrl)
    description = fields.String(SDO.description)
    date_created = fields.Date(SDO.dateCreated)
    date_modified = fields.Date(SDO.dateModified)
    license = fields.IRI(SDO.license)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GithubExtractor


class GitlabExtractor(Extractor):
    def __init__(self, path: str):
        raise NotImplementedError

    def extractor(self):
        raise NotImplementedError

    def to_graph(self) -> Graph:
        """Generate an RDF graph from the instance"""
        raise NotImplementedError

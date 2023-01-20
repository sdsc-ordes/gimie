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
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

from calamus import fields
from calamus.schema import JsonLDSchema
from rdflib import Graph

from gimie.sources.abstract import Extractor
from gimie.models import Organization, OrganizationSchema, Person, PersonSchema
from gimie.graph.namespaces import SDO

GH_API = "https://api.github.com"


@dataclass
class GithubExtractor(Extractor):
    path: str
    name: Optional[str] = None
    author: Optional[Union[Organization, Person]] = None
    contributors: Optional[List[Person]] = None
    prog_language: Optional[List[str]] = None
    download_url: Optional[str] = None
    description: Optional[str] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    license: Optional[str] = None

    def to_graph(self) -> Graph:
        jd = GithubExtractorSchema().dumps(self)
        g: Graph = Graph().parse(format="json-ld", data=str(jd))
        g.bind("schema", SDO)
        return g

    def extract(self):
        self._id = self.path
        self.name = urlparse(self.path).path.strip("/")

        data = self._request(f"repos/{self.name}")
        self.author = self._get_owner(
            data["owner"]["login"], data["owner"]["type"]
        )
        self.contributors = self._get_contributors()
        self.download_url = data["archive_url"][:-6].format(
            archive_format="tarball"
        )
        self.description = data["description"]
        self.date_created = datetime.fromisoformat(data["created_at"][:-1])
        self.date_modified = datetime.fromisoformat(data["updated_at"][:-1])
        self.license = data["license"]["url"]

    @classmethod
    def _request(cls, query_path: str) -> Any:
        """Wrapper to query github api and return
        a dictionary of the json response.

        Parameters
        ----------
        query_path:
            The query, without the base path.

        """
        resp = requests.get(f"{GH_API}/{query_path.lstrip('/')}")
        # If the query fails, explain why
        if resp.status_code != 200:
            raise ConnectionError(resp.json()["message"])
        return resp.json()

    def _get_owner(
        self, name: str, owner_type: str
    ) -> Union[Organization, Person]:
        """Set the person or organization who owns the repository."""
        if owner_type == "User":
            return self._get_user(name)
        elif owner_type == "Organization":
            return self._get_organization(name)
        else:
            raise ValueError(f"Unknown Github owner type: {owner_type}.")

    def _get_user(self, name: str) -> Person:
        """Specialized API query to get user details."""
        # TODO: Handle first/last names and username properly
        user = self._request(f"users/{name}")
        # Get user's affiliations
        orgs = self._request(f"users/{name}/orgs")
        orgs = [
            Organization(
                _id=org["url"],
                name=org["login"],
                description=org["description"],
            )
            for org in orgs
        ]
        return Person(
            _id=user["url"],
            name=user["login"],
            given_name=user["name"],
            email=user["email"],
            affiliations=orgs,
        )

    def _get_organization(self, name: str) -> Organization:
        resp = self._request(f"orgs/{name}")
        return Organization(
            _id=resp["url"],
            name=resp["login"],
            description=resp["description"],
        )

    def _get_contributors(self) -> List[Person]:
        """Specialized API query to get list of contributors names."""
        conts = self._request(f"repos/{self.name}/contributors")
        return [self._get_user(cont["login"]) for cont in conts]


class GithubExtractorSchema(JsonLDSchema):
    """This defines the schema used for json-ld serialization."""

    _id = fields.Id()
    name = fields.String(SDO.name)
    author = fields.Nested(SDO.author, [PersonSchema, OrganizationSchema])
    contributors = fields.Nested(SDO.contributor, PersonSchema, many=True)
    prog_language = fields.List(SDO.programmingLanguage, fields.IRI)
    download_url = fields.IRI(SDO.downloadUrl)
    description = fields.String(SDO.description)
    date_created = fields.Date(SDO.dateCreated)
    date_modified = fields.Date(SDO.dateModified)
    license = fields.IRI(SDO.license)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GithubExtractor

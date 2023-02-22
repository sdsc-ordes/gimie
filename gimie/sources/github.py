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
import os
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse
from dotenv import load_dotenv

from calamus import fields
from calamus.schema import JsonLDSchema
from rdflib import Graph

from gimie.sources.abstract import Extractor
from gimie.models import (
    Organization,
    OrganizationSchema,
    Person,
    PersonSchema,
    IRI,
)
from gimie.graph.namespaces import SDO
from gimie.utils import get_spdx_url

GH_API = "https://api.github.com"
load_dotenv()


@dataclass
class GithubExtractor(Extractor):
    path: str
    github_token: Optional[str] = None

    name: Optional[str] = None
    author: Optional[Union[Organization, Person]] = None
    contributors: Optional[List[Person]] = None
    prog_langs: Optional[List[str]] = None
    download_url: Optional[str] = None
    description: Optional[str] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    keywords: Optional[List[str]] = None
    license: Optional[str] = None
    software_version: Optional[str] = None

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
        # If license is available, convert to standard SPDX URL
        if data["license"]["url"]:
            self.license = get_spdx_url(data["license"]["spdx_id"])
        self.prog_langs = self._get_prog_langs()
        self.keywords = data["topics"]
        self.version = self._get_last_release()

    def _set_auth(self) -> Any:
        try:
            if not self.github_token:
                self.github_token = os.environ.get("ACCESS_TOKEN")
                assert self.github_token
            headers = {"Authorization": f"token {self.github_token}"}

            login = requests.get(
                "https://api.github.com/user", headers=headers
            )
            assert login.json().get("login")
        except AssertionError:
            return {}
        else:
            return headers

    def _request(self, query_path: str) -> Any:
        """Wrapper to query github api and return
        a dictionary of the json response.

        Parameters
        ----------
        query_path:
            The query, without the base path.

        """
        resp = requests.get(
            f"{GH_API}/{query_path.lstrip('/')}", headers=self._set_auth()
        )
        # If the query fails, explain why
        if resp.status_code != 200:
            raise ConnectionError(resp.json()["message"])
        return resp.json()

    def _get_contributors(self) -> List[Person]:
        """Specialized API query to get list of contributors names."""
        conts = self._request(f"repos/{self.name}/contributors")
        return [self._get_user(cont["login"]) for cont in conts]

    def _get_last_release(self) -> Optional[str]:
        resp: List[Dict[str, Any]] = self._request(
            f"repos/{self.name}/releases"
        )
        if len(resp):
            return resp[0]["name"]
        return None

    def _get_organization(self, name: str) -> Organization:
        resp = self._request(f"orgs/{name}")
        return Organization(
            _id=resp["url"],
            name=resp["login"],
            description=resp["description"],
            legal_name=resp["name"],
            logo=resp["avatar_url"],
        )

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

    def _get_prog_langs(self) -> List[str]:
        """Get the list of programming languages used."""
        resp = self._request(f"repos/{self.name}/languages")
        return [lang for lang in resp.keys()]

    def _get_user(self, name: str) -> Person:
        """Specialized API query to get user details."""
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
            identifier=user["login"],
            name=user["name"],
            email=user["email"],
            affiliations=orgs,
        )


class GithubExtractorSchema(JsonLDSchema):
    """This defines the schema used for json-ld serialization."""

    _id = fields.Id()
    name = fields.String(SDO.name)
    author = fields.Nested(SDO.author, [PersonSchema, OrganizationSchema])
    contributors = fields.Nested(SDO.contributor, PersonSchema, many=True)
    prog_langs = fields.List(SDO.programmingLanguage, fields.String)
    download_url = fields.Raw(SDO.downloadUrl)
    description = fields.String(SDO.description)
    date_created = fields.Date(SDO.dateCreated)
    date_modified = fields.Date(SDO.dateModified)
    license = IRI(SDO.license)
    path = IRI(SDO.CodeRepository)
    keywords = fields.List(SDO.keywords, fields.String)
    version = fields.String(SDO.version)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GithubExtractor
        add_value_types = False

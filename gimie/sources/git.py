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
"""Extractor which uses a locally available (usually cloned) repository."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union
import uuid

from calamus import fields
from calamus.schema import JsonLDSchema
import git
import pydriller
from rdflib import Graph

from gimie.models import Person, PersonSchema
from gimie.graph.namespaces import SDO
from gimie.sources.abstract import Extractor
from gimie.utils import generate_uri


@dataclass
class GitExtractor(Extractor):
    """
    This class is responsible for extracting metadata from a git repository.

    Parameters
    ----------
    path: str
        The path to the git repository.

    Attributes
    ----------
    uri: Optional[str]
        The URI to assign the repository in RDF.
    repository: Repository
        The repository we are extracting metadata from.
    """

    path: str
    _id: Optional[str] = None
    author: Optional[Person] = None
    contributors: Optional[List[Person]] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None

    def extract(self):
        self.repository = pydriller.Repository(self.path)
        if self._id is None:
            head_commit_hash = git.Repo(self.path).head.commit.hexsha[:7]
            self._id = generate_uri(head_commit_hash)
        # Assuming author is the first person to commit
        self.author = self._get_creator()
        self.contributors = self._get_contributors()
        self.date_created = self._get_creation_date()
        self.date_modified = self._get_modification_date()

    def to_graph(self) -> Graph:
        """Generate an RDF graph from the instance"""
        jd = GitExtractorSchema().dumps(self)
        g: Graph = Graph().parse(data=str(jd), format="json-ld")
        g.bind("schema", SDO)
        return g

    def _get_contributors(self) -> List[Person]:
        """Get the authors of the repository."""
        authors = set()
        for commit in self.repository.traverse_commits():
            if commit.author is not None:
                authors.add((commit.author.name, commit.author.email))
        return [self._dev_to_person(name, email) for name, email in authors]

    def _get_creation_date(self) -> Optional[datetime]:
        """Get the creation date of the repository."""
        try:
            return next(self.repository.traverse_commits()).author_date
        except StopIteration:
            return None

    def _get_modification_date(self) -> Optional[datetime]:
        """Get the last modification date of the repository."""
        try:
            for commit in self.repository.traverse_commits():
                pass
            return commit.author_date
        except (StopIteration, NameError):
            return None

    def _get_creator(self) -> Optional[Person]:
        """Get the creator of the repository."""
        try:
            creator = next(self.repository.traverse_commits()).author
            return self._dev_to_person(creator.name, creator.email)
        except StopIteration:
            return None

    def _dev_to_person(
        self, name: Optional[str], email: Optional[str]
    ) -> Person:
        """Convert a Developer object to a Person object."""
        if name is None:
            uid = str(uuid.uuid4())
        else:
            uid = name.replace(" ", "_").lower()
        dev_id = f"{self._id}/{uid}"
        return Person(
            _id=dev_id,
            identifier=uid,
            name=name,
            email=email,
        )


class GitExtractorSchema(JsonLDSchema):
    _id = fields.Id()
    author = fields.Nested(SDO.author, PersonSchema)
    contributors = fields.Nested(SDO.contributor, PersonSchema, many=True)
    date_created = fields.Date(SDO.dateCreated)
    date_modified = fields.Date(SDO.dateModified)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GitExtractor
        add_value_types = False

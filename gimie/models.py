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
"""Data models to represent nodes in the graph generated by gimie."""
from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from typing import Optional, List

from calamus.schema import JsonLDSchema
from calamus import fields

from gimie.graph.namespaces import SDO


@dataclass(order=True)
class Release:
    """
    This class represents a release of a repository.

    Parameters
    ----------
    tag: str
        The tag of the release.
    date: datetime.datetime
        The date of the release.
    commit_hash: str
        The commit hash of the release.
    """

    tag: str = field(compare=False)
    date: datetime.datetime = field(compare=True)
    commit_hash: str = field(compare=False)


@dataclass
class Organization:
    """See http//schema.org/Organization"""

    _id: str
    name: str
    legal_name: Optional[str] = None
    email: Optional[List[str]] = None
    description: Optional[str] = None
    logo: Optional[str] = None


class OrganizationSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(SDO.name)
    legal_name = fields.String(SDO.legalName)
    email = fields.String(SDO.email)
    description = fields.String(SDO.description)
    logo = fields.IRI(SDO.logo)

    class Meta:
        rdf_type = SDO.Organization
        model = Organization


@dataclass
class Person:
    """See http//schema.org/Person"""

    _id: str
    identifier: str
    name: Optional[str] = None
    email: Optional[str] = None
    affiliations: Optional[List[Organization]] = None

    def __str__(self):
        name = f"({self.name}) " if self.name else ""
        email = f"<{self.email}> " if self.email else ""
        orgs = (
            f"[{', '.join([org.name for org in self.affiliations])}]"
            if self.affiliations
            else ""
        )
        return f"{self.identifier} {name}{email}{orgs}".strip(" ")


class PersonSchema(JsonLDSchema):
    _id = fields.Id()
    identifier = fields.String(SDO.identifier)
    name = fields.String(SDO.name)
    affiliations = fields.Nested(
        SDO.affiliation, OrganizationSchema, many=True
    )

    class Meta:
        rdf_type = SDO.Person
        model = Person

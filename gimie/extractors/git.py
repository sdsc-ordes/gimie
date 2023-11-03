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
from functools import cached_property
import os
import shutil
import tempfile
from typing import List, Optional
import uuid

import git
import pydriller

from gimie.io import LocalResource
from gimie.models import Person, Repository
from gimie.extractors.abstract import Extractor
from pathlib import Path


@dataclass
class GitExtractor(Extractor):
    """
    This class is responsible for extracting metadata from a git repository.

    Parameters
    ----------
    url: str
        The url of the git repository.
    base_url: Optional[str]
        The base url of the git remote.
    local_path: Optional[str]
        The local path where the cloned git repository is located.

    Attributes
    ----------
    uri: Optional[str]
        The URI to assign the repository in RDF.
    repository: Repository
        The repository we are extracting metadata from.
    """

    url: str
    base_url: Optional[str] = None
    local_path: Optional[str] = None
    _cloned: bool = False

    def extract(self) -> Repository:
        # Assuming author is the first person to commit
        self.repository = self._repo_data

        repo_meta = dict(
            authors=[self._get_creator()],
            contributors=self._get_contributors(),
            date_created=self._get_creation_date(),
            date_modified=self._get_modification_date(),
            name=self.path,
            url=self.url,
        )

        return Repository(**repo_meta)  # type: ignore

    def list_files(self) -> List[LocalResource]:
        self.repository = self._repo_data
        file_list = []

        for path in Path(self.local_path).rglob("*"):  # type: ignore
            if (path.parts[0] == ".git") or not path.is_file():
                continue
            file_list.append(LocalResource(path))

        return file_list

    def __del__(self):
        """Cleanup the cloned repo if it was cloned and is located in tempdir."""
        try:
            # Can't be too careful with temp files
            tempdir = tempfile.gettempdir()
            if (
                self.local_path
                and self._cloned
                and self.local_path.startswith(tempdir)
                and tempdir != os.getcwd()
            ):
                shutil.rmtree(self.local_path)
        except AttributeError:
            pass

    @cached_property
    def _repo_data(self) -> pydriller.Repository:
        """Get the repository data by accessing local data or cloning."""
        if self.local_path is None:
            self._cloned = True
            self.local_path = tempfile.TemporaryDirectory().name
            git.Repo.clone_from(self.url, self.local_path)  # type: ignore
        return pydriller.Repository(self.local_path)

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
        commit = None
        try:
            for commit in self.repository.traverse_commits():
                pass
        except (StopIteration, NameError):
            pass
        finally:
            return commit.author_date if commit else None

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
        dev_id = f"{self.url}/{uid}"
        return Person(
            _id=dev_id,
            identifier=uid,
            name=name,
            email=email,
        )

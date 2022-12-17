from typing import Optional, Tuple
from dataclasses import field, dataclass
from gimie.sources import files, git, license, web


@dataclass
class Repo:
    """A class to represent a git repository.


    Parameters
    ----------
    path :
        The path to the repository, either a file path or a URL.
    use_files :
        Whether to use file-derived metadata.
    use_git :
        Whether to use metadata derived from the git commits.
    use_html :
        Whether to use metadata from the HTML web-page.
    use_license :
        Whether to get the license type.

    Attributes
    ----------
    git_meta :
        Commit-related metadata, including authors and creation date.
    html_meta :
        HTML metadata, including title, description, and keywords.
    files_meta :
        File-related metadata, including file count, programming languages and file types.
    license :
        The license type of the repository.

    Examples
    --------
    >>> repo = Repo("https://github.com/SDSC-ORD/gimie")
    Traceback (most recent call last):
    ...
    NotImplementedError
    """

    path: str
    use_files: bool = True
    use_git: bool = True
    use_html: bool = True
    use_license: bool = True

    def __post_init__(self):
        self.files_meta = self.get_files_meta()
        # Git metadata contains the authors and creation date
        self.git_meta = self.get_git_meta()
        self.html_meta = self.get_html_meta()
        self.license = self.get_license_meta()

    def get_git_meta(self) -> Optional[git.GitMetadata]:
        return git.GitMetadata(self.path) if self.use_git else None

    def get_html_meta(self) -> Optional[web.WebMetadata]:
        return web.WebMetadata(self.path) if self.use_html else None

    def get_files_meta(self) -> Optional[files.FilesMetadata]:
        return files.FilesMetadata(self.path) if self.use_files else None

    def get_license_meta(self) -> Optional[license.LicenseMetadata]:
        return license.LicenseMetadata(self.path) if self.use_license else None

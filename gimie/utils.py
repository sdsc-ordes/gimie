from urllib.parse import urlparse


def validate_url(url: str):
    """Checks if input is a valid URL.
    credits: https://stackoverflow.com/a/38020041

    Examples
    -------------
    >>> validate_url('/data/my_repo')
    False
    >>> validate_url(532)
    False
    >>> validate_url('https://www.github.com/SDSC-ORD/gimie')
    True
    >>> validate_url('github.com/SDSC-ORD/gimie')
    False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def generate_fair_uri(repository_path: str):
    """given a repository_path, returns a URI with a hash for uniqueness, or the repository URL if it's online
    Example input:  -> https://www.github.com/SDSC-ORD/gimie (online)
                    -> my repository (local)"""
    # Compute the SHA-256 hash of the repository name
    hash = hashlib.sha256(repository_path.encode()).hexdigest()
    if validate_url(repository_path):
        fair_uri = repository_path
    else:
        # Return the FAIR URI in the form "sha256-HASH, truncated to 5 characters to promote readability"
        fair_uri = (
            f"gimie:{repository_path}/" + hash[:5]
        )  # TODO decide on URI+prefix we want to use for non online repos
    return fair_uri

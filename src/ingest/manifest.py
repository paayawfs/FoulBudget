"""Fetch and parse shufinskiy/nba_data's list_data.txt manifest."""

from urllib.request import urlopen

MANIFEST_URL = "https://raw.githubusercontent.com/shufinskiy/nba_data/main/list_data.txt"


def fetch_manifest(url: str = MANIFEST_URL) -> dict[str, str]:
    """Return {name: url} for every archive listed in list_data.txt."""
    with urlopen(url) as resp:
        text = resp.read().decode("utf-8")

    manifest = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        name, _, archive_url = line.partition("=")
        manifest[name] = archive_url
    return manifest

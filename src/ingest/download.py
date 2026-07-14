"""Download and extract shufinskiy/nba_data archives into data/raw/<datatype>/<season>/."""

import tarfile
from pathlib import Path
from urllib.request import urlopen

from ingest.manifest import fetch_manifest

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def download_archive(name: str, url: str, dest_dir: Path) -> None:
    """Stream one {datatype}_{season}.tar.xz archive and extract its CSVs into dest_dir."""
    if dest_dir.exists() and any(dest_dir.iterdir()):
        print(f"skip {name}: already extracted at {dest_dir}")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"{name}.tar.xz"

    print(f"downloading {name} from {url}")
    with urlopen(url) as resp, open(archive_path, "wb") as f:
        f.write(resp.read())

    with tarfile.open(archive_path, "r:xz") as tar:
        tar.extractall(dest_dir)

    archive_path.unlink()
    print(f"extracted {name} -> {dest_dir}")


def download_dev_slice(datatypes: list[str], seasons: list[int]) -> None:
    manifest = fetch_manifest()

    for datatype in datatypes:
        for season in seasons:
            name = f"{datatype}_{season}"
            if name not in manifest:
                raise KeyError(f"{name} not found in manifest")
            dest_dir = DATA_DIR / datatype / str(season)
            download_archive(name, manifest[name], dest_dir)


if __name__ == "__main__":
    download_dev_slice(datatypes=["nbastats", "pbpstats"], seasons=[2022, 2023, 2024])

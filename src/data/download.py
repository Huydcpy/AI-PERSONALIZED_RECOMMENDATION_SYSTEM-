"""Download the official MovieLens 100K archive (run from the repository root)."""

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve
from zipfile import ZipFile

URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
RAW_DIR = Path("data/raw")
REQUIRED = ("u.data", "u.item", "u.user", "u1.base", "u1.test")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if all((RAW_DIR / "ml-100k" / name).is_file() for name in REQUIRED):
        print("MovieLens 100K already exists; skipping download/extraction.")
        return
    archive = RAW_DIR / "ml-100k.zip"
    if not archive.exists():
        partial = archive.with_suffix(".zip.part")
        try:
            urlretrieve(URL, partial)
            partial.replace(archive)
        except (OSError, URLError) as exc:
            raise SystemExit(
                f"Download failed: {exc}\nDownload manually: {URL}\n"
                f"Save the archive to {archive}, then rerun this module."
            ) from exc
    else:
        print(f"Using existing archive: {archive}")
    with ZipFile(archive) as source:
        root = RAW_DIR.resolve()
        for member in source.infolist():
            if not (root / member.filename).resolve().is_relative_to(root):
                raise ValueError(f"Unsafe archive path: {member.filename}")
        source.extractall(RAW_DIR)
    if not all((RAW_DIR / "ml-100k" / name).is_file() for name in REQUIRED):
        raise ValueError("Archive does not contain the required MovieLens files")
    print(f"Extracted MovieLens 100K to {RAW_DIR / 'ml-100k'}")


if __name__ == "__main__":
    main()

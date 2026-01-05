from dataclasses import dataclass, field
from pathlib import Path
import shutil
import urllib.request
from urllib.parse import urljoin
from finance_daily.config import AppConfig
from finance_daily.constants import DatasetName, DAILY_RAW_T
from finance_daily.utils import load_tickers


@dataclass
class FetchResult:
    ok: bool
    written_files: dict[DatasetName, Path] = field(default_factory=dict)
    written_series_files: dict[str, Path] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _download_to_path(url: str, output_path: Path) -> None:
    """Stream-download a URL to disk without parsing it into pandas."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as resp:  # nosec - url is configured
        with output_path.open("wb") as f:
            shutil.copyfileobj(resp, f)


def fetch_and_store(config: AppConfig) -> FetchResult:
    """
    Fetch datasets from config.data_src and write them into config.data_dir.

    Returns a FetchResult so the UI can show what happened.
    """
    config.data_dir.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    written_files: dict[DatasetName, Path] = {}
    written_series_files: dict[str, Path] = {}

    base = str(config.data_src).rstrip("/") + "/"

    # --- Fixed datasets (known filenames) ---
    for name in DatasetName:
        # DatasetName values already include the ".csv" extension
        file_name = name.value
        csv_url = urljoin(base, file_name)
        try:
            print(f"Fetching {file_name} from {csv_url}")
            output_path = config.data_dir / file_name
            _download_to_path(csv_url, output_path)
            print(f"Successfully wrote {file_name}")
            written_files[name] = output_path

        except Exception as e:
            errors.append(f"{file_name}: {e}")

    # --- Dynamic datasets (ticker raw series) ---
    symbols = load_tickers(config).to_symbols()
    for sym in symbols:
        file_name = DAILY_RAW_T.format(symbol=sym)
        csv_url = urljoin(base, file_name)
        try:
            print(f"Fetching {file_name} from {csv_url}")
            output_path = config.data_dir / file_name
            _download_to_path(csv_url, output_path)
            print(f"Successfully wrote {file_name}")
            written_series_files[sym] = output_path
        except Exception as e:
            errors.append(f"{file_name}: {e}")

    ok = len(errors) == 0
    return FetchResult(
        ok=ok,
        written_files=written_files,
        written_series_files=written_series_files,
        errors=errors,
    )


def nightly_fetch() -> None:
    config = AppConfig()
    result = fetch_and_store(config)
    if result.ok:
        print("Data fetched successfully")
    else:
        print("Data fetched with errors")
        print(result.errors)


if __name__ == "__main__":
    nightly_fetch()

from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
from urllib.parse import urljoin
from finance_daily.config import AppConfig, DatasetName


@dataclass
class FetchResult:
    ok: bool
    written_files: dict[DatasetName, Path] = field(default_factory=dict)
    row_counts: dict[DatasetName, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def fetch_and_store(config: AppConfig) -> FetchResult:
    """
    Fetch datasets from config.data_src and write them into config.data_dir.

    Returns a FetchResult so the UI can show what happened.
    """
    if config.data_dir is None:
        raise ValueError("config.data_dir is not set")

    config.data_dir.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    written_files: dict[DatasetName, Path] = {}
    row_counts: dict[DatasetName, int] = {}

    base = str(config.data_src).rstrip("/") + "/"

    for name in DatasetName:
        file_name = f"{name.value}.csv"
        csv_url = urljoin(base, file_name)
        try:
            print(f"Fetching {file_name} from {csv_url}")
            df = pd.read_csv(csv_url)
            output_path = config.data_dir / file_name
            print(f"Writing {len(df)} rows to {output_path}")
            df.to_csv(output_path, index=False)
            print(f"Successfully wrote {file_name}")
            written_files[name] = output_path
            row_counts[name] = len(df)
        except Exception as e:
            errors.append(f"{file_name}: {e}")

    ok = len(errors) == 0
    return FetchResult(
        ok=ok, written_files=written_files, row_counts=row_counts, errors=errors
    )

import os
import subprocess
import sys


def dev():
    env = os.environ.copy()
    env["DATA_DIR"] = "./data"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/finance_daily/app.py",
        ],
        check=True,
        env=env,
    )

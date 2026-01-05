import os
import subprocess
import sys


def dev():
    env = os.environ.copy()
    env["DATA_DIR"] = "./data"
    env["CONFIG_DIR"] = "./finance_daily_config"

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


def prod():
    env = os.environ.copy()

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


def dev_nightly_fetch():
    env = os.environ.copy()
    env["DATA_DIR"] = "./data"
    env["CONFIG_DIR"] = "./finance_daily_config"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "finance_daily.services.nightly_fetch",
        ],
        check=True,
        env=env,
    )


def nightly_fetch():
    env = os.environ.copy()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "finance_daily.services.nightly_fetch",
        ],
        check=True,
        env=env,
    )

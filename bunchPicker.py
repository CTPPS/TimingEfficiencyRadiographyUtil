import requests
from pathlib import Path
from datetime import datetime
import sys
import json

API_BASE = "https://gitlab.cern.ch/api/v4"
PROJECT = "lhc-injection-scheme%2Finjection-schemes"
BRANCH = "master"


def list_all_files():
    json_files = []
    page = 1
    per_page = 100

    while True:
        url = f"{API_BASE}/projects/{PROJECT}/repository/tree"
        params = {"ref": BRANCH, "recursive": True, "per_page": per_page, "page": page}

        response = requests.get(url, params=params)
        response.raise_for_status()

        items = response.json()
        if not items:
            break

        json_files.extend(
            f["path"]
            for f in items
            if f["type"] == "blob" and f["path"].endswith(".json")
        )

        page += 1

    return json_files


def get_injection_scheme(
    injection_scheme_name,
):  # filenames with extensions (e.g. file.json)
    url = f"https://gitlab.cern.ch/lhc-injection-scheme/injection-schemes/raw/master/{injection_scheme_name}"
    response = requests.get(url)
    data = response.json()
    return data


def generate_leftmost_bunches(injection_scheme_name):
    data = get_injection_scheme(injection_scheme_name=injection_scheme_name)
    if "collsIP1/5" not in data.keys() or not data["collsIP1/5"]:
        return []
    bx = list(
        map(lambda x: (x - 1) // 10 + 1, data["collsIP1/5"])
    )  # convert from rf bucket to CMS count
    leftmost_bx = [bx[0]] + [bx[i] for i in range(1, len(bx)) if bx[i - 1] + 1 < bx[i]]
    return leftmost_bx


def get_newest_update_timestamp(directory):
    newest = None

    for file in Path(directory).iterdir():
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            update_date = data.get("update_date")
            if update_date:
                dt = datetime.fromisoformat(update_date.rstrip("Z"))
                if newest is None or dt > newest:
                    newest = dt
        except (json.JSONDecodeError, ValueError):
            continue

    return newest.isoformat() + "Z" if newest else None


def which_files_recently_updated(since_update_iso_time):
    changed_files = set()
    page = 1

    while True:
        url = f"{API_BASE}/projects/{PROJECT}/repository/commits"
        params = {
            "ref_name": BRANCH,
            "since": since_update_iso_time,
            "per_page": 100,
            "page": page,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        commits = response.json()

        if not commits:
            break

        for commit in commits:
            sha = commit["id"]
            diff_url = f"{API_BASE}/projects/{PROJECT}/repository/commits/{sha}/diff"
            diff_response = requests.get(diff_url)
            diff_response.raise_for_status()
            diffs = diff_response.json()

            for d in diffs:
                path = d.get("new_path")
                if path and path.endswith(".json"):
                    changed_files.add(path)

        page += 1

    return changed_files


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bunch_picker.py <injection_scheme_directory>")
        sys.exit(1)

    injection_scheme_directory = sys.argv[1]

    injection_scheme_names = list_all_files()

    newest_iso_timestamp = get_newest_update_timestamp(injection_scheme_directory)
    recently_updated_injection_schemes = which_files_recently_updated(
        newest_iso_timestamp
    )

    for injection_scheme_name in injection_scheme_names:
        file_path = (
            Path(injection_scheme_directory) / f"bunches_{injection_scheme_name}"
        )
        if not file_path.exists():
            data = {}
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

        missing_keys = any(k not in data for k in ("leftmost", "update_date"))
        outdated = (
            False
            if missing_keys
            else injection_scheme_name in recently_updated_injection_schemes
        )
        if missing_keys or outdated:
            print(f"Updating {injection_scheme_name}...")
            data["leftmost"] = generate_leftmost_bunches(injection_scheme_name)
            data["update_date"] = datetime.utcnow().isoformat() + "Z"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

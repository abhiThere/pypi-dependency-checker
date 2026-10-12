
import json
import urllib.request
import urllib.error
from datetime import datetime


def check_requirements(filename="requirements.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    checked = len(lines)
    missing_packages = []
    missing_versions = []
    valid_releases = []

    for line in lines:
        # Handle pinned dependencies such as requests==2.31.0
        if "==" not in line:
            print(f"Skipping unsupported requirement format: {line}")
            continue

        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()

        url = f"https://pypi.org/pypi/{name}/json"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "DependencyChecker/1.0"}
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                package_data = json.load(response)

        except urllib.error.HTTPError as error:
            if error.code == 404:
                missing_packages.append(name)
            else:
                print(f"Error checking {name}: HTTP {error.code}")
            continue

        except (urllib.error.URLError, TimeoutError) as error:
            print(f"Error checking {name}: {error}")
            continue

        releases = package_data.get("releases", {})

        if version not in releases or not releases[version]:
            missing_versions.append(f"{name}=={version}")
            continue

        # Use upload_time of the first file listed under urls.
        release_files = releases[version]
        upload_time = release_files[0].get("upload_time")

        if upload_time:
            year = datetime.fromisoformat(
                upload_time.replace("Z", "+00:00")
            ).year

            valid_releases.append(
                (upload_time, f"{name}=={version} ({year})")
            )

    print(f"Dependencies checked: {checked}")
    print(f"Packages not on PyPI: {missing_packages}")
    print(f"Versions not on PyPI: {missing_versions}")

    if valid_releases:
        oldest = min(valid_releases, key=lambda release: release[0])
        print(f"Oldest pinned release: {oldest[1]}")
    else:
        print("Oldest pinned release: None")


if __name__ == "__main__":
    check_requirements()

"""Publish verified assets to a draft; never overwrite release content."""

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from scripts.release import project_version, sha256, verified_assets


class AssetRedirect(urllib.request.HTTPRedirectHandler):
    """Do not forward the API token to the signed asset download host."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        if urllib.parse.urlparse(new_url).scheme != "https":
            raise ValueError("Refusing non-HTTPS asset redirect")
        redirected = super().redirect_request(
            request, response, code, message, headers, new_url
        )
        if redirected is not None and (
            urllib.parse.urlparse(request.full_url).hostname
            != urllib.parse.urlparse(new_url).hostname
        ):
            redirected.remove_header("Authorization")
        return redirected


class GitHub:
    """Small REST client restricted to the GitHub API and upload hosts."""

    def __init__(self, repository: str, token: str):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
            raise ValueError("Invalid GitHub repository")
        self.base = f"https://api.github.com/repos/{repository}"
        self.token = token

    def request(
        self, method: str, url: str, *, data: bytes | None = None,
        accept: str = "application/vnd.github+json",
        content_type: str = "application/json",
    ) -> bytes:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {
            "api.github.com", "uploads.github.com"
        }:
            raise ValueError("Unexpected GitHub API host")
        request = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": accept,
            "Content-Type": content_type,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "auto-pptx-release",
        })
        opener = urllib.request.build_opener(AssetRedirect())
        with opener.open(request, timeout=120) as response:
            return response.read()

    def find_release(self, tag: str) -> dict | None:
        try:
            return json.loads(self.request(
                "GET", f"{self.base}/releases/tags/{urllib.parse.quote(tag, safe='')}"
            ))
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise

    def create_draft(self, tag: str, commit: str) -> dict:
        return json.loads(self.request("POST", f"{self.base}/releases", data=json.dumps({
            "tag_name": tag,
            "target_commitish": commit,
            "name": f"auto-pptx {tag}",
            "draft": True,
            "body": (
                f"Windows x64；源码提交：{commit}\n\n"
                "只需下载 exe 即可运行；首次启动在同目录创建 config.toml，请放在可写目录。\n"
                "可选下载 SHA256SUMS.txt 核对校验和。"
            ),
        }).encode()))

    def assets(self, release: dict) -> list[dict]:
        result = []
        page = 1
        while True:
            batch = json.loads(self.request(
                "GET", f"{self.base}/releases/{release['id']}/assets?per_page=100&page={page}"
            ))
            result.extend(batch)
            if len(batch) < 100:
                return result
            page += 1

    def asset_bytes(self, asset: dict) -> bytes:
        return self.request(
            "GET", f"{self.base}/releases/assets/{asset['id']}",
            accept="application/octet-stream",
        )

    def upload(self, release: dict, path: Path) -> None:
        upload_url = release["upload_url"].split("{", 1)[0]
        self.request(
            "POST", f"{upload_url}?{urllib.parse.urlencode({'name': path.name})}",
            data=path.read_bytes(), content_type="application/octet-stream",
        )


def publish(client: GitHub, tag: str, commit: str, directory: Path) -> str:
    """Preflight all conflicts before mutation; retries upload only missing files."""
    version = project_version(tag=tag)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected a full source commit SHA")
    paths = verified_assets(directory)
    if paths[0].name != f"auto-pptx-v{version}-windows-x64.exe":
        raise ValueError("Package version does not match tag")
    info = json.loads((directory / "release-info.json").read_text(encoding="utf-8"))
    if (
        info["commit"] != commit or info["version"] != version
        or info["trial"] is not None
        or info["executable_sha256"] != sha256(paths[0])
    ):
        raise ValueError("Package provenance does not match the tagged build")
    release = client.find_release(tag)
    if release is not None and not release["draft"]:
        return "Published release left unchanged"
    assets = client.assets(release) if release else []
    missing = []
    for path in paths:
        matches = [asset for asset in assets if asset["name"] == path.name]
        if len(matches) > 1:
            raise ValueError(f"Duplicate remote asset: {path.name}")
        if matches:
            remote_hash = hashlib.sha256(client.asset_bytes(matches[0])).digest()
            if remote_hash != hashlib.sha256(path.read_bytes()).digest():
                raise ValueError(f"Conflicting draft asset: {path.name}")
        else:
            missing.append(path)
    if release is None:
        release = client.create_draft(tag, commit)
    for path in missing:
        client.upload(release, path)
    return "Draft ready"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    client = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
    print(publish(client, args.tag, args.commit, args.directory))


if __name__ == "__main__":
    main()

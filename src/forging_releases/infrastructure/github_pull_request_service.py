"""GitHub API implementation of the PullRequestService outbound port."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from forging_releases.application.ports.outbound.pull_request_service import (
    OpenPullRequestOutput,
    PullRequestService,
)
from forging_releases.domain.entities import ReleasePullRequest


class GitHubPullRequestService(PullRequestService):
    """Opens pull requests against a GitHub repository via the REST API.

    Requires GITHUB_TOKEN env var or a token passed at construction.
    Uses only stdlib (urllib) — no third-party HTTP client needed.
    """

    _API_BASE: str = "https://api.github.com"

    def __init__(
        self,
        *,
        owner: str,
        repo: str,
        token: str | None = None,
        base_url: str = "https://api.github.com",
    ) -> None:
        self._owner = owner
        self._repo = repo
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self._base_url = base_url.rstrip("/")

    def open(self, pull_request: ReleasePullRequest) -> OpenPullRequestOutput:
        """Create a pull request via the GitHub API."""
        url = f"{self._base_url}/repos/{self._owner}/{self._repo}/pulls"
        payload = json.dumps(
            {
                "title": pull_request.title,
                "head": pull_request.head.value,
                "base": pull_request.base.value,
                "body": pull_request.body,
            }
        ).encode("utf-8")

        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return OpenPullRequestOutput(
                    pr_id=str(data.get("number", "")),
                    url=data.get("html_url"),
                )
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API error {exc.code}: {error_body}") from exc

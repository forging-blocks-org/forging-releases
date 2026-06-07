from __future__ import annotations

import json
import urllib.error
import urllib.request

from forging_releases.application.ports.outbound import OpenPullRequestOutput, PullRequestService
from forging_releases.domain.entities import ReleasePullRequest


class GitHubPullRequestService(PullRequestService):
    def __init__(
        self,
        *,
        owner: str,
        repo: str,
        token: str,
        base_url: str = "https://api.github.com",
    ) -> None:
        self._owner = owner
        self._repo = repo
        self._token = token
        self._base_url = base_url

    def open(self, pull_request: ReleasePullRequest) -> OpenPullRequestOutput:
        url = f"{self._base_url}/repos/{self._owner}/{self._repo}/pulls"

        body_dict = {
            "title": pull_request.title,
            "head": pull_request.head.value,
            "base": pull_request.base.value,
            "body": pull_request.body,
        }
        data = json.dumps(body_dict).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "User-Agent": "forging-releases",
            },
        )

        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                return OpenPullRequestOutput(
                    pr_id=str(response_data["number"]),
                    url=response_data["html_url"],
                )
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            raise RuntimeError(
                f"Failed to create pull request: {exc}"
            ) from exc

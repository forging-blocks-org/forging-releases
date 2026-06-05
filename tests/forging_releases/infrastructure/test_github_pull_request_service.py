# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false, reportIncompatibleMethodOverride=false, reportUnusedClass=false, reportFunctionMemberAccess=false, reportOptionalMemberAccess=false
"""Integration tests for GitHubPullRequestService using a local HTTP test server."""

from __future__ import annotations

import json
import threading
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from forging_releases.domain.entities import ReleasePullRequest
from forging_releases.domain.value_objects import ReleaseBaseBranchName, ReleaseBranchName
from forging_releases.infrastructure.github_pull_request_service import (
    GitHubPullRequestService,
)


class _PRHandler(BaseHTTPRequestHandler):
    """Test HTTP handler that simulates GitHub's PR creation endpoint."""

    received_requests: list[dict[str, object]]

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.received_requests = []
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length).decode("utf-8"))
        _PRHandler.received_requests.append(body)

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"number": 42, "html_url": "https://github.com/owner/repo/pull/42"}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        pass  # Suppress logs


@pytest.fixture
def test_http_server() -> Generator[str]:
    """Start a local HTTP server for testing."""
    _PRHandler.received_requests = []
    server = HTTPServer(("127.0.0.1", 0), _PRHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host: str = server.server_address[0]  # type: ignore[assignment]
    port: int = server.server_address[1]  # type: ignore[assignment]
    yield f"http://{host}:{port}"
    server.shutdown()


@pytest.mark.integration
class TestGitHubPullRequestService:
    def test_when_pr_created_then_returns_output(self, test_http_server: str) -> None:
        svc = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake-token",
            base_url=test_http_server,
        )
        pr = ReleasePullRequest.create(
            base=ReleaseBaseBranchName("release/v0.0.0"),
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Automated release",
            external_id=None,
        )

        output = svc.open(pr)

        assert output.pr_id == "42"
        assert output.url == "https://github.com/owner/repo/pull/42"

        assert len(_PRHandler.received_requests) == 1
        req_body = _PRHandler.received_requests[0]
        assert req_body["title"] == "Release v1.0.0"
        assert req_body["head"] == "release/v1.0.0"

    def test_when_api_error_then_raises(self) -> None:
        # Connect to a port where nothing is listening
        svc = GitHubPullRequestService(
            owner="owner",
            repo="repo",
            token="fake-token",
            base_url="http://127.0.0.1:1",
        )
        pr = ReleasePullRequest.create(
            base=ReleaseBaseBranchName("release/v0.0.0"),
            head=ReleaseBranchName("release/v1.0.0"),
            title="Release v1.0.0",
            body="Automated release",
            external_id=None,
        )

        with pytest.raises((RuntimeError, OSError)):
            svc.open(pr)

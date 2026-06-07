from __future__ import annotations

import json
import threading
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest


class _RequestCaptureHandler(BaseHTTPRequestHandler):
    received: ClassVar[list[dict[str, object]]] = []

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length).decode("utf-8"))
        _RequestCaptureHandler.received.append(body)

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"number": 42, "html_url": "https://github.com/owner/repo/pull/42"}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture
def http_pr_server() -> Generator[str]:
    _RequestCaptureHandler.received.clear()
    server = HTTPServer(("127.0.0.1", 0), _RequestCaptureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host: str = server.server_address[0]
    port: int = server.server_address[1]
    yield f"http://{host}:{port}"
    server.shutdown()

import hashlib
import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import attr

FIXTURE_DIR = Path(__file__).parent / "fixtures"
VALID_KEY = "BSA-test-key"
# Fixtures reference this host for every image; the stub rewrites it to itself and serves placeholders,
# so rendered pages have real (if synthetic) images instead of broken ones.
IMAGE_HOST = "https://imgs.example.test"
_PLACEHOLDER_COLORS = ("#8ab4f8", "#f28b82", "#fdd663", "#81c995", "#c58af9", "#78d9ec")

_FIXTURES = {
    "/web/search": "web_search.json",
    "/images/search": "image_search.json",
    "/news/search": "news_search.json",
}


@attr.s(auto_attribs=True, frozen=True)
class BraveStub:
    base_url: str


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802  (BaseHTTPRequestHandler's naming)
        path = urlsplit(self.path).path
        if path.startswith("/img"):
            self._respond_placeholder(path)
            return
        if self.headers.get("X-Subscription-Token") != VALID_KEY:
            self._respond(401, {"error": {"code": "SUBSCRIPTION_TOKEN_INVALID", "detail": "Invalid token"}})
            return
        fixture = _FIXTURES.get(path)
        if fixture is None:
            self._respond(404, {"error": {"detail": f"no stub for {path}"}})
            return
        body = (FIXTURE_DIR / fixture).read_text().replace(IMAGE_HOST, f"http://{self.headers['Host']}/img")
        self._respond(200, json.loads(body))

    def _respond_placeholder(self, path: str) -> None:
        digest = hashlib.sha256(path.encode()).digest()
        color = _PLACEHOLDER_COLORS[digest[0] % len(_PLACEHOLDER_COLORS)]
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 90">'
            f'<rect width="120" height="90" fill="{color}"/>'
            f'<circle cx="{40 + digest[1] % 40}" cy="{30 + digest[2] % 30}" r="18" fill="rgba(255,255,255,.45)"/>'
            "</svg>"
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Content-Length", str(len(svg)))
        self.end_headers()
        self.wfile.write(svg)

    def _respond(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@contextmanager
def run_brave_stub() -> Iterator[BraveStub]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[0], server.server_address[1]
        yield BraveStub(base_url=f"http://{host}:{port}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

import json
import os
import random
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Share of requests to "/" that fail with HTTP 500.
# Good releases keep this at 0.0. The FAIL_RATE env var overrides it.
DEFAULT_FAIL_RATE = 0.0

_lock = threading.Lock()
_counts = {200: 0, 500: 0}


def get_config():
    return {
        "message": os.environ.get("PODINFO_UI_MESSAGE", "Hello"),
        "color": os.environ.get("PODINFO_UI_COLOR", "#555555"),
        "version": os.environ.get("APP_VERSION", "dev"),
        "fail_rate": float(os.environ.get("FAIL_RATE", DEFAULT_FAIL_RATE)),
    }


def record(status):
    with _lock:
        _counts[status] = _counts.get(status, 0) + 1


def render_metrics():
    lines = [
        "# HELP http_requests_total Total HTTP requests, probes excluded.",
        "# TYPE http_requests_total counter",
    ]
    with _lock:
        for code, count in sorted(_counts.items()):
            lines.append(f'http_requests_total{{code="{code}"}} {count}')
    return "\n".join(lines) + "\n"


def route(path):
    cfg = get_config()
    if path in ("/healthz", "/readyz"):
        return 200, "text/plain", "ok"
    if path == "/metrics":
        return 200, "text/plain; version=0.0.4", render_metrics()
    if path == "/version":
        return 200, "application/json", json.dumps({"version": cfg["version"]})
    if path == "/":
        if random.random() < cfg["fail_rate"]:
            return 500, "text/plain", "internal error"
        html = (
            f'<html><body style="background:{cfg["color"]};color:white;'
            f'font-family:sans-serif;text-align:center;padding-top:20vh">'
            f'<h1>{cfg["message"]}</h1><p>version: {cfg["version"]}</p>'
            f"</body></html>"
        )
        return 200, "text/html", html
    return 404, "text/plain", "not found"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, content_type, body = route(self.path)
        if self.path not in ("/healthz", "/readyz", "/metrics"):
            record(status)
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 9898), Handler).serve_forever()

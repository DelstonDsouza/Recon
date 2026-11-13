import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


def get_config():
    return {
        "message": os.environ.get("PODINFO_UI_MESSAGE", "Hello"),
        "color": os.environ.get("PODINFO_UI_COLOR", "#555555"),
        "version": os.environ.get("APP_VERSION", "dev"),
    }


def route(path):
    cfg = get_config()
    if path in ("/healthz", "/readyz"):
        return 200, "text/plain", "ok"
    if path == "/version":
        return 200, "application/json", json.dumps({"version": cfg["version"]})
    if path == "/":
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
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 9898), Handler).serve_forever()

"""gaku_ai_life_report.html を 127.0.0.1:3940 で配信する単一ファイルサーバー.

Tailscale Funnel から本人だけアクセス可能にする前提。
ローカル LAN には公開しない (127.0.0.1 bind)。
"""
from __future__ import annotations

import http.server
import socketserver
import sys
from pathlib import Path

FILE = Path.home() / "Desktop" / "gaku_ai_life_report.html"
PORT = 3940


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html", "/report"):
            try:
                data = FILE.read_bytes()
            except FileNotFoundError:
                self.send_error(404, "report not generated yet")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        sys.stderr.write("[report_server] " + (fmt % args) + "\n")


def main():
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        sys.stderr.write(f"[report_server] listening on 127.0.0.1:{PORT}, serving {FILE}\n")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

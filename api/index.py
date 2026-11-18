from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import analyze_url


class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") == "/api/health":
            self._send_json({"status": "ok", "message": "Backend phishing detection aktif"})
            return

        self._send_json({"error": "Endpoint tidak ditemukan"}, status=404)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/predict":
            self._send_json({"error": "Endpoint tidak ditemukan"}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            payload = json.loads(raw_body or "{}")
            result = analyze_url(payload.get("url", ""))
            self._send_json(result)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except json.JSONDecodeError:
            self._send_json({"error": "Format JSON tidak valid."}, status=400)
        except Exception as exc:
            self._send_json({"error": f"Terjadi masalah di server: {exc}"}, status=500)

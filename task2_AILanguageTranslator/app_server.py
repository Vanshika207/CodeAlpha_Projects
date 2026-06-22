"""
Browser dashboard server for AI Smart Language Translator.

Run:
    python app_server.py

Then open:
    http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import mimetypes
import tempfile
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime

from database import DatabaseManager
from export_service import ExportService
from translator_service import TranslationError, TranslatorService


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


class TranslatorWebApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.translator = TranslatorService()

    def languages(self):
        return {
            "source": self.translator.get_language_names(include_auto=True),
            "target": self.translator.get_language_names(include_auto=False),
        }

    def translate(self, payload):
        text = str(payload.get("text", "")).strip()
        source = str(payload.get("source", "Auto Detect"))
        target = str(payload.get("target", "English"))
        result = self.translator.translate(text, source, target)
        translated_text = result["translated_text"]
        detected_name = result["detected_source_name"]
        self.db.save_translation(text, translated_text, detected_name, target)
        return {
            "translatedText": translated_text,
            "detectedSource": detected_name,
            "target": target,
        }

    def history(self):
        records = self.db.get_history(limit=100)
        return [
            {
                "id": row[0],
                "source_text": row[1],
                "translated_text": row[2],
                "source_language": row[3],
                "target_language": row[4],
                "created_at": row[5] if row[5] else datetime.now().isoformat(),
            }
            for row in records
        ]

    def delete_history(self, entry_id):
        self.db.delete_entry(int(entry_id))
        return self.history()

    def clear_history(self):
        self.db.clear_history()
        return self.history()

    def export_file(self, payload, file_type):
        original = str(payload.get("original", "")).strip()
        translated = str(payload.get("translated", "")).strip()
        source = str(payload.get("source", "Auto Detect"))
        target = str(payload.get("target", "English"))
        if not original or not translated:
            raise ValueError("Translate text before exporting.")

        suffix = ".pdf" if file_type == "pdf" else ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            path = tmp.name

        if file_type == "pdf":
            ExportService.export_to_pdf(path, original, translated, source, target)
            content_type = "application/pdf"
            filename = "translation.pdf"
        else:
            ExportService.export_to_txt(path, original, translated, source, target)
            content_type = "text/plain; charset=utf-8"
            filename = "translation.txt"

        data = Path(path).read_bytes()
        Path(path).unlink(missing_ok=True)
        return data, content_type, filename


APP = TranslatorWebApp()


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "AITranslatorWeb/1.0"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/languages":
            self._json(200, APP.languages())
            return
        if parsed.path == "/api/history":
            self._json(200, APP.history())
            return
        self._static(parsed.path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/translate":
                self._json(200, APP.translate(payload))
                return
            if parsed.path == "/api/export/txt":
                self._download(*APP.export_file(payload, "txt"))
                return
            if parsed.path == "/api/export/pdf":
                self._download(*APP.export_file(payload, "pdf"))
                return
            self._json(404, {"error": "Endpoint not found."})
        except (TranslationError, ValueError) as exc:
            self._json(400, {"error": str(exc)})
        except Exception:
            self._json(500, {"error": "Something went wrong. Please try again."})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/history":
            self._json(200, APP.clear_history())
            return
        if parsed.path.startswith("/api/history/"):
            entry_id = parsed.path.rsplit("/", 1)[-1]
            self._json(200, APP.delete_history(entry_id))
            return
        self._json(404, {"error": "Endpoint not found."})

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _download(self, data, content_type, filename):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _static(self, request_path):
        if request_path in ("", "/"):
            request_path = "/index.html"

        safe_path = Path(urllib.parse.unquote(request_path.lstrip("/")))
        file_path = (WEB_DIR / safe_path).resolve()
        if WEB_DIR not in file_path.parents and file_path != WEB_DIR:
            self._json(403, {"error": "Forbidden"})
            return
        if not file_path.exists() or not file_path.is_file():
            self._json(404, {"error": "File not found"})
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"AI Smart Language Translator is running at http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")
    server.serve_forever()


if __name__ == "__main__":
    run()

"""ZYTHON HTTP server: Render uchun.

Endpointlar:
    GET  /         xizmat haqida ma'lumot
    GET  /health   Render health check
    GET  /version  versiya
    POST /check    kodni faqat tekshirish (parse)
    POST /run      kodni bajarish
"""
from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, request

from zython import Interpreter, ZythonError, __version__, parse_source

MAX_SOURCE = int(os.environ.get("ZYTHON_MAX_SOURCE", "20000"))
MAX_OUTPUT = int(os.environ.get("ZYTHON_MAX_OUTPUT", "100000"))
MAX_STEPS = int(os.environ.get("ZYTHON_MAX_STEPS", "1000000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("zython.server")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_SOURCE + 1024


class CappedOutput:
    """print() chiqishini cheklaydi: cheksiz chiqish xotirani to'ldirmasin."""

    def __init__(self, limit: int):
        self.limit = limit
        self.parts: list[str] = []
        self.size = 0

    def write(self, text: str) -> int:
        self.size += len(text)
        if self.size > self.limit:
            raise ZythonError(
                "output limit exceeded",
                file="<server>",
                hint=f"output is limited to {self.limit} characters",
                kind="RuntimeError",
            )
        self.parts.append(text)
        return len(text)

    def flush(self) -> None:
        pass

    def getvalue(self) -> str:
        return "".join(self.parts)


def error_payload(err: ZythonError) -> dict:
    return {
        "ok": False,
        "error": {
            "kind": err.kind,
            "message": err.message,
            "file": err.file,
            "line": err.line,
            "col": err.col,
            "hint": err.hint,
        },
    }


def read_source():
    """So'rovdan 'source' maydonini oladi. Xato bo'lsa (javob, status) qaytaradi."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("source"), str):
        return None, (jsonify({"ok": False, "error": {"message": "JSON body with string field 'source' is required"}}), 400)
    source = data["source"]
    if len(source) > MAX_SOURCE:
        return None, (jsonify({"ok": False, "error": {"message": f"source is too large (limit {MAX_SOURCE} characters)"}}), 413)
    return source, None


@app.get("/")
def index():
    return jsonify({
        "name": "ZYTHON",
        "version": __version__,
        "endpoints": {
            "GET /health": "health check",
            "GET /version": "version",
            "POST /check": 'body {"source": "..."}: syntax check',
            "POST /run": 'body {"source": "..."}: execute code',
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "version": __version__})


@app.get("/version")
def version():
    return jsonify({"version": __version__})


@app.post("/check")
def check():
    source, error = read_source()
    if error:
        return error
    try:
        parse_source(source, "<server>")
    except ZythonError as err:
        return jsonify(error_payload(err)), 400
    return jsonify({"ok": True})


@app.post("/run")
def run():
    source, error = read_source()
    if error:
        return error

    out = CappedOutput(MAX_OUTPUT)
    try:
        interp = Interpreter("<server>", out)
        interp.max_steps = MAX_STEPS
        interp.run(parse_source(source, "<server>"))
    except ZythonError as err:
        return jsonify(error_payload(err)), 400
    except Exception:
        log.exception("internal error while running user code")
        return jsonify({"ok": False, "error": {"message": "internal server error"}}), 500

    return jsonify({"ok": True, "output": out.getvalue(), "steps": interp.steps})


@app.errorhandler(404)
def not_found(_):
    return jsonify({"ok": False, "error": {"message": "not found"}}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"ok": False, "error": {"message": "method not allowed"}}), 405


if __name__ == "__main__":
    # Lokal ishga tushirish: PORT env yoki 10000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))

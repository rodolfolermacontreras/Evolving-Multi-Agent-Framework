"""HTTP server surface for the SDD state dashboard.

SDD-048 C-1 extraction E2: isolates the live-serve HTTP layer
(``served_html_with_refresh``, ``DashboardHandler``, ``_port_available``,
``serve``) plus the pure reorder request handler (``handle_reorder_request``)
out of the ``state_builder`` god-module into a focused sibling (R-C1-3).

Behavior is preserved verbatim. The five Article X locked functions remain
physically in ``state_builder.py``. Facade-owned surfaces this server needs at
REQUEST time only -- ``build`` and ``_DRAG_SCRIPT_CSP`` (the latter feeds the
locked ``render_html``) -- are resolved lazily via ``_facade()`` so that:
  - there is no circular import at module-load time (the facade re-exports this
    module at the bottom of its own load), and
  - whichever facade instance is already loaded is reused, regardless of the
    import name it was loaded under (``cli.state_builder`` under pytest,
    ``state_builder`` when run as a script).
"""

from __future__ import annotations

import html
import importlib
import json
import re
import socket
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

# In-tree sibling bootstrap (ADR-012): the safeguarded overlay mutator. We reuse
# backlog_reorder.move verbatim -- it enforces the dependency-lock, appends the
# audit row, and never auto-applies force (SDD-041 / ADR-019).
from backlog_reorder import (  # noqa: E402  -- in-tree sibling bootstrap (ADR-012)
    move as _reorder_move,
    ReorderError as _ReorderError,
)

DEFAULT_SDD_ROOT = Path(__file__).resolve().parents[1]   # spec-driven-development/

_REORDER_ITEM_RE = re.compile(r"^[A-Z]{2,}-\d{2,3}$")


def _facade():
    """Return the already-loaded ``state_builder`` facade module.

    The dashboard server depends on a handful of facade-owned surfaces at
    REQUEST time only (``build``, ``_DRAG_SCRIPT_CSP``). Resolving them lazily
    here -- rather than importing at module top -- avoids a circular import (the
    facade re-exports this module) and reuses whichever facade instance is
    already in ``sys.modules``. ``importlib.import_module`` is the stdlib
    fallback for the unusual case where neither name is loaded yet.
    """
    return (sys.modules.get("cli.state_builder")
            or sys.modules.get("state_builder")
            or importlib.import_module("state_builder"))


def handle_reorder_request(sdd_root: Path, payload: object) -> tuple[int, dict]:
    """Validate a drag-drop reorder payload and apply it via the safeguarded mutator.

    Pure function (no HTTP): returns ``(status_code, body_dict)`` so it can be
    unit-tested without a live server. Contract:
      - 400 when the payload is malformed (not a dict, bad ``item`` id, or a
        ``to_rank`` that is not a non-negative int -- bool is rejected).
      - 200 ``{"status":"ok","audit":<row>}`` on a successful move.
      - 409 ``{"status":"blocked","reason":<msg>}`` when a dependency lock
        rejects the move. Force is NEVER auto-applied (ADR-017): the drag layer
        does not pass force, and a block is surfaced, not retried.
      - 400 ``{"status":"error","reason":<msg>}`` for an out-of-range rank.
    """
    if not isinstance(payload, dict):
        return 400, {"status": "error", "reason": "body must be a JSON object"}

    item = payload.get("item")
    if not isinstance(item, str) or not _REORDER_ITEM_RE.match(item):
        return 400, {"status": "error", "reason": "invalid 'item' feature id"}

    to_rank = payload.get("to_rank")
    if isinstance(to_rank, bool) or not isinstance(to_rank, int) or to_rank < 0:
        return 400, {"status": "error", "reason": "'to_rank' must be a non-negative integer"}

    # The drag gesture never forces past a dependency lock (ADR-017). We accept
    # an explicit force only from a deliberate non-drag client; the injected JS
    # omits it entirely.
    force = bool(payload.get("force", False))

    try:
        row = _reorder_move(sdd_root, item=item, to_rank=to_rank, force=force)
    except _ReorderError as exc:
        return 409, {"status": "blocked", "reason": str(exc)}
    except ValueError as exc:
        return 400, {"status": "error", "reason": str(exc)}
    return 200, {"status": "ok", "audit": row}


def served_html_with_refresh(html_doc: str, refresh_seconds: int) -> str:
    if refresh_seconds < 1:
        raise ValueError("refresh_seconds must be positive")
    meta = f'<meta http-equiv="refresh" content="{refresh_seconds}">'
    if re.search(r'<meta http-equiv="refresh" content="\d+">', html_doc):
        return re.sub(r'<meta http-equiv="refresh" content="\d+">', meta, html_doc, count=1)
    return html_doc.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + meta,
        1,
    )


class DashboardHandler(BaseHTTPRequestHandler):
    server_port: int = 8765
    sdd_root: Path = DEFAULT_SDD_ROOT
    refresh_seconds: int = 5

    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write(f"[bridge] {self.address_string()} {format % args}\n")

    def _send(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Security headers (REC-2 from SECURITY-REVIEW.md). script-src is
        # pinned to the SDD-041 drag script hash only -- never 'unsafe-inline'
        # (ADR-019). The served HTML carries the same hash in its meta CSP.
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; "
                         "style-src 'unsafe-inline'; "
                         f"script-src {_facade()._DRAG_SCRIPT_CSP}; "
                         "img-src 'self' data:; "
                         "font-src 'self'; "
                         "connect-src 'self'; "
                         "frame-ancestors 'none'; "
                         "base-uri 'none'; "
                         "form-action 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                info = _facade().build(sdd_root=self.sdd_root, write=False, live_html=True, port=self.server_port)
                html_doc = served_html_with_refresh(info["html"], self.refresh_seconds)
                self._send(200, html_doc.encode("utf-8"))
            except Exception as exc:
                msg = f"<h1>Build failed</h1><pre>{html.escape(repr(exc))}</pre>"
                self._send(500, msg.encode("utf-8"))
            return
        if path == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8"); return
        if path == "/favicon.ico":
            self._send(204, b"", "image/x-icon"); return
        self._send(404, b"<h1>404</h1>not found")

    def do_POST(self) -> None:  # noqa: N802
        # SDD-041 (F-31): the ONLY write endpoint. Localhost-bound (serve()
        # binds 127.0.0.1), input-validated, and delegates to the safeguarded
        # backlog_reorder.move via handle_reorder_request. do_GET is unchanged.
        path = self.path.split("?", 1)[0]
        if path != "/reorder":
            self._send_json(404, {"status": "error", "reason": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except (TypeError, ValueError):
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"status": "error", "reason": "malformed JSON body"})
            return
        try:
            status, body = handle_reorder_request(self.sdd_root, payload)
        except Exception as exc:  # fail closed; never 500 the dashboard write path silently
            self._send_json(500, {"status": "error", "reason": repr(exc)})
            return
        self._send_json(status, body)


def _port_available(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port)); return True
    except OSError:
        return False
    finally:
        s.close()


def serve(sdd_root: Path, host: str = "127.0.0.1", port: int = 8765,
          open_browser: bool = True, refresh_seconds: int = 5) -> int:
    if refresh_seconds < 1:
        print("ERROR: --refresh-seconds must be a positive integer", file=sys.stderr)
        return 1
    if not _port_available(host, port):
        for offset in range(1, 6):
            if _port_available(host, port + offset):
                port = port + offset; break
        else:
            print(f"ERROR: no available port near {port} on {host}", file=sys.stderr); return 1
    DashboardHandler.server_port = port
    DashboardHandler.sdd_root = sdd_root
    DashboardHandler.refresh_seconds = refresh_seconds
    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    url = f"http://{host}:{port}/"
    print(f"Bridge dashboard live at {url}")
    print(f"Each request rebuilds state from artifacts. Page auto-refreshes every {refresh_seconds}s.")
    print("Press Ctrl+C to stop.")
    if open_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try: httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping...")
    finally:
        httpd.server_close()
    return 0

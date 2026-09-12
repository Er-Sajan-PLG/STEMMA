#!/usr/bin/env python3
"""STEMMA CI Bridge — localhost HTTP wrapper for scripts/verify_all.py.

Runs verify_all.py when triggered, returning output.
"""

import contextlib
import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
VERIFY = str(REPO / "scripts" / "verify_all.py")

HOST = os.environ.get("CI_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("CI_BRIDGE_PORT", "8771")) # Using 8771 to not conflict with JARVIS 8770
MAX_TIMEOUT = int(os.environ.get("CI_BRIDGE_TIMEOUT", "900"))

LAST = {}

def run_bridge() -> dict:
    global LAST
    cmd = [PYTHON, VERIFY]
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=MAX_TIMEOUT,
            shell=False,
        )
        result = {
            "ok": proc.returncode == 0,
            "exitCode": proc.returncode,
            "durationSec": round(time.time() - started, 1),
            "cmd": " ".join(cmd),
            "stdout": proc.stdout[-20000:],
            "stderr": proc.stderr[-8000:],
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "ok": False,
            "exitCode": 124,
            "durationSec": round(time.time() - started, 1),
            "cmd": " ".join(cmd),
            "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
            "stderr": f"timed out after {MAX_TIMEOUT}s",
        }
    LAST = result
    return result

class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        data = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/health":
            self._send(200, {"status": "ok", "service": "stemma-ci-bridge"})
        elif path == "/last":
            self._send(200, LAST or {"info": "no runs yet"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path.split("?")[0] == "/run":
            self._send(200, run_bridge())
        else:
            self._send(404, {"error": "not found"})

def main() -> int:
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"stemma-ci-bridge listening on http://{HOST}:{PORT}")
    with contextlib.suppress(KeyboardInterrupt):
        srv.serve_forever()
    return 0

if __name__ == "__main__":
    sys.exit(main())

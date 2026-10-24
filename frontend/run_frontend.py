import http.server
import socketserver
import webbrowser
from pathlib import Path


# ============================================================
# TAMIL NADU TOLLNET
# FRONTEND SERVER
# ============================================================

FRONTEND_DIR = Path(__file__).resolve().parent

PORT = 5501


# ============================================================
# CHANGE DIRECTORY TO FRONTEND
# ============================================================

import os

os.chdir(FRONTEND_DIR)


# ============================================================
# SERVER
# ============================================================

handler = http.server.SimpleHTTPRequestHandler


class ReusableTCPServer(
    socketserver.TCPServer
):

    allow_reuse_address = True


print("=" * 60)
print("TAMIL NADU TOLLNET - FRONTEND SERVER")
print("=" * 60)

print()

print(
    "Frontend folder:"
)

print(
    FRONTEND_DIR
)

print()

print(
    "Opening:"
)

print(
    f"http://127.0.0.1:{PORT}/index.html"
)

print()

print("=" * 60)
print()


with ReusableTCPServer(
    ("127.0.0.1", PORT),
    handler
) as server:

    # Open Chrome automatically
    webbrowser.open(
        f"http://127.0.0.1:{PORT}/index.html"
    )

    print(
        f"Frontend running at "
        f"http://127.0.0.1:{PORT}/index.html"
    )

    print(
        "Press CTRL+C in this window to stop."
    )

    print()

    server.serve_forever()
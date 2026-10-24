import subprocess
import sys
import time
from pathlib import Path


# ============================================================
# TAMIL NADU TOLLNET - START COMPLETE PROJECT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


BACKEND_FILE = (
    BASE_DIR
    / "backend"
    / "scripts"
    / "14_prediction.py"
)


FRONTEND_FILE = (
    BASE_DIR
    / "frontend"
    / "run_frontend.py"
)


print("=" * 70)
print("TAMIL NADU TOLLNET - STARTING COMPLETE PROJECT")
print("=" * 70)
print()


# ============================================================
# CHECK FILES
# ============================================================

if not BACKEND_FILE.exists():

    raise FileNotFoundError(
        f"Backend file not found:\n{BACKEND_FILE}"
    )


if not FRONTEND_FILE.exists():

    raise FileNotFoundError(
        f"Frontend server file not found:\n{FRONTEND_FILE}"
    )


# ============================================================
# START BACKEND
# ============================================================

print("Starting FastAPI backend...")

backend_process = subprocess.Popen(
    [
        sys.executable,
        str(BACKEND_FILE)
    ],
    cwd=(
        BASE_DIR
        / "backend"
    )
)


# ============================================================
# GIVE BACKEND TIME TO START
# ============================================================

time.sleep(3)


# ============================================================
# START FRONTEND
# ============================================================

print("Starting frontend server...")

frontend_process = subprocess.Popen(
    [
        sys.executable,
        str(FRONTEND_FILE)
    ],
    cwd=(
        BASE_DIR
        / "frontend"
    )
)


print()
print("=" * 70)
print("TAMIL NADU TOLLNET IS RUNNING")
print("=" * 70)
print()
print(
    "Frontend:"
)
print(
    "http://127.0.0.1:5501/index.html"
)
print()
print(
    "Backend:"
)
print(
    "http://127.0.0.1:8000"
)
print()
print(
    "Swagger:"
)
print(
    "http://127.0.0.1:8000/docs"
)
print()
print("=" * 70)
print()
print(
    "Keep this terminal running."
)
print(
    "Press CTRL+C here to stop the complete project."
)
print()


# ============================================================
# KEEP BOTH SERVERS RUNNING
# ============================================================

try:

    while True:

        # Check backend
        if (
            backend_process.poll()
            is not None
        ):

            print()
            print(
                "WARNING: Backend stopped."
            )

            break


        # Check frontend
        if (
            frontend_process.poll()
            is not None
        ):

            print()
            print(
                "WARNING: Frontend stopped."
            )

            break


        time.sleep(1)


except KeyboardInterrupt:

    print()
    print(
        "Stopping Tamil Nadu TollNet..."
    )


finally:

    # --------------------------------------------------------
    # Stop backend
    # --------------------------------------------------------

    if (
        backend_process.poll()
        is None
    ):

        backend_process.terminate()


    # --------------------------------------------------------
    # Stop frontend
    # --------------------------------------------------------

    if (
        frontend_process.poll()
        is None
    ):

        frontend_process.terminate()


    print(
        "Project stopped."
    )
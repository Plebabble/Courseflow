import json
import queue
import re
import site
import socket
import subprocess
import sys
import threading
import time
import traceback
import venv
from datetime import datetime
from pathlib import Path
from tkinter import StringVar, Tk, messagebox, ttk


FOLDER = Path(__file__).resolve().parent
APP_FILE = FOLDER / "app.py"
REQUIREMENTS_FILE = FOLDER / "requirements.txt"
VENV_FOLDER = FOLDER / ".venv"
VENV_PYTHON = VENV_FOLDER / "Scripts" / "python.exe"
STARTUP_LOG = FOLDER / "planner_startup.log"
LAUNCHER_LOG = FOLDER / "planner_launcher.log"


def log_launcher(message):
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with LAUNCHER_LOG.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {message}\n")


class SetupCancelled(Exception):
    pass


def run_setup_command(command, description):
    result = subprocess.run(
        command,
        cwd=FOLDER,
        capture_output=True,
        text=True,
        timeout=900,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        STARTUP_LOG.write_text(
            f"{description} failed.\n\n{details}\n", encoding="utf-8"
        )
        raise RuntimeError(f"{description} failed. See planner_startup.log for details.")


def choose_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def saved_button_color():
    """Use the current palette button color as Streamlit's primary color."""
    try:
        saved_data = json.loads((FOLDER / "assignments.json").read_text(encoding="utf-8"))
        color = saved_data.get("app_theme", {}).get("button")
        if isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            return color
    except (OSError, json.JSONDecodeError, AttributeError):
        pass
    return "#A98767"


def start_planner(cancelled):
    log_launcher("Preparing planner startup.")
    if cancelled.is_set():
        raise SetupCancelled()
    if not APP_FILE.exists() or not REQUIREMENTS_FILE.exists():
        raise RuntimeError("The planner files are missing. Keep this launcher beside app.py.")

    if not VENV_PYTHON.exists():
        log_launcher("Creating the private Python environment.")
        run_setup_command(
            [sys.executable, "-m", "venv", str(VENV_FOLDER)],
            "Creating the planner's private Python environment",
        )
    if cancelled.is_set():
        raise SetupCancelled()

    log_launcher("Checking required packages.")
    run_setup_command(
        [str(VENV_PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQUIREMENTS_FILE)],
        "Installing the planner's required packages",
    )
    if cancelled.is_set():
        raise SetupCancelled()

    port = choose_port()
    command = [
        str(VENV_PYTHON), "-m", "streamlit", "run", str(APP_FILE),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        f"--theme.primaryColor={saved_button_color()}",
        "--browser.gatherUsageStats=false",
    ]
    log_file = STARTUP_LOG.open("w", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=FOLDER,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    finally:
        log_file.close()
    log_launcher(f"Started Streamlit process on port {port}.")

    ready_marker = "Uvicorn server started"
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if cancelled.is_set():
            stop_planner(process)
            raise SetupCancelled()
        if process.poll() is not None:
            raise RuntimeError("The planner stopped while starting. See planner_startup.log for details.")
        try:
            startup_output = STARTUP_LOG.read_text(encoding="utf-8", errors="replace")
        except OSError:
            startup_output = ""
        if ready_marker in startup_output:
            time.sleep(1)
            log_launcher("Streamlit reported ready.")
            return process, port
        time.sleep(0.3)

    process.terminate()
    raise RuntimeError("The planner took too long to start. See planner_startup.log for details.")


def stop_planner(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def show_setup_window():
    result_queue = queue.Queue()
    outcome = {}
    cancelled = threading.Event()
    window = Tk()
    window.title("Assignment Planner")
    window.geometry("390x145")
    window.resizable(False, False)
    window.eval("tk::PlaceWindow . center")

    frame = ttk.Frame(window, padding=22)
    frame.pack(fill="both", expand=True)
    status = StringVar(value="Starting your planner…")
    ttk.Label(frame, textvariable=status, wraplength=340).pack(anchor="w", pady=(0, 14))
    progress = ttk.Progressbar(frame, mode="indeterminate", length=340)
    progress.pack(fill="x")
    progress.start(10)

    def prepare():
        try:
            started = start_planner(cancelled)
            if cancelled.is_set():
                stop_planner(started[0])
                result_queue.put(("cancelled", None))
            else:
                result_queue.put(("ready", started))
        except SetupCancelled:
            result_queue.put(("cancelled", None))
        except Exception as error:
            log_launcher(f"Setup failed: {error}\n{traceback.format_exc()}")
            result_queue.put(
                ("cancelled", None) if cancelled.is_set() else ("error", str(error))
            )

    def check_result():
        try:
            kind, value = result_queue.get_nowait()
        except queue.Empty:
            window.after(150, check_result)
            return
        progress.stop()
        window.destroy()
        if kind == "ready":
            outcome["started"] = value
        elif kind == "error":
            outcome["error"] = value

    def close_setup():
        cancelled.set()
        status.set("Closing after the current setup step…")

    window.protocol("WM_DELETE_WINDOW", close_setup)
    threading.Thread(target=prepare, daemon=True).start()
    window.after(150, check_result)
    window.mainloop()
    if "error" in outcome:
        messagebox.showerror("Assignment Planner", outcome["error"])
    return outcome.get("started")


def main():
    log_launcher("Desktop launcher opened.")
    started = show_setup_window()
    if not started:
        log_launcher("Planner startup was cancelled or did not complete.")
        return

    process, port = started
    try:
        log_launcher("Loading the desktop window package.")
        site.addsitedir(str(VENV_FOLDER / "Lib" / "site-packages"))
        import webview

        log_launcher("Creating the planner window.")
        webview.create_window(
            "Assignment Planner",
            f"http://127.0.0.1:{port}",
            width=1280,
            height=850,
            min_size=(960, 640),
        )
        log_launcher("Opening the planner window.")
        webview.start()
        log_launcher("Planner window closed.")
    except Exception as error:
        log_launcher(f"Desktop window failed: {error}\n{traceback.format_exc()}")
        messagebox.showerror("Assignment Planner", f"Could not open the desktop window.\n\n{error}")
    finally:
        stop_planner(process)


if __name__ == "__main__":
    main()

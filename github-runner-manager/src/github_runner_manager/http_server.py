#  Copyright 2025 Canonical Ltd.
#  See LICENSE file for licensing details.

"""The HTTP server for github-runner-manager.

The HTTP server for request to the github-runner-manager.
"""

from threading import Lock

from flask import Flask

from github_runner_manager.cli_config import Configuration

app = Flask(__name__)


# The path under /lock are for tests.
@app.route("/lock/status")
def lock_status() -> tuple[str, int]:
    """Get the status of the lock.

    This is for tests.

    Returns:
        Whether the lock is locked.
    """
    return ("locked", 200) if _get_lock().locked() else ("unlocked", 200)


@app.route("/lock/acquire")
def lock_acquire() -> tuple[str, int]:
    """Acquire the thread lock.

    This is for tests.

    Returns:
        A 200 OK response
    """
    _get_lock().acquire(blocking=True)
    return ("", 200)


@app.route("/lock/release")
def lock_release() -> tuple[str, int]:
    """Release the thread lock.

    This is for tests.

    Returns:
        A 200 OK response
    """
    _get_lock().release()
    return ("", 200)


def _get_lock() -> Lock:
    """Get the thread lock.

    Returns:
        The thread lock.
    """
    return app.config["lock"]


def start_http_server(_: Configuration, lock: Lock, host: str, port: int) -> None:
    """Start the HTTP server for interacting with the github-runner-manager service.

    Args:
        lock: The lock representing modification access to the managed set of runners.
        host: The hostname to listen on for the HTTP server.
        port: The port to listen on for the HTTP server.
    """
    app.config["lock"] = lock
    app.run(host=host, port=port, use_reloader=False)

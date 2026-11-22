#!/usr/bin/env python3
"""
Start one or more local servers, wait until their TCP ports accept connections,
run a test/automation command, and cleanly terminate all started servers.

Usage:
  python with_server.py --server "npm run dev" --port 5173 -- python test_app.py
  python with_server.py --server "python api.py" --port 3000 --server "npm run dev" --port 5173 -- python test_app.py
"""
import argparse
import os
import signal
import socket
import subprocess
import sys
import time


def wait_for_port(host: str, port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                if sock.connect_ex((host, port)) == 0:
                    return True
            except OSError:
                pass
        time.sleep(0.25)
    return False


def terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.terminate()
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except Exception:
        try:
            if os.name == "nt":
                proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a command while managing one or more local servers."
    )
    parser.add_argument(
        "--server",
        action="append",
        required=True,
        help="Shell command to start a server (may be repeated).",
    )
    parser.add_argument(
        "--port",
        action="append",
        type=int,
        required=True,
        help="TCP port to wait for (must match number of --server args).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to probe for port readiness (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for each server port (default: 30).",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute after '--'.",
    )

    args = parser.parse_args()
    if len(args.server) != len(args.port):
        parser.error("Each --server must have a matching --port.")

    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        parser.error("Provide a command to run after '--'.")

    procs: list[subprocess.Popen] = []
    try:
        for srv_cmd, port in zip(args.server, args.port):
            popen_kwargs: dict = {"shell": True}
            if os.name != "nt":
                popen_kwargs["preexec_fn"] = os.setsid
            proc = subprocess.Popen(srv_cmd, **popen_kwargs)
            procs.append(proc)
            if not wait_for_port(args.host, port, args.timeout):
                print(
                    f"[with_server] Timeout waiting for {args.host}:{port} ({srv_cmd})",
                    file=sys.stderr,
                )
                return 1
        result = subprocess.run(cmd)
        return result.returncode
    finally:
        for proc in reversed(procs):
            terminate_process(proc)


if __name__ == "__main__":
    sys.exit(main())

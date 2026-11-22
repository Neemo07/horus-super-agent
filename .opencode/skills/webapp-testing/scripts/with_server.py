#!/usr/bin/env python3
"""Run a command while one or more dev servers are up.

Usage:
  python with_server.py --server "npm run dev" --port 5173 -- python test.py
  python with_server.py --server "cd be && python app.py" --port 3000 \
                        --server "cd fe && npm run dev" --port 5173 -- python test.py

Each --server is paired, in order, with a --port. Servers start in order, the
command runs only after every port accepts connections, and every server process
tree is terminated afterwards. Exit code is the command's exit code.
"""
import argparse
import os
import signal
import socket
import subprocess
import sys
import time


def port_open(port, host="127.0.0.1"):
    for h in (host, "localhost", "::1"):
        try:
            with socket.create_connection((h, port), timeout=0.5):
                return True
        except OSError:
            continue
    return False


def wait_for(port, timeout, proc):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False, f"server exited early with code {proc.returncode}"
        if port_open(port):
            return True, ""
        time.sleep(0.25)
    return False, f"port {port} not ready after {timeout}s"


def spawn(cmd):
    if os.name == "nt":
        return subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen(cmd, shell=True, start_new_session=True)


def stop(proc):
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           capture_output=True, check=False)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", action="append", dest="servers", required=True, help="server command (repeatable)")
    ap.add_argument("--port", action="append", dest="ports", type=int, required=True, help="port for the matching --server (repeatable)")
    ap.add_argument("--timeout", type=int, default=30, help="seconds to wait per server (default 30)")
    ap.add_argument("command", nargs=argparse.REMAINDER, help="command to run after '--'")
    a = ap.parse_args()
    cmd = a.command[1:] if a.command and a.command[0] == "--" else a.command
    if not cmd:
        ap.error("no command given after '--'")
    if len(a.servers) != len(a.ports):
        ap.error("each --server needs a matching --port")

    procs = []
    try:
        for s, port in zip(a.servers, a.ports):
            print(f"[with_server] starting: {s} (port {port})", flush=True)
            p = spawn(s)
            procs.append(p)
            ok, why = wait_for(port, a.timeout, p)
            if not ok:
                print(f"[with_server] FAILED: {why}", file=sys.stderr)
                return 3
            print(f"[with_server] ready on port {port}", flush=True)
        return subprocess.call(cmd)
    finally:
        for p in reversed(procs):
            stop(p)


if __name__ == "__main__":
    sys.exit(main())

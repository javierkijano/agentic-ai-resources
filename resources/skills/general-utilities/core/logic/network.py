import socket
import os
import signal
import subprocess

def is_port_in_use(port: int) -> bool:
    """Checks if a port is currently occupied on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port(start_port: int, max_attempts: int = 100) -> int:
    """Finds the next available port starting from start_port."""
    port = start_port
    while port < start_port + max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
    raise IOError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")

def kill_process_on_port(port: int) -> bool:
    """Attempts to kill the process occupying the specified port."""
    try:
        # Usamos lsof para encontrar el PID
        result = subprocess.check_output(["lsof", "-t", f"-i:{port}"])
        pids = result.decode().strip().split("\n")
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
        return True
    except (subprocess.CalledProcessError, ValueError, ProcessLookupError):
        return False

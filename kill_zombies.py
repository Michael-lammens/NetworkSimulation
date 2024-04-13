import psutil

def kill_process_by_port(port, process_name):
    """Kills the process with the given name running on the specified port."""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            if proc.name() == process_name:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        print(f"Killing {process_name} process with PID {proc.pid} on port {port}")
                        proc.kill()  # terminate the process
                        return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

# Ports and process names to check
process_ports = {32400: 'server', 32582: 'emulate'}

# Iterate over the dictionary to kill each required process
for port, name in process_ports.items():
    if not kill_process_by_port(port, name):
        print(f"No {name} process found on port {port}")

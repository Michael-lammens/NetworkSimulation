import sys
import psutil

def kill_processes_on_port(port):
    processes_killed = False
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            if proc.name() == 'emulate':
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"Killing process {proc.pid} running on port {port}")
                        proc.kill()
                        processes_killed = True
                        break
        except psutil.AccessDenied:
            # Handle processes we don't have permission to access
            pass

    if not processes_killed:
        print(f"No processes named 'emulate' found running on port {port}")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kill_processes_on_port.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Port must be an integer")
        sys.exit(1)

    kill_processes_on_port(port)
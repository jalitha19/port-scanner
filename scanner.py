import socket

def scan_port(host, port, timeout=1):
    """
    Try to connect to host:port.
    Returns True if open, False if closed/filtered.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0   # 0 means connection succeeded
    except socket.error:
        return False

def main():
    host = "127.0.0.1"       # localhost — scanning my machine, always safe
    ports = range(1, 1025)   # first 1024 ports (well-known ports)

    print(f"\nScanning {host} ...\n")
    open_ports = []

    for port in ports:
        if scan_port(host, port):
            open_ports.append(port)
            print(f"  Port {port} -- OPEN")

    print(f"\nDone. {len(open_ports)} open port(s) found.")

if __name__ == "__main__":
    main()
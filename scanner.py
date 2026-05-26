import socket
import threading

# This list stores open ports found during the scan
open_ports = []

# A lock prevents two threads from writing to open_ports at the same time
# (without this you can get corrupted/missing results)
lock = threading.Lock()

def scan_port(host, port, timeout=0.5):
    """
    Try to connect to host:port using TCP.
    If the connection succeeds, the port is open.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            with lock:
                open_ports.append(port)

    except socket.error:
        pass

def main():
    host = "127.0.0.1"
    ports = range(1, 1025)
    threads = []

    print(f"\nScanning {host} ...\n")

    # Spin up one thread per port
    for port in ports:
        t = threading.Thread(target=scan_port, args=(host, port))
        threads.append(t)
        t.start()

    # Wait for every thread to finish before printing results
    for t in threads:
        t.join()

    # Sort so output is in order (threads finish in random order)
    open_ports.sort()

    for port in open_ports:
        print(f"  Port {port} -- OPEN")

    print(f"\nDone. {len(open_ports)} open port(s) found.")

if __name__ == "__main__":
    main()
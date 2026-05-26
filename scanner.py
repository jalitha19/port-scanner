import socket
import threading

open_ports = []
lock = threading.Lock()

# Common port to service name mapping
# This is a manual fallback for when banner grabbing doesn't work
COMMON_SERVICES = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    135:  "MS RPC",
    139:  "NetBIOS",
    143:  "IMAP",
    443:  "HTTPS",
    445:  "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-alt",
    8443: "HTTPS-alt",
}

def grab_banner(host, port, timeout=1):
    """
    After connecting, wait briefly to see if the service
    sends us an intro message (the banner).
    Some services need a nudge (we send a newline first).
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # Some services (like HTTP) need you to say something first
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")

        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()
        return banner if banner else None

    except Exception:
        return None

def scan_port(host, port, timeout=0.5):
    """
    Check if port is open. If yes, attempt banner grab
    and look up service name.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            banner  = grab_banner(host, port)
            service = COMMON_SERVICES.get(port, "Unknown")

            with lock:
                open_ports.append({
                    "port":    port,
                    "service": service,
                    "banner":  banner,
                })

    except socket.error:
        pass

def main():
    host = "127.0.0.1"
    ports = range(1, 1025)
    threads = []

    print(f"\nScanning {host} ...\n")

    for port in ports:
        t = threading.Thread(target=scan_port, args=(host, port))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Sort by port number
    open_ports.sort(key=lambda x: x["port"])

    print(f"{'PORT':<8} {'SERVICE':<16} {'BANNER'}")
    print("-" * 60)

    for entry in open_ports:
        banner_preview = entry["banner"][:40] if entry["banner"] else "—"
        print(f"  {entry['port']:<6} {entry['service']:<16} {banner_preview}")

    print(f"\nDone. {len(open_ports)} open port(s) found.")

if __name__ == "__main__":
    main()
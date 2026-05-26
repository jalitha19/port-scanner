import socket
import threading
import argparse
import datetime
from concurrent.futures import ThreadPoolExecutor

open_ports = []
lock = threading.Lock()

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
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()
        return banner if banner else None
    except Exception:
        return None

def scan_port(host, port, timeout=0.5):
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

def build_report(host, start_port, end_port, duration):
    """
    Builds the scan report as a string.
    Used for both printing to screen and saving to file.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("  PORT SCANNER REPORT")
    lines.append("=" * 60)
    lines.append(f"  Target  : {host}")
    lines.append(f"  Range   : {start_port} - {end_port}")
    lines.append(f"  Time    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Duration: {duration:.2f} seconds")
    lines.append(f"  Open    : {len(open_ports)} port(s)")
    lines.append("")
    lines.append(f"  {'PORT':<8} {'SERVICE':<16} {'BANNER'}")
    lines.append("  " + "-" * 56)

    for entry in open_ports:
        banner_preview = entry["banner"][:38] if entry["banner"] else "—"
        lines.append(f"  {entry['port']:<8} {entry['service']:<16} {banner_preview}")

    lines.append("=" * 60)
    return "\n".join(lines)

def main():
    # argparse sets up the command-line interface
    parser = argparse.ArgumentParser(
        description="Python TCP Port Scanner with Banner Grabbing"
    )
    parser.add_argument("host",                          help="Target IP or hostname (e.g. 127.0.0.1)")
    parser.add_argument("--start",   type=int, default=1,    help="Start port (default: 1)")
    parser.add_argument("--end",     type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("--threads", type=int, default=100,  help="Max threads (default: 100)")
    parser.add_argument("--output",  type=str, default=None, help="Save report to this file (optional)")
    args = parser.parse_args()

    print(f"\nScanning {args.host} (ports {args.start}-{args.end}) ...\n")

    start_time = datetime.datetime.now()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for port in range(args.start, args.end + 1):
            executor.submit(scan_port, args.host, port)

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    open_ports.sort(key=lambda x: x["port"])

    report = build_report(args.host, args.start, args.end, duration)
    print(report)

    # Save to file if --output was provided
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n  Report saved to: {args.output}")

if __name__ == "__main__":
    main()
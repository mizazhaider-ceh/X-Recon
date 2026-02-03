import socket
import threading
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Lock for writing to file in multithreaded mode
lock = threading.Lock()

# Default common ports
common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080, 8443]

def grab_banner(ip, port, timeout):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        banner = s.recv(1024).decode(errors='ignore').strip()
        s.close()
        return banner if banner else "No banner received"
    except socket.timeout:
        return "Timeout"
    except Exception:
        return None

def scan_port(ip, port, timeout, output_file):
    banner = grab_banner(ip, port, timeout)
    if banner:
        colored_output = f"{Fore.GREEN}[+] {ip}:{port} - {banner}"
        print(colored_output)

        with lock:
            with open(output_file, "a") as f:
                f.write(f"{ip}:{port} - {banner}\n")
    else:
        print(f"{Fore.RED}[-] {ip}:{port} - No response")

def start_scan(ip, ports, timeout, output_file):
    print(f"{Fore.CYAN}[*] Starting banner grabbing on {ip} at {datetime.now()}\n")
    
    threads = []
    for port in ports:
        t = threading.Thread(target=scan_port, args=(ip, port, timeout, output_file))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"\n{Fore.YELLOW}[✔] Scan completed. Results saved to '{output_file}'")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}{Style.BRIGHT}\n--- Banner Grabbing Tool ---\n")

    target_ip = input(f"{Fore.BLUE}Enter target IP or domain: ").strip()

    custom_ports = input(f"{Fore.BLUE}Do you want to scan a custom port range? (y/N): ").lower()
    if custom_ports == 'y':
        try:
            start_port = int(input("Start port: "))
            end_port = int(input("End port: "))
            ports = list(range(start_port, end_port + 1))
        except:
            print(f"{Fore.RED}Invalid port range. Using default ports.")
            ports = common_ports
    else:
        ports = common_ports

    try:
        timeout = float(input("Enter timeout in seconds (default 3): ") or 3)
    except:
        timeout = 3

    output_file = input("Enter output file name (default: banner_results.txt): ").strip()
    if output_file == "":
        output_file = "banner_results.txt"

    # Clear previous results
    open(output_file, "w").close()

    start_scan(target_ip, ports, timeout, output_file)

# modules/port_scanner.py
# v1.1: Foundations & Efficiency (AsyncIO Upgrade)

import asyncio
import socket
import os
from colorama import init, Fore, Style
from tqdm.asyncio import tqdm_asyncio
try:
    from modules.utils import RichConsole, ResultSaver, InputValidator
except ImportError:
    # Fallback for direct execution testing
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from modules.utils import RichConsole, ResultSaver, InputValidator

# Initialize utilities
console = RichConsole.get_console()
saver = ResultSaver("portscan")

async def scan_port(host, port, semaphore):
    """
    Async worker to scan a single port.
    """
    async with semaphore:
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=1.5)
            
            # Try to grab a banner
            banner = ""
            try:
                # Send a dummy byte to trigger a response if needed
                # writer.write(b'\n')
                # await writer.drain()
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    banner = data.decode(errors='ignore').strip()
            except (asyncio.TimeoutError, ConnectionResetError):
                pass
            finally:
                writer.close()
                await writer.wait_closed()
                
            return port, True, banner
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return port, False, None

async def run_scan(target_host, ports, concurrency=500):
    """
    Orchestrates the async scan.
    """
    console.print(f"\n[info][*] Starting Async Scan on {target_host} with limit {concurrency}...[/info]")
    
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [scan_port(target_host, port, semaphore) for port in ports]
    
    open_ports = []
    
    # Use tqdm for async progress bar
    for f in tqdm_asyncio.as_completed(tasks, desc=f"{Fore.CYAN}Scanning Ports", unit="port"):
        port, is_open, banner = await f
        if is_open:
            open_ports.append((port, banner))
            
    return sorted(open_ports)

def print_and_save(target_host, target_ip, open_ports):
    if not open_ports:
        console.print(f"\n[warning][-] No open ports found on {target_host}.[/warning]")
        return

    console.print(f"\n\n[success]✅ Async Scan Complete! Found {len(open_ports)} open port(s).[/success]\n")
    
    # Print Table
    console.print(f"[highlight]{'PORT':<10}{'STATUS':<10}{'BANNER'}[/highlight]")
    console.print(f"[white]{'-'*4:<10}{'-'*6:<10}{'-'*20}[/white]")
    
        
    # JSON Data for HTML
    html_content = "<table><thead><tr><th>PORT</th><th>STATUS</th><th>BANNER/SERVICE</th></tr></thead><tbody>"
    
    file_lines = [f"--- Async Port Scan Results for {target_host} ({target_ip}) ---\n\n"]
    
    for port, banner in open_ports:
        svc_str = banner if banner else "Unknown Service"
        console.print(f"[green]{port:<10}[/green][green]OPEN      [/green][yellow]{svc_str}[/yellow]")
        file_lines.append(f"Port: {port} | Status: OPEN | Banner: {svc_str}\n")
        
        # Add to HTML
        html_content += f"<tr><td>{port}</td><td><span style='color:#0aff0a'>OPEN</span></td><td>{svc_str}</td></tr>"
        
    html_content += "</tbody></table>"

    # Save Text (CLI Backup)
    saver.save_text(target_host, file_lines)
    
    # Save HTML (Web Report)
    html_path = saver.save_html(target_host, f"Port Scan: {target_host}", html_content)
    
    if html_path:
        console.print(f"\n[info][+] HTML Report saved to: {html_path}[/info]")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    RichConsole.print_banner("Async Port Scanner v1.1")
    
    import sys
    target_input = ""
    choice = '1' # Default to Top 100
    spd = '2'    # Default to Fast
    
    # Check if arguments are provided (Non-Interactive Mode)
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
        console.print(f"[info]Target received via CLI: {target_input}[/info]")
        console.print("[dim]Running in automated mode (Profile: Top 100, Speed: Fast)[/dim]")
    else:
        # Interactive Mode
        target_input = console.input("[info]Enter target IP or Domain: [/info]").strip()
    
    # Resolve IP
    try:
        target_ip = socket.gethostbyname(target_input)
        console.print(f"[success][i] Resolved to: {target_ip}[/success]")
    except socket.gaierror:
        console.print(f"[error][!] Could not resolve hostname '{target_input}'.[/error]")
        return

    # Port selection (Only ask if interactive)
    ports_to_scan = []
    
    if len(sys.argv) <= 1:
        console.print("\n[header]---[ Scan Profile ]---[/header]")
        console.print("1. Top 100 Common Ports")
        console.print("2. Full Range (1-65535)")
        console.print("3. Custom Range")
        choice = console.input("[info]Select profile: [/info]").strip()

    if choice == '1':
        # Mix of common TCP ports
        ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 1433, 3306, 3389, 5432, 5900, 8080, 8443] + list(range(8081, 8100))
    elif choice == '2':
        ports_to_scan = range(1, 65536)
    elif choice == '3':
        rng = console.input("[info]Enter range (e.g. 1-1000): [/info]").strip()
        valid, (start, end) = InputValidator.validate_port_range(rng)
        if valid:
            ports_to_scan = range(start, end + 1)
        else:
            console.print("[error][!] Invalid range.[/error]")
            return
    else:
        return

    # Speed / Concurrency (Only ask if interactive)
    concurrency = 500
    if len(sys.argv) <= 1:
        console.print("\n[header]---[ Concurrency Level ]---[/header]")
        console.print("1. Safe (100)")
        console.print("2. Fast (500) [Default]")
        console.print("3. Aggressive (2000)")
        spd = console.input("[info]Select speed: [/info]").strip()
        
    if spd == '1': concurrency = 100
    elif spd == '3': concurrency = 2000
    
    # Run Async Loop
    try:
        open_ports = asyncio.run(run_scan(target_ip, list(ports_to_scan), concurrency))
        print_and_save(target_input, target_ip, open_ports)
    except KeyboardInterrupt:
        console.print("\n[warning][!] Scan interrupted by user.[/warning]")

if __name__ == "__main__":
    main()
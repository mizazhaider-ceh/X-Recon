# modules/service_detector.py
# v1.5: AsyncIO High-Performance Version
# Non-blocking, ultra-fast service detection and banner grabbing.

import asyncio
from colorama import init, Fore, Style
from tqdm.asyncio import tqdm
import os
import socket

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to save results in the right place
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

def print_detector_banner():
    """prints the banner for this specific module."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    banner = r"""
   ______                                 __         __            
  / ____/___  ________     ____  _________/ /_  ___  / /_____  ____ 
 / /   / __ \/ ___/ _ \   / __ \/ ___/ __  / / / / _ \/ __/ __ \/ __ \
/ /___/ /_/ / /  /  __/  / /_/ / /  / /_/ / /_/ /  __/ /_/ /_/ / / / /
\____/\____/_/   \___/   \____/_/   \__,_/\__, /\___/\__/\____/_/ /_/ 
                                        /____/                      
            >> Smart Service & Banner Analysis (AsyncIO) <<
"""
    print(banner)
    print(Style.RESET_ALL)

def parse_ports(port_string):
    """our smart function to parse strings like "21,22,80-90" into a list of numbers."""
    ports = set()
    parts = port_string.split(',')
    for part in parts:
        part = part.strip()
        if not part: continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if 1 <= start <= end <= 65535:
                    ports.update(range(start, end + 1))
                else: raise ValueError(f"Invalid port range '{part}'")
            except ValueError: raise ValueError(f"Invalid format for range '{part}'")
        else:
            try:
                port_num = int(part)
                if 1 <= port_num <= 65535:
                    ports.add(port_num)
                else: raise ValueError(f"Invalid port number '{port_num}'")
            except ValueError: raise ValueError(f"Invalid format for port '{part}'")
    return sorted(list(ports))

async def check_and_grab_banner(target_ip, port, semaphore):
    """
    Async worker function.
    Checks if port is open and grabs banner using non-blocking I/O.
    """
    async with semaphore:
        try:
            # Try to connect with a short timeout
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port), 
                timeout=1.5
            )
            
            try:
                # Connected! Port is open. Now try to read banner.
                # We wait a bit for the server to say something (hello message)
                banner = await asyncio.wait_for(reader.read(1024), timeout=2.0)
                banner_text = banner.decode(errors='ignore').strip()
                
                writer.close()
                await writer.wait_closed()
                
                if banner_text:
                    return port, True, banner_text
                else:
                    return port, True, "Service detected, but no banner."
            except (asyncio.TimeoutError, ConnectionResetError):
                # Connection worked, but reading failed/timed out
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
                return port, True, "Service detected (Headless/No Banner)"
                
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return port, False, None

def print_and_save_results(target_host, open_ports_info):
    """prints the beautiful results table and saves to a file."""
    if not open_ports_info:
        print(f"\n{Fore.YELLOW}[-] Analysis Complete. No open ports with banners were found in the specified range.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Analysis Complete! Found {len(open_ports_info)} open service(s) on {target_host}.\n")
    
    print(f"{Style.BRIGHT}{Fore.WHITE}{'PORT':<10}{'STATUS':<10}{'SERVICE / BANNER'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'----':<10}{'------':<10}{'------------------'}{Style.RESET_ALL}")

    file_content = [f"--- Service Detection Results for {target_host} ---\n\n"]
    
    # sort the results by port number before printing for a clean report
    for port, banner in sorted(open_ports_info):
        # Clean up banner for display (remove newlines)
        clean_banner = banner.replace('\n', ' ').replace('\r', '')[:80] 
        print(f"{Fore.GREEN}{port:<10}{'OPEN':<10}{Fore.YELLOW}{clean_banner}{Style.RESET_ALL}")
        file_content.append(f"[PORT] {port}\n     Banner: {banner}\n\n")

    results_file = os.path.join(RESULTS_DIR, f'servicedetect_{target_host}.txt')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.writelines(file_content)
    
    print(f"\n{Fore.CYAN}[+] Results saved to: {results_file}{Style.RESET_ALL}")

async def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_detector_banner()
    
    target_host = input(f"{Fore.CYAN}Enter the target IP or domain: {Style.RESET_ALL}").strip()

    try:
        # Resolve hostname synchronously (fast enough generally)
        target_ip = socket.gethostbyname(target_host)
        print(f"{Fore.GREEN}[i] Target resolved to IP: {target_ip}{Style.RESET_ALL}")
    except socket.gaierror:
        print(f"{Fore.RED}[!] Invalid hostname. Exiting.{Style.RESET_ALL}"); return

    ports_input = input(f"{Fore.CYAN}Enter ports to analyze (e.g., 21,22,80-1024): {Style.RESET_ALL}")
    
    try:
        ports_to_check = parse_ports(ports_input)
        if not ports_to_check: raise ValueError("No valid ports provided.")
    except ValueError as e:
        print(f"{Fore.RED}[!] Error in port selection: {e}. Exiting.{Style.RESET_ALL}"); return
    
    print("\n---[ Scan Speed (Async Concurrency) ]---")
    print("[1] Normal (50 concurrent connections)")
    print("[2] Fast (200 concurrent connections)")
    print("[3] Insane (500 concurrent connections)")
    speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
    
    concurrency = 50 
    if speed_choice == '2': concurrency = 200
    elif speed_choice == '3': concurrency = 500

    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Analyzing {len(ports_to_check)} port(s) with concurrency level {concurrency}...{Style.RESET_ALL}")
    
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [check_and_grab_banner(target_ip, p, semaphore) for p in ports_to_check]
    
    open_ports_with_banners = []
    
    # Run tasks with progress bar
    for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"{Fore.CYAN}Analyzing", unit="port"):
        port, is_open, banner = await future
        if is_open:
            open_ports_with_banners.append((port, banner))

    # --- Show the final report ---
    print_and_save_results(target_host, open_ports_with_banners)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
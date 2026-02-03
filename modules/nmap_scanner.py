# modules/nmap_scanner.py
# this module is a python wrapper to control the powerful nmap tool.

import nmap
from colorama import init, Fore, Style
import os
import socket

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to save results
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

def print_nmap_banner():
    """prints the banner for this specific module."""
    """prints the banner for this specific module."""
    print(f"{Fore.RED}{Style.BRIGHT}")
    banner = r"""
    _   __               __                         
   / | / /___  ____     / /____  _________  ____  
  /  |/ / __ \/ __ \   / __/ _ \/ ___/ __ \/ __ \ 
 / /|  / /_/ / /_/ /  / /_/  __/ /  / /_/ / /_/ / 
/_/ |_/\____/\____/   \__/\___/_/   \____/\____/  
                                                 
            >> Advanced Nmap Integration Engine <<
"""
    print(banner)
    print(Style.RESET_ALL)

def perform_nmap_scan(target, arguments):
    """
    initializes the nmap scanner and runs the specified scan.
    """
    try:
        nm = nmap.PortScanner()
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Starting Nmap scan on {target} with arguments '{arguments}'...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[i] This may take several minutes depending on the scan type. Please be patient.{Style.RESET_ALL}")
        
        # this is where we run the actual nmap command
        # the scan() function blocks until nmap is finished
        nm.scan(hosts=target, arguments=arguments)
        
        return nm
    except nmap.nmap.PortScannerError:
        print(f"\n{Fore.RED}[!] Nmap Error: Nmap is not installed or not in your system's PATH.")
        print(f"{Fore.YELLOW}    Please install it from https://nmap.org/download.html{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"\n{Fore.RED}[!] An unexpected error occurred: {e}")
        return None

def print_and_save_results(target, scanner_results):
    """
    parses the complex nmap results dictionary and prints a beautiful report and saves HTML.
    """
    if not scanner_results.all_hosts():
        print(f"\n{Fore.YELLOW}[-] Scan failed or the host seems to be down.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Nmap Scan Complete for {target}.\n")
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_hosts = ""
    
    # nmap can scan multiple hosts, so we loop through them
    for host in scanner_results.all_hosts():
        hostname = scanner_results[host].hostname()
        state = scanner_results[host].state()
        state_color = "#00ff9d" if state == "up" else "#ff4757"
        
        print(f"{Style.BRIGHT}Host: {Fore.CYAN}{host} ({hostname}){Style.RESET_ALL}")
        print(f"State: {Fore.GREEN if state == 'up' else Fore.RED}{state}{Style.RESET_ALL}")

        os_html = ""
        if 'osmatch' in scanner_results[host] and scanner_results[host]['osmatch']:
            os_guess = scanner_results[host]['osmatch'][0]['name']
            os_accuracy = scanner_results[host]['osmatch'][0]['accuracy']
            print(f"OS Guess: {Fore.YELLOW}{os_guess} ({os_accuracy}% accuracy){Style.RESET_ALL}\n")
            os_html = f'<div class="badge badge-os">🖥️ OS: {os_guess} ({os_accuracy}%)</div>'

        # --- create the beautiful table header ---
        print(f"{Style.BRIGHT}{Fore.WHITE}{'PORT':<10}{'STATE':<10}{'SERVICE':<20}{'PRODUCT/VERSION'}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'----':<10}{'-----':<10}{'-------':<20}{'---------------'}{Style.RESET_ALL}")
        
        port_rows = ""
        # loop through all protocols (tcp, udp, etc.)
        for proto in scanner_results[host].all_protocols():
            ports = scanner_results[host][proto].keys()
            for port in sorted(ports):
                port_state = scanner_results[host][proto][port]['state']
                name = scanner_results[host][proto][port]['name']
                product = scanner_results[host][proto][port]['product']
                version = scanner_results[host][proto][port]['version']
                
                full_service_info = f"{product} {version}".strip()
                
                print(f"{Fore.GREEN}{port:<10}{port_state:<10}{name:<20}{Fore.YELLOW}{full_service_info}{Style.RESET_ALL}")
                
                port_state_color = "#00ff9d" if port_state == "open" else "#ffa502" if port_state == "filtered" else "#ff4757"
                port_rows += f"""
                <tr>
                    <td><code>{port}/{proto}</code></td>
                    <td><span style="color: {port_state_color}; font-weight: bold;">{port_state.upper()}</span></td>
                    <td>{name}</td>
                    <td>{full_service_info or '-'}</td>
                </tr>"""
        
        html_hosts += f"""
        <div class="host-section">
            <div class="host-header">
                <h3>🎯 {host} ({hostname or 'Unknown'})</h3>
                <span class="badge" style="background: rgba({0 if state == 'up' else 255}, {255 if state == 'up' else 71}, {157 if state == 'up' else 87}, 0.2); 
                       border-color: {state_color}; color: {state_color};">
                    {state.upper()}
                </span>
            </div>
            {os_html}
            <table>
                <thead>
                    <tr>
                        <th>Port</th>
                        <th>State</th>
                        <th>Service</th>
                        <th>Product / Version</th>
                    </tr>
                </thead>
                <tbody>
                    {port_rows}
                </tbody>
            </table>
        </div>"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nmap Scan Report - {target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            padding: 2rem;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 71, 87, 0.3);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            border-bottom: 2px solid #ff4757;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .header-icon {{ font-size: 2.5rem; }}
        h1 {{ color: #ff4757; font-size: 1.75rem; margin-bottom: 0.25rem; }}
        .subtitle {{ color: #888; font-size: 0.9rem; }}
        .meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid rgba(255, 71, 87, 0.3);
            border-radius: 8px;
            font-size: 0.85rem;
        }}
        .badge-os {{
            background: rgba(255, 165, 2, 0.1);
            border-color: rgba(255, 165, 2, 0.3);
            color: #ffa502;
            margin: 0.5rem 0 1rem 0;
        }}
        .host-section {{
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .host-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .host-header h3 {{ color: #00f3ff; font-size: 1.1rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            background: rgba(255, 71, 87, 0.1);
            color: #ff4757;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        code {{
            background: rgba(0, 243, 255, 0.1);
            color: #00f3ff;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
        }}
        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="header-icon">🔬</span>
            <div>
                <h1>Nmap Scan Report</h1>
                <div class="subtitle">Advanced Network Reconnaissance</div>
            </div>
        </div>
        
        <div class="meta">
            <div class="badge">🎯 Target: <strong>{target}</strong></div>
            <div class="badge">📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        {html_hosts}
        
        <div class="footer">
            <p>Generated by <strong>X-Recon v3.0</strong> - Nmap Integration Engine | Created by Muhammad Izaz Haider</p>
        </div>
    </div>
</body>
</html>"""

    safe_name = target.replace('/', '_').replace(':', '_')
    results_file = os.path.join(RESULTS_DIR, f'nmapscan_{safe_name}_{timestamp}.html')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.CYAN}[+] HTML Report saved to: {results_file}{Style.RESET_ALL}")

# this is the main part of our script
if __name__ == "__main__":
    import sys
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_nmap_banner()
    
    target_host = ""
    nmap_args = ""
    
    if len(sys.argv) > 1:
        target_host = sys.argv[1]
        print(f"{Fore.CYAN}[info]Target received via CLI: {target_host}[/info]")
        
        # Determine scan type from 2nd arg or default to Fast
        if len(sys.argv) > 2:
             # simple mapping: fast, intense, udp, vuln
            mode = sys.argv[2]
            if mode == 'intense': nmap_args = "-p- -sV -O"
            elif mode == 'vuln': nmap_args = "-sV --script vuln"
            else: nmap_args = "-F" # Default
        else:
             nmap_args = "-F"
             
        print(f"[dim]Running in automated mode (Args: {nmap_args})[/dim]")

    else:
        target_host = input(f"{Fore.CYAN}Enter the target IP or domain: {Style.RESET_ALL}").strip()
        if not target_host:
            print(f"{Fore.RED}[!] No target provided. Exiting.{Style.RESET_ALL}"); exit()

        print("\n---[ Nmap Scan Type ]---")
        print("[1] Simple Scan (Top ports, fast)")
        print("[2] Intense Scan (All ports, service versions, OS detection)")
        print("[3] UDP Scan (Top UDP ports, slow)")
        print("[4] Vuln Scan (Checks for common vulnerabilities)")
        scan_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()

        if scan_choice == '1':
            # -F is for "Fast" mode, scans top 100 ports
            nmap_args = "-F"
        elif scan_choice == '2':
            # -p- scans all 65535 ports, -sV gets versions, -O gets OS
            nmap_args = "-p- -sV -O"
        elif scan_choice == '3':
            # -sU scans UDP, --top-ports 20 scans the 20 most common UDP ports
            nmap_args = "-sU --top-ports 20"
        elif scan_choice == '4':
            # -sV gets versions, --script vuln runs the vulnerability script category
            nmap_args = "-sV --script vuln"
        else:
            print(f"{Fore.RED}[!] Invalid option. Exiting.{Style.RESET_ALL}"); exit()

    scan_results = perform_nmap_scan(target_host, nmap_args)
    
    if scan_results:
        print_and_save_results(target_host, scan_results)
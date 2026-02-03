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
    parses the complex nmap results dictionary and prints a beautiful report.
    """
    if not scanner_results.all_hosts():
        print(f"\n{Fore.YELLOW}[-] Scan failed or the host seems to be down.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Nmap Scan Complete for {target}.\n")
    
    file_content = [f"--- Nmap Scan Results for {target} ---\n\n"]
    
    # nmap can scan multiple hosts, so we loop through them
    for host in scanner_results.all_hosts():
        print(f"{Style.BRIGHT}Host: {Fore.CYAN}{host} ({scanner_results[host].hostname()}){Style.RESET_ALL}")
        print(f"State: {Fore.GREEN if scanner_results[host].state() == 'up' else Fore.RED}{scanner_results[host].state()}{Style.RESET_ALL}")
        file_content.append(f"Host: {host} ({scanner_results[host].hostname()})\nState: {scanner_results[host].state()}\n")

        # check for os detection results
        if 'osmatch' in scanner_results[host] and scanner_results[host]['osmatch']:
            os_guess = scanner_results[host]['osmatch'][0]['name']
            os_accuracy = scanner_results[host]['osmatch'][0]['accuracy']
            print(f"OS Guess: {Fore.YELLOW}{os_guess} ({os_accuracy}% accuracy){Style.RESET_ALL}\n")
            file_content.append(f"OS Guess: {os_guess} ({os_accuracy}% accuracy)\n\n")

        # --- create the beautiful table header ---
        print(f"{Style.BRIGHT}{Fore.WHITE}{'PORT':<10}{'STATE':<10}{'SERVICE':<20}{'PRODUCT/VERSION'}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'----':<10}{'-----':<10}{'-------':<20}{'---------------'}{Style.RESET_ALL}")
        file_content.append(f"{'PORT':<10}{'STATE':<10}{'SERVICE':<20}{'PRODUCT/VERSION'}\n")
        
        # loop through all protocols (tcp, udp, etc.)
        for proto in scanner_results[host].all_protocols():
            ports = scanner_results[host][proto].keys()
            for port in sorted(ports):
                state = scanner_results[host][proto][port]['state']
                name = scanner_results[host][proto][port]['name']
                product = scanner_results[host][proto][port]['product']
                version = scanner_results[host][proto][port]['version']
                
                full_service_info = f"{product} {version}".strip()
                
                print(f"{Fore.GREEN}{port:<10}{state:<10}{name:<20}{Fore.YELLOW}{full_service_info}{Style.RESET_ALL}")
                file_content.append(f"{port:<10}{state:<10}{name:<20}{full_service_info}\n")
    
    safe_name = target.replace('/', '_')
    results_file = os.path.join(RESULTS_DIR, f'nmapscan_{safe_name}.txt')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.writelines(file_content)
    
    print(f"\n{Fore.CYAN}[+] Detailed report saved to: {results_file}{Style.RESET_ALL}")

# this is the main part of our script
if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_nmap_banner()
    
    target_host = input(f"{Fore.CYAN}Enter the target IP or domain: {Style.RESET_ALL}").strip()
    if not target_host:
        print(f"{Fore.RED}[!] No target provided. Exiting.{Style.RESET_ALL}"); exit()

    print("\n---[ Nmap Scan Type ]---")
    print("[1] Simple Scan (Top ports, fast)")
    print("[2] Intense Scan (All ports, service versions, OS detection)")
    print("[3] UDP Scan (Top UDP ports, slow)")
    print("[4] Vuln Scan (Checks for common vulnerabilities)")
    scan_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()

    nmap_args = ""
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
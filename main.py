#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          X-RECON v3.0 - Main CLI                              ║
║                    Created by Muhammad Izaz Haider                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Display the X-Recon banner"""
    banner = f"""{Fore.CYAN}{Style.BRIGHT}

   ██╗  ██╗       ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
   ╚██╗██╔╝       ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
    ╚███╔╝  █████╗██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
    ██╔██╗  ╚════╝██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
   ██╔╝ ██╗       ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║   {Fore.GREEN}v3.0{Fore.CYAN}
   ╚═╝  ╚═╝       ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

            {Fore.YELLOW}>> Advanced Reconnaissance & Security Toolkit <<{Fore.CYAN}

                  {Fore.MAGENTA}⚡ Elite Cybersecurity Toolkit ⚡{Fore.CYAN}

               {Fore.WHITE}Built by {Fore.YELLOW}MIHx0 {Fore.WHITE}({Fore.GREEN}Muhammad Izaz Haider{Fore.WHITE}){Fore.CYAN}
                     {Fore.WHITE}Powered by {Fore.MAGENTA}The PenTrix{Fore.CYAN}

 {Fore.GREEN}🇵🇰 → 🇧🇪  {Fore.WHITE}DevSecOps Engineer | Penetration Tester | AI Security{Fore.CYAN}

{Style.RESET_ALL}"""
    print(banner)

def print_menu():
    """Display the main menu"""
    menu = f"""

{Fore.CYAN}═══════════════════════════════════════════════════════════════════════════════
                         X-RECON COMMAND CENTER
═══════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.YELLOW}─────────────────────────────────────────────────────────────────────────────
  PHASE 1: RECONNAISSANCE & ENUMERATION
─────────────────────────────────────────────────────────────────────────────{Style.RESET_ALL}

  {Fore.GREEN}[1]{Style.RESET_ALL}  Domain Intelligence      │  {Fore.GREEN}[5]{Style.RESET_ALL}  Advanced Port Scanner
      WHOIS & DNS Analysis         │      Nmap Deep Scan

  {Fore.GREEN}[2]{Style.RESET_ALL}  Subdomain Scanner        │  {Fore.GREEN}[6]{Style.RESET_ALL}  Service Detector
      Find Hidden Subdomains       │      Banner Grabbing & Versions

  {Fore.GREEN}[3]{Style.RESET_ALL}  Email Harvester          │  {Fore.GREEN}[7]{Style.RESET_ALL}  Directory Scanner
      OSINT Email Discovery        │      Web Path Fuzzing

  {Fore.GREEN}[4]{Style.RESET_ALL}  Async Port Scanner       │  {Fore.GREEN}[8]{Style.RESET_ALL}  CVE Lookup
      Fast TCP Connect Scan        │      Vulnerability Database

  {Fore.GREEN}[9]{Style.RESET_ALL}  Password Generator
      Custom Wordlist Creation

{Fore.YELLOW}─────────────────────────────────────────────────────────────────────────────
  PHASE 2: AI & WEB INTERFACE
─────────────────────────────────────────────────────────────────────────────{Style.RESET_ALL}

  {Fore.GREEN}[10]{Style.RESET_ALL} AI Cyber-Assistant       │  {Fore.GREEN}[WEB]{Style.RESET_ALL} Web Dashboard
      Powered by Cerebras Llama    │      Modern Visual Interface

  {Fore.MAGENTA}[SERVER]{Style.RESET_ALL} Server Management
      Start/Stop/Restart/Foreground/Background

{Fore.CYAN}═══════════════════════════════════════════════════════════════════════════════
  [EXIT] Exit Toolkit
═══════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
    print(menu)

def run_module(module_name):
    """Run a specific module"""
    module_path = os.path.join('modules', module_name)
    if os.path.exists(module_path):
        os.system(f'python {module_path}')
    else:
        print(f"{Fore.RED}[!] Module not found: {module_name}{Style.RESET_ALL}")

def launch_web_dashboard():
    """Launch the web dashboard"""
    print(f"\n{Fore.CYAN}[*] Starting X-Recon Web Server...{Style.RESET_ALL}")
    # Add server directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
    from server_manager import start_server
    start_server(background=False)

def launch_server_manager():
    """Launch server management menu"""
    print(f"\n{Fore.CYAN}[*] Opening Server Manager...{Style.RESET_ALL}")
    # Add server directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
    from server_manager import ServerManager
    manager = ServerManager()
    manager.show_menu()

def launch_ai_assistant():
    """Launch AI assistant"""
    from modules.ai_assistant import run_ai_assistant
    run_ai_assistant()

def main():
    """Main application loop"""
    while True:
        print_banner()
        print_menu()
        
        choice = input(f"\n{Fore.CYAN}┌─[X-Recon]─[Select Tool]\n└──╼ $ {Style.RESET_ALL}").strip().lower()
        
        if choice == '1':
            run_module('dns_scanner.py')
        elif choice == '2':
            run_module('subdomain_scanner.py')
        elif choice == '3':
            run_module('email_harvester.py')
        elif choice == '4':
            run_module('port_scanner.py')
        elif choice == '5':
            run_module('nmap_scanner.py')
        elif choice == '6':
            run_module('service_detector.py')
        elif choice == '7':
            run_module('dir_bruteforcer.py')
        elif choice == '8':
            run_module('cve_lookup.py')
        elif choice == '9':
            run_module('password_generator.py')
        elif choice == '10':
            launch_ai_assistant()
        elif choice == 'web':
            launch_web_dashboard()
        elif choice == 'server' or choice == 'servermenu':
            launch_server_manager()
        elif choice == 'exit':
            print(f"\n{Fore.GREEN}[✓] Exiting X-Recon. Stay secure!{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}[!] Invalid option{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
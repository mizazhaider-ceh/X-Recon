# main.py
# this is the final command center for the entire x-recon toolkit.
# it manages the user interface and dispatches tasks to the various modules.

import os
import subprocess
import time
from colorama import init, Fore, Style

# initialize colorama for colors. autoreset=True means colors will reset after each print.
init(autoreset=True)

# get the absolute path to the directory where this script is located.
# this is a robust way to ensure we can always find our 'modules' folder,
# no matter where the user runs the script from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(SCRIPT_DIR, 'modules')

def print_main_banner():
    """prints the main banner for the entire toolkit."""
    # using an f-string with """ makes creating multi-line, colored text easy.
    # Raw string r"" prevents escape sequence warnings
    print(f"{Fore.RED}{Style.BRIGHT}")
    banner = r"""
    __   __          _____                      
    \ \ / /         |  __ \                     
     \ V /____      | |__) |___  ___ ___  _ __  
      > <|______|   |  _  // _ \/ __/ _ \| '_ \ 
     / . \          | | \ \  __/ (_| (_) | | | |
    /_/ \_\         |_|  \_\___|\___\___/|_| |_|
                                              
          >> A Comprehensive Reconnaissance & Attack Toolkit - by Izaz <<
"""
    print(banner)
    print(f"{Style.RESET_ALL}{Fore.YELLOW}")

def show_menu():
    """displays the main, two-column menu of all available tools."""
    # the menu is formatted to look professional and organized by attack phase.
    menu = f"""
{Fore.YELLOW}{Style.BRIGHT}===============================================[ X-Recon Toolkit ]======================================================={Style.RESET_ALL}

{Fore.CYAN}{Style.BRIGHT}-------------------------------------[ Phase 1: Passive & Active Reconnaissance ]---------------------------{Style.RESET_ALL}

  {Fore.MAGENTA}[1]{Style.RESET_ALL} Domain Intelligence      (WHOIS & DNS)            {Fore.MAGENTA}[5]{Style.RESET_ALL} Advanced Port Scanner    (Nmap Deep Scan)
  {Fore.MAGENTA}[2]{Style.RESET_ALL} Subdomain Scanner        (Find Subdomains)        {Fore.MAGENTA}[6]{Style.RESET_ALL} Service Version Detector (Banner Grabbing)
  {Fore.MAGENTA}[3]{Style.RESET_ALL} Email Harvester          (Find Public Emails)     {Fore.MAGENTA}[7]{Style.RESET_ALL} Web Directory Scanner    (Find Hidden Pages)
  {Fore.MAGENTA}[4]{Style.RESET_ALL} Async Port Scanner       (TCP Connect Scan )      {Fore.MAGENTA}[8]{Style.RESET_ALL} CVE Lookup              (Find Vulnerabilities)
  {Fore.MAGENTA}[9]{Style.RESET_ALL} Password List Generator  (Create Custom Wordlists)
  
  {Fore.CYAN}{Style.BRIGHT}-------------------------------------------[ Phase 2: AI & Utilities ]--------------------------------------{Style.RESET_ALL}
  {Fore.MAGENTA}[10]{Style.RESET_ALL}  AI Cyber-Assistant       (Powered by Cerebras)      
  {Fore.MAGENTA}[0]{Style.RESET_ALL}   Exit Toolkit
{Fore.YELLOW}{Style.BRIGHT}=========================================================================================================================={Style.RESET_ALL}
"""
    print(menu)

def run_module(script_name):
    """
    finds and runs the specified module script.
    it also handles clearing the screen for a better user experience.
    """
    module_path = os.path.join(MODULES_DIR, script_name)
    
    # first, check if the module file actually exists before trying to run it.
    if not os.path.exists(module_path):
        print(f"\n{Fore.RED}[!] Error: Module '{script_name}' not found in the 'modules' directory.{Style.RESET_ALL}")
        return

    # clear the screen for a clean transition to the new module.
    # 'cls' is for windows, 'clear' is for linux/macos.
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        # use subprocess.run to execute the python script.
        # this is the modern, secure, and recommended way to run other scripts.
        # check=True will raise an error if the module exits with a non-zero status.
        subprocess.run(['python', module_path], check=True)
    except subprocess.CalledProcessError:
        # this catches errors if the module script itself has a bug and crashes.
        print(f"\n{Fore.RED}[!] Module '{script_name}' exited with an error.")
    except KeyboardInterrupt:
        # this handles the case where the user presses ctrl+c in the middle of a module's execution.
        print(f"\n{Fore.YELLOW}[i] Module execution stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        # a general catch-all for any other unexpected problems.
        print(f"\n{Fore.RED}[!] An unexpected error occurred while running the module: {e}")


# this is the main entry point of our application.
# the `if __name__ == "__main__":` block ensures this code only runs
# when you execute `python main.py` directly.
if __name__ == "__main__":
    # --- map user choices to the corresponding script file names ---
    # this dictionary is the "brain" of our menu. it's clean and easy to update.
    menu_actions = {
        "1": "dns_scanner.py",
        "2": "subdomain_scanner.py",
        "3": "email_harvester.py",
        "4": "port_scanner.py",
        "5": "nmap_scanner.py",
        "6": "service_detector.py",
        "7": "dir_bruteforcer.py",
        "8": "cve_lookup.py",
        "9": "password_generator.py",
        "10": "ai_assistant.py",
    }
    
    # the main loop that keeps the menu running until the user chooses to exit.
    while True:
        # clear the screen to show a fresh menu each time.
        os.system('cls' if os.name == 'nt' else 'clear')
        print_main_banner()
        show_menu()
        
        # get user input and convert to uppercase for case-insensitive matching.
        choice = input(f"{Fore.CYAN}Select a tool to use: {Style.RESET_ALL}").strip().upper()

        if choice in menu_actions:
            run_module(menu_actions[choice])
            # after a module finishes, pause and wait for the user to press enter.
            # this gives them time to read the results before returning to the menu.
            input(f"\n{Fore.BLUE}[Press Enter to return to the main menu...]")
            
        elif choice == "0":
            print(f"\n{Fore.GREEN}Exiting X-Recon Toolkit... Stay safe! ☠️\n")
            break # exit the while loop, which ends the program.
        else:
            print(f"\n{Fore.RED}[!] Invalid option '{choice}'. Please try again.")
            time.sleep(1.5) # pause briefly so the user can see the error message.
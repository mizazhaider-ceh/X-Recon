# modules/subdomain_scanner.py
# v1.5: AsyncIO + aiodns Version
# Ultra-fast, non-blocking DNS resolution for finding subdomains.

import asyncio
import aiodns
from colorama import init, Fore, Style
from tqdm.asyncio import tqdm
import os
from urllib.parse import urlparse

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to find our wordlist and save results
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDLIST_PATH = os.path.join(PROJECT_DIR, 'data', 'wordlists', 'common_subdomains.txt')
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

def print_subdomain_banner():
    """prints the banner for this specific module."""
    print(f"{Fore.BLUE}{Style.BRIGHT}")
    banner = r"""
   _____       __           __      __                        
  / ___/____  / /_  _______/ /___  / /____  _________  ____  
  \__ \/ __ \/ / / / / ___/ __/ __ \/ __/ _ \/ ___/ __ \/ __ \ 
 ___/ / /_/ / / /_/ (__  ) /_/ /_/ / /_/  __/ /  / / / / /_/ /
/____/\____/_/\__,_/____/\__/\____/\__/\___/_/  /_/ /_/\____/ 
                                                              
            >> Multi-Threaded Subdomain Discovery Tool (AsyncIO) <<
"""
    print(banner)
    print(Style.RESET_ALL)

def sanitize_domain(domain_string):
    """
    clean user input to get a proper domain name.
    e.g., "https://www.google.com/" becomes "google.com"
    """
    # use urlparse to break down the url
    parsed = urlparse(domain_string)
    # get the network location (e.g., 'www.google.com') or the path if scheme is missing
    domain = parsed.netloc or parsed.path
    
    # remove 'www.' from the beginning if it exists
    if domain.startswith('www.'):
        domain = domain[4:]
        
    # remove any trailing slashes or other path components
    domain = domain.split('/')[0]
    
    return domain

async def resolve_subdomain(resolver, subdomain, semaphore):
    """
    Async worker function using aiodns.
    """
    async with semaphore:
        try:
            # aiodns query returns a list of result objects
            answers = await resolver.query(subdomain, 'A')
            # Look at the first answer (answers[0]) and get its 'host' (IP)
            return subdomain, True, answers[0].host
        except (aiodns.error.DNSError, Exception):
            return subdomain, False, None

def print_and_save_results(target_domain, found_subdomains):
    """prints a beautiful summary table and saves the results."""
    if not found_subdomains:
        print(f"\n{Fore.YELLOW}[-] Scan Complete. No active subdomains found.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Scan Complete! Found {len(found_subdomains)} active subdomain(s) for {target_domain}.\n")
    
    print(f"{Style.BRIGHT}{Fore.WHITE}{'SUBDOMAIN':<40}{'IP ADDRESS'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'---------':<40}{'----------'}{Style.RESET_ALL}")

    file_content = [f"--- Subdomain Scan Results for {target_domain} ---\n\n"]
    
    for subdomain, ip in sorted(found_subdomains):
        print(f"{Fore.GREEN}{subdomain:<40}{Fore.YELLOW}{ip}{Style.RESET_ALL}")
        file_content.append(f"{subdomain:<40} -> {ip}\n")

    results_file = os.path.join(RESULTS_DIR, f'subdomains_{target_domain}.txt')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.writelines(file_content)
    
    print(f"\n{Fore.CYAN}[+] Results saved to: {results_file}{Style.RESET_ALL}")

async def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_subdomain_banner()
    
    target_input = input(f"{Fore.CYAN}Enter the target domain (e.g., tesla.com): {Style.RESET_ALL}").strip()

    if not target_input:
        print(f"{Fore.RED}[!] No domain entered. Exiting.{Style.RESET_ALL}"); return

    # --- THIS IS THE NEW, SMART PART ---
    target_domain = sanitize_domain(target_input)
    print(f"{Fore.GREEN}[i] Sanitized target to: {target_domain}{Style.RESET_ALL}")
    # --- END OF NEW PART ---

    try:
        with open(WORDLIST_PATH, 'r') as f:
            subdomains_to_check = [f"{line.strip()}.{target_domain}" for line in f if line.strip()]
        print(f"{Fore.GREEN}[i] Successfully loaded {len(subdomains_to_check)} subdomains from wordlist.{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Wordlist not found at '{WORDLIST_PATH}'. Exiting.{Style.RESET_ALL}"); return

    print("\n---[ Scan Speed (Async - Huge Concurrency) ]---")
    print("[1] Normal (50 concurrent queries)")
    print("[2] Fast (500 concurrent queries)")
    print("[3] Insane (1000 concurrent queries)")
    speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
    
    concurrency = 50
    if speed_choice == '2': concurrency = 500
    elif speed_choice == '3': concurrency = 1000

    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Starting scan for {target_domain} with concurrency level {concurrency}...{Style.RESET_ALL}")
    
    # Initialize aiodns Resolver
    resolver = aiodns.DNSResolver()
    semaphore = asyncio.Semaphore(concurrency)
    
    tasks = [resolve_subdomain(resolver, sub, semaphore) for sub in subdomains_to_check]
    
    found_subdomains = []
    
    # Execute with smart progress bar
    for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"{Fore.CYAN}Scanning", unit="sub"):
        subdomain, is_found, ip_address = await future
        if is_found:
            found_subdomains.append((subdomain, ip_address))

    print_and_save_results(target_domain, found_subdomains)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
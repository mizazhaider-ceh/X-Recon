# modules/dir_bruteforcer.py
# v1.5: AsyncIO + aiohttp Version
# High-speed web directory scanning.

import asyncio
import aiohttp
from colorama import init, Fore, Style
from tqdm.asyncio import tqdm
import os
import random

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to find our wordlist and save results
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDLIST_PATH = os.path.join(PROJECT_DIR, 'data', 'wordlists', 'common_directories.txt')
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

def print_dir_banner():
    """prints the banner for this specific module."""
    print(f"{Fore.GREEN}{Style.BRIGHT}")
    banner = r"""
    ____  _                __                       __
   / __ \(_)_______  _____/ /_  ______ _________   / /
  / / / / / ___/ _ \/ ___/ __ \/ __ \ `/ ___/ _ \ / / 
 / /_/ / / /  /  __/ /__/ / / / /_/ / /__/  __/ / /  
/_____/_/_/   \___/\___/_/ /_/\____/\__,_/\___/_/_/   
                                                     
            >> Multi-Threaded Web Directory Scanner (AsyncIO) <<
"""
    print(banner)
    print(Style.RESET_ALL)

async def check_url(session, url, semaphore):
    """
    Async worker.
    """
    async with semaphore:
        try:
            # common user-agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # send a 'head' request. it's faster than 'get'.
            async with session.head(url, headers=headers, timeout=5, allow_redirects=True) as response:
                if 200 <= response.status < 400:
                    return url, response.status
                return url, None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return url, None

def get_status_color(status_code):
    """returns a color based on the http status code."""
    if status_code is None: return Fore.WHITE
    if 200 <= status_code < 300: return Fore.GREEN  # Success
    if 300 <= status_code < 400: return Fore.CYAN   # Redirection
    return Fore.RED                                # Error

def print_and_save_results(target_url, found_paths):
    """prints a beautiful summary table and saves the results."""
    if not found_paths:
        print(f"\n{Fore.YELLOW}[-] Scan Complete. No accessible directories or files found.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Scan Complete! Found {len(found_paths)} accessible path(s) on {target_url}.\n")
    
    print(f"{Style.BRIGHT}{Fore.WHITE}{'STATUS':<10}{'URL'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'------':<10}{'---'}{Style.RESET_ALL}")

    file_content = [f"--- Directory Scan Results for {target_url} ---\n\n"]
    
    for url, status_code in sorted(found_paths, key=lambda x: x[1]):
        color = get_status_color(status_code)
        print(f"{color}{status_code:<10}{Fore.YELLOW}{url}{Style.RESET_ALL}")
        file_content.append(f"[{status_code}] {url}\n")

    safe_name = target_url.replace('://', '_').replace('/', '_')
    results_file = os.path.join(RESULTS_DIR, f'dirscan_{safe_name}.txt')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.writelines(file_content)
    
    print(f"\n{Fore.CYAN}[+] Results saved to: {results_file}{Style.RESET_ALL}")

async def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_dir_banner()
    
    target_url = input(f"{Fore.CYAN}Enter the full target URL (e.g., http://example.com): {Style.RESET_ALL}").strip()

    if not (target_url.startswith('http://') or target_url.startswith('https://')):
        print(f"{Fore.RED}[!] Invalid URL. Please include 'http://' or 'https://'. Exiting.{Style.RESET_ALL}"); return
    if target_url.endswith('/'):
        target_url = target_url[:-1] # remove trailing slash if it exists

    try:
        with open(WORDLIST_PATH, 'r') as f:
            paths_to_check = [line.strip() for line in f if line.strip()]
        print(f"{Fore.GREEN}[i] Successfully loaded {len(paths_to_check)} paths from wordlist.{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Wordlist not found at '{WORDLIST_PATH}'. Exiting.{Style.RESET_ALL}"); return

    print("\n---[ Scan Speed (Async) ]---")
    print("[1] Normal (50 concurrent requests)")
    print("[2] Fast (200 concurrent requests)")
    print("[3] Insane (500 concurrent requests)")
    speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
    
    concurrency = 50
    if speed_choice == '2': concurrency = 200
    elif speed_choice == '3': concurrency = 500

    found_paths = []
    full_urls_to_check = [f"{target_url}/{path}" for path in paths_to_check]
    total_urls = len(full_urls_to_check)
    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Starting scan on {target_url} with concurrency {concurrency}...{Style.RESET_ALL}")
    
    # Process in chunks to avoid overloading memory with too many Task objects
    # Even with async, creating 700k Task objects at once is heavy.
    chunk_size = 50000 
    
    semaphore = asyncio.Semaphore(concurrency)
    
    async with aiohttp.ClientSession() as session:
        # Tqdm context
        with tqdm(total=total_urls, desc=f"{Fore.CYAN}Scanning", unit="path") as pbar:
            for i in range(0, total_urls, chunk_size):
                chunk = full_urls_to_check[i:i + chunk_size]
                tasks = [check_url(session, url, semaphore) for url in chunk]
                
                # We await each chunk's completion before moving to next chunk
                # For massive lists, this keeps memory usage flat.
                for future in asyncio.as_completed(tasks):
                    url, status_code = await future
                    if status_code is not None:
                        found_paths.append((url, status_code))
                        # Real-time output
                        color = get_status_color(status_code)
                        tqdm.write(f"{color}[+] Found: {status_code} - {url}{Style.RESET_ALL}")
                    
                    pbar.update(1)

    print_and_save_results(target_url, found_paths)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
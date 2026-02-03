# modules/email_harvester.py
# v1.5: AsyncIO + aiohttp Version
# High-speed asynchronous scraping.

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from colorama import init, Fore, Style
from tqdm.asyncio import tqdm
import os
from urllib.parse import urlparse, quote_plus
import random

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to save results
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

# using a list of user agents makes our scraper look less like a bot
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
]

def print_harvester_banner():
    """prints the banner for this specific module."""
    print(f"{Fore.YELLOW}{Style.BRIGHT}")
    banner = r"""
    ______                    __                     __
   / ____/___  ____ _________/ /     ____ __________/ /_
  / __/ / __ \/ __ `/ ___/ __/ /_____/ __ `/ ___/ __/ __/
 / /___/ / / / /_/ / /  / /_/ /_____/ /_/ / /__/ /_/ /_
/_____/_/ /_/\__,_/_/  /____/\__/   \__,_/\___/\__/\__/

         >> Advanced Deep Web & Social Media Harvester (AsyncIO) <<
"""
    print(banner)
    print(Style.RESET_ALL)

def sanitize_domain(domain_string):
    """cleans up user input to get a proper domain name."""
    parsed = urlparse(domain_string)
    domain = parsed.netloc or parsed.path
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.split('/')[0]

async def fetch_url(session, url):
    """Async helper to get fetch URL content."""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                return await response.text()
            return None
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None

async def search_for_query(session, query):
    """Worker for stage 1 search queries."""
    urls = set()
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    
    html = await fetch_url(session, search_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', class_='result__a')
        for link in links:
            urls.add(link['href'])
    
    # Random sleep to be polite is harder in async context for "inter-request" delay, 
    # but we can sleep slightly after fetching.
    await asyncio.sleep(random.uniform(0.5, 1.5)) 
    return urls

async def search_for_urls(queries):
    """
    stage 1: gather urls asynchronously.
    """
    urls_to_scrape = set()
    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Stage 1: Gathering URLs from search engines...{Style.RESET_ALL}")
    
    async with aiohttp.ClientSession() as session:
        # We process queries reasonably concurrently
        tasks = [search_for_query(session, q) for q in queries]
        
        # Use simple tqdm iteration
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"{Fore.CYAN}Querying", unit="query"):
            found_urls = await future
            urls_to_scrape.update(found_urls)
            
    return list(urls_to_scrape)

async def scrape_url_for_emails(session, url, semaphore):
    """
    stage 2 worker: async scraping of a single url.
    """
    async with semaphore:
        html = await fetch_url(session, url)
        if html:
            email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            return set(re.findall(email_regex, html))
        return set()

def print_and_save_results(target_domain, found_emails):
    """filters the results, prints a clean list, and saves them as HTML."""
    final_emails = sorted([email for email in found_emails if email.endswith(f".{target_domain}")])

    if not final_emails:
        print(f"\n{Fore.YELLOW}[-] Search Complete. No email addresses matching '{target_domain}' were found.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Search Complete! Found {len(final_emails)} unique email address(es) for {target_domain}.\n")
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_rows = ""
    for email in final_emails:
        print(f"{Fore.CYAN}{Style.BRIGHT}  [+] {email}{Style.RESET_ALL}")
        # Extract username and domain parts for display
        parts = email.split('@')
        html_rows += f"""
            <tr>
                <td><a href="mailto:{email}" style="color: #ffa502; text-decoration: none;">{email}</a></td>
                <td>{parts[0] if len(parts) > 0 else ''}</td>
                <td>@{parts[1] if len(parts) > 1 else ''}</td>
            </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Harvest - {target_domain}</title>
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
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 165, 2, 0.3);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            border-bottom: 2px solid #ffa502;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .header-icon {{ font-size: 2.5rem; }}
        h1 {{ color: #ffa502; font-size: 1.75rem; margin-bottom: 0.25rem; }}
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
            background: rgba(255, 165, 2, 0.1);
            border: 1px solid rgba(255, 165, 2, 0.3);
            border-radius: 8px;
            font-size: 0.85rem;
        }}
        .badge-success {{ background: rgba(0, 255, 157, 0.1); border-color: rgba(0, 255, 157, 0.3); color: #00ff9d; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            background: rgba(255, 165, 2, 0.1);
            color: #ffa502;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        td {{ padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
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
            <span class="header-icon">📧</span>
            <div>
                <h1>Email Harvest Report</h1>
                <div class="subtitle">Deep Web & Social Media Harvester</div>
            </div>
        </div>
        
        <div class="meta">
            <div class="badge">🎯 Target: <strong>{target_domain}</strong></div>
            <div class="badge badge-success">✓ Found: <strong>{len(final_emails)}</strong> emails</div>
            <div class="badge">📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Email Address</th>
                    <th>Username</th>
                    <th>Domain</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generated by <strong>X-Recon v3.0</strong> | Created by Muhammad Izaz Haider</p>
        </div>
    </div>
</body>
</html>"""

    results_file = os.path.join(RESULTS_DIR, f'emails_{target_domain}_{timestamp}.html')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.CYAN}[+] HTML Report saved to: {results_file}{Style.RESET_ALL}")

async def main():
    import sys
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_harvester_banner()
    
    target_input = ""
    concurrency = 100
    
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
        print(f"{Fore.CYAN}[info]Target received via CLI: {target_input}[/info]")
        print("[dim]Running in automated mode (Speed: Fast)[/dim]")
    else:
        target_input = input(f"{Fore.CYAN}Enter the target domain (e.g., mit.edu): {Style.RESET_ALL}").strip()
        
    if not target_input:
        print(f"{Fore.RED}[!] No domain entered. Exiting.{Style.RESET_ALL}"); return
    
    target_domain = sanitize_domain(target_input)
    print(f"{Fore.GREEN}[i] Sanitized target to: {target_domain}{Style.RESET_ALL}")
    
    # --- create a much larger and smarter list of search queries ---
    keywords = ['email', 'contact', 'about', 'support', 'team', 'staff', 'directory', 'press']
    filetypes = ['pdf', 'docx', 'xlsx', 'txt']
    social_media = ['linkedin', 'twitter']
    
    search_queries = [f'"@{target_domain}"']
    search_queries.extend([f'"{keyword}" site:{target_domain}' for keyword in keywords])
    search_queries.extend([f'filetype:{ft} "email" site:{target_domain}' for ft in filetypes])
    search_queries.extend([f'site:{sm}.com "{target_domain}"' for sm in social_media])
    
    # --- stage 1: gather urls ---
    urls_to_scrape = await search_for_urls(search_queries)

    if not urls_to_scrape:
        print(f"{Fore.YELLOW}[!] Could not gather any URLs from search engines. Target may be obscure or search is being blocked.{Style.RESET_ALL}")
        return
        
    print(f"{Fore.GREEN}[i] Stage 1 Complete. Gathered {len(urls_to_scrape)} unique URLs to scrape.{Style.RESET_ALL}")

    # --- stage 2: scrape urls with threads ---
    if len(sys.argv) == 1:
        print("\n---[ Scrape Speed (Async) ]---")
        print("[1] Normal (50 concurrent requests)")
        print("[2] Fast (100 concurrent requests)")
        print("[3] Aggressive (200 concurrent requests)")
        speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
        
        concurrency = 50
        if speed_choice == '2': concurrency = 100
        elif speed_choice == '3': concurrency = 200

    all_found_emails = set()
    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Stage 2: Scraping {len(urls_to_scrape)} URLs with concurrency {concurrency}...{Style.RESET_ALL}")
    
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url_for_emails(session, url, semaphore) for url in urls_to_scrape]
        
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"{Fore.CYAN}Scraping", unit="url"):
            result_set = await future
            all_found_emails.update(result_set)
            
    print_and_save_results(target_domain, all_found_emails)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
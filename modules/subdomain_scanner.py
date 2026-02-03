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

def load_wordlist():
    """Load subdomain prefixes from wordlist file."""
    subdomains = []
    if os.path.exists(WORDLIST_PATH):
        try:
            with open(WORDLIST_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                subdomains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"{Fore.GREEN}[+] Loaded {len(subdomains)} subdomain prefixes from wordlist.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error loading wordlist: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[!] Wordlist not found at {WORDLIST_PATH}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Using default common subdomains...{Style.RESET_ALL}")
        # Default common subdomains if wordlist is missing
        subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
            'dns', 'dns1', 'dns2', 'mx', 'mx1', 'mx2', 'blog', 'dev', 'www2', 'admin',
            'forum', 'news', 'vpn', 'ns3', 'mail2', 'new', 'mysql', 'old', 'lists',
            'support', 'mobile', 'mx3', 'wiki', 'shop', 'sql', 'secure', 'beta',
            'static', 'jobs', 'ads', 'live', 'stage', 'staging', 'app', 'api',
            'cdn', 'cloud', 'git', 'test', 'demo', 'portal', 'host', 'server',
            'web', 'email', 'images', 'img', 'media', 'assets', 'files', 'download',
            'upload', 'backup', 'db', 'database', 'data', 'cache', 'proxy', 'gateway',
            'auth', 'sso', 'login', 'register', 'account', 'accounts', 'user', 'users',
            'member', 'members', 'client', 'clients', 'customer', 'customers', 'partner',
            'partners', 'internal', 'intranet', 'extranet', 'corp', 'corporate', 'hr',
            'finance', 'sales', 'marketing', 'engineering', 'ops', 'operations', 'devops',
            'docs', 'documentation', 'help', 'helpdesk', 'ticket', 'tickets', 'issue',
            'issues', 'jira', 'confluence', 'slack', 'chat', 'meet', 'meeting', 'zoom',
            'calendar', 'schedule', 'crm', 'erp', 'inventory', 'analytics', 'stats',
            'status', 'monitor', 'monitoring', 'health', 'ping', 'grafana', 'kibana',
            'prometheus', 'jenkins', 'ci', 'cd', 'build', 'release', 'deploy', 'prod',
            'production', 'uat', 'qa', 'testing', 'sandbox', 'preview', 'review'
        ]
    return subdomains

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
    """prints a beautiful summary table and saves the results as HTML."""
    if not found_subdomains:
        print(f"\n{Fore.YELLOW}[-] Scan Complete. No active subdomains found.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Scan Complete! Found {len(found_subdomains)} active subdomain(s) for {target_domain}.\n")
    
    print(f"{Style.BRIGHT}{Fore.WHITE}{'SUBDOMAIN':<40}{'IP ADDRESS'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'---------':<40}{'----------'}{Style.RESET_ALL}")

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_rows = ""
    for subdomain, ip in sorted(found_subdomains):
        print(f"{Fore.GREEN}{subdomain:<40}{Fore.YELLOW}{ip}{Style.RESET_ALL}")
        html_rows += f"""
            <tr>
                <td><a href="http://{subdomain}" target="_blank" style="color: #00f3ff; text-decoration: none;">{subdomain}</a></td>
                <td><code>{ip}</code></td>
            </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subdomain Scan - {target_domain}</title>
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
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 119, 255, 0.3);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            border-bottom: 2px solid #0077ff;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .header-icon {{ font-size: 2.5rem; }}
        h1 {{ color: #0077ff; font-size: 1.75rem; margin-bottom: 0.25rem; }}
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
            background: rgba(0, 119, 255, 0.1);
            border: 1px solid rgba(0, 119, 255, 0.3);
            border-radius: 8px;
            font-size: 0.85rem;
        }}
        .badge-success {{ background: rgba(0, 255, 157, 0.1); border-color: rgba(0, 255, 157, 0.3); color: #00ff9d; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            background: rgba(0, 119, 255, 0.1);
            color: #0077ff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        td {{ padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        code {{
            background: rgba(0, 255, 157, 0.1);
            color: #00ff9d;
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
            <span class="header-icon">🌐</span>
            <div>
                <h1>Subdomain Scan Report</h1>
                <div class="subtitle">AsyncIO Multi-Threaded Discovery</div>
            </div>
        </div>
        
        <div class="meta">
            <div class="badge">🎯 Target: <strong>{target_domain}</strong></div>
            <div class="badge badge-success">✓ Found: <strong>{len(found_subdomains)}</strong> subdomains</div>
            <div class="badge">📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Subdomain</th>
                    <th>IP Address</th>
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

    results_file = os.path.join(RESULTS_DIR, f'subdomains_{target_domain}_{timestamp}.html')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.CYAN}[+] HTML Report saved to: {results_file}{Style.RESET_ALL}")

async def main():
    import sys
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_subdomain_banner()
    
    target_input = ""
    concurrency = 500 # Default for CLI
    
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
        print(f"{Fore.CYAN}[info]Target received via CLI: {target_input}[/info]")
        print("[dim]Running in automated mode (Speed: Fast)[/dim]")
    else:
        target_input = input(f"{Fore.CYAN}Enter the target domain (e.g., tesla.com): {Style.RESET_ALL}").strip()
        print("\n---[ Scan Speed (Async - Huge Concurrency) ]---")
        print("[1] Normal (50 concurrent queries)")
        print("[2] Fast (500 concurrent queries)")
        print("[3] Insane (1000 concurrent queries)")
        speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
        
        concurrency = 50
        if speed_choice == '2': concurrency = 500
        elif speed_choice == '3': concurrency = 1000

    if not target_input:
        print(f"{Fore.RED}[!] No domain entered. Exiting.{Style.RESET_ALL}"); return

    target_domain = sanitize_domain(target_input)
    
    # Load subdomain prefixes from wordlist
    subdomain_prefixes = load_wordlist()
    
    if not subdomain_prefixes:
        print(f"{Fore.RED}[!] No subdomain prefixes to check. Exiting.{Style.RESET_ALL}")
        return
    
    # Build full subdomain names by appending target domain
    subdomains_to_check = [f"{prefix}.{target_domain}" for prefix in subdomain_prefixes]
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Starting scan for {target_domain} with concurrency level {concurrency}...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Checking {len(subdomains_to_check)} potential subdomains...{Style.RESET_ALL}")
    
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
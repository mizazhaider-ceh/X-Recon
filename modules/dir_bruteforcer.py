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

def load_wordlist():
    """Load directory paths from wordlist file."""
    paths = []
    if os.path.exists(WORDLIST_PATH):
        try:
            with open(WORDLIST_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"{Fore.GREEN}[+] Loaded {len(paths)} paths from wordlist.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error loading wordlist: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[!] Wordlist not found at {WORDLIST_PATH}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Using default common directories...{Style.RESET_ALL}")
        # Default common directories if wordlist is missing
        paths = [
            'admin', 'administrator', 'login', 'wp-admin', 'wp-login', 'dashboard',
            'panel', 'cpanel', 'phpmyadmin', 'api', 'backup', 'backups', 'config',
            'uploads', 'upload', 'images', 'img', 'css', 'js', 'javascript',
            'assets', 'static', 'media', 'files', 'docs', 'documents', 'downloads',
            'robots.txt', 'sitemap.xml', '.git', '.env', '.htaccess', 'wp-content',
            'wp-includes', 'includes', 'inc', 'lib', 'libs', 'src', 'source',
            'test', 'tests', 'dev', 'development', 'staging', 'beta', 'debug',
            'server-status', 'server-info', 'info.php', 'phpinfo.php', 'info',
            'temp', 'tmp', 'cache', 'log', 'logs', 'error', 'errors', 'cgi-bin',
            'bin', 'scripts', 'script', 'shell', 'console', 'terminal', 'exec',
            'data', 'database', 'db', 'sql', 'mysql', 'postgres', 'mongodb',
            'user', 'users', 'member', 'members', 'account', 'accounts', 'profile',
            'register', 'signup', 'signin', 'auth', 'authenticate', 'oauth',
            'api/v1', 'api/v2', 'api/v3', 'rest', 'graphql', 'swagger', 'docs/api',
            'admin.php', 'login.php', 'index.php', 'config.php', 'setup.php',
            'install', 'installation', 'setup', 'readme', 'readme.txt', 'readme.md',
            'changelog', 'license', 'license.txt', 'version', 'version.txt'
        ]
    return paths

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
    """prints a beautiful summary table and saves the results as HTML."""
    if not found_paths:
        print(f"\n{Fore.YELLOW}[-] Scan Complete. No accessible directories or files found.{Style.RESET_ALL}")
        return

    print(f"\n\n{Fore.GREEN}{Style.BRIGHT}✅ Scan Complete! Found {len(found_paths)} accessible path(s) on {target_url}.\n")
    
    print(f"{Style.BRIGHT}{Fore.WHITE}{'STATUS':<10}{'URL'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'------':<10}{'---'}{Style.RESET_ALL}")

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_rows = ""
    for url, status_code in sorted(found_paths, key=lambda x: x[1]):
        color = get_status_color(status_code)
        print(f"{color}{status_code:<10}{Fore.YELLOW}{url}{Style.RESET_ALL}")
        
        status_color = "#00ff9d" if 200 <= status_code < 300 else "#00f3ff" if 300 <= status_code < 400 else "#ff4757"
        html_rows += f"""
            <tr>
                <td><span style="color: {status_color}; font-weight: bold;">{status_code}</span></td>
                <td><a href="{url}" target="_blank" style="color: #ffa502; text-decoration: none;">{url}</a></td>
            </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Scan - {target_url}</title>
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
            border: 1px solid rgba(0, 255, 157, 0.3);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            border-bottom: 2px solid #00ff9d;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .header-icon {{ font-size: 2.5rem; }}
        h1 {{ color: #00ff9d; font-size: 1.75rem; margin-bottom: 0.25rem; }}
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
            background: rgba(0, 255, 157, 0.1);
            border: 1px solid rgba(0, 255, 157, 0.3);
            border-radius: 8px;
            font-size: 0.85rem;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            background: rgba(0, 255, 157, 0.1);
            color: #00ff9d;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        td {{ padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        .legend {{
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 0.5rem; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
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
            <span class="header-icon">📁</span>
            <div>
                <h1>Directory Scan Report</h1>
                <div class="subtitle">AsyncIO Web Directory Discovery</div>
            </div>
        </div>
        
        <div class="meta">
            <div class="badge">🎯 Target: <strong>{target_url}</strong></div>
            <div class="badge">✓ Found: <strong>{len(found_paths)}</strong> paths</div>
            <div class="badge">📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="legend">
            <div class="legend-item"><span class="dot" style="background: #00ff9d;"></span> 2xx Success</div>
            <div class="legend-item"><span class="dot" style="background: #00f3ff;"></span> 3xx Redirect</div>
            <div class="legend-item"><span class="dot" style="background: #ff4757;"></span> 4xx/5xx Error</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 100px;">Status</th>
                    <th>URL</th>
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

    safe_name = target_url.replace('://', '_').replace('/', '_').replace(':', '_')
    results_file = os.path.join(RESULTS_DIR, f'dirscan_{safe_name}_{timestamp}.html')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.CYAN}[+] HTML Report saved to: {results_file}{Style.RESET_ALL}")

async def main():
    import sys
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_dir_banner()
    
    target_url = ""
    concurrency = 200
    
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        # Auto-add http if missing for robust CLI usage
        if not target_url.startswith('http'):
            target_url = 'http://' + target_url
        print(f"{Fore.CYAN}[info]Target received via CLI: {target_url}[/info]")
        print("[dim]Running in automated mode (Speed: Fast)[/dim]")
    else:
        target_url = input(f"{Fore.CYAN}Enter the full target URL (e.g., http://example.com): {Style.RESET_ALL}").strip()
        print("\n---[ Scan Speed (Async) ]---")
        print("[1] Normal (50 concurrent requests)")
        print("[2] Fast (200 concurrent requests)")
        print("[3] Insane (500 concurrent requests)")
        speed_choice = input(f"{Fore.CYAN}Select an option: {Style.RESET_ALL}").strip()
        
        concurrency = 50
        if speed_choice == '2': concurrency = 200
        elif speed_choice == '3': concurrency = 500

    paths_to_check = load_wordlist()
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
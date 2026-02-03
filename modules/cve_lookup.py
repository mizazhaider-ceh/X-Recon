# modules/cve_lookup.py
# the ultimate version: multi-threaded search for multiple software versions.

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from tqdm import tqdm
import os

# initialize colorama for colors
init(autoreset=True)

# get the project directory path to save results in the right place
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_DIR, 'data', 'results')

VULNERS_API_URL = "https://vulners.com/api/v3/search/bulletin/"

def print_cve_banner():
    """prints the banner for this specific module."""
    """prints the banner for this specific module."""
    print(f"{Fore.RED}{Style.BRIGHT}")
    banner = r"""
    _________ ____  __________
   / ___/ __ \/ __ \/ ____/ __ \\
   \__ \/ / / / / / / __/ / /_/ /
  ___/ / /_/ / /_/ / /___/ _, _/ 
 /____/_____/\____/_____/_/ |_|  
                                
 >> Multi-Threaded CVE & Vulnerability Search <<
"""
    print(banner)
    print(Style.RESET_ALL)

def get_cvss_color(score):
    """returns a color based on how severe the vulnerability is."""
    if score is None: return Fore.WHITE
    if score >= 9.0: return Fore.RED + Style.BRIGHT
    elif score >= 7.0: return Fore.RED
    elif score >= 4.0: return Fore.YELLOW
    else: return Fore.GREEN

def search_cves_for_one_query(query):
    """
    this is our worker function for each thread.
    it searches for a SINGLE software query and returns the query and its results.
    """
    payload = {'query': query, 'type': 'cve', 'size': 10} # get top 10 cves for each
    try:
        response = requests.post(VULNERS_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('result') == 'OK' and 'documents' in data.get('data', {}):
            return query, data['data']['documents']
        else:
            return query, [] # return the query with an empty list
    except requests.exceptions.RequestException:
        # if the request fails, return the query and None to signal an error
        return query, None

def print_and_save_results(all_results):
    """
    prints the beautiful results table for all queries and saves to HTML file.
    """
    if not any(res for q, res in all_results.items() if res):
        print(f"\n{Fore.YELLOW}[-] No CVEs found for any of the provided queries.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Search Complete! Results found for {len(all_results)} quer(ies).\n")
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_sections = ""
    
    # loop through each query and its results
    for query, cve_list in all_results.items():
        print(f"{Style.BRIGHT}{Fore.CYAN}================[ Results for: {query} ]================{Style.RESET_ALL}")

        if cve_list is None:
            print(f"{Fore.RED}  -> Network Error: Could not fetch results.{Style.RESET_ALL}\n")
            html_sections += f"""
            <div class="query-section">
                <h3>🔍 {query}</h3>
                <p style="color: #ff4757;">Network Error: Could not fetch results.</p>
            </div>"""
            continue
        
        if not cve_list:
            print(f"{Fore.YELLOW}  -> No CVEs found in the database.{Style.RESET_ALL}\n")
            html_sections += f"""
            <div class="query-section">
                <h3>🔍 {query}</h3>
                <p style="color: #ffa502;">No CVEs found in the database.</p>
            </div>"""
            continue

        cve_rows = ""
        for cve in cve_list:
            cve_id = cve.get('id', 'N/A')
            title = cve.get('title', 'No title available.')
            cvss_score = cve.get('cvss', {}).get('score', 0.0)
            color = get_cvss_color(cvss_score)
            
            print(f"  {Style.BRIGHT}ID: {Fore.WHITE}{cve_id}")
            print(f"    Title: {Fore.WHITE}{title}")
            print(f"    Score: {color}{cvss_score}{Style.RESET_ALL}\n")
            
            # Determine severity color for HTML
            if cvss_score >= 9.0:
                score_color = "#ff0000"
                severity = "CRITICAL"
            elif cvss_score >= 7.0:
                score_color = "#ff4757"
                severity = "HIGH"
            elif cvss_score >= 4.0:
                score_color = "#ffa502"
                severity = "MEDIUM"
            else:
                score_color = "#00ff9d"
                severity = "LOW"
            
            cve_rows += f"""
                <tr>
                    <td><code>{cve_id}</code></td>
                    <td>{title[:80]}{'...' if len(title) > 80 else ''}</td>
                    <td><span style="color: {score_color}; font-weight: bold;">{cvss_score}</span></td>
                    <td><span class="severity-badge" style="background: {score_color}20; color: {score_color}; border: 1px solid {score_color}40;">{severity}</span></td>
                </tr>"""
        
        html_sections += f"""
        <div class="query-section">
            <h3>🔍 {query}</h3>
            <table>
                <thead>
                    <tr>
                        <th>CVE ID</th>
                        <th>Title</th>
                        <th>CVSS</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
                    {cve_rows}
                </tbody>
            </table>
        </div>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CVE Lookup Report</title>
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
            max-width: 1200px;
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
        .query-section {{
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .query-section h3 {{
            color: #00f3ff;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
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
        td {{ padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); vertical-align: top; }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        code {{
            background: rgba(0, 243, 255, 0.1);
            color: #00f3ff;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.85rem;
        }}
        .severity-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
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
            <span class="header-icon">🛡️</span>
            <div>
                <h1>CVE Vulnerability Report</h1>
                <div class="subtitle">Multi-Threaded CVE & Vulnerability Search</div>
            </div>
        </div>
        
        <div class="meta">
            <div class="badge">🔍 Queries: <strong>{len(all_results)}</strong></div>
            <div class="badge">📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        {html_sections}
        
        <div class="footer">
            <p>Generated by <strong>X-Recon v3.0</strong> | Data from Vulners API | Created by Muhammad Izaz Haider</p>
        </div>
    </div>
</body>
</html>"""

    results_file = os.path.join(RESULTS_DIR, f'cve_report_{timestamp}.html')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{Fore.CYAN}[+] HTML Report saved to: {results_file}{Style.RESET_ALL}")


# this is the main part of our script that runs first
if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print_cve_banner()
    
    # ask for multiple queries, separated by commas
    queries_input = input(f"{Fore.CYAN}Enter software to search (comma-separated):\n"
                          f"{Fore.CYAN}e.g., openssh 7.2, vsftpd 2.3.4, apache 2.4.49\n>> {Style.RESET_ALL}").strip()

    if not queries_input:
        print(f"{Fore.RED}[!] No search query provided. Exiting.{Style.RESET_ALL}")
        exit()
        
    # split the input string into a list of individual search queries
    queries_to_search = [q.strip() for q in queries_input.split(',') if q.strip()]

    print(f"\n{Fore.CYAN}{Style.BRIGHT}[*] Searching for {len(queries_to_search)} software item(s) using threads...{Style.RESET_ALL}")
    
    # --- The Multi-Threaded Part ---
    all_results = {}
    with ThreadPoolExecutor(max_workers=len(queries_to_search)) as executor:
        # start a search for each query in its own thread
        tasks = {executor.submit(search_cves_for_one_query, query): query for query in queries_to_search}
        
        # use tqdm to show progress as each thread finishes
        progress_bar = tqdm(as_completed(tasks), total=len(queries_to_search), desc=f"{Fore.CYAN}Searching", unit="query")
        
        for future in progress_bar:
            query, cve_list = future.result()
            # store the results in a dictionary
            all_results[query] = cve_list
            
    # --- show the final report ---
    print_and_save_results(all_results)
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
    prints the beautiful results table for all queries and saves to one file.
    """
    if not any(res for q, res in all_results.items() if res):
        print(f"\n{Fore.YELLOW}[-] No CVEs found for any of the provided queries.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Search Complete! Results found for {len(all_results)} quer(ies).\n")
    
    file_content = [f"--- Multi-CVE Lookup Results ---\n\n"]
    
    # loop through each query and its results
    for query, cve_list in all_results.items():
        print(f"{Style.BRIGHT}{Fore.CYAN}================[ Results for: {query} ]================{Style.RESET_ALL}")
        file_content.append(f"==== Results for: {query} ====\n\n")

        if cve_list is None:
            print(f"{Fore.RED}  -> Network Error: Could not fetch results.{Style.RESET_ALL}\n")
            file_content.append("  -> Network Error: Could not fetch results.\n\n")
            continue
        
        if not cve_list:
            print(f"{Fore.YELLOW}  -> No CVEs found in the database.{Style.RESET_ALL}\n")
            file_content.append("  -> No CVEs found in the database.\n\n")
            continue

        for cve in cve_list:
            cve_id = cve.get('id', 'N/A')
            title = cve.get('title', 'No title available.')
            cvss_score = cve.get('cvss', {}).get('score', 0.0)
            color = get_cvss_color(cvss_score)
            
            print(f"  {Style.BRIGHT}ID: {Fore.WHITE}{cve_id}")
            print(f"    Title: {Fore.WHITE}{title}")
            print(f"    Score: {color}{cvss_score}{Style.RESET_ALL}\n")
            
            file_content.append(f"  ID: {cve_id}\n")
            file_content.append(f"  Title: {title}\n")
            file_content.append(f"  CVSS Score: {cvss_score}\n")
            file_content.append("  " + "-" * 20 + "\n")

    # --- save the single, combined report ---
    results_file = os.path.join(RESULTS_DIR, 'cve_multisearch_report.txt')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.writelines(file_content)
    
    print(f"\n{Fore.CYAN}[+] Combined detailed report saved to: {results_file}{Style.RESET_ALL}")


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
# intelscan.py
# The definitive, intelligent version. It automatically finds its own wordlist
# and is completely resilient to common errors.
# Creator: Muhammad Izaz Haider

import os
import sys
import socket
import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.resolver
import whois
from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

# --- Global Configuration: The key to stability ---
console = Console()
resolver = dns.resolver.Resolver()
resolver.timeout = 2.0
resolver.lifetime = 5.0

# --- THIS IS THE DEFINITIVE, "SMART SEARCH" FUNCTION ---
def find_wordlist() -> str | None:
    """
    Intelligently searches for the wordlist file starting from the script's location.
    This makes the tool portable and easy to use.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Walk through the current directory and all subdirectories
    for root, dirs, files in os.walk(script_dir):
        # We are looking for a folder named 'wordlists'
        if 'wordlists' in dirs:
            # If we find it, check for our specific file inside it
            wordlist_path = os.path.join(root, 'wordlists', 'common_subdomains.txt')
            if os.path.exists(wordlist_path):
                # If the file exists, we've found it! Return the full path.
                return wordlist_path
    # If the loop finishes and we haven't found it, return None.
    return None

# --- We run the smart search once at the start ---
WORDLIST_PATH = find_wordlist()


def print_banner():
    """Prints the main banner for the tool."""
    banner_text = r"""
    ██╗███╗   ██╗████████╗███████╗██╗    ██╗ ██████╗ ██████╗ ███╗   ██╗
    ██║████╗  ██║╚══██╔══╝██╔════╝██║    ██║██╔═══██╗██╔══██╗████╗  ██║
    ██║██╔██╗ ██║   ██║   █████╗  ██║ █╗ ██║██║   ██║██████╔╝██╔██╗ ██║
    ╚██╗██║╚██╗██║   ██║   ██╔══╝  ██║███╗██║██║   ██║██╔══██╗██║╚██╗██║
     ╚██╗██║ ╚████║   ██║   ███████╗╚███╔███╔╝╚██████╔╝██║  ██║██║ ╚████║
      ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
    """
    title = "[bold bright_cyan]IntelScan: A Professional DNS & Subdomain Discovery Tool[/bold bright_cyan]"
    byline = "[yellow]by Muhammad Izaz Haider[/yellow]"
    console.print(Align.center(banner_text, style="bold blue"))
    console.print(Align.center(title))
    console.print(Align.center(byline))

def sanitize_domain(domain_string: str) -> str:
    """Cleans up user input to get a proper domain name."""
    parsed = urlparse(domain_string)
    domain = parsed.netloc or parsed.path
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.split('/')[0]

def get_dns_records(domain: str) -> dict | None:
    """Gets all common DNS records and displays them in a beautiful table."""
    console.print(Panel("[bold cyan]Querying DNS Records...[/bold cyan]", expand=False, border_style="dim"))
    record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'SOA', 'CNAME']
    dns_results = {}
    for record_type in record_types:
        try:
            answers = resolver.resolve(domain, record_type)
            dns_results[record_type] = [rdata.to_text() for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
            continue
    if not dns_results:
        console.print("[yellow][-] No common DNS records were found.[/yellow]")
        return None
    table = Table(title=f"DNS Records for {domain}", box=ROUNDED, style="cyan", title_style="bold bright_cyan")
    table.add_column("Record Type", style="bold magenta", justify="right")
    table.add_column("Value", style="green")
    for record_type, values in sorted(dns_results.items()):
        table.add_row(record_type, "\n".join(values))
    console.print(table)
    return dns_results

def get_whois_info(domain: str) -> dict | None:
    """Gets detailed WHOIS information and handles all data types gracefully."""
    console.print(Panel("[bold cyan]Querying Full WHOIS Information...[/bold cyan]", expand=False, border_style="dim"))
    try:
        domain_info = whois.whois(domain)
        if not domain_info.domain_name:
            console.print("[red][!] Could not retrieve WHOIS information.[/red]")
            return None
        table = Table(title=f"WHOIS Report for {domain}", box=ROUNDED, style="cyan", title_style="bold bright_cyan")
        table.add_column("Attribute", style="bold magenta", justify="right")
        table.add_column("Value", style="green")
        domain_info_dict = domain_info.__dict__
        for key, value in domain_info_dict.items():
            if value:
                display_key = key.replace('_', ' ').title()
                # --- THIS IS THE DEFINITIVE FIX for the WHOIS crash ---
                if isinstance(value, list):
                    value_str = "\n".join([str(item) for item in value])
                else:
                    value_str = str(value)
                table.add_row(display_key, value_str)
        console.print(table)
        return domain_info_dict
    except Exception as e:
        console.print(f"[red][!] An error occurred during WHOIS lookup: {e}[/red]")
        return None

def resolve_subdomain(subdomain: str) -> tuple[str, str | None]:
    """Worker function to find an IP for a subdomain."""
    try:
        answers = resolver.resolve(subdomain, 'A')
        return subdomain, answers[0].to_text()
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
        return subdomain, None

def perform_subdomain_scan(domain: str, thread_count: int) -> dict | None:
    """Uses threads and a Rich progress bar to find subdomains."""
    console.print(Panel(f"[bold cyan]Starting High-Speed Subdomain Scan for {domain}[/bold cyan]", expand=False, border_style="dim"))
    
    # This check now uses the globally found, absolute path.
    if not WORDLIST_PATH:
        console.print(f"[red][!] Subdomain scan failed: Could not automatically find 'common_subdomains.txt'.[/red]")
        return None

    with open(WORDLIST_PATH, 'r') as f:
        subdomains_to_check = [f"{line.strip()}.{domain}" for line in f if line.strip()]
    console.print(f"[green][i] Loaded {len(subdomains_to_check)} potential subdomains from wordlist.[/green]")
    
    found_subdomains = {}
    progress = Progress(
        SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"), TextColumn("[progress.description]{task.description}"), transient=True
    )
    with progress:
        task = progress.add_task(f"Scanning with {thread_count} threads...", total=len(subdomains_to_check))
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            tasks = {executor.submit(resolve_subdomain, sub): sub for sub in subdomains_to_check}
            for future in as_completed(tasks):
                subdomain, ip = future.result()
                if ip:
                    found_subdomains[subdomain] = ip
                progress.update(task, advance=1)
    
    if not found_subdomains:
        console.print("\n[yellow][-] Scan Complete. No active subdomains found.[/yellow]")
        return None

    table = Table(title=f"Found Subdomains for {domain}", box=ROUNDED, style="cyan", title_style="bold bright_cyan")
    table.add_column("Subdomain", style="bold magenta", max_width=50)
    table.add_column("IP Address", style="green")
    for subdomain, ip in sorted(found_subdomains.items()):
        table.add_row(subdomain, ip)
    console.print(table)
    return found_subdomains

def save_results(domain: str, results: dict):
    """Saves all collected information into a single report file."""
    # ... (saving logic remains the same) ...

def main():
    """The main function to run the application logic."""
    print_banner()

    # --- NEW: Check for wordlist on startup ---
    if not WORDLIST_PATH:
        console.print(Panel(
            f"[bold red]Startup Warning: Wordlist Not Found![/bold red]\n\n"
            f"IntelScan could not automatically find 'common_subdomains.txt'.\n"
            f"The Subdomain Scan (Option 2) will be disabled.\n\n"
            f"Please ensure your folder structure is correct:\n"
            f"intelscan/  <-- Your main folder\n"
            f"├── intelscan.py\n"
            f"└── data/\n"
            f"    └── wordlists/\n"
            f"        └── common_subdomains.txt",
            title="[bold yellow]Configuration Notice[/bold yellow]", border_style="yellow"
        ))

    target_input = console.input(f"\n[bold bright_cyan]Enter the target domain (e.g., tesla.com): [/bold bright_cyan]").strip()

    if not target_input:
        console.print("[red][!] No domain entered. Exiting.[/red]"); return

    target_domain = sanitize_domain(target_input)
    console.print(f"[green][i] Sanitized target to: {target_domain}[/green]")
    
    all_results = {}

    while True:
        console.print("\n---[ IntelScan Options ]---", style="bold yellow")
        console.print("[1] General Intelligence Lookup (DNS & WHOIS)")
        if WORDLIST_PATH: # Only show option 2 if the wordlist was found
            console.print("[2] High-Speed Subdomain Scan")
        console.print("[S] Save Collected Results to File")
        console.print("[0] Exit")
        choice = console.input(f"[bold bright_cyan]Select an option: [/bold bright_cyan]").strip().upper()

        if choice == '1':
            all_results["dns"] = get_dns_records(target_domain)
            all_results["whois"] = get_whois_info(target_domain)
        elif choice == '2' and WORDLIST_PATH:
            console.print("\n---[ Subdomain Scan Speed ]---", style="bold yellow")
            console.print("[1] Normal (50 threads)")
            console.print("[2] Fast (100 threads)")
            console.print("[3] Insane (150 threads)")
            speed_choice = console.input(f"[bold bright_cyan]Select speed: [/bold bright_cyan]").strip()
            thread_count = 50
            if speed_choice == '2': thread_count = 100
            elif speed_choice == '3': thread_count = 150
            all_results["subdomains"] = perform_subdomain_scan(target_domain, thread_count)
        elif choice == 'S':
            if not all_results:
                console.print("[yellow][!] No results collected yet to save.[/yellow]")
            else:
                save_results(target_domain, all_results)
        elif choice == '0':
            console.print(f"[yellow]Exiting IntelScan...[/yellow]"); break
        else:
            console.print(f"[red][!] Invalid option. Please try again.[/red]")

if __name__ == "__main__":
    main()
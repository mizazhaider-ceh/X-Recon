#!/usr/bin/env python3
"""
X-Recon AI Setup Helper
Quick setup for Cerebras API integration
"""

import os
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print(r"""
    ╔═══════════════════════════════════════════════╗
    ║   🤖 X-Recon AI Setup Helper                 ║
    ║   Get your FREE Cerebras API key in 2 mins!  ║
    ╚═══════════════════════════════════════════════╝
    """)
    print(Style.RESET_ALL)

def main():
    print_banner()
    
    # Check if .env already exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            if 'CEREBRAS_API_KEY' in content and len(content.split('=')[-1].strip()) > 10:
                print(f"{Fore.GREEN}✅ API key is already configured in .env file!")
                print(f"{Fore.YELLOW}   If you want to update it, edit the .env file directly.")
                return
    
    print(f"{Fore.CYAN}📋 Follow these simple steps:{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}1. Open your browser and go to: {Fore.YELLOW}https://cloud.cerebras.ai/{Style.RESET_ALL}")
    print(f"{Fore.WHITE}2. Sign up for FREE (no credit card required){Style.RESET_ALL}")
    print(f"{Fore.WHITE}3. Go to API Keys section{Style.RESET_ALL}")
    print(f"{Fore.WHITE}4. Click 'Create New API Key'{Style.RESET_ALL}")
    print(f"{Fore.WHITE}5. Copy your API key{Style.RESET_ALL}")
    print()
    
    # Prompt for API key
    print(f"{Fore.GREEN}Enter your Cerebras API key:{Style.RESET_ALL}")
    api_key = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
    
    if not api_key:
        print(f"{Fore.RED}❌ No API key entered. Setup cancelled.{Style.RESET_ALL}")
        return
    
    # Validate key format (basic check)
    if len(api_key) < 20:
        print(f"{Fore.YELLOW}⚠️  Warning: This doesn't look like a valid API key (too short){Style.RESET_ALL}")
        confirm = input(f"{Fore.CYAN}Continue anyway? (y/n): {Style.RESET_ALL}").lower()
        if confirm != 'y':
            return
    
    # Write to .env file
    try:
        with open(env_path, 'w') as f:
            f.write(f"# X-Recon AI Configuration\n")
            f.write(f"# Get your free API key from: https://cloud.cerebras.ai/\n\n")
            f.write(f"CEREBRAS_API_KEY={api_key}\n")
        
        print(f"\n{Fore.GREEN}✅ Success! API key saved to .env file{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 You can now use the AI Assistant (Option 10) in X-Recon!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Tip: Never share your .env file or commit it to Git!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error writing .env file: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
    input(f"\n{Fore.WHITE}Press Enter to exit...{Style.RESET_ALL}")

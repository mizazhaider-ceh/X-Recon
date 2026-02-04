# modules/ai_assistant.py
# v1.1: Powering X-Recon with Cerebras AI (Llama-3.3-70b)

import os
import sys

# --- CORRECTED PATHING LOGIC ---
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(MODULE_DIR)
sys.path.append(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, 'server'))

try:
    import config
    if not hasattr(config, 'CEREBRAS_API_KEY') or not config.CEREBRAS_API_KEY:
        error_msg = "CEREBRAS_API_KEY not found in config.py"
        # We will handle this gracefully in run_ai_assistant
except ImportError:
    class DummyConfig:
        CEREBRAS_API_KEY = None
    config = DummyConfig()

from cerebras.cloud.sdk import Cerebras
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.align import Align
from rich.box import ROUNDED
from rich.theme import Theme
from rich.text import Text
from rich.console import Group
from rich.padding import Padding

# --- A VIBRANT AND PROFESSIONAL CUSTOM COLOR THEME ---
custom_theme = Theme({
    "markdown.h1": "bold bright_cyan",
    "markdown.h2": "bold cyan",
    "markdown.bold": "bold bright_white",
    "markdown.italic": "italic yellow",
    "markdown.link": "bold bright_yellow underline",
})

console = Console(theme=custom_theme)

def print_ai_banner():
    """prints the banner for this specific module."""
    # Using raw strings (r"...") fixes the 'invalid escape sequence' warning
    banner = r"""
    [bold magenta]
    __   __      ____                         
    \ \ / /     |  _ \                        
     \ V /______| |_) |___  ___ ___  _ __     
      > <|______|  _ <| _ \/ __/ _ \| '_ \    
     / . \      | |_) | (_) (__ (_) | | | |   
    /_/ \_\     |____/ \___\___\___/|_| |_|   
                                              
    >> AI Cyber-Assistant (Powered by Cerebras) <<[/bold magenta]
"""
    console.print(Align.center(banner))

def render_response(response_text: str) -> Group:
    """
    Parses the AI's response and renders commands in a clean,
    professional code block style.
    """
    renderables = []
    lines = response_text.split('\n')
    markdown_buffer = []
    COMMAND_PREFIX = "Command:"

    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.startswith(COMMAND_PREFIX):
            if markdown_buffer:
                renderables.append(Markdown('\n'.join(markdown_buffer)))
                markdown_buffer = []

            # Clean up the command text (remove 'Command:' and backticks)
            command_text = stripped_line[len(COMMAND_PREFIX):].strip().strip('`')
            indent_size = len(line) - len(line.lstrip(' '))

            # Use Rich Syntax Highlighting for the command
            # We assume it's usually bash/shell but generic 'shell' works well
            syntax_highlighted = Syntax(command_text, "bash", theme="monokai", line_numbers=False, word_wrap=True)

            command_block = Panel(
                syntax_highlighted,
                style="on #1e1e1e", # Dark background for the code block
                box=ROUNDED,
                border_style="dim white",
                padding=(1, 2), # Increased padding for better look
                expand=False
            )
            
            # Application of Padding for indentation
            indented_block = Padding(command_block, (0, 0, 0, indent_size))
            renderables.append(indented_block)
        else:
            markdown_buffer.append(line)
    
    if markdown_buffer:
        renderables.append(Markdown('\n'.join(markdown_buffer)))
        
    return Group(*renderables)

def run_ai_assistant():
    """The main function to run the interactive chat session."""
    api_key = getattr(config, 'CEREBRAS_API_KEY', None)
    
    if not api_key or "YOUR_CEREBRAS_API_KEY" in api_key or api_key == "your_api_key_here":
        console.print("\n[bold red]╔════════════════════════════════════════════════════════╗[/bold red]")
        console.print("[bold red]║  ❌ Cerebras API Key Not Configured                   ║[/bold red]")
        console.print("[bold red]╚════════════════════════════════════════════════════════╝[/bold red]\n")
        
        console.print("[bold yellow]🚀 Quick Setup (Takes 2 minutes!):[/bold yellow]\n")
        console.print("[white]1. Run: [bold cyan]python setup_ai.py[/bold cyan][/white]")
        console.print("[white]   OR[/white]")
        console.print("[white]2. Get FREE API key from: [bold cyan]https://cloud.cerebras.ai/[/bold cyan][/white]")
        console.print("[white]3. Create [bold].env[/bold] file in project root[/white]")
        console.print("[white]4. Add: [bold]CEREBRAS_API_KEY=your_key_here[/bold][/white]\n")
        
        console.print("[bold green]💡 Why Cerebras?[/bold green]")
        console.print("[white]   • 100% FREE (no credit card)[/white]")
        console.print("[white]   • Llama 3.3 70B - Best AI for cybersecurity[/white]")
        console.print("[white]   • Lightning fast responses[/white]\n")
        
        # Ask if user wants to open browser
        try:
            from colorama import Fore, Style
            response = input(f"{Fore.CYAN}Would you like to open the setup page now? (y/n): {Style.RESET_ALL}").lower()
            if response == 'y':
                import webbrowser
                webbrowser.open('https://cloud.cerebras.ai/')
                console.print(f"\n[bold green]✅ Opening browser... Follow the steps above to get your key![/bold green]\n")
        except:
            pass
        
        return

    try:
        # Initialize Cerebras Client
        client = Cerebras(api_key=api_key)
        
        # --- Model Selection ---
        console.print("\n[bold cyan]---[ AI Model Selection ]---[/bold cyan]")
        console.print("1. Llama 3.3 70B (Recommended - Fast & Smart)")
        console.print("2. Llama 3.1 8B  (Ultra Fast)")
        
        choice = console.input("[bold green]Select model [1]: [/bold green]").strip()
        model_id = "llama-3.3-70b"
        if choice == '2':
            model_id = "llama3.1-8b"
            
        console.print(f"[dim]Selected: {model_id}[/dim]")

        # --- SYSTEM PERSONA ---
        system_instruction = (
            "You are X-AI, an elite cybersecurity assistant for the 'X-Recon' toolkit, created by Muhammad Izaz Haider. "
            "You MUST follow these formatting rules: \n"
            "1. **Spacing:** Insert a blank line between paragraphs. \n"
            "2. **Commands:** Prefix terminal commands with `Command:` (e.g., Command: nmap -A target). \n"
            "3. **Code:** Use markdown code blocks. \n"
            "4. **Signature:** End every response with: `--- \n*Created by Muhammad Izaz Haider*`"
        )
        
        history = [
            {"role": "system", "content": system_instruction}
        ]

        console.print("\n[green]X-AI is online (Cerebras Inference Engine Connected).[/green]")
        console.print("[yellow]Type 'exit' to return to menu.[/yellow]")

        while True:
            prompt = console.input(f"\n[bold cyan]You > [/bold cyan]").strip()
            
            if prompt.lower() in ['exit', 'quit']:
                console.print(f"\n[green]X-AI signing off.[/green]"); break
            if not prompt: continue

            # Append user message
            history.append({"role": "user", "content": prompt})

            try:
                with console.status("[bold magenta]X-AI is thinking...[/bold magenta]", spinner="dots"):
                    chat_completion = client.chat.completions.create(
                        messages=history,
                        model=model_id,
                        temperature=0.7
                    )
                    
                response_text = chat_completion.choices[0].message.content
                
                # Append assistant response to history
                history.append({"role": "assistant", "content": response_text})
                
                # Render
                rendered_content = render_response(response_text)
                
                ai_panel = Panel(
                    rendered_content,
                    title="[bold green]X-AI Response[/bold green]",
                    title_align="left",
                    border_style="green",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(ai_panel)

            except Exception as e:
                console.print(f"\n[bold red][!] Cerebras API Error: {e}[/bold red]")
                # If it's a context length error, we might want to clear history, but for now just show error.

    except Exception as e:
        console.print(f"\n[bold red][!] Initialization Error: {e}[/bold red]")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print_ai_banner()
    run_ai_assistant()
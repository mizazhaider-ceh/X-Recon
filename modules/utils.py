# modules/utils.py
import re
import os
import json
from datetime import datetime
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel

# --- Centralized UI ---
class RichConsole:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RichConsole, cls).__new__(cls)
            custom_theme = Theme({
                "info": "cyan",
                "warning": "yellow",
                "error": "bold red",
                "success": "bold green",
                "header": "bold magenta",
                "highlight": "bold white"
            })
            cls._instance.console = Console(theme=custom_theme)
        return cls._instance

    @classmethod
    def get_console(cls):
        return cls().console

    @classmethod
    def print_banner(cls, title):
        console = cls.get_console()
        console.print(Panel(f"[header]{title}[/header]", expand=False, border_style="cyan"))

# --- Input Validation ---
class InputValidator:
    @staticmethod
    def validate_ip(ip_str):
        pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(pattern, ip_str))

    @staticmethod
    def validate_domain(domain_str):
        pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        return bool(re.match(pattern, domain_str))

    @staticmethod
    def validate_port_range(port_str):
        try:
            if '-' in port_str:
                start, end = map(int, port_str.split('-'))
                return 0 < start <= end <= 65535, (start, end)
            else:
                port = int(port_str)
                return 0 < port <= 65535, (port, port)
        except ValueError:
            return False, None

# --- Result Saving ---
class ResultSaver:
    def __init__(self, module_name):
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results_dir = os.path.join(self.project_dir, 'data', 'results')
        os.makedirs(self.results_dir, exist_ok=True)
        self.module_name = module_name

    def save_text(self, identifier, content_lines):
        """Save results as HTML report"""
        filename = f"{self.module_name}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.results_dir, filename)
        try:
            # Convert text content to HTML
            html_content = self._generate_html_report(identifier, content_lines)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            return filepath
        except Exception as e:
            Logger.log_error(f"Failed to save HTML results: {e}")
            return None
    
    def _generate_html_report(self, identifier, content_lines):
        """Generate professional HTML report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert content lines to HTML
        if isinstance(content_lines, list):
            content_html = '<br>'.join(str(line).strip() for line in content_lines)
        else:
            content_html = str(content_lines).replace('\n', '<br>')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.module_name} - {identifier}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            border-bottom: 2px solid #00f3ff;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        h1 {{
            color: #00f3ff;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .meta {{
            color: #888;
            font-size: 0.9rem;
        }}
        .content {{
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #00ff9d;
            font-family: 'Courier New', monospace;
            font-size: 0.95rem;
            overflow-x: auto;
        }}
        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(0, 243, 255, 0.2);
            border: 1px solid #00f3ff;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-right: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 {self.module_name.replace('_', ' ').title()}</h1>
            <div class="meta">
                <span class="badge">Target: {identifier}</span>
                <span class="badge">Generated: {timestamp}</span>
                <span class="badge">X-Recon v3.0</span>
            </div>
        </div>
        <div class="content">
            {content_html}
        </div>
        <div class="footer">
            <p>Generated by <strong>X-Recon v3.0</strong> | Created by Muhammad Izaz Haider</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def save_json(self, identifier, data_dict):
        filename = f"{self.module_name}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=4)
            return filepath
        except Exception as e:
            Logger.log_error(f"Failed to save JSON results: {e}")
            return None

    def save_html(self, identifier, title, body_content):
        filename = f"{self.module_name}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.results_dir, filename)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X-Recon Report - {identifier}</title>
    <link href="https://fonts.googleapis.com/css2?family=Jersey+15&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg-dark: #0a0a0f; --text-main: #e0e0e0; --neon-cyan: #00f3ff; --neon-magenta: #bc13fe; }}
        body {{ background-color: var(--bg-dark); color: var(--text-main); font-family: 'Inter', sans-serif; margin: 0; padding: 2rem; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #13131f; padding: 2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
        h1 {{ color: var(--neon-cyan); font-family: 'Jersey 15', monospace; letter-spacing: 2px; border-bottom: 2px solid var(--neon-cyan); padding-bottom: 0.5rem; }}
        .meta {{ color: #888; font-size: 0.9rem; margin-bottom: 2rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: var(--neon-magenta); text-transform: uppercase; font-size: 0.8rem; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        .footer {{ margin-top: 3rem; text-align: center; color: #555; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>X-RECON SCAN REPORT</h1>
        <div class="meta">
            Target: <strong>{identifier}</strong><br>
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Module: {self.module_name.upper()}
        </div>
        
        <h2>Results</h2>
        {body_content}
        
        <div class="footer">
            GENERATED BY X-RECON TOOLKIT
        </div>
    </div>
</body>
</html>
"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_template)
            return filepath
        except Exception as e:
            Logger.log_error(f"Failed to save HTML results: {e}")
            return None

# --- Centralized Logging ---
class Logger:
    @staticmethod
    def log_error(message):
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_dir, 'data', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        filepath = os.path.join(log_dir, "errors.log")
        with open(filepath, "a") as f:
            f.write(f"[{datetime.now()}] {message}\n")

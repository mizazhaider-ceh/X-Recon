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
        filename = f"{self.module_name}_{identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.results_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(content_lines)
            return filepath
        except Exception as e:
            Logger.log_error(f"Failed to save text results: {e}")
            return None

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

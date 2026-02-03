"""
X-Recon Server Manager
Handles web server lifecycle: start, stop, restart, background mode
"""

import os
import sys
import subprocess
import signal
import time
import psutil
from pathlib import Path
from colorama import Fore, Style

class ServerManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.server_script = self.script_dir / "server.py"
        self.pid_file = self.script_dir / ".server.pid"
        self.log_file = self.script_dir / "server.log"
        
    def is_running(self):
        """Check if server is currently running"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if 'python' in proc.name().lower() and 'server.py' in ' '.join(proc.cmdline()):
                    return True
        except (ValueError, psutil.NoSuchProcess):
            pass
        
        # Clean up stale PID file
        if self.pid_file.exists():
            self.pid_file.unlink()
        return False
    
    def get_pid(self):
        """Get server PID if running"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except (FileNotFoundError, ValueError, OSError, PermissionError) as e:
                # Log error but don't crash - PID file may be corrupted
                return None
        return None
    
    def start_foreground(self):
        """Start server in foreground (blocking)"""
        if self.is_running():
            print(f"{Fore.YELLOW}[!] Server is already running (PID: {self.get_pid()}){Style.RESET_ALL}")
            return False
        
        print(f"{Fore.CYAN}>> Starting X-Recon Web Server on http://127.0.0.1:8000{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Press CTRL+C to stop the server{Style.RESET_ALL}\n")
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Stream output
            for line in process.stdout:
                print(line, end='')
            
            process.wait()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[i] Shutting down server...{Style.RESET_ALL}")
            process.terminate()
            process.wait()
        finally:
            if self.pid_file.exists():
                self.pid_file.unlink()
        
        return True
    
    def start_background(self):
        """Start server in background (non-blocking)"""
        if self.is_running():
            print(f"{Fore.YELLOW}[!] Server is already running (PID: {self.get_pid()}){Style.RESET_ALL}")
            return False
        
        print(f"{Fore.CYAN}>> Starting X-Recon Web Server in background...{Style.RESET_ALL}")
        
        # Open log file
        log_handle = open(self.log_file, 'w')
        
        # Start process in background
        process = subprocess.Popen(
            [sys.executable, str(self.server_script)],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            start_new_session=True if os.name != 'nt' else False
        )
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment to check if it started successfully
        time.sleep(2)
        
        if self.is_running():
            print(f"{Fore.GREEN}✓ Server started successfully (PID: {process.pid}){Style.RESET_ALL}")
            print(f"{Fore.CYAN}  URL: http://127.0.0.1:8000{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Logs: {self.log_file}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ Server failed to start. Check {self.log_file} for details.{Style.RESET_ALL}")
            return False
    
    def stop(self):
        """Stop the running server"""
        if not self.is_running():
            print(f"{Fore.YELLOW}[!] Server is not running{Style.RESET_ALL}")
            return False
        
        pid = self.get_pid()
        print(f"{Fore.CYAN}>> Stopping server (PID: {pid})...{Style.RESET_ALL}")
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # Wait for graceful shutdown
            try:
                proc.wait(timeout=5)
                print(f"{Fore.GREEN}✓ Server stopped successfully{Style.RESET_ALL}")
            except psutil.TimeoutExpired:
                # Force kill if it doesn't stop
                proc.kill()
                print(f"{Fore.YELLOW}✓ Server force-stopped{Style.RESET_ALL}")
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except psutil.NoSuchProcess:
            print(f"{Fore.YELLOW}[!] Process not found, cleaning up...{Style.RESET_ALL}")
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def restart(self):
        """Restart the server"""
        print(f"{Fore.CYAN}>> Restarting server...{Style.RESET_ALL}")
        self.stop()
        time.sleep(1)
        return self.start_background()
    
    def status(self):
        """Show server status"""
        if self.is_running():
            pid = self.get_pid()
            proc = psutil.Process(pid)
            uptime = time.time() - proc.create_time()
            
            print(f"\n{Fore.GREEN}● Server Status: RUNNING{Style.RESET_ALL}")
            print(f"  PID: {pid}")
            print(f"  Uptime: {int(uptime)}s")
            print(f"  URL: http://127.0.0.1:8000")
            print(f"  Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB\n")
        else:
            print(f"\n{Fore.RED}○ Server Status: STOPPED{Style.RESET_ALL}\n")
    
    def show_menu(self):
        """Show server management menu"""
        while True:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{Style.BRIGHT}║   X-RECON WEB SERVER MANAGER        ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{Style.BRIGHT}╚══════════════════════════════════════╝{Style.RESET_ALL}\n")
            
            self.status()
            
            print(f"{Fore.MAGENTA}[1]{Style.RESET_ALL} Start Server (Foreground)")
            print(f"{Fore.MAGENTA}[2]{Style.RESET_ALL} Start Server (Background)")
            print(f"{Fore.MAGENTA}[3]{Style.RESET_ALL} Stop Server")
            print(f"{Fore.MAGENTA}[4]{Style.RESET_ALL} Restart Server")
            print(f"{Fore.MAGENTA}[5]{Style.RESET_ALL} View Logs")
            print(f"{Fore.RED}[0]{Style.RESET_ALL} Back to Main Menu\n")
            
            choice = input(f"{Fore.GREEN}Select option: {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.start_foreground()
            elif choice == '2':
                self.start_background()
            elif choice == '3':
                self.stop()
            elif choice == '4':
                self.restart()
            elif choice == '5':
                if self.log_file.exists():
                    print(f"\n{Fore.CYAN}=== Server Logs ==={Style.RESET_ALL}\n")
                    with open(self.log_file, 'r') as f:
                        print(f.read())
                    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[!] No log file found{Style.RESET_ALL}")
            elif choice == '0':
                break
            else:
                print(f"{Fore.RED}[!] Invalid option{Style.RESET_ALL}")

if __name__ == "__main__":
    manager = ServerManager()
    manager.show_menu()

# ============================================================================
# Wrapper Functions for Easy Importing
# ============================================================================

def start_server(background=False):
    """
    Start the X-Recon web server
    
    Args:
        background (bool): If True, start in background. If False, start in foreground.
    
    Returns:
        bool: True if server started successfully
    """
    manager = ServerManager()
    if background:
        return manager.start_background()
    else:
        return manager.start_foreground()

def stop_server():
    """Stop the running server"""
    manager = ServerManager()
    return manager.stop()

def restart_server():
    """Restart the server"""
    manager = ServerManager()
    return manager.restart()

def get_server_status():
    """Get server status as string"""
    manager = ServerManager()
    if manager.is_running():
        return f"RUNNING (PID: {manager.get_pid()})"
    else:
        return "STOPPED"

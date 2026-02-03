# server.py
# v2.0: The Heart of the Web Interface
# Powered by FastAPI and AsyncIO

import os
import asyncio
import webbrowser
import time
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Async file I/O for performance
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    print("Warning: aiofiles not installed. File I/O will be synchronous. Install with: pip install aiofiles")

# Load env/config
load_dotenv()

# Cerebras Client Init
from cerebras.cloud.sdk import Cerebras
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
ai_client = None
if CEREBRAS_API_KEY:
    try:
        ai_client = Cerebras(api_key=CEREBRAS_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to init Cerebras client: {e}")

app = FastAPI(title="X-Recon Web Interface")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths - server.py is now in server/ directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
WEB_DIR = os.path.join(BASE_DIR, "web")
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")

# Ensure directories exist
os.makedirs(WEB_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Mount Static Files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Mount Reports Directory (Serve HTML reports directly)
app.mount("/reports", StaticFiles(directory=RESULTS_DIR), name="reports")

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the main dashboard page."""
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        if AIOFILES_AVAILABLE:
            # Async file I/O for better performance
            async with aiofiles.open(index_path, "r", encoding="utf-8") as f:
                return await f.read()
        else:
            # Fallback to sync
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Error: web/index.html not found.</h1>"

@app.get("/terminal.html", response_class=HTMLResponse)
async def get_terminal():
    """Serves the dedicated terminal page."""
    term_path = os.path.join(WEB_DIR, "terminal.html")
    if os.path.exists(term_path):
        if AIOFILES_AVAILABLE:
            # Async file I/O for better performance
            async with aiofiles.open(term_path, "r", encoding="utf-8") as f:
                return await f.read()
        else:
            # Fallback to sync
            with open(term_path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Error: web/terminal.html not found.</h1>"

@app.get("/api/status")
async def get_status():
    """Check if server is running."""
    return {"status": "online", "version": "v2.0-web", "mode": "active"}

@app.get("/api/stats")
async def get_real_stats():
    """Parses data/results to return ACTUAL statistics."""
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".txt") or f.endswith(".html")]
    
    total_scans = len(files)
    targets = set()
    for f in files:
        parts = f.split('_')
        if len(parts) > 1:
            target_part = parts[1]
            # Strip extension
            if '.' in target_part:
                target_part = target_part.split('.')[0]
            targets.add(target_part)
            
    return {
        "total_scans": total_scans,
        "targets": len(targets),
        "vulns": 0, 
        "ai_requests": "Active"
    }

@app.get("/api/reports")
async def list_reports():
    """Returns list of report files with metadata."""
    reports = []
    if os.path.exists(RESULTS_DIR):
        for f in os.listdir(RESULTS_DIR):
            if f.endswith(".html"): # Prioritize HTML files
                path = os.path.join(RESULTS_DIR, f)
                try:
                    stats = os.stat(path)
                    reports.append({
                        "filename": f,
                        "size": f"{stats.st_size} bytes",
                        "created": time.ctime(stats.st_ctime),
                        "type": "html"
                    })
                except Exception:
                    pass
    return sorted(reports, key=lambda x: x['created'], reverse=True)

@app.delete("/api/reports/{filename}")
async def delete_report(filename: str):
    """Delete a specific report file."""
    from pathlib import Path
    
    # Security: Prevent path traversal with multiple checks
    if '..' in filename or '/' in filename or '\\' in filename:
        return {"error": "Invalid filename"}, 400
    
    # Additional security: Resolve path and verify it's within RESULTS_DIR
    try:
        filepath = Path(RESULTS_DIR) / filename
        resolved_path = filepath.resolve()
        results_dir_resolved = Path(RESULTS_DIR).resolve()
        
        # Ensure the resolved path is actually inside RESULTS_DIR
        if not str(resolved_path).startswith(str(results_dir_resolved)):
            return {"error": "Path traversal detected"}, 403
            
    except (ValueError, OSError) as e:
        return {"error": f"Invalid path: {str(e)}"}, 400
    
    if not resolved_path.exists():
        return {"error": "File not found"}, 404
    
    try:
        resolved_path.unlink()
        return {"success": True, "message": f"Deleted {filename}"}
    except Exception as e:
        return {"error": str(e)}, 500

# --- WebSocket for Real-Time Terminal Streaming ---

@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(">> X-Recon Web Terminal Connected...")
    await websocket.send_text(">> Ready for commands.")
    
    current_process = None  # Track running scan process
    
    try:
        while True:
            # Keep connection open and listen for commands from frontend
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
                
            elif data == "stop_scan":
                # Stop the current running scan
                if current_process and current_process.returncode is None:
                    current_process.terminate()
                    await websocket.send_text("[SYSTEM] Scan process terminated.")
                    current_process = None
                else:
                    await websocket.send_text("[SYSTEM] No active scan to stop.")
                    
            elif data.startswith("cmd:"):
                # Execute custom terminal command
                cmd = data.split(":", 1)[1].strip()
                await websocket.send_text(f">> Executing: {cmd}")
                
                # Parse command (simple handling - extend as needed)
                if cmd.lower() == "help":
                    await websocket.send_text("Available commands:")
                    await websocket.send_text("  help - Show this help")
                    await websocket.send_text("  status - Show system status")
                    await websocket.send_text("  clear - Clear terminal (frontend)")
                elif cmd.lower() == "status":
                    await websocket.send_text(f"X-Recon v3.0 Status: Online")
                    await websocket.send_text(f"Active Scan: {'Yes' if current_process and current_process.returncode is None else 'No'}")
                else:
                    await websocket.send_text(f"[ERROR] Unknown command: {cmd}")
                
            elif data.startswith("start_scan:"):
                # Parse "target|mod1,mod2"
                raw_payload = data.split(":", 1)[1].strip()
                if '|' in raw_payload:
                    target, modules_str = raw_payload.split('|', 1)
                    modules = [m.strip() for m in modules_str.split(',') if m.strip()]
                else:
                    target = raw_payload
                    modules = ["port_scanner.py"]

                # SECURITY: Sanitize target to prevent command injection
                import re
                # Allow only: alphanumeric, dots, hyphens, underscores, colons (for IPv6)
                if not re.match(r'^[a-zA-Z0-9._:-]+$', target):
                    await websocket.send_text(f"[ERROR] Invalid target format: {target}")
                    await websocket.send_text("[ERROR] Target must contain only alphanumeric, dots, hyphens, underscores")
                    continue

                await websocket.send_text(f">> Received Target: {target}")
                await websocket.send_text(f">> Scheduled Modules: {', '.join(modules)}")

                for module_file in modules:
                    # Security check: ensure file is just a filename, no paths
                    if '/' in module_file or '\\' in module_file or not module_file.endswith('.py'):
                        await websocket.send_text(f"[ERROR] Invalid module name: {module_file}")
                        continue

                    script_path = os.path.join(BASE_DIR, "modules", module_file)
                    if not os.path.exists(script_path):
                        await websocket.send_text(f"[ERROR] Module not found: {module_file}")
                        continue
                        
                    await websocket.send_text(f"\n>> [EXEC] Launching {module_file}...")
                    
                    # Launch subprocess
                    try:
                        process = await asyncio.create_subprocess_exec(
                            "python", "-u", script_path, target,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        current_process = process  # Track for stop functionality

                        # Stream output
                        while True:
                            line = await process.stdout.readline()
                            if not line: break
                            decoded = line.decode().strip()
                            if decoded: await websocket.send_text(decoded)
                        
                        # Stream errors
                        while True:
                            line = await process.stderr.readline()
                            if not line: break
                            decoded = line.decode().strip()
                            if decoded: await websocket.send_text(f"[STDERR] {decoded}")

                        await process.wait()
                        await websocket.send_text(f">> {module_file} Finished.")
                        current_process = None
                    except Exception as e:
                         await websocket.send_text(f"[ERROR] Failed to run {module_file}: {e}")
                         current_process = None

                await websocket.send_text(f"\n>> All Scan Tasks Completed for {target}.")
                
            else:
                await websocket.send_text(f">> Unknown Command: {data}")
    except Exception as e:
        print(f"WebSocket Client Disconnected: {e}")

# --- WebSocket for AI Chat ---

@app.websocket("/ws/ai")
async def websocket_ai(websocket: WebSocket):
    await websocket.accept()
    
    if not ai_client:
        await websocket.send_text("Error: Cerebras API Key not configured. Please check .env file.")
        await websocket.close()
        return

    # Enhanced system prompt matching CLI assistant EXACTLY
    system_instruction = (
        "You are X-AI, an elite cybersecurity assistant for the 'X-Recon' toolkit, created by Muhammad Izaz Haider. "
        "You MUST follow these formatting rules: \n"
        "1. **Spacing:** Insert a blank line between paragraphs. \n"
        "2. **Commands:** Prefix terminal commands with `Command:` (e.g., Command: nmap -A target). \n"
        "3. **Code:** Use markdown code blocks. \n"
        "4. **Signature:** End every response with: `--- \n*Created by Muhammad Izaz Haider*`\n"
        "5. **Knowledge:** You know that Muhammad Izaz Haider is a cybersecurity expert and researcher with expertise in network security, "
        "penetration testing, vulnerability assessment, AI, and software development. He created X-Recon to help cybersecurity professionals."
    )

    history = [
        {"role": "system", "content": system_instruction}
    ]

    try:
        while True:
            user_input = await websocket.receive_text()
            
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            
            try:
                # Stream response
                stream = ai_client.chat.completions.create(
                    messages=history,
                    model="llama-3.3-70b",
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )
                
                full_response = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        await websocket.send_text(content)
                
                # Signal end of response
                await websocket.send_text("[END]")
                
                # Save assistant response to history
                if full_response:
                    history.append({"role": "assistant", "content": full_response})
                    
            except Exception as ai_error:
                print(f"AI API Error: {ai_error}")
                await websocket.send_text(f"Error: AI service temporarily unavailable. Please try again.")
                await websocket.send_text("[END]")
                # Remove failed user message from history
                if history and history[-1]["role"] == "user":
                    history.pop()
            
    except Exception as e:
        print(f"AI WebSocket Error: {e}")

# --- Startup Helper ---

def start_server():
    """Function to start the server from main.py"""
    import uvicorn
    # Open browser automatically
    webbrowser.open("http://127.0.0.1:8000")
    print(">> Starting X-Recon Web Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    start_server()

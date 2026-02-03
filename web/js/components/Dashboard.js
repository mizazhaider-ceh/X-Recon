/**
 * X-Recon v3.0 - Dashboard Component
 * Real-time statistics and activity monitoring with persistent state
 */

import { api } from '../api.js';
import { appState } from '../state.js';

export class Dashboard {
    constructor() {
        this.statsInterval = null;
        this.ws = null;
        this.isScanning = false;
        this.wsConnected = false;
        this.pendingScanData = null;
        this.terminalLines = []; // Local cache of terminal lines
    }

    async render(container) {
        // Restore last target from state
        const lastTarget = appState.getState('lastTarget') || '';
        
        container.innerHTML = `
            <div class="page-header">
                <h2 class="page-title">COMMAND CENTER</h2>
            </div>
            
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-info">
                        <div class="stat-value" id="stat-scans">--</div>
                        <div class="stat-label">Total Scans</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-info">
                        <div class="stat-value" id="stat-targets">--</div>
                        <div class="stat-label">Targets</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-info">
                        <div class="stat-value" id="stat-vulns">--</div>
                        <div class="stat-label">Vulnerabilities</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🤖</div>
                    <div class="stat-info">
                        <div class="stat-value" id="stat-ai">--</div>
                        <div class="stat-label">AI Status</div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Scan Widget -->
            <div class="card" id="quick-scan-card" style="margin-bottom: var(--space-lg);">
                <div class="card-header" style="margin-bottom: 0; padding-bottom: 0; border-bottom: none;">
                    <h3>⚡ Quick Scan</h3>
                    <div id="scan-status" style="display: flex; align-items: center; gap: 0.5rem;">
                        <span class="status-dot" id="scan-status-dot"></span>
                        <span id="scan-status-text">Ready</span>
                    </div>
                </div>
                <div style="padding-top: 1rem;">
                    <div style="display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 250px;">
                            <label class="form-label">Target</label>
                            <input type="text" id="quick-target" class="form-input" placeholder="e.g. scanme.nmap.org" value="${lastTarget}" style="margin-bottom: 0;">
                        </div>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            <label class="quick-scan-option" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.03); border-radius: var(--radius-md); cursor: pointer;">
                                <input type="checkbox" class="quick-module" value="port_scanner.py" checked> 🚀 Ports
                            </label>
                            <label class="quick-scan-option" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.03); border-radius: var(--radius-md); cursor: pointer;">
                                <input type="checkbox" class="quick-module" value="service_detector.py" checked> 🔍 Services
                            </label>
                            <label class="quick-scan-option" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.03); border-radius: var(--radius-md); cursor: pointer;">
                                <input type="checkbox" class="quick-module" value="dns_scanner.py"> 🧠 DNS
                            </label>
                        </div>
                        <button class="btn btn-primary" id="btn-quick-scan" style="white-space: nowrap;">
                            <span id="scan-btn-icon">☠️</span>
                            <span id="scan-btn-text">LAUNCH SCAN</span>
                        </button>
                        <button class="btn btn-danger" id="btn-stop-scan" style="white-space: nowrap; display: none;">
                            <span>⏹️</span>
                            <span>STOP</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Live Terminal -->
            <div class="card">
                <div class="card-header">
                    <h3>🖥️ Live Terminal Output</h3>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm" id="btn-clear-terminal">Clear</button>
                    </div>
                </div>
                <div id="terminal-output" style="
                    background: linear-gradient(180deg, #0a0a0a 0%, #050505 100%);
                    color: #00f3ff;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
                    padding: 1.25rem;
                    height: 350px;
                    overflow-y: auto;
                    border-radius: var(--radius-md) var(--radius-md) 0 0;
                    font-size: 0.9rem;
                    line-height: 1.6;
                    border: 1px solid rgba(0, 243, 255, 0.1);
                    border-bottom: none;
                ">
                    <div class="terminal-line terminal-success">
                        <span class="terminal-prefix">▶</span>
                        <span class="terminal-time">[${new Date().toLocaleTimeString()}]</span>
                        <span>X-Recon Terminal Initialized. Ready for commands...</span>
                    </div>
                </div>
                <div style="display: flex; gap: 0; background: #0a0a0a; border: 1px solid rgba(0, 243, 255, 0.1); border-top: 1px solid rgba(0, 243, 255, 0.2); border-radius: 0 0 var(--radius-md) var(--radius-md); padding: 0.75rem;">
                    <span style="color: var(--brand-green); font-family: 'JetBrains Mono', monospace; padding: 0.5rem; font-weight: 700;">$</span>
                    <input type="text" id="terminal-input" placeholder="Enter command..." style="flex: 1; background: transparent; border: none; color: var(--text-main); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; outline: none;">
                    <button class="btn btn-sm" id="btn-send-cmd" style="background: rgba(0, 243, 255, 0.1); border: 1px solid rgba(0, 243, 255, 0.3); padding: 0.4rem 1rem;">Send</button>
                </div>
            </div>
        `;

        this.setupDashboard();
        this.restoreTerminalHistory();
        this.loadStats();
        this.checkPendingScan();
    }

    restoreTerminalHistory() {
        const history = appState.getState('terminalHistory') || [];
        const output = document.getElementById('terminal-output');
        
        if (history.length > 0 && output) {
            // Clear the initial message and restore history
            output.innerHTML = '';
            history.forEach(entry => {
                const line = document.createElement('div');
                line.className = `terminal-line terminal-${entry.type}`;
                line.innerHTML = `
                    <span class="terminal-prefix">${entry.prefix}</span>
                    <span class="terminal-time">[${entry.time}]</span>
                    <span class="terminal-msg">${this.escapeHtml(entry.message)}</span>
                `;
                output.appendChild(line);
            });
            output.scrollTop = output.scrollHeight;
            
            // Add restoration notice
            this.addTerminalLine('Session restored. Previous output preserved.', 'info', '📋', false);
        }
    }

    setupDashboard() {
        // Setup terminal WebSocket
        this.ws = api.createWebSocket('/ws/terminal', {
            onOpen: () => {
                this.wsConnected = true;
                this.addTerminalLine('Connected to X-Recon Core.', 'success', 'SYSTEM');
                appState.setState('isConnected', true);
                this.updateConnectionStatus(true);
                
                // Check for pending scan after connection is established
                if (this.pendingScanData) {
                    const { target, modules } = this.pendingScanData;
                    this.pendingScanData = null;
                    this.executeScan(target, modules);
                }
            },
            onMessage: (data) => {
                this.handleTerminalMessage(data);
            },
            onClose: () => {
                this.wsConnected = false;
                this.addTerminalLine('Connection lost. Please refresh.', 'error', 'ERROR');
                appState.setState('isConnected', false);
                this.updateConnectionStatus(false);
            }
        });

        // Clear terminal button
        const clearBtn = document.getElementById('btn-clear-terminal');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                const output = document.getElementById('terminal-output');
                if (output) {
                    output.innerHTML = `<div class="terminal-line terminal-success">
                        <span class="terminal-prefix">▶</span>
                        <span class="terminal-time">[${new Date().toLocaleTimeString()}]</span>
                        <span>Terminal cleared.</span>
                    </div>`;
                }
                // Clear persisted history
                appState.clearTerminalHistory();
            });
        }

        // Quick Scan button
        const quickScanBtn = document.getElementById('btn-quick-scan');
        if (quickScanBtn) {
            quickScanBtn.addEventListener('click', () => this.launchQuickScan());
        }

        // Stop Scan button
        const stopScanBtn = document.getElementById('btn-stop-scan');
        if (stopScanBtn) {
            stopScanBtn.addEventListener('click', () => this.stopScan());
        }

        // Enter key on target input
        const targetInput = document.getElementById('quick-target');
        if (targetInput) {
            targetInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.launchQuickScan();
            });
        }

        // Terminal input
        const terminalInput = document.getElementById('terminal-input');
        const sendCmdBtn = document.getElementById('btn-send-cmd');
        
        if (terminalInput) {
            terminalInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendTerminalCommand();
            });
        }
        
        if (sendCmdBtn) {
            sendCmdBtn.addEventListener('click', () => this.sendTerminalCommand());
        }

        // Start stats polling
        this.statsInterval = setInterval(() => this.loadStats(), 5000);
    }

    handleTerminalMessage(data) {
        // Detect message type from content
        let type = 'info';
        let prefix = 'INFO';
        
        if (data.includes('[ERROR]') || data.includes('[STDERR]')) {
            type = 'error';
            prefix = 'ERR';
        } else if (data.includes('Finished') || data.includes('Complete') || data.includes('SUCCESS')) {
            type = 'success';
            prefix = '✓';
            // Check if all scans completed
            if (data.includes('All Scan Tasks Completed')) {
                this.onScanComplete();
            }
        } else if (data.includes('[EXEC]') || data.includes('Launching')) {
            type = 'warning';
            prefix = '⚡';
        } else if (data.includes('>>')) {
            type = 'info';
            prefix = '▶';
        } else if (data.includes('OPEN') || data.includes('Found')) {
            type = 'highlight';
            prefix = '🎯';
        }
        
        this.addTerminalLine(data.replace(/^>>/g, '').trim(), type, prefix);
    }

    updateConnectionStatus(connected) {
        const dot = document.getElementById('scan-status-dot');
        const text = document.getElementById('scan-status-text');
        if (dot && text && !this.isScanning) {
            if (connected) {
                dot.className = 'status-dot online';
                text.textContent = 'Ready';
            } else {
                dot.className = 'status-dot';
                text.textContent = 'Disconnected';
            }
        }
    }

    launchQuickScan() {
        const target = document.getElementById('quick-target')?.value.trim();
        const modules = Array.from(document.querySelectorAll('.quick-module:checked')).map(cb => cb.value);

        if (!target) {
            this.showToast('Please enter a target', 'error');
            return;
        }

        if (modules.length === 0) {
            this.showToast('Please select at least one scan type', 'error');
            return;
        }

        this.executeScan(target, modules);
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-panel-solid);
            border: 1px solid var(--border-medium);
            border-left: 4px solid var(--color-${type === 'error' ? 'red' : type === 'success' ? 'green' : 'cyan'});
            padding: 1rem 1.5rem;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    addTerminalLine(message, type = 'info', prefix = '▶', persist = true) {
        const output = document.getElementById('terminal-output');
        if (!output) return;

        const line = document.createElement('div');
        line.className = `terminal-line terminal-${type}`;
        
        const timestamp = new Date().toLocaleTimeString();

        line.innerHTML = `
            <span class="terminal-prefix">${prefix}</span>
            <span class="terminal-time">[${timestamp}]</span>
            <span class="terminal-msg">${this.escapeHtml(message)}</span>
        `;
        
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;

        // Persist to state for restoration
        if (persist) {
            appState.addTerminalEntry({
                message,
                type,
                prefix,
                time: timestamp
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async loadStats() {
        try {
            const stats = await api.getStats();
            document.getElementById('stat-scans').textContent = stats.total_scans || 0;
            document.getElementById('stat-targets').textContent = stats.targets || 0;
            document.getElementById('stat-vulns').textContent = stats.vulns || 0;
            document.getElementById('stat-ai').textContent = stats.ai_requests || 'Online';
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    checkPendingScan() {
        const pendingScan = appState.getState('pendingScan');

        if (pendingScan && pendingScan.timestamp) {
            // Check if scan is recent (within last 10 seconds)
            const age = Date.now() - pendingScan.timestamp;
            if (age < 10000) {
                // Clear the pending scan from state
                appState.setState('pendingScan', null);

                // If WebSocket is connected, execute immediately
                // Otherwise, store for execution when connection opens
                if (this.wsConnected && this.ws?.readyState === WebSocket.OPEN) {
                    this.executeScan(pendingScan.target, pendingScan.modules);
                } else {
                    // Store for later execution when WS connects
                    this.pendingScanData = {
                        target: pendingScan.target,
                        modules: pendingScan.modules
                    };
                    this.addTerminalLine('Waiting for connection to start scan...', 'warning', '⏳');
                }
            }
        }
    }

    executeScan(target, modules) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addTerminalLine('Terminal not connected. Please refresh the page.', 'error', 'ERR');
            return;
        }

        if (this.isScanning) {
            this.addTerminalLine('A scan is already running. Please wait...', 'warning', '⚠️');
            return;
        }

        // Save last target for persistence
        appState.setState('lastTarget', target);

        // Update UI to scanning state
        this.isScanning = true;
        this.updateScanUI(true, target);

        this.addTerminalLine(`Initiating scan on target: ${target}`, 'warning', '🎯');
        this.addTerminalLine(`Modules: ${modules.join(', ')}`, 'info', '📦');

        // Send scan command via WebSocket
        const payload = `${target}|${modules.join(',')}`;
        this.ws.send(`start_scan:${payload}`);

        // Add to scan history
        appState.addScanEntry({
            target,
            modules,
            timestamp: Date.now(),
            status: 'running'
        });

        // Increment stats
        appState.incrementStat('totalScans');
    }

    stopScan() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addTerminalLine('Terminal not connected.', 'error', 'ERR');
            return;
        }

        if (!this.isScanning) {
            this.addTerminalLine('No scan is currently running.', 'warning', '⚠️');
            return;
        }

        this.ws.send('stop_scan');
        this.isScanning = false;
        this.updateScanUI(false);
        this.addTerminalLine('Scan stopped by user.', 'warning', '⏹️');
    }

    sendTerminalCommand() {
        const input = document.getElementById('terminal-input');
        if (!input) return;

        const command = input.value.trim();
        if (!command) return;

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addTerminalLine('Terminal not connected. Please refresh.', 'error', 'ERR');
            return;
        }

        // Display user command
        this.addTerminalLine(command, 'user', '$');
        
        // Send to server
        this.ws.send(`cmd:${command}`);
        
        // Clear input
        input.value = '';
    }

    updateScanUI(scanning, target = '') {
        const btn = document.getElementById('btn-quick-scan');
        const stopBtn = document.getElementById('btn-stop-scan');
        const btnIcon = document.getElementById('scan-btn-icon');
        const btnText = document.getElementById('scan-btn-text');
        const statusDot = document.getElementById('scan-status-dot');
        const statusText = document.getElementById('scan-status-text');

        if (scanning) {
            if (btn) btn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'inline-flex';
            if (statusDot) statusDot.className = 'status-dot scanning';
            if (statusText) statusText.textContent = `Scanning ${target}`;
        } else {
            if (btn) {
                btn.disabled = false;
                btn.style.display = 'inline-flex';
            }
            if (stopBtn) stopBtn.style.display = 'none';
            if (btnIcon) btnIcon.textContent = '☠️';
            if (btnText) btnText.textContent = 'LAUNCH SCAN';
            if (statusDot) statusDot.className = 'status-dot online';
            if (statusText) statusText.textContent = 'Ready';
        }
    }

    onScanComplete() {
        this.isScanning = false;
        this.updateScanUI(false);
        this.addTerminalLine('Scan completed successfully!', 'success', '✅');
        this.loadStats(); // Refresh stats
        this.showToast('Scan completed!', 'success');
    }

    destroy() {
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
        }
        api.closeWebSocket('/ws/terminal');
    }
}

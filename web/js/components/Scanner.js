/**
 * X-Recon v3.0 - Scanner Component
 * Scan configuration and execution
 */

import { appState } from '../state.js';

export class Scanner {
    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2 class="page-title">START SCAN</h2>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: var(--space-lg);">New Scan Objective</h3>
                
                <div class="form-group">
                    <label class="form-label">Target Domain / IP</label>
                    <input 
                        type="text" 
                        id="scan-target" 
                        class="form-input" 
                        placeholder="e.g. scanme.nmap.org"
                        autocomplete="off"
                    >
                </div>
                
                <div class="form-group">
                    <label class="form-label">Select Attack Vectors</label>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
                        ${this.renderModuleOptions()}
                    </div>
                </div>
                
                <button class="btn btn-primary" id="btn-launch-scan" style="width: 100%;">
                    <span style="font-size: 1.2rem;">☠️</span>
                    INITIATE OFFENSIVE SCAN
                </button>
            </div>
        `;

        // Event listener
        document.getElementById('btn-launch-scan').addEventListener('click', () => {
            this.launchScan();
        });
    }

    renderModuleOptions() {
        const modules = [
            { id: 'port_scanner.py', icon: '🚀', name: 'Fast Port Scan', desc: 'Async TCP connect scan (Top 100)', checked: true },
            { id: 'service_detector.py', icon: '🔍', name: 'Service Detect', desc: 'Fingerprint versions & banners', checked: true },
            { id: 'subdomain_scanner.py', icon: '🌐', name: 'Subdomain Enum', desc: 'Passive & active sub-domain discovery' },
            { id: 'dir_bruteforcer.py', icon: '📂', name: 'Dir Bruteforce', desc: 'Fuzz common web paths' },
            { id: 'email_harvester.py', icon: '📧', name: 'Email Harvester', desc: 'OSINT for public email addresses' },
            { id: 'cve_lookup.py', icon: '🛡️', name: 'CVE Lookup', desc: 'Check found services for vulns' },
            { id: 'dns_scanner.py', icon: '🧠', name: 'Whois & DNS', desc: 'Deep domain intelligence' },
            { id: 'nmap_scanner.py', icon: '🕸️', name: 'Nmap Deep Scan', desc: 'Full OS detection (Slow)' }
        ];

        return modules.map(mod => `
            <label style="
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border-subtle);
                padding: 1rem;
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: all var(--transition-base);
                display: block;
            " class="module-option">
                <input 
                    type="checkbox" 
                    class="module-checkbox"
                    value="${mod.id}" 
                    ${mod.checked ? 'checked' : ''}
                    style="margin-right: 0.5rem;"
                >
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">
                        ${mod.icon} ${mod.name}
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        ${mod.desc}
                    </div>
                </div>
            </label>
        `).join('');
    }

    launchScan() {
        const target = document.getElementById('scan-target').value.trim();
        const selectedModules = Array.from(
            document.querySelectorAll('.module-checkbox:checked')
        ).map(cb => cb.value);

        if (!target) {
            this.showToast('Please enter a target', 'error');
            return;
        }

        if (selectedModules.length === 0) {
            this.showToast('Please select at least one module', 'error');
            return;
        }

        // Save scan configuration to state
        appState.setState('pendingScan', {
            target,
            modules: selectedModules,
            timestamp: Date.now()
        });

        // Navigate to Dashboard
        window.location.hash = '#dashboard';

        this.showToast('Launching scan in Dashboard terminal...', 'success');
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

    destroy() {
        // Cleanup if needed
    }
}

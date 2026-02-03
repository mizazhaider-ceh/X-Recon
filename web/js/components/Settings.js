/**
 * X-Recon v3.0 - Settings Component
 * Application configuration and theme management
 */

import { appState } from '../state.js';

export class Settings {
    async render(container) {
        const currentTheme = appState.getState('theme');

        container.innerHTML = `
            <div class="page-header">
                <h2 class="page-title">SETTINGS</h2>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: var(--space-lg);">System Configuration</h3>
                
                <div class="form-group">
                    <label class="form-label">AI Model</label>
                    <select id="setting-model" class="form-select">
                        <option>Cerebras Llama-3.3-70b (Fastest)</option>
                        <option disabled>OpenAI GPT-4 (Coming Soon)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Theme</label>
                    <select id="setting-theme" class="form-select">
                        <option value="cyberpunk" ${currentTheme === 'cyberpunk' ? 'selected' : ''}>
                            Cyberpunk Neon (Default)
                        </option>
                        <option value="dark" ${currentTheme === 'dark' ? 'selected' : ''}>
                            Stealth Dark
                        </option>
                        <option value="green" ${currentTheme === 'green' ? 'selected' : ''}>
                            Matrix Green
                        </option>
                    </select>
                </div>
                
                <div style="padding: 1rem; border-top: 1px solid var(--border-subtle); margin-top: 2rem; color: var(--text-muted); text-align: center;">
                    X-Recon v3.0 // Licensed to OPERATOR
                </div>
            </div>
        `;

        // Event listeners
        document.getElementById('setting-theme').addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        document.getElementById('setting-model').addEventListener('change', (e) => {
            localStorage.setItem('xrecon_model', e.target.value);
            this.showToast('AI Model preference saved', 'success');
        });
    }

    changeTheme(theme) {
        // Remove all theme classes
        document.body.classList.remove('theme-green', 'theme-dark');

        // Apply new theme
        if (theme === 'green') {
            document.body.classList.add('theme-green');
        } else if (theme === 'dark') {
            document.body.classList.add('theme-dark');
        }

        // Save to state and localStorage
        appState.setState('theme', theme);
        localStorage.setItem('xrecon_theme', theme);

        this.showToast(`Theme changed to ${theme}`, 'success');
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
        `;

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    destroy() {
        // Cleanup if needed
    }
}

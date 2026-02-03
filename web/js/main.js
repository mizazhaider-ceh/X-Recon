/**
 * X-Recon v3.0 - Main Application
 * Application bootstrap and initialization
 */

import { router } from './router.js';
import { appState } from './state.js';
import { Dashboard } from './components/Dashboard.js';
import { Scanner } from './components/Scanner.js';
import { Reports } from './components/Reports.js';
import { AIChat } from './components/AIChat.js';
import { Settings } from './components/Settings.js';

class App {
    constructor() {
        this.components = {
            dashboard: new Dashboard(),
            scanner: new Scanner(),
            reports: new Reports(),
            ai: new AIChat(),
            settings: new Settings()
        };
    }

    async init() {
        console.log('🚀 X-Recon v3.0 Initializing...');

        // Apply saved theme
        this.applyTheme();

        // Register routes
        router.register('dashboard', this.components.dashboard);
        router.register('scanner', this.components.scanner);
        router.register('reports', this.components.reports);
        router.register('ai', this.components.ai);
        router.register('settings', this.components.settings);

        // Set router container
        const container = document.getElementById('app-content');
        router.setContainer(container);

        // Setup navigation
        this.setupNavigation();

        // Subscribe to connection state
        appState.subscribe('isConnected', (connected) => {
            this.updateConnectionStatus(connected);
        });

        console.log('✅ X-Recon v3.0 Ready');
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = link.dataset.route;
                if (route) {
                    router.navigate(route);
                }
            });
        });
    }

    applyTheme() {
        const theme = appState.getState('theme');
        document.body.classList.remove('theme-green', 'theme-dark');

        if (theme === 'green') {
            document.body.classList.add('theme-green');
        } else if (theme === 'dark') {
            document.body.classList.add('theme-dark');
        }
    }

    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-indicator span:last-child');

        if (statusDot) {
            if (connected) {
                statusDot.classList.add('online');
                if (statusText) statusText.textContent = 'System Online';
            } else {
                statusDot.classList.remove('online');
                if (statusText) statusText.textContent = 'System Offline';
            }
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});

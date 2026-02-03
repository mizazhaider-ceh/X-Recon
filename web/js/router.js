/**
 * X-Recon v3.0 - SPA Router
 * Hash-based routing for single-page navigation
 */

import { appState } from './state.js';

class Router {
    constructor() {
        this.routes = new Map();
        this.currentComponent = null;
        this.container = null;

        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    /**
     * Register a route
     * @param {string} path - Route path (e.g., 'dashboard')
     * @param {Object} component - Component with render() method
     */
    register(path, component) {
        this.routes.set(path, component);
    }

    /**
     * Set the container element for rendering
     * @param {HTMLElement} element - Container element
     */
    setContainer(element) {
        this.container = element;
    }

    /**
     * Navigate to a route
     * @param {string} path - Route path
     */
    navigate(path) {
        window.location.hash = path;
    }

    /**
     * Handle route changes
     * @private
     */
    async handleRoute() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        const component = this.routes.get(hash);

        if (!component) {
            console.error(`Route not found: ${hash}`);
            this.navigate('dashboard');
            return;
        }

        // Update active nav link
        this.updateActiveNav(hash);

        // Update state
        appState.setState('currentView', hash);

        // Cleanup previous component
        if (this.currentComponent?.destroy) {
            this.currentComponent.destroy();
        }

        // Render new component
        this.currentComponent = component;

        if (this.container) {
            this.container.innerHTML = '';
            await component.render(this.container);
        }
    }

    /**
     * Update active navigation link
     * @private
     */
    updateActiveNav(path) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.route === path) {
                link.classList.add('active');
            }
        });
    }
}

// Export singleton instance
export const router = new Router();

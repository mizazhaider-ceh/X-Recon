/**
 * X-Recon v3.0 - API Client
 * Clean abstraction for backend communication
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.wsConnections = new Map();
    }

    /**
     * Generic HTTP request handler
     * @private
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // === API Endpoints ===

    /**
     * Fetch dashboard statistics
     */
    async getStats() {
        return this.get('/api/stats');
    }

    /**
     * Fetch all reports
     */
    async getReports() {
        return this.get('/api/reports');
    }

    /**
     * Delete a report
     * @param {string} filename - Report filename
     */
    async deleteReport(filename) {
        return this.delete(`/api/reports/${filename}`);
    }

    /**
     * Create WebSocket connection
     * @param {string} endpoint - WebSocket endpoint
     * @param {Object} handlers - Event handlers
     * @returns {WebSocket}
     */
    createWebSocket(endpoint, handlers = {}) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsURL = `${protocol}//${window.location.host}${endpoint}`;

        const ws = new WebSocket(wsURL);

        ws.onopen = (event) => {
            console.log(`WebSocket connected: ${endpoint}`);
            handlers.onOpen?.(event);
        };

        ws.onmessage = (event) => {
            handlers.onMessage?.(event.data);
        };

        ws.onerror = (error) => {
            console.error(`WebSocket error [${endpoint}]:`, error);
            handlers.onError?.(error);
        };

        ws.onclose = (event) => {
            console.log(`WebSocket closed: ${endpoint}`);
            handlers.onClose?.(event);
        };

        this.wsConnections.set(endpoint, ws);
        return ws;
    }

    /**
     * Close WebSocket connection
     * @param {string} endpoint - WebSocket endpoint
     */
    closeWebSocket(endpoint) {
        const ws = this.wsConnections.get(endpoint);
        if (ws) {
            ws.close();
            this.wsConnections.delete(endpoint);
        }
    }

    /**
     * Close all WebSocket connections
     */
    closeAllWebSockets() {
        this.wsConnections.forEach(ws => ws.close());
        this.wsConnections.clear();
    }
}

// Export singleton instance
export const api = new APIClient();

/**
 * X-Recon v3.0 - State Management
 * Centralized application state with observer pattern and persistence
 */

const STORAGE_KEY = 'xrecon_state';
const PERSISTENT_KEYS = ['stats', 'terminalHistory', 'scanHistory', 'lastTarget', 'chatHistory'];

class AppState {
    constructor() {
        // Load persisted state from localStorage
        const savedState = this.loadPersistedState();
        
        this.state = {
            currentView: 'dashboard',
            theme: localStorage.getItem('xrecon_theme') || 'cyberpunk',
            stats: savedState.stats || {
                totalScans: 0,
                targets: 0,
                vulns: 0,
                aiRequests: 0
            },
            reports: [],
            isConnected: false,
            isLoading: false,
            // Persistent state
            terminalHistory: savedState.terminalHistory || [],
            scanHistory: savedState.scanHistory || [],
            lastTarget: savedState.lastTarget || '',
            dashboardState: savedState.dashboardState || null,
            chatHistory: savedState.chatHistory || []
        };

        this.observers = new Map();
        
        // Debug: log loaded state
        console.log('[State] Loaded persisted state:', Object.keys(savedState));
    }

    /**
     * Load persisted state from localStorage
     * @returns {Object} Persisted state object
     */
    loadPersistedState() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.warn('[State] Failed to load persisted state:', e);
            return {};
        }
    }

    /**
     * Save current state to localStorage
     */
    persistState() {
        try {
            const toPersist = {};
            PERSISTENT_KEYS.forEach(key => {
                if (this.state[key] !== undefined) {
                    toPersist[key] = this.state[key];
                }
            });
            // Also persist dashboard state
            if (this.state.dashboardState) {
                toPersist.dashboardState = this.state.dashboardState;
            }
            localStorage.setItem(STORAGE_KEY, JSON.stringify(toPersist));
        } catch (e) {
            console.warn('[State] Failed to persist state:', e);
        }
    }

    /**
     * Subscribe to state changes
     * @param {string} key - State key to watch
     * @param {Function} callback - Function to call on change
     * @returns {Function} Unsubscribe function
     */
    subscribe(key, callback) {
        if (!this.observers.has(key)) {
            this.observers.set(key, new Set());
        }
        this.observers.get(key).add(callback);

        // Return unsubscribe function
        return () => {
            this.observers.get(key).delete(callback);
        };
    }

    /**
     * Update state and notify observers
     * @param {string} key - State key to update
     * @param {*} value - New value
     * @param {boolean} persist - Whether to persist this change
     */
    setState(key, value, persist = true) {
        const oldValue = this.state[key];
        this.state[key] = value;

        // Persist if this is a persistent key
        if (persist && PERSISTENT_KEYS.includes(key)) {
            this.persistState();
        }

        // Notify observers
        if (this.observers.has(key)) {
            this.observers.get(key).forEach(callback => {
                callback(value, oldValue);
            });
        }
    }

    /**
     * Get current state value
     * @param {string} key - State key
     * @returns {*} State value
     */
    getState(key) {
        return this.state[key];
    }

    /**
     * Add to terminal history (with limit)
     * @param {Object} entry - Terminal entry {type, content, timestamp}
     */
    addTerminalEntry(entry) {
        const history = [...this.state.terminalHistory, entry];
        // Keep last 100 entries
        if (history.length > 100) {
            history.shift();
        }
        this.setState('terminalHistory', history);
    }

    /**
     * Add to scan history
     * @param {Object} scan - Scan entry {target, type, timestamp, status}
     */
    addScanEntry(scan) {
        const history = [...this.state.scanHistory, scan];
        // Keep last 50 scans
        if (history.length > 50) {
            history.shift();
        }
        this.setState('scanHistory', history);
    }

    /**
     * Clear terminal history
     */
    clearTerminalHistory() {
        this.setState('terminalHistory', []);
    }

    /**
     * Update nested state (e.g., stats.totalScans)
     * @param {string} path - Dot-notation path
     * @param {*} value - New value
     */
    setNestedState(path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((obj, key) => obj[key], this.state);

        target[lastKey] = value;

        // Persist if parent is a persistent key
        if (PERSISTENT_KEYS.includes(keys[0])) {
            this.persistState();
        }

        // Notify observers of parent object
        const parentKey = keys[0];
        if (this.observers.has(parentKey)) {
            this.observers.get(parentKey).forEach(callback => {
                callback(this.state[parentKey]);
            });
        }
    }

    /**
     * Increment a stat counter
     * @param {string} statKey - Stat key (totalScans, targets, vulns, aiRequests)
     */
    incrementStat(statKey) {
        if (this.state.stats[statKey] !== undefined) {
            this.state.stats[statKey]++;
            this.persistState();
            
            if (this.observers.has('stats')) {
                this.observers.get('stats').forEach(callback => {
                    callback(this.state.stats);
                });
            }
        }
    }
}

// Export singleton instance
export const appState = new AppState();

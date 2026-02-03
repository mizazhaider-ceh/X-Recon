/**
 * X-Recon v3.0 - Reports Component
 * Report management with delete/download features
 */

import { api } from '../api.js';
import { appState } from '../state.js';

export class Reports {
    constructor() {
        this.allReports = [];
    }

    async render(container) {
        container.innerHTML = `
            <div class="page-header">
                <h2 class="page-title">MISSION REPORTS</h2>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        <input 
                            type="text" 
                            id="report-search" 
                            class="form-input" 
                            placeholder="Search reports..."
                            style="width: 300px; margin-bottom: 0;"
                        >
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm" id="btn-refresh">
                            🔄 Refresh
                        </button>
                        <button class="btn btn-danger btn-sm" id="btn-clear-all">
                            🗑️ Clear All
                        </button>
                    </div>
                </div>
                
                <div id="reports-container" class="reports-grid">
                    <div class="loading-spinner"></div>
                </div>
            </div>
        `;

        // Load reports
        await this.loadReports();

        // Event listeners
        document.getElementById('report-search').addEventListener('input', (e) => {
            this.filterReports(e.target.value);
        });

        document.getElementById('btn-refresh').addEventListener('click', () => {
            this.loadReports();
        });

        document.getElementById('btn-clear-all').addEventListener('click', () => {
            this.clearAllReports();
        });
    }

    async loadReports() {
        try {
            this.allReports = await api.getReports();
            appState.setState('reports', this.allReports);
            this.renderReports(this.allReports);
        } catch (error) {
            console.error('Failed to load reports:', error);
            document.getElementById('reports-container').innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: var(--color-red); padding: 2rem;">
                    Failed to load reports. Please try again.
                </div>
            `;
        }
    }

    renderReports(reports) {
        const container = document.getElementById('reports-container');

        if (reports.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem;">
                    No reports found. Run a scan to generate data.
                </div>
            `;
            return;
        }

        container.innerHTML = reports.map(report => {
            const icon = report.filename.endsWith('.html') ? '🌐' :
                report.filename.endsWith('.json') ? '📊' : '📄';

            return `
                <div class="report-card">
                    <div class="report-icon">${icon}</div>
                    <div class="report-name">${report.filename}</div>
                    <div class="report-meta">
                        <span>${report.size}</span>
                        <span>${new Date(report.created).toLocaleDateString()}</span>
                    </div>
                    <div class="report-actions">
                        <button 
                            class="btn btn-primary btn-sm" 
                            onclick="window.open('/reports/${report.filename}', '_blank')"
                            style="flex: 1;"
                        >
                            📖 Open
                        </button>
                        <button 
                            class="btn btn-danger btn-sm" 
                            data-filename="${report.filename}"
                            style="flex: 1;"
                        >
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        // Add delete listeners
        container.querySelectorAll('.btn-danger').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Use currentTarget to ensure we get the button element with the dataset
                const button = e.currentTarget;
                const filename = button.dataset.filename;
                if (filename) {
                    this.deleteReport(filename);
                } else {
                    console.error('Delete button missing filename data attribute');
                }
            });
        });
    }

    filterReports(searchTerm) {
        const filtered = this.allReports.filter(report =>
            report.filename.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderReports(filtered);
    }

    async deleteReport(filename) {
        if (!confirm(`Delete report: ${filename}?`)) {
            return;
        }

        try {
            await api.deleteReport(filename);
            this.allReports = this.allReports.filter(r => r.filename !== filename);
            this.renderReports(this.allReports);
            this.showToast('Report deleted successfully', 'success');
        } catch (error) {
            console.error('Failed to delete report:', error);
            this.showToast('Failed to delete report', 'error');
        }
    }

    async clearAllReports() {
        if (!confirm('Delete ALL reports? This cannot be undone!')) {
            return;
        }

        try {
            for (const report of this.allReports) {
                await api.deleteReport(report.filename);
            }
            this.allReports = [];
            this.renderReports([]);
            this.showToast('All reports cleared', 'success');
        } catch (error) {
            console.error('Failed to clear reports:', error);
            this.showToast('Failed to clear all reports', 'error');
        }
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

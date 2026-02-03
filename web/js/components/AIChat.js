/**
 * X-Recon v3.0 - AI Chat Component (Simplified)
 * Clean, minimal chat interface
 * Created by Muhammad Izaz Haider
 */

import { api } from '../api.js';
import { appState } from '../state.js';

export class AIChat {
    constructor() {
        this.ws = null;
        this.isTyping = false;
        this.chatHistory = [];
    }

    async render(container) {
        // Load fresh history
        this.chatHistory = appState.getState('chatHistory') || [];
        const savedModel = localStorage.getItem('xrecon_ai_model') || 'llama-3.3-70b';
        
        container.innerHTML = `
            <div class="ai-chat-simple">
                <div class="chat-header-bar">
                    <div class="chat-title">
                        <span class="chat-icon">🤖</span>
                        <span>X-AI Assistant</span>
                        <span id="connection-badge" class="connection-badge offline">Connecting...</span>
                    </div>
                    <div class="chat-options">
                        <select id="model-select" class="model-select" title="AI Model">
                            <option value="llama-3.3-70b" ${savedModel === 'llama-3.3-70b' ? 'selected' : ''}>🧠 Llama 70B</option>
                            <option value="llama3.1-8b" ${savedModel === 'llama3.1-8b' ? 'selected' : ''}>⚡ Llama 8B</option>
                        </select>
                        <button id="btn-export" class="btn-option" title="Export Chat">📥</button>
                        <button id="btn-clear" class="btn-option btn-danger" title="Clear Chat">🗑️</button>
                    </div>
                </div>
                
                <div id="chat-messages" class="chat-body">
                    ${this.chatHistory.length > 0 ? this.renderHistory() : this.getWelcome()}
                </div>
                
                <div id="typing-bar" class="typing-bar" style="display:none;">
                    <span>🤖</span>
                    <span class="dots"><i></i><i></i><i></i></span>
                    <span>X-AI is thinking...</span>
                </div>
                
                <div class="chat-footer">
                    <input type="text" id="chat-input" placeholder="Ask about security, commands, vulnerabilities..." autocomplete="off">
                    <button id="btn-send" class="btn-send" title="Send message">➤</button>
                </div>
            </div>
        `;

        this.setupEvents();
        this.connectWS();
        this.scrollDown();
    }

    getWelcome() {
        return `
            <div class="welcome-msg">
                <div class="welcome-icon">🤖</div>
                <h3>Hi! I'm <span class="hl-name">X-AI</span></h3>
                <p>Your elite cybersecurity assistant by <span class="hl-creator">Muhammad Izaz Haider</span></p>
                <div class="quick-asks">
                    <button class="quick-btn" data-q="How do I scan ports with nmap?">🔍 Port Scanning</button>
                    <button class="quick-btn" data-q="Explain SQL injection">💉 SQL Injection</button>
                    <button class="quick-btn" data-q="How to find subdomains?">🌐 Subdomain Enum</button>
                    <button class="quick-btn" data-q="What is XSS attack?">⚡ XSS Attacks</button>
                </div>
            </div>
        `;
    }

    renderHistory() {
        return this.chatHistory.map(m => this.msgHTML(m.sender, m.text)).join('');
    }

    msgHTML(sender, text) {
        const isUser = sender === 'user';
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        return `
            <div class="msg ${isUser ? 'msg-user' : 'msg-ai'}">
                <div class="msg-avatar">${isUser ? '👤' : '🤖'}</div>
                <div class="msg-content">
                    <div class="msg-bubble">${isUser ? this.esc(text) : this.formatAI(text)}</div>
                    <div class="msg-time">${time}</div>
                </div>
            </div>
        `;
    }

    esc(t) {
        const d = document.createElement('div');
        d.textContent = t;
        return d.innerHTML;
    }

    formatAI(text) {
        let html = this.esc(text);
        
        // Code blocks with syntax highlighting
        html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, code) => {
            const highlighted = this.highlightCode(code, lang || 'bash');
            return `<div class="code-wrapper"><div class="code-lang">${lang || 'code'}</div><pre class="code-block">${highlighted}</pre></div>`;
        });
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        
        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Commands - special highlight
        html = html.replace(/Command:\s*(.+)/g, '<div class="cmd-box"><span class="cmd-prefix">$</span> <span class="cmd-text">$1</span></div>');
        
        // Highlight important names
        html = html.replace(/(Muhammad Izaz Haider)/gi, '<span class="hl-creator">$1</span>');
        html = html.replace(/(X-AI|X-Recon)/gi, '<span class="hl-name">$1</span>');
        
        // Highlight security terms
        html = html.replace(/\b(nmap|nikto|dirb|gobuster|hydra|sqlmap|burp|metasploit|wireshark)\b/gi, '<span class="hl-tool">$1</span>');
        html = html.replace(/\b(CVE-\d{4}-\d+)\b/gi, '<span class="hl-cve">$1</span>');
        html = html.replace(/\b(critical|high|medium|low)\s+(severity|risk|vulnerability)?\b/gi, '<span class="hl-severity hl-$1">$1 $2</span>');
        
        // URLs
        html = html.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" class="hl-link">$1</a>');
        
        // Numbered lists
        html = html.replace(/^(\d+\.\s)/gm, '<span class="list-num">$1</span>');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        // Signature
        html = html.replace(/---\s*<br>\s*\*?Created by/gi, '<div class="ai-signature">— Created by');
        
        return html;
    }
    
    highlightCode(code, lang) {
        let html = code;
        
        // Keywords
        const keywords = ['if', 'else', 'for', 'while', 'return', 'function', 'def', 'class', 'import', 'from', 'try', 'except', 'catch', 'const', 'let', 'var', 'async', 'await', 'sudo', 'echo', 'cat', 'grep', 'awk', 'sed'];
        keywords.forEach(kw => {
            html = html.replace(new RegExp(`\\b(${kw})\\b`, 'g'), '<span class="syn-keyword">$1</span>');
        });
        
        // Strings
        html = html.replace(/(["'])(?:(?!\1)[^\\]|\\.)*\1/g, '<span class="syn-string">$&</span>');
        
        // Comments
        html = html.replace(/(#.*?)(<br>|$)/g, '<span class="syn-comment">$1</span>$2');
        html = html.replace(/(\/\/.*?)(<br>|$)/g, '<span class="syn-comment">$1</span>$2');
        
        // Flags (like -A, --version)
        html = html.replace(/\s(-{1,2}[a-zA-Z][a-zA-Z0-9-]*)/g, ' <span class="syn-flag">$1</span>');
        
        // Numbers
        html = html.replace(/\b(\d+\.?\d*)\b/g, '<span class="syn-number">$1</span>');
        
        // IPs
        html = html.replace(/\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b/g, '<span class="syn-ip">$1</span>');
        
        return html;
    }

    setupEvents() {
        document.getElementById('btn-send')?.addEventListener('click', () => this.send());
        document.getElementById('chat-input')?.addEventListener('keydown', e => {
            if (e.key === 'Enter') this.send();
        });
        document.getElementById('btn-clear')?.addEventListener('click', () => this.clearChat());
        
        // Model selector
        document.getElementById('model-select')?.addEventListener('change', e => {
            localStorage.setItem('xrecon_ai_model', e.target.value);
        });
        
        // Export chat
        document.getElementById('btn-export')?.addEventListener('click', () => this.exportChat());
        
        // Quick ask buttons
        this.setupQuickBtns();
    }
    
    setupQuickBtns() {
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const q = btn.dataset.q;
                if (q) {
                    document.getElementById('chat-input').value = q;
                    this.send();
                }
            });
        });
    }
    
    exportChat() {
        if (this.chatHistory.length === 0) return;
        
        let text = '=== X-Recon AI Chat Export ===\n';
        text += `Date: ${new Date().toLocaleString()}\n\n`;
        
        this.chatHistory.forEach(m => {
            const sender = m.sender === 'user' ? 'You' : 'X-AI';
            text += `[${sender}]\n${m.text}\n\n`;
        });
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `xrecon-chat-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    connectWS() {
        this.ws = api.createWebSocket('/ws/ai', {
            onOpen: () => this.setStatus(true),
            onMessage: (data) => this.handleMessage(data),
            onClose: () => this.setStatus(false),
            onError: () => this.setStatus(false)
        });
    }

    setStatus(online) {
        const badge = document.getElementById('connection-badge');
        if (badge) {
            badge.className = 'connection-badge ' + (online ? 'online' : 'offline');
            badge.textContent = online ? 'Online' : 'Offline';
        }
    }

    send() {
        const input = document.getElementById('chat-input');
        const text = input?.value.trim();
        if (!text || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        // Add user message
        this.addMsg('user', text);
        this.chatHistory.push({sender: 'user', text});
        this.save();

        // Send
        this.ws.send(text);
        this.showTyping(true);
        input.value = '';
    }

    handleMessage(data) {
        if (data === '[END]') {
            this.showTyping(false);
            this.finalizeAI();
            this.save();
            return;
        }
        this.appendAI(data);
    }

    addMsg(sender, text) {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        // Remove welcome if present
        const welcome = container.querySelector('.welcome-msg');
        if (welcome) welcome.remove();
        
        container.insertAdjacentHTML('beforeend', this.msgHTML(sender, text));
        this.scrollDown();
    }

    appendAI(chunk) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        let lastAI = container.querySelector('.msg-ai:last-child:not(.complete)');
        if (!lastAI) {
            // Create new AI message
            container.insertAdjacentHTML('beforeend', `
                <div class="msg msg-ai" data-raw="">
                    <div class="msg-avatar">🤖</div>
                    <div class="msg-content">
                        <div class="msg-bubble"></div>
                        <div class="msg-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                    </div>
                </div>
            `);
            lastAI = container.querySelector('.msg-ai:last-child');
            this.chatHistory.push({sender: 'ai', text: ''});
        }

        const raw = (lastAI.dataset.raw || '') + chunk;
        lastAI.dataset.raw = raw;
        lastAI.querySelector('.msg-bubble').innerHTML = this.formatAI(raw);
        
        // Update history
        if (this.chatHistory.length > 0) {
            this.chatHistory[this.chatHistory.length - 1].text = raw;
        }
        
        this.scrollDown();
    }

    finalizeAI() {
        const container = document.getElementById('chat-messages');
        const lastAI = container?.querySelector('.msg-ai:last-child');
        if (lastAI) lastAI.classList.add('complete');
    }

    showTyping(show) {
        const el = document.getElementById('typing-bar');
        if (el) el.style.display = show ? 'flex' : 'none';
        this.isTyping = show;
    }

    scrollDown() {
        const el = document.getElementById('chat-messages');
        if (el) el.scrollTop = el.scrollHeight;
    }

    save() {
        // Keep last 30 messages
        if (this.chatHistory.length > 30) {
            this.chatHistory = this.chatHistory.slice(-30);
        }
        appState.setState('chatHistory', this.chatHistory);
    }

    clearChat() {
        this.chatHistory = [];
        appState.setState('chatHistory', []);
        const container = document.getElementById('chat-messages');
        if (container) container.innerHTML = this.getWelcome();
    }

    destroy() {
        api.closeWebSocket('/ws/ai');
        this.ws = null;
    }
}

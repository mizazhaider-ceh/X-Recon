# 🔥 X-Recon v3.0

<div align="center">

![X-Recon Banner](https://img.shields.io/badge/X--Recon-v3.0-00f3ff?style=for-the-badge&logo=hackaday&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI-Cerebras%20Llama-ff6b6b?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=4000&pause=1000&color=00F3FF&center=true&vCenter=true&width=600&lines=Elite+Cybersecurity+Reconnaissance;CLI+%2B+AI+%2B+Web+Dashboard;Built+by+a+Security+Engineer;For+Pentesters+%26+Bug+Hunters" alt="Typing SVG" />

### **🛡️ Elite Cybersecurity Reconnaissance Toolkit**

*Professional-grade security reconnaissance with AI-powered analysis and modern web interface*

**Created with ❤️ by [Muhammad Izaz Haider](https://linkedin.com/in/muhammad-izaz-haider-091639314)**

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📸 Screenshots](#-screenshots) • [🔧 Installation](#-installation) • [👤 About Me](#-the-story-behind-x-recon)

---

![Stars](https://img.shields.io/github/stars/mizazhaider-ceh/X-Recon?style=social)
![Forks](https://img.shields.io/github/forks/mizazhaider-ceh/X-Recon?style=social)
![Issues](https://img.shields.io/github/issues/mizazhaider-ceh/X-Recon)

</div>

---

## 🎯 What is X-Recon?

**X-Recon** is an all-in-one cybersecurity reconnaissance toolkit designed for security professionals, penetration testers, and bug bounty hunters. It combines powerful scanning modules with an AI assistant and a sleek cyberpunk-themed web interface.

<table>
<tr>
<td>

### 🔥 The Evolution

```
v1.0 → CLI Tools Only
v2.0 → CLI + AI Integration  
v3.0 → CLI + AI + Web Dashboard ← You are here!
```

</td>
<td>

### 💡 Why X-Recon?

- 🚀 **All-in-One** - No switching between tools
- 🤖 **AI-Powered** - Smart analysis & suggestions
- 🌐 **Web Interface** - Modern, real-time dashboard
- ⚡ **Async** - Blazing fast scans

</td>
</tr>
</table>

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mizazhaider-ceh/X-Recon.git
cd X-Recon

# Install dependencies
pip install -r requirements.txt

# Set up AI (optional but recommended)
echo "CEREBRAS_API_KEY=your_api_key" > .env

# Launch X-Recon
python main.py
```

> 💡 Select **Option 1** → Opens web dashboard at `http://127.0.0.1:8000`

<details>
<summary><b>⚡ One-Liner for Windows</b></summary>

```batch
git clone https://github.com/mizazhaider-ceh/X-Recon.git && cd X-Recon && pip install -r requirements.txt && python main.py
```

</details>

---

## 📁 Project Structure

```
X-Recon/
├── main.py                 # Main entry point
├── server/                 # Backend server files
│   ├── server.py          # FastAPI web server
│   ├── server_manager.py  # Server lifecycle management
│   └── config.py          # Configuration
├── modules/               # Scan modules
│   ├── port_scanner.py
│   ├── subdomain_scanner.py
│   ├── dir_bruteforcer.py
│   ├── email_harvester.py
│   ├── ai_assistant.py
│   └── ...
├── web/                   # Frontend files
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── components/
│       ├── api.js
│       ├── router.js
│       └── state.js
├── results/               # Scan reports (HTML)
└── wordlists/            # Fuzzing wordlists
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🌐 Web Dashboard
- **Real-time Terminal** - Live scan output via WebSocket
- **Scan Controls** - Start, stop, monitor scans
- **Command Input** - Enter terminal commands directly
- **Session Persistence** - Preserves history on refresh
- **Responsive Design** - Works on all devices

</td>
<td width="50%">

### 🤖 AI Assistant (X-AI)
- **Powered by Cerebras** - Llama 3.3 70B model
- **Context-Aware** - Knows X-Recon toolkit
- **Syntax Highlighting** - Beautiful code blocks
- **Quick Actions** - One-click common queries
- **Export Chats** - Download conversations

</td>
</tr>
</table>

### 🔍 Reconnaissance Modules

| Module | Description | Speed |
|--------|-------------|-------|
| 🚀 **Port Scanner** | Async TCP port scanning | ⚡ 1000+ ports/sec |
| 🌐 **Subdomain Scanner** | DNS enumeration | ⚡ 500 concurrent |
| 📁 **Directory Bruteforcer** | Web path fuzzing | ⚡ 200 concurrent |
| 📧 **Email Harvester** | OSINT email collection | 🔍 Multi-source |
| 🔎 **Service Detector** | Banner grabbing | 🎯 Smart detection |
| 🛡️ **CVE Lookup** | Vulnerability search | 📊 NVD database |
| 🧬 **DNS Scanner** | WHOIS & DNS intel | 📋 Full records |
| 🔧 **Nmap Integration** | Advanced OS detection | 🔬 Deep scan |

---

## 📸 Screenshots

<details>
<summary><b>🖥️ Dashboard - Command Center</b></summary>

- Quick scan with module selection
- Real-time terminal output
- Interactive command input
- Live stats and status

</details>

<details>
<summary><b>🎯 Scanner - Multi-Module</b></summary>

- Target configuration
- Module selection with descriptions
- One-click scan launch
- Real-time progress tracking

</details>

<details>
<summary><b>🤖 AI Assistant - X-AI</b></summary>

- Cybersecurity Q&A
- Code syntax highlighting
- Keyword emphasis (CVEs, tools)
- Export conversations

</details>

<details>
<summary><b>📊 Reports - Professional Output</b></summary>

- HTML report viewer
- Download & delete options
- Sortable by date/type
- Interactive report content

</details>

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- (Optional) Nmap for advanced scanning

### Step-by-Step

```bash
# 1. Clone repository
git clone https://github.com/mizazhaider-ceh/X-Recon.git
cd X-Recon

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AI (optional but recommended)
cp .env.example .env
# Edit .env and add your Cerebras API key

# 5. Launch
python main.py
```

### 🤖 Get Cerebras API Key (Free!)
1. Go to https://cloud.cerebras.ai/
2. Sign up for free account
3. Generate API key
4. Add to `.env` file

> 💡 **Why Cerebras?** Llama 3.3 70B at lightning speed — perfect for security analysis!

---

## 🎯 Usage

### Web Interface (Recommended)
1. Run `python main.py`
2. Select **Option 1** - Launch Web Dashboard
3. Navigate to `http://127.0.0.1:8000`
4. Go to **Scanner** tab
5. Enter target and select modules
6. Click **INITIATE OFFENSIVE SCAN**
7. View real-time output in Dashboard terminal
8. Check **Reports** tab for HTML results

### CLI Mode
```bash
python main.py
# Select Option 2 for CLI scan
# Select Option 3 for AI Assistant
```

---

## 📊 Report Format

All scan results are saved as **HTML reports** in the `results/` directory:

- **Interactive** - Click to expand sections
- **Professional** - Clean, modern design
- **Comprehensive** - All findings with timestamps
- **Shareable** - Self-contained HTML files

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file:
```env
CEREBRAS_API_KEY=your_api_key_here
```

Get your API key from: https://cloud.cerebras.ai/

### Server Settings
Edit `server/config.py`:
```python
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
RESULTS_DIR = "results"
```

---

## 🛡️ Security Best Practices

✅ **Legal Use Only** - Only scan targets you own or have permission to test  
✅ **Rate Limiting** - Respect target servers  
✅ **Stealth Mode** - Use low-noise scanning when needed  
✅ **Responsible Disclosure** - Report vulnerabilities ethically  

---

## 🔧 Development

### Adding New Modules
1. Create `modules/your_module.py`
2. Follow the template structure
3. Add to Scanner component in `web/js/components/Scanner.js`
4. Module will auto-integrate with web dashboard

### Tech Stack
- **Backend**: Python 3.8+, FastAPI, WebSockets
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **AI**: Cerebras Cloud SDK
- **Architecture**: SPA with hash routing

---

## 📝 Changelog

### v3.0 (Current - February 2026)
- ✅ Complete web dashboard overhaul
- ✅ Real-time terminal with WebSocket streaming
- ✅ Scan start/stop controls
- ✅ Terminal command input
- ✅ AI assistant with syntax highlighting
- ✅ Model selection (Llama 70B/8B)
- ✅ Chat export functionality
- ✅ Quick action buttons
- ✅ Keyword highlighting (CVEs, tools, names)
- ✅ CSS modular architecture (14 files)
- ✅ Session persistence
- ✅ Professional HTML reports
- ✅ Fixed subdomain/directory scanner bugs

### v2.0
- CLI-based scanning
- Basic HTML reports
- AI integration

### v1.0
- Initial release
- Core scanning modules

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 The Story Behind X-Recon

<div align="center">

### 🚀 From a Pakistani Village to European Cybersecurity

</div>

> *"As a cybersecurity engineer, I thought: first build CLI tools, then add AI integration, then a web interface. CLI + AI + Web GUI. It took me a lot of time, but now it's done."*

**X-Recon** started as a personal project to solve a real problem: **too many scattered tools, no unified workflow**. As a penetration tester, I was tired of switching between terminals, scripts, and tools. I wanted everything in one place.

### 📍 The Journey

| Phase | What I Built | Why |
|-------|-------------|-----|
| **v1.0** | CLI scanning modules | Learn by building |
| **v2.0** | Added AI assistant | Smart analysis needed |
| **v3.0** | Full web dashboard | Professional workflow |

### 💡 Philosophy

```
✅ Building over collecting certificates
✅ Practice over theory
✅ Real tools over endless tutorials
✅ If I fail, the failure is mine. If I succeed, the credit belongs to Allah.
```

---

## 👤 Author

<div align="center">

<img src="https://github.com/mizazhaider-ceh.png" width="150" style="border-radius: 50%;" alt="Muhammad Izaz Haider"/>

### **Muhammad Izaz Haider**

**Junior DevSecOps & AI Security Engineer** @ Damno Solutions  
**Penetration Tester** | **Cybersecurity Student** @ Howest University 🇧🇪  
**AI Security Researcher** | **Founder** @ The PenTrix  

---

🇵🇰 → 🇧🇪 *From a small Pakistani village to Belgium's cybersecurity field*

*Built on self-learning, persistence, and faith — Alhamdulillah* 🤲

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Muhammad%20Izaz%20Haider-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/muhammad-izaz-haider-091639314/)
[![GitHub](https://img.shields.io/badge/GitHub-mizazhaider--ceh-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mizazhaider-ceh)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit%20Now-FF6B6B?style=for-the-badge&logo=google-chrome&logoColor=white)](https://mizazhaider-ceh.github.io/My-Portfolio/)
[![Email](https://img.shields.io/badge/Email-Contact%20Me-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mizazhaiderceh@gmail.com)

</div>

### 🏆 Recognition & Achievements

- 🌟 **"The Next-Gen Technologist from Pakistan"** — PakSphere
- 🌟 **"Rising Star"** — Ek Pakistan  
- 📺 **Featured on ABN News** — National television appearance
- 🎓 **16.40/20 CGPA** — First semester at Howest University
- 🔐 **Found 13 vulnerabilities** — Including critical RCE & SQLi fixes

### 💼 What I Do

- 🔐 Hardening CI/CD pipelines & Kubernetes containers
- 🤖 Building LLM-powered vulnerability scanners
- 🛡️ Penetration testing & security audits
- 🌍 Securing multi-region cloud infrastructure

---

## 🤝 Want to Build Together?

<div align="center">

**Got ideas? Found a bug? Want to contribute?**

I'm always open to collaboration! Whether you want to:
- 🐛 Report issues
- 💡 Suggest features  
- 🔧 Submit pull requests
- 💬 Just chat about cybersecurity

**Reach out on [LinkedIn](https://www.linkedin.com/in/muhammad-izaz-haider-091639314/) — Let's build the future of security together!**

</div>

---

## 🙏 Acknowledgments

- **Allah Almighty** — Every achievement is by His grace 🤲
- **Cerebras** — Lightning-fast AI inference
- **FastAPI** — Modern Python web framework
- **The Security Community** — Inspiration & feedback
- **My Family** — Unwavering support from Pakistan to Belgium

---

<div align="center">

### ⭐ Star this repo if you find it useful!

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=24&duration=3000&pause=1000&color=00FF9D&center=true&vCenter=true&width=500&lines=X-Recon+v3.0;Reconnaissance+Redefined;Built+with+%E2%9D%A4%EF%B8%8F+in+Belgium" alt="Footer" />

**Made with ❤️ by Muhammad Izaz Haider**

*"Don't wait for opportunities; build them."*

---

![Visitors](https://api.visitorbadge.io/api/visitors?path=mizazhaider-ceh%2FX-Recon&label=Visitors&countColor=%2300f3ff)

</div>

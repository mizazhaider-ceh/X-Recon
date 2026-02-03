# X-Recon: Champion Recon Toolkit 🚀

**X-Recon** is a comprehensive, modular reconnaissance and vulnerability assessment toolkit designed for security professionals and bug bounty hunters. It combines powerful passive and active reconnaissance techniques with an AI-powered assistant to streamline the intelligence-gathering phase of penetration testing.

## 🌟 Key Features

X-Recon features a professional command-line interface (CLI) with 10 specialized modules:

### Phase 1: Passive & Active Reconnaissance
1.  **Domain Intelligence (`dns_scanner.py`)**
    *   Retrieves common DNS records (A, AAAA, MX, TXT, NS, SOA).
    *   Performs detailed WHOIS lookups.
    *   **Smart Feature**: Auto-locates wordlists for subdomain scanning.
2.  **Subdomain Scanner (`subdomain_scanner.py`)**
    *   High-speed, multi-threaded subdomain discovery.
    *   Configurable thread speeds (Normal, Fast, Insane).
3.  **Email Harvester (`email_harvester.py`)**
    *   **Dual-Stage engine**: First gathers URLs from search engines (DuckDuckGo), then scrapes them for emails.
    *   Uses rotating user-agents to avoid blocking.
4.  **Async Port Scanner (`port_scanner.py`)** [v1.1]
    *   **Powered by AsyncIO**: Extremely fast, non-blocking TCP connect scanner.
    *   Capable of scanning thousands of ports in seconds.
5.  **Advanced Nmap Scanner (`nmap_scanner.py`)**
    *   Wrapper for the powerful Nmap engine.
    *   Supports Simple, Intense, UDP, and Vulnerability scans.
    *   *Requires Nmap installed on the system.*
6.  **Service Version Detector (`service_detector.py`)**
    *   Performs usage banner grabbing to identify service versions running on open ports.
7.  **Web Directory Scanner (`dir_bruteforcer.py`)**
    *   Multi-threaded brute-forcer to find hidden directories and files.
    *   Status code coloring and intelligent error handling.
8.  **Multi-CVE Lookup (`cve_lookup.py`)**
    *   Searches the Vulners database for vulnerabilities matching specific software versions.
    *   Features multi-threaded searching for bulk queries.
9.  **Password List Generator (`password_generator.py`)** [v1.1]
    *   **Memory Optimized**: Uses generators to create massive wordlists without crashing RAM.
    *   Creates custom wordlists based on user inputs (keywords, years, special chars).

### Phase 2: AI & Utilities
10. **AI Cyber-Assistant (`ai_assistant.py`)**
    *   **Powered by Cerebras AI**: Uses the lightning-fast **Llama 3.3 70B** and **Llama 3.1 8B** models.
    *   **Interactive Chat**: Context-aware chatbot for cybersecurity queries.
    *   **Model Selection**: Choose between speed (8B) and intelligence (70B) at runtime.
    *   Renders responses with professional markdown and code highlighting in the terminal.

## 🛠️ Prerequisites

*   **Python 3.8+**
*   **Nmap**: Required for the Nmap Scanner module.
    *   [Download Nmap here](https://nmap.org/download.html) and ensure it is in your system's PATH.

## 📦 Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/mizazhaider-ceh/X-Recon.git
    cd X-Recon
    ```

2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

To use the **AI Cyber-Assistant**, you need a Cerebras API Key.

1.  Get a free API key from [Cerebras Cloud](https://cloud.cerebras.ai/).
2.  Open `config.py` in the root directory.
3.  Paste your API key into the variable:
    ```python
    CEREBRAS_API_KEY = "YOUR_CEREBRAS_API_KEY_HERE"
    ```

## 🚀 Usage

Run the main command center to access all tools:

```bash
python main.py
```

Navigate the menu by entering the number corresponding to the tool you wish to use. Follow the on-screen prompts for each module.

## ⚠️ Disclaimer

**X-Recon is for educational and authorized testing purposes only.**
Do not use this toolkit on any system or network without explicit permission from the owner. The creator and contributors are not responsible for any illegal misuse of this tool.

## 👨‍💻 Credits

Created by **Muhammad Izaz Haider**
*   Certified Ethical Hacker (CEH)
*   **GitHub**: [mizazhaider-ceh](https://github.com/mizazhaider-ceh)

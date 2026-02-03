
#!/bin/bash

# Reconic - Hunt. Detect. Exploit.
# Author: Inayat Hussain (Security Researcher)

GREEN="\033[1;32m"
RED="\033[1;31m"
RESET="\033[0m"

TOOLS=(subfinder httpx gau nuclei qsreplace)

banner() {
    echo -e "${GREEN}"
    echo "    ____                          _     "
    echo "   |  _ \ ___  ___ ___  _ __ ___| |__  "
    echo "   | |_) / _ \/ __/ _ \| '__/ __| '_ \ "
    echo "   |  _ <  __/ (_| (_) | | | (__| | | |"
    echo "   |_| \_\___|\___\___/|_|  \___|_| |_|"
    echo "       Reconic - Hunt. Detect. Exploit."
    echo -e "${RESET}"
}

install_requirements() {
    echo -e "${GREEN}[*] Checking and installing required tools...${RESET}"

    if ! command -v go >/dev/null 2>&1; then
        echo -e "${RED}[!] Go is not installed. Trying to install...${RESET}"
        sudo apt update && sudo apt install golang -y
        export PATH=$PATH:/usr/local/go/bin
    fi

    for tool in "${TOOLS[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo -e "${RED}[-] $tool not found. Installing...${RESET}"
            go install github.com/projectdiscovery/$tool/cmd/$tool@latest
            export PATH=$PATH:$(go env GOPATH)/bin
        else
            echo -e "${GREEN}[+] $tool is already installed.${RESET}"
        fi
    done

    if ! command -v jq >/dev/null 2>&1; then
        echo -e "${RED}[-] jq not found. Installing...${RESET}"
        sudo apt update && sudo apt install jq -y
    fi
}

# Main Script Start
if [ -z "$1" ]; then
    echo -e "${RED}[!] Usage: $0 <domain.com or targets.txt>${RESET}"
    exit 1
fi

banner
install_requirements

INPUT=$1
DATE=$(date +"%Y-%m-%d_%H-%M")
OUTPUT_DIR="reconic_output_$DATE"
mkdir -p "$OUTPUT_DIR"

domains=()

if [[ -f "$INPUT" ]]; then
    mapfile -t domains < "$INPUT"
else
    domains+=("$INPUT")
fi

for domain in "${domains[@]}"; do
    echo -e "${GREEN}[+] Starting recon for $domain${RESET}"

    SUBS_FILE="$OUTPUT_DIR/${domain}_subs.txt"
    LIVE_FILE="$OUTPUT_DIR/${domain}_live.txt"
    URLS_FILE="$OUTPUT_DIR/${domain}_urls.txt"
    PARAMS_FILE="$OUTPUT_DIR/${domain}_params.txt"
    VULNS_FILE="$OUTPUT_DIR/${domain}_vulns.txt"

    echo -e "${GREEN}[*] Enumerating subdomains...${RESET}"
    subfinder -d "$domain" -silent | tee "$SUBS_FILE"

    echo -e "${GREEN}[*] Probing for live hosts...${RESET}"
    httpx -silent -l "$SUBS_FILE" | tee "$LIVE_FILE"
    LIVE_COUNT=$(wc -l < "$LIVE_FILE")
    echo -e "${GREEN}[i] Found $LIVE_COUNT live hosts.${RESET}"

    echo -e "${GREEN}[*] Gathering URLs from gau...${RESET}"
    cat "$LIVE_FILE" | gau --threads 5 | tee "$URLS_FILE"

    echo -e "${GREEN}[*] Extracting endpoints with parameters...${RESET}"
    cat "$URLS_FILE" | grep "=" | qsreplace -a | sort -u | tee "$PARAMS_FILE"
    PARAM_COUNT=$(wc -l < "$PARAMS_FILE")
    echo -e "${GREEN}[i] Found $PARAM_COUNT parameterized URLs.${RESET}"

    echo -e "${GREEN}[*] Running nuclei scan (this may take a while)...${RESET}"
    nuclei -l "$LIVE_FILE" -severity low,medium,high,critical | tee "$VULNS_FILE"

    echo -e "${GREEN}[✔] Done with $domain. Output stored in $OUTPUT_DIR${RESET}"
    echo
done

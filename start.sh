#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  willAI session start script
#  Works on: Amazon Linux 2/2023, Ubuntu
#  Run with: bash start.sh
# ─────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYAN}[setup]${NC} $1"; }
ok()   { echo -e "${GREEN}[done]${NC}  $1"; }
warn() { echo -e "${YELLOW}[skip]${NC}  $1"; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  willAI — AWS Session Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Detect distro ─────────────────────────────────────────────────────────────
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi
log "Detected OS: $DISTRO"

# ── 1. OS upgrade ─────────────────────────────────────────────────────────────
log "Upgrading OS packages..."
case "$DISTRO" in
    amzn)
        sudo yum update -y -q
        ok "yum packages upgraded"
        ;;
    ubuntu|debian)
        sudo apt-get update -qq
        sudo apt-get upgrade -y -qq
        sudo apt-get autoremove -y -qq
        ok "apt packages upgraded"
        ;;
    *)
        warn "Unknown distro ($DISTRO) — skipping OS upgrade"
        ;;
esac

# ── 2. Install base dependencies if missing ───────────────────────────────────
log "Ensuring base dependencies (git, curl, unzip)..."
case "$DISTRO" in
    amzn)
        sudo yum install -y -q git curl unzip tar
        ;;
    ubuntu|debian)
        sudo apt-get install -y -qq git curl unzip tar build-essential
        ;;
esac
ok "base dependencies ready"

# ── 3. Python ─────────────────────────────────────────────────────────────────
log "Setting up Python..."
if ! command -v python3 &>/dev/null; then
    case "$DISTRO" in
        amzn)   sudo yum install -y -q python3 python3-pip ;;
        ubuntu) sudo apt-get install -y -qq python3 python3-pip python3-venv ;;
    esac
fi
python3 -m pip install --upgrade pip setuptools wheel --quiet
ok "Python ready  ($(python3 --version))"

# ── 4. Common research packages ───────────────────────────────────────────────
log "Upgrading research packages..."
pip3 install --upgrade \
    numpy scipy matplotlib pandas \
    scikit-learn \
    anthropic \
    --quiet
ok "research packages up to date"

# ── 5. Node.js ────────────────────────────────────────────────────────────────
log "Setting up Node.js..."
if ! command -v node &>/dev/null; then
    log "Installing Node.js via nvm..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install --lts --silent
    nvm use --lts --silent
else
    # Make sure nvm is loaded if it exists
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi
ok "Node ready  ($(node --version))"

# ── 6. Claude Code CLI ────────────────────────────────────────────────────────
log "Installing/upgrading Claude Code CLI..."
npm install -g @anthropic-ai/claude-code@latest --silent
ok "Claude Code ready  ($(claude --version 2>/dev/null || echo 'restart shell to activate'))"

# ── 7. Summary ───────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Versions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
command -v python3 &>/dev/null && echo "  python : $(python3 --version 2>&1)"
command -v pip3    &>/dev/null && echo "  pip    : $(pip3 --version 2>&1 | cut -d' ' -f1-2)"
command -v node    &>/dev/null && echo "  node   : $(node --version)"
command -v npm     &>/dev/null && echo "  npm    : $(npm --version)"
command -v claude  &>/dev/null && echo "  claude : $(claude --version 2>/dev/null)"
echo ""
echo "  Ready. Good luck today."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

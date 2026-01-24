#!/usr/bin/env bash
#
# Agentic Developer - Dependency Installation Script (Unix/macOS/Linux)
# Generated for Run: {{RUN_ID}}
# Generated at: {{TIMESTAMP}}
#
# This script installs missing development dependencies.
# Run with: chmod +x install-dependencies.sh && ./install-dependencies.sh
#
# Requirements:
# - macOS 10.15+ or Linux (Ubuntu 20.04+, Fedora 35+, Arch)
# - Bash 4.0 or later
# - sudo access (for some installations)

set -e

# ============================================================
# Configuration
# ============================================================

# {{TOOLS_ARRAY}}
# Example format - replace with actual detected requirements:
# TOOLS=(
#   "nodejs:Node.js:node:brew:nodejs:apt:nodejs:dnf:nodejs:pacman:nodejs"
#   "python:Python:python3:brew:python@3.11:apt:python3:dnf:python3:pacman:python"
#   "git:Git:git:brew:git:apt:git:dnf:git:pacman:git"
#   "docker:Docker:docker:brew:docker:apt:docker.io:dnf:docker:pacman:docker"
# )
# Format: "name:display_name:check_cmd:brew_pkg:apt_pkg:dnf_pkg:pacman_pkg"

TOOLS=()

DRY_RUN=false
VERBOSE=false

# ============================================================
# Color Output
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info() {
    echo -e "${CYAN}[*]${NC} $1"
}

success() {
    echo -e "${GREEN}[+]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
}

# ============================================================
# Platform Detection
# ============================================================

detect_platform() {
    local os=""
    local pkg_manager=""
    
    case "$(uname -s)" in
        Darwin*)
            os="macos"
            if command -v brew &> /dev/null; then
                pkg_manager="brew"
            fi
            ;;
        Linux*)
            os="linux"
            if command -v apt-get &> /dev/null; then
                pkg_manager="apt"
            elif command -v dnf &> /dev/null; then
                pkg_manager="dnf"
            elif command -v yum &> /dev/null; then
                pkg_manager="yum"
            elif command -v pacman &> /dev/null; then
                pkg_manager="pacman"
            elif command -v zypper &> /dev/null; then
                pkg_manager="zypper"
            fi
            ;;
        *)
            os="unknown"
            ;;
    esac
    
    echo "$os:$pkg_manager"
}

# ============================================================
# Package Manager Installation
# ============================================================

install_homebrew() {
    info "Installing Homebrew..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would install Homebrew"
        return 0
    fi
    
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add to PATH for this session
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    success "Homebrew installed"
}

# ============================================================
# Package Installation Functions
# ============================================================

install_with_brew() {
    local package="$1"
    local display_name="$2"
    
    info "Installing $display_name via Homebrew..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would run: brew install $package"
        return 0
    fi
    
    if brew install "$package"; then
        success "$display_name installed successfully"
        return 0
    else
        error "Failed to install $display_name"
        return 1
    fi
}

install_with_apt() {
    local package="$1"
    local display_name="$2"
    
    info "Installing $display_name via apt..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would run: sudo apt-get install -y $package"
        return 0
    fi
    
    if sudo apt-get install -y "$package"; then
        success "$display_name installed successfully"
        return 0
    else
        error "Failed to install $display_name"
        return 1
    fi
}

install_with_dnf() {
    local package="$1"
    local display_name="$2"
    
    info "Installing $display_name via dnf..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would run: sudo dnf install -y $package"
        return 0
    fi
    
    if sudo dnf install -y "$package"; then
        success "$display_name installed successfully"
        return 0
    else
        error "Failed to install $display_name"
        return 1
    fi
}

install_with_pacman() {
    local package="$1"
    local display_name="$2"
    
    info "Installing $display_name via pacman..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would run: sudo pacman -S --noconfirm $package"
        return 0
    fi
    
    if sudo pacman -S --noconfirm "$package"; then
        success "$display_name installed successfully"
        return 0
    else
        error "Failed to install $display_name"
        return 1
    fi
}

# ============================================================
# Tool Installation Router
# ============================================================

install_tool() {
    local tool_spec="$1"
    local pkg_manager="$2"
    
    # Parse tool specification
    IFS=':' read -r name display_name check_cmd brew_pkg apt_pkg dnf_pkg pacman_pkg <<< "$tool_spec"
    
    local package=""
    
    case "$pkg_manager" in
        brew)
            package="$brew_pkg"
            install_with_brew "$package" "$display_name"
            ;;
        apt)
            package="$apt_pkg"
            install_with_apt "$package" "$display_name"
            ;;
        dnf|yum)
            package="$dnf_pkg"
            install_with_dnf "$package" "$display_name"
            ;;
        pacman)
            package="$pacman_pkg"
            install_with_pacman "$package" "$display_name"
            ;;
        *)
            error "Unknown package manager: $pkg_manager"
            return 1
            ;;
    esac
}

# ============================================================
# Special Installers
# ============================================================

install_nvm_node() {
    info "Installing Node.js via nvm..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would install nvm and Node.js LTS"
        return 0
    fi
    
    # Install nvm
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    # Install latest LTS
    nvm install --lts
    nvm use --lts
    
    success "Node.js installed via nvm"
}

install_rustup() {
    info "Installing Rust via rustup..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would install rustup"
        return 0
    fi
    
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    
    success "Rust installed via rustup"
}

install_docker_linux() {
    info "Installing Docker..."
    
    if $DRY_RUN; then
        info "[DRY RUN] Would install Docker"
        return 0
    fi
    
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    
    success "Docker installed (logout/login required for group membership)"
}

# ============================================================
# Main Installation Logic
# ============================================================

main() {
    echo ""
    echo "========================================"
    echo "  Agentic Developer - Dependency Setup "
    echo "========================================"
    echo ""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if $DRY_RUN; then
        warning "Running in DRY RUN mode - no changes will be made"
        echo ""
    fi
    
    # Detect platform
    local platform_info
    platform_info=$(detect_platform)
    IFS=':' read -r os pkg_manager <<< "$platform_info"
    
    info "Detected OS: $os"
    
    if [[ -z "$pkg_manager" ]]; then
        if [[ "$os" == "macos" ]]; then
            warning "No package manager found. Installing Homebrew..."
            install_homebrew
            pkg_manager="brew"
        else
            error "No supported package manager found. Please install one of: apt, dnf, pacman"
            exit 1
        fi
    fi
    
    info "Using package manager: $pkg_manager"
    echo ""
    
    # Update package manager
    if ! $DRY_RUN; then
        info "Updating package manager..."
        case "$pkg_manager" in
            brew)
                brew update
                ;;
            apt)
                sudo apt-get update
                ;;
            dnf)
                sudo dnf check-update || true
                ;;
            pacman)
                sudo pacman -Sy
                ;;
        esac
    fi
    
    # Install each tool
    local success_count=0
    local fail_count=0
    
    for tool in "${TOOLS[@]}"; do
        echo "---"
        
        if install_tool "$tool" "$pkg_manager"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
    done
    
    # Summary
    echo ""
    echo "========================================"
    echo "  Installation Summary"
    echo "========================================"
    success "Successful: $success_count"
    
    if [[ $fail_count -gt 0 ]]; then
        error "Failed: $fail_count"
    fi
    
    echo ""
    warning "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    echo ""
}

# ============================================================
# Verification Section
# ============================================================

verify_installations() {
    echo ""
    echo "========================================"
    echo "  Verifying Installations"
    echo "========================================"
    echo ""
    
    local verify_commands=(
        "git:git --version"
        "node:node --version"
        "npm:npm --version"
        "python:python3 --version"
        "docker:docker --version"
        "go:go version"
        "rustc:rustc --version"
        "java:java -version"
    )
    
    for entry in "${verify_commands[@]}"; do
        IFS=':' read -r name cmd <<< "$entry"
        
        if output=$(eval "$cmd" 2>&1); then
            success "$name: $output"
        else
            error "$name: Not found or not in PATH"
        fi
    done
}

# Run main installation
main "$@"

# Verify if not dry run
if ! $DRY_RUN; then
    verify_installations
fi

echo ""
info "Done. Re-run dependency check to verify all tools are installed."

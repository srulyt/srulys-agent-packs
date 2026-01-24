# Agentic Developer - Dependency Installation Script (Windows)
# Generated for Run: {{RUN_ID}}
# Generated at: {{TIMESTAMP}}
#
# This script installs missing development dependencies.
# Run with: .\install-dependencies.ps1
#
# Requirements:
# - Windows 10/11
# - PowerShell 5.1 or later
# - Administrator privileges (for some installations)

#Requires -Version 5.1

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# ============================================================
# Configuration
# ============================================================

$tools = @(
    # {{TOOLS_ARRAY}}
    # Example entries - replace with actual detected requirements:
    # @{ Name = "nodejs"; DisplayName = "Node.js"; WingetId = "OpenJS.NodeJS.LTS"; ChocoId = "nodejs-lts"; Required = $true }
    # @{ Name = "python"; DisplayName = "Python"; WingetId = "Python.Python.3.11"; ChocoId = "python311"; Required = $true }
    # @{ Name = "git"; DisplayName = "Git"; WingetId = "Git.Git"; ChocoId = "git"; Required = $true }
    # @{ Name = "docker"; DisplayName = "Docker Desktop"; WingetId = "Docker.DockerDesktop"; ChocoId = "docker-desktop"; Required = $false }
)

# ============================================================
# Helper Functions
# ============================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    $colors = @{
        "Info" = "Cyan"
        "Success" = "Green"
        "Warning" = "Yellow"
        "Error" = "Red"
    }
    
    $prefix = switch ($Type) {
        "Info" { "[*]" }
        "Success" { "[+]" }
        "Warning" { "[!]" }
        "Error" { "[-]" }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $colors[$Type]
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Command {
    param([string]$Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

function Get-PackageManager {
    if (Test-Command "winget") {
        return "winget"
    }
    elseif (Test-Command "choco") {
        return "chocolatey"
    }
    else {
        return $null
    }
}

function Install-Winget {
    Write-Status "Installing winget (Windows Package Manager)..." "Info"
    
    # winget is included in Windows 11 and recent Windows 10
    # For older systems, install via Microsoft Store or manual download
    
    $installerUrl = "https://aka.ms/getwinget"
    $installerPath = "$env:TEMP\Microsoft.DesktopAppInstaller.msixbundle"
    
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        Add-AppxPackage -Path $installerPath
        Write-Status "winget installed successfully" "Success"
        return $true
    }
    catch {
        Write-Status "Failed to install winget: $_" "Error"
        return $false
    }
}

function Install-Chocolatey {
    Write-Status "Installing Chocolatey..." "Info"
    
    if (-not (Test-Administrator)) {
        Write-Status "Chocolatey installation requires administrator privileges" "Error"
        return $false
    }
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Status "Chocolatey installed successfully" "Success"
        return $true
    }
    catch {
        Write-Status "Failed to install Chocolatey: $_" "Error"
        return $false
    }
}

function Install-WithWinget {
    param([string]$PackageId, [string]$DisplayName)
    
    Write-Status "Installing $DisplayName via winget..." "Info"
    
    if ($DryRun) {
        Write-Status "[DRY RUN] Would run: winget install --id $PackageId --accept-package-agreements --accept-source-agreements" "Info"
        return $true
    }
    
    try {
        $result = winget install --id $PackageId --accept-package-agreements --accept-source-agreements --silent
        if ($LASTEXITCODE -eq 0) {
            Write-Status "$DisplayName installed successfully" "Success"
            return $true
        }
        else {
            Write-Status "Failed to install $DisplayName (exit code: $LASTEXITCODE)" "Error"
            return $false
        }
    }
    catch {
        Write-Status "Error installing $DisplayName : $_" "Error"
        return $false
    }
}

function Install-WithChocolatey {
    param([string]$PackageId, [string]$DisplayName)
    
    Write-Status "Installing $DisplayName via Chocolatey..." "Info"
    
    if ($DryRun) {
        Write-Status "[DRY RUN] Would run: choco install $PackageId -y" "Info"
        return $true
    }
    
    try {
        choco install $PackageId -y
        if ($LASTEXITCODE -eq 0) {
            Write-Status "$DisplayName installed successfully" "Success"
            return $true
        }
        else {
            Write-Status "Failed to install $DisplayName" "Error"
            return $false
        }
    }
    catch {
        Write-Status "Error installing $DisplayName : $_" "Error"
        return $false
    }
}

# ============================================================
# Main Installation Logic
# ============================================================

function Main {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Agentic Developer - Dependency Setup " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($DryRun) {
        Write-Status "Running in DRY RUN mode - no changes will be made" "Warning"
        Write-Host ""
    }
    
    # Check for admin privileges
    if (Test-Administrator) {
        Write-Status "Running with administrator privileges" "Info"
    }
    else {
        Write-Status "Running without administrator privileges - some installations may fail" "Warning"
    }
    
    # Detect package manager
    $packageManager = Get-PackageManager
    
    if (-not $packageManager) {
        Write-Status "No package manager found. Attempting to install winget..." "Warning"
        
        if (Install-Winget) {
            $packageManager = "winget"
        }
        elseif (Test-Administrator) {
            Write-Status "Falling back to Chocolatey..." "Warning"
            if (Install-Chocolatey) {
                $packageManager = "chocolatey"
            }
        }
        
        if (-not $packageManager) {
            Write-Status "Could not install a package manager. Please install winget or Chocolatey manually." "Error"
            exit 1
        }
    }
    
    Write-Status "Using package manager: $packageManager" "Info"
    Write-Host ""
    
    # Install each tool
    $successCount = 0
    $failCount = 0
    
    foreach ($tool in $tools) {
        Write-Host "---" -ForegroundColor DarkGray
        
        $packageId = if ($packageManager -eq "winget") { $tool.WingetId } else { $tool.ChocoId }
        
        if (-not $packageId) {
            Write-Status "No package ID for $($tool.DisplayName) with $packageManager" "Warning"
            continue
        }
        
        $success = if ($packageManager -eq "winget") {
            Install-WithWinget -PackageId $packageId -DisplayName $tool.DisplayName
        }
        else {
            Install-WithChocolatey -PackageId $packageId -DisplayName $tool.DisplayName
        }
        
        if ($success) {
            $successCount++
        }
        else {
            $failCount++
        }
    }
    
    # Summary
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Installation Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Status "Successful: $successCount" "Success"
    
    if ($failCount -gt 0) {
        Write-Status "Failed: $failCount" "Error"
    }
    
    Write-Host ""
    Write-Status "Please restart your terminal to ensure PATH is updated." "Warning"
    Write-Host ""
}

# ============================================================
# Verification Section
# ============================================================

function Verify-Installations {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Verifying Installations" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $verifyCommands = @{
        "git" = "git --version"
        "node" = "node --version"
        "npm" = "npm --version"
        "python" = "python --version"
        "docker" = "docker --version"
        "dotnet" = "dotnet --version"
        "go" = "go version"
        "rustc" = "rustc --version"
        "java" = "java -version"
    }
    
    foreach ($tool in $tools) {
        $cmd = $verifyCommands[$tool.Name]
        if ($cmd) {
            try {
                $output = Invoke-Expression $cmd 2>&1
                Write-Status "$($tool.DisplayName): $output" "Success"
            }
            catch {
                Write-Status "$($tool.DisplayName): Not found or not in PATH" "Error"
            }
        }
    }
}

# Run main installation
Main

# Verify if not dry run
if (-not $DryRun) {
    Verify-Installations
}

Write-Host ""
Write-Status "Done. Re-run dependency check to verify all tools are installed." "Info"

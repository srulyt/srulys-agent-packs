@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Agent Factory Installer
:: Usage: init.cmd [roo|copilot|both]
:: Default: both
:: ============================================

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=both"

:: Validate argument
if /i "%ACTION%"=="roo" goto :valid
if /i "%ACTION%"=="copilot" goto :valid
if /i "%ACTION%"=="both" goto :valid
echo Usage: init.cmd [roo^|copilot^|both]
echo   roo     - Install the Roo Agent Factory ^(.roo/ and .roomodes^)
echo   copilot - Install the Copilot Factory ^(.github/^)
echo   both    - Install both ^(default^)
exit /b 1
:valid

set "ROOT=%~dp0"

:: ============================================
:: Install Roo Agent Factory
:: ============================================
if /i "%ACTION%"=="roo" goto :install_roo
if /i "%ACTION%"=="both" goto :install_roo
goto :check_copilot

:install_roo
echo Installing Roo Agent Factory...

if not exist "%ROOT%agent-packs\roo-agent-factory\.roomodes" (
    echo ERROR: agent-packs\roo-agent-factory not found.
    exit /b 1
)

:: Copy .roo directory
xcopy "%ROOT%agent-packs\roo-agent-factory\.roo" "%ROOT%.roo" /E /I /Y /Q >nul
if errorlevel 1 (
    echo ERROR: Failed to copy .roo directory.
    exit /b 1
)

:: Copy .roomodes file
copy /Y "%ROOT%agent-packs\roo-agent-factory\.roomodes" "%ROOT%.roomodes" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy .roomodes file.
    exit /b 1
)

echo   [OK] .roo/ directory installed
echo   [OK] .roomodes file installed

:check_copilot
:: ============================================
:: Install Copilot Factory
:: ============================================
if /i "%ACTION%"=="copilot" goto :install_copilot
if /i "%ACTION%"=="both" goto :install_copilot
goto :done

:install_copilot
echo Installing Copilot Factory...

if not exist "%ROOT%agent-packs\copilot-factory\.github" (
    echo ERROR: agent-packs\copilot-factory not found.
    exit /b 1
)

:: Copy all .github subdirectories dynamically
for /d %%D in ("%ROOT%agent-packs\copilot-factory\.github\*") do (
    xcopy "%%D" "%ROOT%.github\%%~nxD" /E /I /Y /Q >nul
    if errorlevel 1 (
        echo   [WARN] Failed to copy .github/%%~nxD/
    ) else (
        echo   [OK] .github/%%~nxD/ installed
    )
)

:: NOTE: agent-packs\eval-framework is DEPRECATED. Its @eval-judge agent is
:: superseded by the eval-pilot plugin's bundled judge (shipped as evalpilot
:: package data), which the evals/ harness stages automatically. We no longer
:: install the eval-framework agent into .github\agents.
if exist "%ROOT%agent-packs\eval-framework\.github\agents" (
    echo   [SKIP] eval-framework is deprecated; use the eval-pilot plugin ^(agent-packs\eval-pilot^) instead
)

:done
echo.
echo Factory installation complete!
if /i "%ACTION%"=="roo" echo   Roo Agent Factory is ready. Open in VS Code with Roo Code.
if /i "%ACTION%"=="copilot" echo   Copilot Factory is ready. Use with GitHub Copilot CLI.
if /i "%ACTION%"=="both" (
    echo   Roo Agent Factory is ready. Open in VS Code with Roo Code.
    echo   Copilot Factory is ready. Use with GitHub Copilot CLI.
)

endlocal

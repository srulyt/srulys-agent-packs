@echo off
setlocal

set "ROOT=%~dp0"
set "SOURCE=%ROOT%agent-packs\agent-factory\skills\agent-factory"
set "DESTINATION=%ROOT%.github\skills\agent-factory"

if not "%~1"=="" (
    echo Usage: init.cmd
    echo Installs the skill-first Agent Factory for Copilot in this checkout.
    exit /b 1
)

if not exist "%SOURCE%\SKILL.md" (
    echo ERROR: agent-packs\agent-factory\skills\agent-factory not found.
    exit /b 1
)

if not exist "%DESTINATION%\" (
    mkdir "%DESTINATION%"
    if errorlevel 1 (
        echo ERROR: Failed to create the agent-factory skill directory.
        exit /b 1
    )
)

echo Installing skill-first Agent Factory...
xcopy "%SOURCE%" "%DESTINATION%\" /E /I /Y /Q >nul
if errorlevel 1 (
    echo ERROR: Failed to copy the agent-factory skill.
    exit /b 1
)

echo   [OK] .github\skills\agent-factory installed
echo Use the agent-factory skill with GitHub Copilot.
endlocal
exit /b 0

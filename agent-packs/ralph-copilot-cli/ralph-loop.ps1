<#
.SYNOPSIS
    Ralph External Loop - Manages the Ralph agentic developer lifecycle.

.DESCRIPTION
    This script manages the Ralph agent's execution loop, handling:
    - Multi-run STM initialization with session isolation
    - Agent restarts between tasks
    - Activity-based timeout detection (file monitoring)
    - User communication (questions, approval)
    - Progress display
    - Single completion + verification pass

.PARAMETER Task
    The development task to execute. Required on first run.

.PARAMETER Resume
    Resume from existing STM state instead of starting fresh.

.PARAMETER Timeout
    Activity timeout in minutes. Default: 15

.EXAMPLE
    .\ralph-loop.ps1 -Task "Add user authentication with JWT"

.EXAMPLE
    .\ralph-loop.ps1 -Resume
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Task,

    [switch]$Resume,

    [int]$Timeout = 15
)

# Configuration
$STM_DIR = ".ralph-stm"
$ACTIVE_RUN_FILE = "$STM_DIR/active-run.json"
$RUNS_DIR = "$STM_DIR/runs"
$HISTORY_DIR = "$STM_DIR/history"

# Dynamic paths (set after session resolution)
$script:SESSION_DIR = $null
$script:STATE_FILE = $null
$script:HEARTBEAT_FILE = $null
$script:QUESTION_FILE = $null
$script:RESPONSE_FILE = $null
$script:APPROVAL_FILE = $null
$script:REJECTION_FILE = $null
$script:SIGNALS_DIR = $null

# Colors for output
$Colors = @{
    Header  = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "White"
    Phase   = "Magenta"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $Colors.Header
    Write-Host "  $Text" -ForegroundColor $Colors.Header
    Write-Host ("=" * 60) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Status {
    param(
        [string]$Label,
        [string]$Value,
        [string]$Color = "White"
    )
    Write-Host "  $Label`: " -NoNewline -ForegroundColor $Colors.Info
    Write-Host $Value -ForegroundColor $Color
}

function Write-Phase {
    param([string]$Phase, [int]$PhaseId)
    $phases = @{
        0 = "Intake"
        1 = "Discovery"
        2 = "Specification"
        3 = "Planning"
        4 = "Approval"
        5 = "Execution"
        6 = "Verification"
        7 = "Cleanup"
        8 = "Complete"
    }
    $phaseName = $phases[$PhaseId]
    Write-Host ""
    Write-Host "  Phase $PhaseId`: $phaseName" -ForegroundColor $Colors.Phase
}

function Get-SessionId {
    $datePart = Get-Date -Format "yyyy-MM-dd"
    $guidPart = [guid]::NewGuid().ToString().Substring(0, 8).ToLower()
    return "$datePart-$guidPart"
}

function Set-SessionPaths {
    param([string]$SessionId)
    
    $script:SESSION_DIR = "$RUNS_DIR/$SessionId"
    $script:STATE_FILE = "$script:SESSION_DIR/state.json"
    $script:HEARTBEAT_FILE = "$script:SESSION_DIR/heartbeat.json"
    $script:QUESTION_FILE = "$script:SESSION_DIR/communication/pending-question.md"
    $script:RESPONSE_FILE = "$script:SESSION_DIR/communication/user-response.md"
    $script:APPROVAL_FILE = "$script:SESSION_DIR/communication/approval.md"
    $script:REJECTION_FILE = "$script:SESSION_DIR/communication/rejection.md"
    $script:SIGNALS_DIR = "$script:SESSION_DIR/signals"
}

function Get-ActiveRun {
    if (Test-Path $ACTIVE_RUN_FILE) {
        return Get-Content $ACTIVE_RUN_FILE -Raw | ConvertFrom-Json
    }
    return $null
}

function Initialize-STM {
    param([string]$UserTask)
    
    Write-Host "  Initializing STM directory..." -ForegroundColor $Colors.Info
    
    # Generate session ID
    $sessionId = Get-SessionId
    $timestamp = Get-Date -Format "o"
    
    # Create directory structure
    New-Item -ItemType Directory -Path $STM_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path $RUNS_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path $HISTORY_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path "$RUNS_DIR/$sessionId" -Force | Out-Null
    New-Item -ItemType Directory -Path "$RUNS_DIR/$sessionId/events" -Force | Out-Null
    New-Item -ItemType Directory -Path "$RUNS_DIR/$sessionId/communication" -Force | Out-Null
    New-Item -ItemType Directory -Path "$RUNS_DIR/$sessionId/signals" -Force | Out-Null
    
    # Set session paths
    Set-SessionPaths -SessionId $sessionId
    
    # Create active-run.json
    $activeRun = @{
        current_run   = $sessionId
        started_at    = $timestamp
        last_activity = $timestamp
    }
    $activeRun | ConvertTo-Json | Set-Content -Path $ACTIVE_RUN_FILE -Encoding UTF8
    
    # Create initial state
    $state = @{
        session_id         = $sessionId
        created_at         = $timestamp
        updated_at         = $timestamp
        phase              = "intake"
        phase_id           = 0
        status             = "in_progress"
        user_request       = $UserTask
        current_plan_phase = 0
        total_plan_phases  = 0
        last_task          = "stm-initialized"
        last_event_id      = 0
        error              = $null
        checkpoint         = @{
            can_resume  = $true
            resume_hint = "Begin context discovery"
        }
    }
    
    $state | ConvertTo-Json -Depth 10 | Set-Content -Path $script:STATE_FILE -Encoding UTF8
    
    # Initialize heartbeat
    Update-Heartbeat -Activity "Session initialized" -Task "init"
    
    Write-Host "  STM initialized with session: $sessionId" -ForegroundColor $Colors.Success
    return $state
}

function Get-State {
    if (Test-Path $script:STATE_FILE) {
        try {
            return Get-Content $script:STATE_FILE -Raw | ConvertFrom-Json
        }
        catch {
            Write-Host "  Warning: State file corrupted or invalid JSON." -ForegroundColor $Colors.Warning
            Write-Host "  Run with -Task to start a fresh session, or fix the file manually." -ForegroundColor $Colors.Info
            return $null
        }
    }
    return $null
}

function Update-Heartbeat {
    param(
        [string]$Activity,
        [string]$Task
    )
    
    $heartbeat = @{
        timestamp = Get-Date -Format "o"
        activity  = $Activity
        task      = $Task
        pid       = $PID
    }
    
    $heartbeat | ConvertTo-Json | Set-Content -Path $script:HEARTBEAT_FILE -Encoding UTF8
    
    # Also update active-run last_activity
    if (Test-Path $ACTIVE_RUN_FILE) {
        $activeRun = Get-Content $ACTIVE_RUN_FILE -Raw | ConvertFrom-Json
        $activeRun.last_activity = Get-Date -Format "o"
        $activeRun | ConvertTo-Json | Set-Content -Path $ACTIVE_RUN_FILE -Encoding UTF8
    }
}

function Get-SessionActivityAge {
    # Monitor for ANY file changes in the session directory
    $latestFile = Get-ChildItem $script:SESSION_DIR -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    
    if ($latestFile) {
        return ((Get-Date) - $latestFile.LastWriteTime).TotalMinutes
    }
    
    return [double]::MaxValue  # No files = ancient
}

function Test-Timeout {
    $age = Get-SessionActivityAge
    return $age -gt $Timeout
}

function Test-PhaseSignal {
    param([int]$PhaseId)
    
    $signalPath = "$script:SIGNALS_DIR/phase-$PhaseId-complete.signal"
    
    if (-not (Test-Path $signalPath)) {
        return $false
    }
    
    try {
        $signal = Get-Content $signalPath -Raw | ConvertFrom-Json
        return $signal.phase_id -eq $PhaseId
    }
    catch {
        return $false
    }
}

function Handle-UserQuestion {
    if (-not (Test-Path $script:QUESTION_FILE)) {
        return $false
    }
    
    Write-Header "Ralph Needs Your Input"
    
    $questionContent = Get-Content $script:QUESTION_FILE -Raw
    Write-Host $questionContent -ForegroundColor $Colors.Info
    Write-Host ""
    
    $response = Read-Host "Your response"
    
    # Write response
    $responseContent = @"
# User Response

**Timestamp**: $(Get-Date -Format "o")

## Answer
$response
"@
    
    Set-Content -Path $script:RESPONSE_FILE -Value $responseContent -Encoding UTF8
    Remove-Item $script:QUESTION_FILE -Force
    
    Write-Host ""
    Write-Host "  Response recorded. Continuing..." -ForegroundColor $Colors.Success
    
    return $true
}

function Handle-Approval {
    param([object]$State)
    
    Write-Header "Approval Required"
    
    $specFile = "$script:SESSION_DIR/spec.md"
    $planFile = "$script:SESSION_DIR/plan.md"
    
    # Display spec summary
    if (Test-Path $specFile) {
        Write-Host "  === SPECIFICATION ===" -ForegroundColor $Colors.Phase
        Write-Host ""
        $specContent = Get-Content $specFile -Raw
        # Show first 50 lines or so
        $specLines = $specContent -split "`n"
        $previewLines = [Math]::Min(50, $specLines.Count)
        $specLines[0..($previewLines - 1)] | ForEach-Object { Write-Host "  $_" }
        if ($specLines.Count -gt 50) {
            Write-Host "  ... (truncated, see $specFile for full spec)" -ForegroundColor $Colors.Warning
        }
        Write-Host ""
    }
    
    # Display plan summary
    if (Test-Path $planFile) {
        Write-Host "  === IMPLEMENTATION PLAN ===" -ForegroundColor $Colors.Phase
        Write-Host ""
        $planContent = Get-Content $planFile -Raw
        $planLines = $planContent -split "`n"
        $previewLines = [Math]::Min(50, $planLines.Count)
        $planLines[0..($previewLines - 1)] | ForEach-Object { Write-Host "  $_" }
        if ($planLines.Count -gt 50) {
            Write-Host "  ... (truncated, see $planFile for full plan)" -ForegroundColor $Colors.Warning
        }
        Write-Host ""
    }
    
    Write-Host ""
    Write-Host "  Review the spec and plan above." -ForegroundColor $Colors.Info
    Write-Host "  Full documents available at:" -ForegroundColor $Colors.Info
    Write-Host "    - $specFile" -ForegroundColor $Colors.Info
    Write-Host "    - $planFile" -ForegroundColor $Colors.Info
    Write-Host ""
    
    $choice = Read-Host "Approve and proceed? (yes/no/feedback)"
    
    if ($choice -match "^y(es)?$") {
        $approvalContent = @"
# Approval

**Timestamp**: $(Get-Date -Format "o")
**Decision**: APPROVED

User approved the spec and plan to proceed with implementation.
"@
        Set-Content -Path $script:APPROVAL_FILE -Value $approvalContent -Encoding UTF8
        Write-Host ""
        Write-Host "  Approved! Proceeding with implementation..." -ForegroundColor $Colors.Success
        return $true
    }
    else {
        $feedback = $choice
        if ($choice -match "^n(o)?$") {
            $feedback = Read-Host "Please provide feedback for revision"
        }
        
        $rejectionContent = @"
# Rejection

**Timestamp**: $(Get-Date -Format "o")
**Decision**: REJECTED

## Feedback
$feedback
"@
        Set-Content -Path $script:REJECTION_FILE -Value $rejectionContent -Encoding UTF8
        Write-Host ""
        Write-Host "  Feedback recorded. Ralph will revise..." -ForegroundColor $Colors.Warning
        return $true
    }
}

function Show-Progress {
    param([object]$State)
    
    $phases = @{
        0 = "Intake"
        1 = "Discovery"
        2 = "Specification"
        3 = "Planning"
        4 = "Approval"
        5 = "Execution"
        6 = "Verification"
        7 = "Cleanup"
        8 = "Complete"
    }
    
    Write-Host ""
    Write-Host "  Progress:" -ForegroundColor $Colors.Info
    
    for ($i = 0; $i -le 8; $i++) {
        $marker = " "
        $color = "DarkGray"
        
        if ($i -lt $State.phase_id) {
            $marker = "✓"
            $color = $Colors.Success
        }
        elseif ($i -eq $State.phase_id) {
            $marker = "►"
            $color = $Colors.Phase
        }
        
        Write-Host "    $marker $i. $($phases[$i])" -ForegroundColor $color
    }
    
    if ($State.phase_id -eq 5 -and $State.total_plan_phases -gt 0) {
        Write-Host ""
        Write-Host "    Execution Progress: $($State.current_plan_phase)/$($State.total_plan_phases) phases" -ForegroundColor $Colors.Info
    }
    
    Write-Host ""
}

function Invoke-Ralph {
    param([string]$Prompt)
    
    Write-Host "  Running Ralph agent..." -ForegroundColor $Colors.Info
    Write-Host ""
    
    # Update heartbeat before invoking
    Update-Heartbeat -Activity "Invoking agent" -Task "agent-run"
    
    # Run the Copilot CLI with Ralph agent
    # copilot is a standalone CLI (not a gh extension)
    # -p runs in non-interactive mode (exits after completion)
    # --allow-all-tools enables autonomous operation without confirmation prompts
    # --agent specifies the custom agent to use
    try {
        copilot --agent ralph -p $Prompt --allow-all-tools --allow-all-paths --allow-all-urls
    }
    catch {
        Write-Host "  Error running agent: $_" -ForegroundColor $Colors.Error
    }
}

function Archive-Run {
    param([string]$SessionId)
    
    Write-Host "  Archiving session $SessionId..." -ForegroundColor $Colors.Info
    
    $sourceDir = "$RUNS_DIR/$SessionId"
    $destDir = "$HISTORY_DIR/$SessionId"
    
    if (Test-Path $sourceDir) {
        # Create summary
        $state = Get-Content "$sourceDir/state.json" -Raw | ConvertFrom-Json
        $summary = @{
            session_id   = $SessionId
            archived_at  = Get-Date -Format "o"
            final_phase  = $state.phase
            final_status = $state.status
            user_request = $state.user_request
        }
        
        # Move to history
        Move-Item $sourceDir $destDir -Force
        
        # Save summary
        $summary | ConvertTo-Json | Set-Content -Path "$destDir/summary.json" -Encoding UTF8
        
        Write-Host "  Session archived to history." -ForegroundColor $Colors.Success
    }
}

# Verification prompt for completion pass
$VERIFICATION_PROMPT = @"
You have signaled task completion. Perform a final verification:

1. Read the original user request from state.json
2. Read the spec.md acceptance criteria
3. Verify each criterion is satisfied
4. Check that all planned files exist
5. Run any quick validation (tests, lint, build)

If all good, update state.json status to "verified" and output:
[RALPH-VERIFIED] All acceptance criteria satisfied

If issues found, update state.json status to "issues_found" and output:
[RALPH-ISSUES] Found problems: {list}
"@

# Signal handling for graceful exit
try {
    $null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
        Write-Host ""
        Write-Host "  Interrupted. STM state preserved at $STM_DIR" -ForegroundColor $Colors.Warning
        Write-Host "  Run with -Resume to continue later." -ForegroundColor $Colors.Info
    }
}
catch {
    # Event registration may fail in some PowerShell hosts - continue anyway
}

# Main execution
Write-Header "Ralph - Agentic Developer"

# Check for existing session via active-run.json
$activeRun = Get-ActiveRun

if ($Resume) {
    if (-not $activeRun) {
        Write-Host "  No existing session found. Start a new task instead." -ForegroundColor $Colors.Error
        exit 1
    }
    Set-SessionPaths -SessionId $activeRun.current_run
    $state = Get-State
    if (-not $state) {
        Write-Host "  Session state file missing. Start a new task." -ForegroundColor $Colors.Error
        exit 1
    }
    Write-Host "  Resuming session: $($activeRun.current_run)" -ForegroundColor $Colors.Success
    Write-Status "Phase" $state.phase
    Write-Status "Status" $state.status
}
elseif ($activeRun -and -not $Task) {
    Set-SessionPaths -SessionId $activeRun.current_run
    $state = Get-State
    Write-Host "  Existing session found: $($activeRun.current_run)" -ForegroundColor $Colors.Warning
    $choice = Read-Host "  Resume existing session? (yes/no)"
    if ($choice -match "^y(es)?$") {
        $Resume = $true
    }
    else {
        Write-Host "  Archiving existing session..." -ForegroundColor $Colors.Info
        Archive-Run -SessionId $activeRun.current_run
        Remove-Item $ACTIVE_RUN_FILE -Force
        $state = $null
        $activeRun = $null
    }
}

if (-not $activeRun -and -not $Task) {
    Write-Host "  Usage: .\ralph-loop.ps1 -Task `"Your development task`"" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -Resume" -ForegroundColor $Colors.Error
    exit 1
}

if (-not $activeRun) {
    $state = Initialize-STM -UserTask $Task
}
else {
    # Ensure session paths are set before reading state
    Set-SessionPaths -SessionId $activeRun.current_run
    $state = Get-State
}

$prompt = if ($Task -and -not $Resume) { $Task } else { "Continue the development task" }

# Main loop with single completion + verification pattern
$iteration = 0
$maxIterations = 100  # Safety limit
$verificationDone = $false

while ($iteration -lt $maxIterations) {
    $iteration++
    
    Write-Host ""
    Write-Host "  ─────────────────────────────────────────────────" -ForegroundColor "DarkGray"
    Write-Host "  Iteration $iteration" -ForegroundColor $Colors.Info
    Write-Phase -Phase $state.phase -PhaseId $state.phase_id
    Show-Progress -State $state
    
    # Check for timeout using activity detection
    if (Test-Timeout) {
        Write-Host "  ⚠ Activity timeout detected. Restarting agent..." -ForegroundColor $Colors.Warning
    }
    
    # Handle user questions
    if (Handle-UserQuestion) {
        # Question was handled, update state and continue
        $state = Get-State
    }
    
    # Handle approval phase
    if ($state.status -eq "waiting_for_user" -and $state.phase -eq "approval") {
        if (Handle-Approval -State $state) {
            $state = Get-State
        }
    }
    
    # Check for complete status - single completion + verification pass
    if (($state.status -eq "complete" -or $state.phase -eq "complete") -and -not $verificationDone) {
        Write-Host "  Task signaled complete. Running verification pass..." -ForegroundColor $Colors.Info
        
        Invoke-Ralph -Prompt $VERIFICATION_PROMPT
        $verificationDone = $true
        $state = Get-State
        
        if ($state.status -eq "verified") {
            Write-Host "  ✓ Verification passed!" -ForegroundColor $Colors.Success
            break  # Success - exit loop
        }
        elseif ($state.status -eq "issues_found") {
            Write-Host "  Verification found issues. Presenting to user..." -ForegroundColor $Colors.Warning
            # Could restart for fixes or exit for manual intervention
            # For now, break and let user decide
            break
        }
    }
    elseif (($state.status -eq "complete" -or $state.phase -eq "complete") -and $verificationDone) {
        # Already verified, exit
        break
    }
    
    # Run the agent
    Invoke-Ralph -Prompt $prompt
    
    # After first invocation, always use continue prompt
    $prompt = "Continue the development task"
    
    # Read updated state
    $previousPhase = $state.phase_id
    $state = Get-State
    
    if (-not $state) {
        Write-Host "  Error: State file missing after agent run" -ForegroundColor $Colors.Error
        exit 1
    }
    
    $currentPhase = $state.phase_id
    
    # Validate phase completion signal
    if ($currentPhase -gt $previousPhase) {
        # Phase advanced - verify signal exists
        if (-not (Test-PhaseSignal -PhaseId $previousPhase)) {
            Write-Host "  Warning: Phase $previousPhase completed without signal file" -ForegroundColor $Colors.Warning
        }
    }
    
    # Handle error status
    if ($state.status -eq "error") {
        Write-Host ""
        Write-Host "  ⚠ Agent reported an error:" -ForegroundColor $Colors.Error
        Write-Host "    $($state.error)" -ForegroundColor $Colors.Error
        
        $choice = Read-Host "  Retry? (yes/no)"
        if ($choice -notmatch "^y(es)?$") {
            Write-Host "  Exiting. STM preserved for debugging." -ForegroundColor $Colors.Warning
            exit 1
        }
    }
    
    # Small delay between iterations
    Start-Sleep -Milliseconds 500
}

# Completion
if ($state.status -eq "verified") {
    Write-Header "Task Complete - Verified!"
    Write-Host "  Ralph has completed and verified the development task." -ForegroundColor $Colors.Success
    Write-Host ""
    Write-Status "Session" $state.session_id
    Write-Status "Total Iterations" $iteration
    Write-Host ""
    
    # Check for PR description
    if (Test-Path "PR_DESCRIPTION.md") {
        Write-Host "  PR description saved to: PR_DESCRIPTION.md" -ForegroundColor $Colors.Info
    }
    
    Write-Host ""
    Write-Host "  The .ralph-stm directory can be safely removed." -ForegroundColor $Colors.Info
    Write-Host "  Or keep it - new tasks will create isolated sessions." -ForegroundColor $Colors.Info
}
elseif ($state.status -eq "complete" -or $state.phase -eq "complete") {
    Write-Header "Task Complete!"
    Write-Host "  Ralph has completed the development task." -ForegroundColor $Colors.Success
    Write-Host ""
    Write-Status "Session" $state.session_id
    Write-Status "Total Iterations" $iteration
    Write-Host ""
    
    # Check for PR description
    if (Test-Path "PR_DESCRIPTION.md") {
        Write-Host "  PR description saved to: PR_DESCRIPTION.md" -ForegroundColor $Colors.Info
    }
    
    Write-Host ""
    Write-Host "  The .ralph-stm directory can be safely removed." -ForegroundColor $Colors.Info
    Write-Host "  Or keep it - new tasks will create isolated sessions." -ForegroundColor $Colors.Info
}
elseif ($state.status -eq "issues_found") {
    Write-Header "Verification Found Issues"
    Write-Host "  The verification pass identified issues that need attention." -ForegroundColor $Colors.Warning
    Write-Host ""
    Write-Status "Session" $state.session_id
    Write-Host ""
    Write-Host "  Review the verification output above and decide next steps." -ForegroundColor $Colors.Info
    Write-Host "  Run with -Resume to continue after addressing issues." -ForegroundColor $Colors.Info
}
elseif ($iteration -ge $maxIterations) {
    Write-Host ""
    Write-Host "  Maximum iterations reached. Something may be wrong." -ForegroundColor $Colors.Error
    Write-Host "  STM preserved for debugging at $STM_DIR" -ForegroundColor $Colors.Warning
    exit 1
}

Write-Host ""

<#
.SYNOPSIS
    Ralph External Loop - Manages the Ralph agentic developer lifecycle.

.DESCRIPTION
    This script manages the Ralph agent's execution loop, handling:
    - STM initialization
    - Agent restarts between tasks
    - Heartbeat monitoring and timeout detection
    - User communication (questions, approval)
    - Progress display

.PARAMETER Task
    The development task to execute. Required on first run.

.PARAMETER Resume
    Resume from existing STM state instead of starting fresh.

.PARAMETER Timeout
    Heartbeat timeout in minutes. Default: 15

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
$STATE_FILE = "$STM_DIR/state.json"
$HEARTBEAT_FILE = "$STM_DIR/heartbeat.json"
$QUESTION_FILE = "$STM_DIR/communication/pending-question.md"
$RESPONSE_FILE = "$STM_DIR/communication/user-response.md"
$APPROVAL_FILE = "$STM_DIR/communication/approval.md"
$REJECTION_FILE = "$STM_DIR/communication/rejection.md"

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

function Initialize-STM {
    param([string]$UserTask)
    
    Write-Host "  Initializing STM directory..." -ForegroundColor $Colors.Info
    
    # Create directories
    New-Item -ItemType Directory -Path $STM_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path "$STM_DIR/events" -Force | Out-Null
    New-Item -ItemType Directory -Path "$STM_DIR/communication" -Force | Out-Null
    
    # Create initial state
    $sessionId = "{0}-{1}" -f (Get-Date -Format "yyyy-MM-dd"), ([guid]::NewGuid().ToString().Substring(0, 8))
    $timestamp = Get-Date -Format "o"
    
    $state = @{
        session_id        = $sessionId
        created_at        = $timestamp
        updated_at        = $timestamp
        phase             = "intake"
        phase_id          = 0
        status            = "in_progress"
        user_request      = $UserTask
        current_plan_phase = 0
        total_plan_phases  = 0
        last_task         = "stm-initialized"
        last_event_id     = 0
        error             = $null
        checkpoint        = @{
            can_resume  = $true
            resume_hint = "Begin context discovery"
        }
    }
    
    $state | ConvertTo-Json -Depth 10 | Set-Content -Path $STATE_FILE -Encoding UTF8
    
    # Initialize heartbeat
    Update-Heartbeat -Activity "Session initialized" -Task "init"
    
    Write-Host "  STM initialized with session: $sessionId" -ForegroundColor $Colors.Success
    return $state
}

function Get-State {
    if (Test-Path $STATE_FILE) {
        return Get-Content $STATE_FILE -Raw | ConvertFrom-Json
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
    
    $heartbeat | ConvertTo-Json | Set-Content -Path $HEARTBEAT_FILE -Encoding UTF8
}

function Get-HeartbeatAge {
    if (Test-Path $HEARTBEAT_FILE) {
        $heartbeat = Get-Content $HEARTBEAT_FILE -Raw | ConvertFrom-Json
        $lastUpdate = [DateTime]::Parse($heartbeat.timestamp)
        $age = (Get-Date) - $lastUpdate
        return $age.TotalMinutes
    }
    return 0
}

function Test-Timeout {
    $age = Get-HeartbeatAge
    return $age -gt $Timeout
}

function Handle-UserQuestion {
    if (-not (Test-Path $QUESTION_FILE)) {
        return $false
    }
    
    Write-Header "Ralph Needs Your Input"
    
    $questionContent = Get-Content $QUESTION_FILE -Raw
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
    
    Set-Content -Path $RESPONSE_FILE -Value $responseContent -Encoding UTF8
    Remove-Item $QUESTION_FILE -Force
    
    Write-Host ""
    Write-Host "  Response recorded. Continuing..." -ForegroundColor $Colors.Success
    
    return $true
}

function Handle-Approval {
    param([object]$State)
    
    Write-Header "Approval Required"
    
    # Display spec summary
    if (Test-Path "$STM_DIR/spec.md") {
        Write-Host "  === SPECIFICATION ===" -ForegroundColor $Colors.Phase
        Write-Host ""
        $specContent = Get-Content "$STM_DIR/spec.md" -Raw
        # Show first 50 lines or so
        $specLines = $specContent -split "`n"
        $previewLines = [Math]::Min(50, $specLines.Count)
        $specLines[0..($previewLines - 1)] | ForEach-Object { Write-Host "  $_" }
        if ($specLines.Count -gt 50) {
            Write-Host "  ... (truncated, see .ralph-stm/spec.md for full spec)" -ForegroundColor $Colors.Warning
        }
        Write-Host ""
    }
    
    # Display plan summary
    if (Test-Path "$STM_DIR/plan.md") {
        Write-Host "  === IMPLEMENTATION PLAN ===" -ForegroundColor $Colors.Phase
        Write-Host ""
        $planContent = Get-Content "$STM_DIR/plan.md" -Raw
        $planLines = $planContent -split "`n"
        $previewLines = [Math]::Min(50, $planLines.Count)
        $planLines[0..($previewLines - 1)] | ForEach-Object { Write-Host "  $_" }
        if ($planLines.Count -gt 50) {
            Write-Host "  ... (truncated, see .ralph-stm/plan.md for full plan)" -ForegroundColor $Colors.Warning
        }
        Write-Host ""
    }
    
    Write-Host ""
    Write-Host "  Review the spec and plan above." -ForegroundColor $Colors.Info
    Write-Host "  Full documents available at:" -ForegroundColor $Colors.Info
    Write-Host "    - $STM_DIR/spec.md" -ForegroundColor $Colors.Info
    Write-Host "    - $STM_DIR/plan.md" -ForegroundColor $Colors.Info
    Write-Host ""
    
    $choice = Read-Host "Approve and proceed? (yes/no/feedback)"
    
    if ($choice -match "^y(es)?$") {
        $approvalContent = @"
# Approval

**Timestamp**: $(Get-Date -Format "o")
**Decision**: APPROVED

User approved the spec and plan to proceed with implementation.
"@
        Set-Content -Path $APPROVAL_FILE -Value $approvalContent -Encoding UTF8
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
        Set-Content -Path $REJECTION_FILE -Value $rejectionContent -Encoding UTF8
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
        copilot --agent ralph -p $Prompt --allow-all-tools
    }
    catch {
        Write-Host "  Error running agent: $_" -ForegroundColor $Colors.Error
    }
}

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

# Check for existing session
$state = Get-State

if ($Resume) {
    if (-not $state) {
        Write-Host "  No existing session found. Start a new task instead." -ForegroundColor $Colors.Error
        exit 1
    }
    Write-Host "  Resuming session: $($state.session_id)" -ForegroundColor $Colors.Success
    Write-Status "Phase" $state.phase
    Write-Status "Status" $state.status
}
elseif ($state -and -not $Task) {
    Write-Host "  Existing session found: $($state.session_id)" -ForegroundColor $Colors.Warning
    $choice = Read-Host "  Resume existing session? (yes/no)"
    if ($choice -match "^y(es)?$") {
        $Resume = $true
    }
    else {
        Write-Host "  Clearing existing session..." -ForegroundColor $Colors.Info
        Remove-Item -Path $STM_DIR -Recurse -Force
        $state = $null
    }
}

if (-not $state -and -not $Task) {
    Write-Host "  Usage: .\ralph-loop.ps1 -Task `"Your development task`"" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -Resume" -ForegroundColor $Colors.Error
    exit 1
}

if (-not $state) {
    $state = Initialize-STM -UserTask $Task
}

$prompt = if ($Task -and -not $Resume) { $Task } else { "Continue the development task" }

# Main loop
$iteration = 0
$maxIterations = 100  # Safety limit

while ($state.status -ne "complete" -and $state.phase -ne "complete" -and $iteration -lt $maxIterations) {
    $iteration++
    
    Write-Host ""
    Write-Host "  ─────────────────────────────────────────────────" -ForegroundColor "DarkGray"
    Write-Host "  Iteration $iteration" -ForegroundColor $Colors.Info
    Write-Phase -Phase $state.phase -PhaseId $state.phase_id
    Show-Progress -State $state
    
    # Check for timeout
    if (Test-Timeout) {
        Write-Host "  ⚠ Heartbeat timeout detected. Restarting agent..." -ForegroundColor $Colors.Warning
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
    
    # Skip agent invocation if complete
    if ($state.status -eq "complete" -or $state.phase -eq "complete") {
        break
    }
    
    # Run the agent
    Invoke-Ralph -Prompt $prompt
    
    # After first invocation, always use continue prompt
    $prompt = "Continue the development task"
    
    # Read updated state
    $state = Get-State
    
    if (-not $state) {
        Write-Host "  Error: State file missing after agent run" -ForegroundColor $Colors.Error
        exit 1
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
if ($state.status -eq "complete" -or $state.phase -eq "complete") {
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
}
elseif ($iteration -ge $maxIterations) {
    Write-Host ""
    Write-Host "  Maximum iterations reached. Something may be wrong." -ForegroundColor $Colors.Error
    Write-Host "  STM preserved for debugging at $STM_DIR" -ForegroundColor $Colors.Warning
    exit 1
}

Write-Host ""

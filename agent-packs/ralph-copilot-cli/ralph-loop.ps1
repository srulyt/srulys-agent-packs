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

.PARAMETER PromptFile
    Path to a file containing the development task prompt. Mutually exclusive with -Task and -TaskListFile.

.PARAMETER TaskListFile
    Path to a text file containing one task per non-empty line. Each task runs in its own isolated STM session.

.PARAMETER TaskFolder
    Path to a folder containing one prompt file per task. Files are executed in sorted order with isolated STM per task.

.PARAMETER Resume
    Resume from existing STM state instead of starting fresh.

.PARAMETER IncludeAdoPrComments
    Loads Azure DevOps PR comments via az CLI and appends them as task input.

.PARAMETER AdoOrganization
    Azure DevOps organization URL (e.g., https://dev.azure.com/contoso).

.PARAMETER AdoProject
    Azure DevOps project name.

.PARAMETER AdoRepository
    Azure DevOps repository name or ID.

.PARAMETER AdoPullRequestId
    Azure DevOps pull request ID.

.PARAMETER Timeout
    Activity timeout in minutes. Default: 15

.EXAMPLE
    .\ralph-loop.ps1 -Task "Add user authentication with JWT"

.EXAMPLE
    .\ralph-loop.ps1 -Resume

.EXAMPLE
    .\ralph-loop.ps1 -PromptFile .\prompts\task.md

.EXAMPLE
    .\ralph-loop.ps1 -TaskListFile .\tasks.txt -IncludeAdoPrComments -AdoOrganization "https://dev.azure.com/contoso" -AdoProject "App" -AdoRepository "web" -AdoPullRequestId 42

.EXAMPLE
    .\ralph-loop.ps1 -TaskFolder .\task-prompts
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Task,

    [string]$PromptFile,

    [string]$TaskListFile,

    [string]$TaskFolder,

    [switch]$Resume,

    [switch]$IncludeAdoPrComments,

    [string]$AdoOrganization,

    [string]$AdoProject,

    [string]$AdoRepository,

    [int]$AdoPullRequestId,

    [int]$Timeout = 15
)

# Configuration
$STM_DIR = ".ralph-stm"
$ACTIVE_RUN_FILE = "$STM_DIR/active-run.json"
$RUNS_DIR = "$STM_DIR/runs"
$HISTORY_DIR = "$STM_DIR/history"
$BATCH_STATE_FILE = "$STM_DIR/batch-state.json"
$BATCH_HISTORY_DIR = "$STM_DIR/batch-history"

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

function Get-TaskFromPromptFile {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath -PathType Leaf)) {
        throw "Prompt file not found: $FilePath"
    }

    $content = Get-Content $FilePath -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        throw "Prompt file is empty: $FilePath"
    }

    return $content.Trim()
}

function Get-TaskListFromFile {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath -PathType Leaf)) {
        throw "Task list file not found: $FilePath"
    }

    $tasks = Get-Content $FilePath |
        ForEach-Object { $_.Trim() } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith("#") }

    if (-not $tasks -or $tasks.Count -eq 0) {
        throw "Task list file has no tasks (expects one task per non-empty line): $FilePath"
    }

    return $tasks
}

function Get-AdoPrCommentsInput {
    param(
        [string]$Organization,
        [string]$Project,
        [string]$Repository,
        [int]$PullRequestId
    )

    Write-Host "  Loading Azure DevOps PR comments with az CLI..." -ForegroundColor $Colors.Info

    $azCheck = Get-Command az -ErrorAction SilentlyContinue
    if (-not $azCheck) {
        throw "az CLI not found. Install Azure CLI and azure-devops extension before using -IncludeAdoPrComments."
    }

    $json = az repos pr thread list --organization $Organization --project $Project --repository $Repository --id $PullRequestId --output json 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($json)) {
        throw "Failed to load PR threads from Azure DevOps. Verify az login, extension setup, and ADO parameters."
    }

    $threads = $json | ConvertFrom-Json
    $comments = @()

    foreach ($thread in $threads) {
        if ($null -eq $thread.comments) {
            continue
        }

        foreach ($comment in $thread.comments) {
            if ($null -eq $comment) {
                continue
            }

            if ($comment.isDeleted -eq $true) {
                continue
            }

            if ([string]::IsNullOrWhiteSpace($comment.content)) {
                continue
            }

            $author = if ($comment.author -and $comment.author.displayName) { $comment.author.displayName } else { "unknown" }
            $comments += "- [$author] $($comment.content.Trim())"
        }
    }

    if (-not $comments -or $comments.Count -eq 0) {
        throw "No non-deleted PR comments found for PR #$PullRequestId."
    }

    return @"
## Azure DevOps PR Comment Context

Source:
- Organization: $Organization
- Project: $Project
- Repository: $Repository
- Pull Request: $PullRequestId

Comments:
$($comments -join "`n")
"@
}

function Get-BatchState {
    if (Test-Path $BATCH_STATE_FILE) {
        try {
            return Get-Content $BATCH_STATE_FILE -Raw | ConvertFrom-Json
        }
        catch {
            Write-Host "  Warning: Batch state file corrupted or invalid JSON." -ForegroundColor $Colors.Warning
            return $null
        }
    }
    return $null
}

function Save-BatchState {
    param([object]$BatchState)

    $BatchState.updated_at = Get-Date -Format "o"
    New-Item -ItemType Directory -Path $STM_DIR -Force | Out-Null
    $BatchState | ConvertTo-Json -Depth 10 | Set-Content -Path $BATCH_STATE_FILE -Encoding UTF8
}

function Initialize-TaskFolderBatchState {
    param(
        [string]$FolderPath,
        [switch]$WithAdoComments
    )

    if (-not (Test-Path $FolderPath -PathType Container)) {
        throw "Task folder not found: $FolderPath"
    }

    $resolvedFolder = (Resolve-Path $FolderPath).Path
    $taskFiles = Get-ChildItem -Path $resolvedFolder -File -Recurse |
        Sort-Object FullName |
        Select-Object -ExpandProperty FullName

    if (-not $taskFiles -or $taskFiles.Count -eq 0) {
        throw "Task folder has no files: $resolvedFolder"
    }

    $batchId = Get-SessionId
    $timestamp = Get-Date -Format "o"

    return [PSCustomObject]@{
        batch_id                  = $batchId
        mode                      = "task_folder"
        folder_path               = $resolvedFolder
        status                    = "in_progress"
        started_at                = $timestamp
        updated_at                = $timestamp
        current_index             = 0
        current_task_file         = $null
        current_task_session      = $null
        task_files                = $taskFiles
        completed_tasks           = @()
        include_ado_pr_comments   = [bool]$WithAdoComments
        ado_organization          = $AdoOrganization
        ado_project               = $AdoProject
        ado_repository            = $AdoRepository
        ado_pull_request_id       = $AdoPullRequestId
        last_error                = $null
    }
}

function Archive-BatchState {
    param([object]$BatchState)

    if (-not $BatchState) {
        return
    }

    New-Item -ItemType Directory -Path $BATCH_HISTORY_DIR -Force | Out-Null
    $archiveFile = "$BATCH_HISTORY_DIR/$($BatchState.batch_id).json"
    $BatchState | ConvertTo-Json -Depth 10 | Set-Content -Path $archiveFile -Encoding UTF8

    if (Test-Path $BATCH_STATE_FILE) {
        Remove-Item $BATCH_STATE_FILE -Force
    }
}

function Complete-BatchTask {
    param(
        [object]$BatchState,
        [string]$TaskFile
    )

    $alreadyCompleted = $BatchState.completed_tasks -contains $TaskFile
    if (-not $alreadyCompleted) {
        $BatchState.completed_tasks = @($BatchState.completed_tasks) + @($TaskFile)
    }

    $BatchState.current_index = [int]$BatchState.current_index + 1
    $BatchState.current_task_file = $null
    $BatchState.current_task_session = $null
    $BatchState.last_error = $null
    Save-BatchState -BatchState $BatchState
}

function Invoke-TaskFolderBatch {
    param([object]$BatchState)

    $shellExecutable = (Get-Process -Id $PID).Path

    Write-Header "Ralph - Task Folder Batch"
    Write-Status "Batch" $BatchState.batch_id
    Write-Status "Folder" $BatchState.folder_path
    Write-Status "Tasks" $BatchState.task_files.Count

    while ($BatchState.status -eq "in_progress" -and [int]$BatchState.current_index -lt $BatchState.task_files.Count) {
        $taskFile = $BatchState.task_files[[int]$BatchState.current_index]
        $BatchState.current_task_file = $taskFile
        Save-BatchState -BatchState $BatchState

        Write-Host "" 
        Write-Host "  [Folder Batch $([int]$BatchState.current_index + 1)/$($BatchState.task_files.Count)]" -ForegroundColor $Colors.Phase
        Write-Host "  Task file: $taskFile" -ForegroundColor $Colors.Info

        $activeRun = Get-ActiveRun

        if ($activeRun) {
            Set-SessionPaths -SessionId $activeRun.current_run
            $activeState = Get-State

            if ($BatchState.current_task_session -and $activeRun.current_run -eq $BatchState.current_task_session) {
                if ($activeState -and (($activeState.status -in @("complete", "verified")) -or $activeState.phase -eq "complete")) {
                    Complete-BatchTask -BatchState $BatchState -TaskFile $taskFile
                    continue
                }
            }
            elseif ($activeState -and (($activeState.status -in @("complete", "verified", "issues_found")) -or $activeState.phase -eq "complete")) {
                Write-Host "  Found stale completed session outside current batch task. Archiving it..." -ForegroundColor $Colors.Warning
                Archive-Run -SessionId $activeRun.current_run
                if (Test-Path $ACTIVE_RUN_FILE) {
                    Remove-Item $ACTIVE_RUN_FILE -Force
                }
                $activeRun = $null
            }
            else {
                $BatchState.last_error = "Found in-progress active session ($($activeRun.current_run)) that does not match current batch task session."
                Save-BatchState -BatchState $BatchState
                Write-Host "  Batch paused due to session mismatch. Resolve active session and run with -Resume." -ForegroundColor $Colors.Error
                exit 1
            }
        }

        $childArgs = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", $PSCommandPath,
            "-Timeout", $Timeout
        )

        if ($activeRun) {
            Write-Host "  Resuming in-progress task session..." -ForegroundColor $Colors.Info
            $childArgs += "-Resume"
        }
        else {
            Write-Host "  Starting new task session from file..." -ForegroundColor $Colors.Info
            $childArgs += @("-PromptFile", $taskFile)

            if ($BatchState.include_ado_pr_comments) {
                $childArgs += @(
                    "-IncludeAdoPrComments",
                    "-AdoOrganization", $BatchState.ado_organization,
                    "-AdoProject", $BatchState.ado_project,
                    "-AdoRepository", $BatchState.ado_repository,
                    "-AdoPullRequestId", $BatchState.ado_pull_request_id
                )
            }
        }

        & $shellExecutable @childArgs
        if ($LASTEXITCODE -ne 0) {
            $BatchState.last_error = "Child loop exited with code $LASTEXITCODE on task file: $taskFile"
            Save-BatchState -BatchState $BatchState
            Write-Host "  Batch paused. Resume with -Resume to continue from this task." -ForegroundColor $Colors.Warning
            exit $LASTEXITCODE
        }

        $activeRunAfter = Get-ActiveRun
        if (-not $activeRunAfter) {
            $BatchState.last_error = "No active session found after child execution for task file: $taskFile"
            Save-BatchState -BatchState $BatchState
            Write-Host "  Batch paused. Resume with -Resume to retry this task." -ForegroundColor $Colors.Warning
            exit 1
        }

        Set-SessionPaths -SessionId $activeRunAfter.current_run
        $activeStateAfter = Get-State

        if (-not $BatchState.current_task_session) {
            $BatchState.current_task_session = $activeRunAfter.current_run
            Save-BatchState -BatchState $BatchState
        }

        if ($activeStateAfter -and (($activeStateAfter.status -in @("complete", "verified")) -or $activeStateAfter.phase -eq "complete")) {
            Complete-BatchTask -BatchState $BatchState -TaskFile $taskFile
            continue
        }

        if ($activeStateAfter -and $activeStateAfter.status -eq "issues_found") {
            $BatchState.last_error = "Task requires intervention (issues_found): $taskFile"
            Save-BatchState -BatchState $BatchState
            Write-Host "  Task needs intervention. After addressing issues, run with -Resume." -ForegroundColor $Colors.Warning
            exit 1
        }

        $BatchState.last_error = "Task did not reach completion status: $taskFile"
        Save-BatchState -BatchState $BatchState
        Write-Host "  Batch paused. Resume with -Resume to continue current task." -ForegroundColor $Colors.Warning
        exit 1
    }

    if ([int]$BatchState.current_index -ge $BatchState.task_files.Count) {
        $BatchState.status = "complete"
        $BatchState.current_task_file = $null
        $BatchState.current_task_session = $null
        $BatchState.last_error = $null
        Save-BatchState -BatchState $BatchState
        Archive-BatchState -BatchState $BatchState
        Write-Host "" 
        Write-Host "  Task folder batch completed successfully." -ForegroundColor $Colors.Success
        return
    }
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

# Validate input mode
$hasTask = -not [string]::IsNullOrWhiteSpace($Task)
$hasPromptFile = -not [string]::IsNullOrWhiteSpace($PromptFile)
$hasTaskList = -not [string]::IsNullOrWhiteSpace($TaskListFile)
$hasTaskFolder = -not [string]::IsNullOrWhiteSpace($TaskFolder)

$activeBatchState = Get-BatchState

if ($Resume -and $activeBatchState -and $activeBatchState.status -eq "in_progress" -and $activeBatchState.mode -eq "task_folder") {
    if ($hasTask -or $hasPromptFile -or $hasTaskList) {
        Write-Host "  -Resume with active task-folder batch cannot be combined with -Task, -PromptFile, or -TaskListFile." -ForegroundColor $Colors.Error
        exit 1
    }

    if ($hasTaskFolder) {
        $resolvedTaskFolder = (Resolve-Path $TaskFolder -ErrorAction SilentlyContinue)
        if (-not $resolvedTaskFolder -or $resolvedTaskFolder.Path -ne $activeBatchState.folder_path) {
            Write-Host "  -TaskFolder does not match active batch folder in .ralph-stm/batch-state.json." -ForegroundColor $Colors.Error
            exit 1
        }
    }

    Invoke-TaskFolderBatch -BatchState $activeBatchState
    exit 0
}

if ($Resume -and ($hasTask -or $hasPromptFile -or $hasTaskList -or $hasTaskFolder)) {
    Write-Host "  -Resume cannot be combined with -Task, -PromptFile, -TaskListFile, or -TaskFolder." -ForegroundColor $Colors.Error
    exit 1
}

if (($hasTask -and $hasPromptFile) -or ($hasTask -and $hasTaskList) -or ($hasTask -and $hasTaskFolder) -or ($hasPromptFile -and $hasTaskList) -or ($hasPromptFile -and $hasTaskFolder) -or ($hasTaskList -and $hasTaskFolder)) {
    Write-Host "  -Task, -PromptFile, -TaskListFile, and -TaskFolder are mutually exclusive." -ForegroundColor $Colors.Error
    exit 1
}

if ($IncludeAdoPrComments) {
    if ([string]::IsNullOrWhiteSpace($AdoOrganization) -or [string]::IsNullOrWhiteSpace($AdoProject) -or [string]::IsNullOrWhiteSpace($AdoRepository) -or $AdoPullRequestId -le 0) {
        Write-Host "  -IncludeAdoPrComments requires -AdoOrganization, -AdoProject, -AdoRepository, and -AdoPullRequestId." -ForegroundColor $Colors.Error
        exit 1
    }
}

# Task folder mode: one prompt file per task, persisted batch state for resilient resume.
if ($hasTaskFolder) {
    if ($activeBatchState -and $activeBatchState.status -eq "in_progress") {
        Write-Host "  Existing in-progress batch detected. Run with -Resume to continue it." -ForegroundColor $Colors.Error
        exit 1
    }

    try {
        $folderBatchState = Initialize-TaskFolderBatchState -FolderPath $TaskFolder -WithAdoComments:$IncludeAdoPrComments
    }
    catch {
        Write-Host "  $_" -ForegroundColor $Colors.Error
        exit 1
    }

    Save-BatchState -BatchState $folderBatchState
    Invoke-TaskFolderBatch -BatchState $folderBatchState
    exit 0
}

# Batch mode: each task runs in an isolated session by invoking this script per task
if ($hasTaskList) {
    try {
        $batchTasks = Get-TaskListFromFile -FilePath $TaskListFile
    }
    catch {
        Write-Host "  $_" -ForegroundColor $Colors.Error
        exit 1
    }

    Write-Header "Ralph - Batch Task List"
    Write-Host "  Tasks to run: $($batchTasks.Count)" -ForegroundColor $Colors.Info

    $shellExecutable = (Get-Process -Id $PID).Path

    $taskIndex = 0
    foreach ($batchTask in $batchTasks) {
        $taskIndex++
        Write-Host "" 
        Write-Host "  [Batch $taskIndex/$($batchTasks.Count)] Starting task..." -ForegroundColor $Colors.Phase
        Write-Host "  $batchTask" -ForegroundColor $Colors.Info

        $childArgs = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", $PSCommandPath,
            "-Task", $batchTask,
            "-Timeout", $Timeout
        )

        if ($IncludeAdoPrComments) {
            $childArgs += @(
                "-IncludeAdoPrComments",
                "-AdoOrganization", $AdoOrganization,
                "-AdoProject", $AdoProject,
                "-AdoRepository", $AdoRepository,
                "-AdoPullRequestId", $AdoPullRequestId
            )
        }

        & $shellExecutable @childArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Batch stopped: task $taskIndex failed with exit code $LASTEXITCODE." -ForegroundColor $Colors.Error
            exit $LASTEXITCODE
        }
    }

    Write-Host "" 
    Write-Host "  Batch task list completed successfully." -ForegroundColor $Colors.Success
    exit 0
}

$resolvedTask = $null
if (-not $Resume) {
    if ($hasTask) {
        $resolvedTask = $Task
    }
    elseif ($hasPromptFile) {
        try {
            $resolvedTask = Get-TaskFromPromptFile -FilePath $PromptFile
        }
        catch {
            Write-Host "  $_" -ForegroundColor $Colors.Error
            exit 1
        }
    }

    if ($IncludeAdoPrComments) {
        try {
            $adoContext = Get-AdoPrCommentsInput -Organization $AdoOrganization -Project $AdoProject -Repository $AdoRepository -PullRequestId $AdoPullRequestId
        }
        catch {
            Write-Host "  $_" -ForegroundColor $Colors.Error
            exit 1
        }

        if ([string]::IsNullOrWhiteSpace($resolvedTask)) {
            $resolvedTask = $adoContext
        }
        else {
            $resolvedTask = "$resolvedTask`n`n$adoContext"
        }
    }
}

# Check for existing session via active-run.json
$activeRun = Get-ActiveRun

# If a new task is explicitly provided, always start a fresh session.
# Existing active runs are archived to avoid unintentionally resuming old work.
if ($resolvedTask -and -not $Resume -and $activeRun) {
    Set-SessionPaths -SessionId $activeRun.current_run
    $existingState = Get-State
    
    if ($existingState -and (($existingState.status -in @("complete", "verified", "issues_found")) -or $existingState.phase -eq "complete")) {
        Write-Host "  Previous session is complete. Archiving and starting new task..." -ForegroundColor $Colors.Info
    }
    else {
        Write-Host "  Existing active session found. Archiving and starting new task..." -ForegroundColor $Colors.Warning
    }
    
    Archive-Run -SessionId $activeRun.current_run
    if (Test-Path $ACTIVE_RUN_FILE) {
        Remove-Item $ACTIVE_RUN_FILE -Force
    }
    $activeRun = $null
}

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

if (-not $activeRun -and -not $resolvedTask) {
    Write-Host "  Usage: .\ralph-loop.ps1 -Task `"Your development task`"" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -PromptFile .\prompts\task.md" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -TaskListFile .\tasks.txt" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -TaskFolder .\task-prompts" -ForegroundColor $Colors.Error
    Write-Host "         .\ralph-loop.ps1 -Resume" -ForegroundColor $Colors.Error
    exit 1
}

if (-not $activeRun) {
    $state = Initialize-STM -UserTask $resolvedTask
}
else {
    # Ensure session paths are set before reading state
    Set-SessionPaths -SessionId $activeRun.current_run
    $state = Get-State
}

$prompt = if ($resolvedTask -and -not $Resume) { $resolvedTask } else { "Continue the development task" }

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

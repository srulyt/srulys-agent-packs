#!/usr/bin/env bash
#
# Ralph External Loop - Manages the Ralph agentic developer lifecycle.
#
# This script manages the Ralph agent's execution loop, handling:
# - STM initialization
# - Agent restarts between tasks
# - Heartbeat monitoring and timeout detection
# - User communication (questions, approval)
# - Progress display
#
# Usage:
#   ./ralph-loop.sh "Add user authentication with JWT"  # Start new task
#   ./ralph-loop.sh --resume                            # Resume existing session
#   ./ralph-loop.sh --timeout 20 "Task description"     # Custom timeout (minutes)

set -e

# Configuration
STM_DIR=".ralph-stm"
STATE_FILE="$STM_DIR/state.json"
HEARTBEAT_FILE="$STM_DIR/heartbeat.json"
QUESTION_FILE="$STM_DIR/communication/pending-question.md"
RESPONSE_FILE="$STM_DIR/communication/user-response.md"
APPROVAL_FILE="$STM_DIR/communication/approval.md"
REJECTION_FILE="$STM_DIR/communication/rejection.md"

TIMEOUT_MINUTES=15
RESUME=false
TASK=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resume|-r)
            RESUME=true
            shift
            ;;
        --timeout|-t)
            TIMEOUT_MINUTES="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [TASK]"
            echo ""
            echo "Options:"
            echo "  --resume, -r       Resume existing session"
            echo "  --timeout, -t MIN  Heartbeat timeout in minutes (default: 15)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 \"Add user authentication with JWT\""
            echo "  $0 --resume"
            echo "  $0 --timeout 20 \"Implement payment processing\""
            exit 0
            ;;
        *)
            TASK="$1"
            shift
            ;;
    esac
done

# Utility functions
write_header() {
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo ""
}

write_status() {
    echo -e "  ${WHITE}$1:${NC} $2"
}

write_phase() {
    local phase_id=$1
    local phases=("Intake" "Discovery" "Specification" "Planning" "Approval" "Execution" "Verification" "Cleanup" "Complete")
    echo ""
    echo -e "  ${MAGENTA}Phase $phase_id: ${phases[$phase_id]}${NC}"
}

# JSON parsing (works with jq if available, fallback to grep/sed)
json_get() {
    local file="$1"
    local key="$2"
    
    if command -v jq &> /dev/null; then
        jq -r ".$key // empty" "$file" 2>/dev/null
    else
        # Basic fallback - works for simple string values
        grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$file" 2>/dev/null | \
            sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1
    fi
}

json_get_num() {
    local file="$1"
    local key="$2"
    
    if command -v jq &> /dev/null; then
        jq -r ".$key // 0" "$file" 2>/dev/null
    else
        grep -o "\"$key\"[[:space:]]*:[[:space:]]*[0-9]*" "$file" 2>/dev/null | \
            sed 's/.*:[[:space:]]*//' | head -1
    fi
}

get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

generate_session_id() {
    local date_part=$(date +"%Y-%m-%d")
    local uuid_part=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "$(date +%s)$(( RANDOM ))" | md5sum | cut -c1-8)
    uuid_part=$(echo "$uuid_part" | tr '[:upper:]' '[:lower:]' | cut -c1-8)
    echo "${date_part}-${uuid_part}"
}

initialize_stm() {
    local user_task="$1"
    
    echo -e "  ${WHITE}Initializing STM directory...${NC}"
    
    # Create directories
    mkdir -p "$STM_DIR/events"
    mkdir -p "$STM_DIR/communication"
    
    # Generate session ID
    local session_id=$(generate_session_id)
    local timestamp=$(get_timestamp)
    
    # Create initial state
    cat > "$STATE_FILE" << EOF
{
  "session_id": "$session_id",
  "created_at": "$timestamp",
  "updated_at": "$timestamp",
  "phase": "intake",
  "phase_id": 0,
  "status": "in_progress",
  "user_request": "$user_task",
  "current_plan_phase": 0,
  "total_plan_phases": 0,
  "last_task": "stm-initialized",
  "last_event_id": 0,
  "error": null,
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Begin context discovery"
  }
}
EOF
    
    # Initialize heartbeat
    update_heartbeat "Session initialized" "init"
    
    echo -e "  ${GREEN}STM initialized with session: $session_id${NC}"
}

update_heartbeat() {
    local activity="$1"
    local task="$2"
    local timestamp=$(get_timestamp)
    
    cat > "$HEARTBEAT_FILE" << EOF
{
  "timestamp": "$timestamp",
  "activity": "$activity",
  "task": "$task",
  "pid": $$
}
EOF
}

get_heartbeat_age() {
    if [[ ! -f "$HEARTBEAT_FILE" ]]; then
        echo "0"
        return
    fi
    
    local last_update=$(json_get "$HEARTBEAT_FILE" "timestamp")
    
    if [[ -z "$last_update" ]]; then
        echo "0"
        return
    fi
    
    # Convert to epoch and calculate difference
    local now=$(date +%s)
    local then
    
    # Handle different date formats
    if date --version &>/dev/null; then
        # GNU date
        then=$(date -d "$last_update" +%s 2>/dev/null || echo "$now")
    else
        # BSD date (macOS)
        then=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_update" +%s 2>/dev/null || echo "$now")
    fi
    
    local diff=$(( (now - then) / 60 ))
    echo "$diff"
}

check_timeout() {
    local age=$(get_heartbeat_age)
    [[ $age -gt $TIMEOUT_MINUTES ]]
}

handle_user_question() {
    if [[ ! -f "$QUESTION_FILE" ]]; then
        return 1
    fi
    
    write_header "Ralph Needs Your Input"
    
    cat "$QUESTION_FILE"
    echo ""
    
    read -p "Your response: " response
    
    # Write response
    cat > "$RESPONSE_FILE" << EOF
# User Response

**Timestamp**: $(get_timestamp)

## Answer
$response
EOF
    
    rm -f "$QUESTION_FILE"
    
    echo ""
    echo -e "  ${GREEN}Response recorded. Continuing...${NC}"
    
    return 0
}

handle_approval() {
    write_header "Approval Required"
    
    # Display spec summary
    if [[ -f "$STM_DIR/spec.md" ]]; then
        echo -e "  ${MAGENTA}=== SPECIFICATION ===${NC}"
        echo ""
        head -50 "$STM_DIR/spec.md" | sed 's/^/  /'
        local spec_lines=$(wc -l < "$STM_DIR/spec.md")
        if [[ $spec_lines -gt 50 ]]; then
            echo -e "  ${YELLOW}... (truncated, see $STM_DIR/spec.md for full spec)${NC}"
        fi
        echo ""
    fi
    
    # Display plan summary
    if [[ -f "$STM_DIR/plan.md" ]]; then
        echo -e "  ${MAGENTA}=== IMPLEMENTATION PLAN ===${NC}"
        echo ""
        head -50 "$STM_DIR/plan.md" | sed 's/^/  /'
        local plan_lines=$(wc -l < "$STM_DIR/plan.md")
        if [[ $plan_lines -gt 50 ]]; then
            echo -e "  ${YELLOW}... (truncated, see $STM_DIR/plan.md for full plan)${NC}"
        fi
        echo ""
    fi
    
    echo ""
    echo -e "  ${WHITE}Review the spec and plan above.${NC}"
    echo -e "  ${WHITE}Full documents available at:${NC}"
    echo -e "    - $STM_DIR/spec.md"
    echo -e "    - $STM_DIR/plan.md"
    echo ""
    
    read -p "Approve and proceed? (yes/no/feedback): " choice
    
    case "$choice" in
        y|yes|Y|YES)
            cat > "$APPROVAL_FILE" << EOF
# Approval

**Timestamp**: $(get_timestamp)
**Decision**: APPROVED

User approved the spec and plan to proceed with implementation.
EOF
            echo ""
            echo -e "  ${GREEN}Approved! Proceeding with implementation...${NC}"
            ;;
        *)
            local feedback="$choice"
            if [[ "$choice" =~ ^(n|no|N|NO)$ ]]; then
                read -p "Please provide feedback for revision: " feedback
            fi
            
            cat > "$REJECTION_FILE" << EOF
# Rejection

**Timestamp**: $(get_timestamp)
**Decision**: REJECTED

## Feedback
$feedback
EOF
            echo ""
            echo -e "  ${YELLOW}Feedback recorded. Ralph will revise...${NC}"
            ;;
    esac
    
    return 0
}

show_progress() {
    local phase_id=$(json_get_num "$STATE_FILE" "phase_id")
    local current_plan=$(json_get_num "$STATE_FILE" "current_plan_phase")
    local total_plan=$(json_get_num "$STATE_FILE" "total_plan_phases")
    
    local phases=("Intake" "Discovery" "Specification" "Planning" "Approval" "Execution" "Verification" "Cleanup" "Complete")
    
    echo ""
    echo -e "  ${WHITE}Progress:${NC}"
    
    for i in {0..8}; do
        local marker=" "
        local color="$GRAY"
        
        if [[ $i -lt $phase_id ]]; then
            marker="✓"
            color="$GREEN"
        elif [[ $i -eq $phase_id ]]; then
            marker="►"
            color="$MAGENTA"
        fi
        
        echo -e "    ${color}$marker $i. ${phases[$i]}${NC}"
    done
    
    if [[ $phase_id -eq 5 && $total_plan -gt 0 ]]; then
        echo ""
        echo -e "    ${WHITE}Execution Progress: $current_plan/$total_plan phases${NC}"
    fi
    
    echo ""
}

invoke_ralph() {
    local prompt="$1"
    
    echo -e "  ${WHITE}Running Ralph agent...${NC}"
    echo ""
    
    # Update heartbeat before invoking
    update_heartbeat "Invoking agent" "agent-run"
    
    # Run the Copilot CLI with Ralph agent
    gh copilot --agent ralph "$prompt" || true
}

# Signal handling
cleanup() {
    echo ""
    echo -e "  ${YELLOW}Interrupted. STM state preserved at $STM_DIR${NC}"
    echo -e "  ${WHITE}Run with --resume to continue later.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main execution
write_header "Ralph - Agentic Developer"

# Check for jq availability
if ! command -v jq &> /dev/null; then
    echo -e "  ${YELLOW}Warning: jq not found. Using basic JSON parsing.${NC}"
    echo -e "  ${WHITE}For better reliability, install jq: https://stedolan.github.io/jq/${NC}"
    echo ""
fi

# Check for gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "  ${RED}Error: GitHub CLI (gh) not found.${NC}"
    echo -e "  ${WHITE}Install from: https://cli.github.com/${NC}"
    exit 1
fi

# Check for existing session
if [[ -f "$STATE_FILE" ]]; then
    if $RESUME; then
        session_id=$(json_get "$STATE_FILE" "session_id")
        phase=$(json_get "$STATE_FILE" "phase")
        status=$(json_get "$STATE_FILE" "status")
        
        echo -e "  ${GREEN}Resuming session: $session_id${NC}"
        write_status "Phase" "$phase"
        write_status "Status" "$status"
    elif [[ -z "$TASK" ]]; then
        session_id=$(json_get "$STATE_FILE" "session_id")
        echo -e "  ${YELLOW}Existing session found: $session_id${NC}"
        read -p "  Resume existing session? (yes/no): " choice
        
        if [[ "$choice" =~ ^(y|yes|Y|YES)$ ]]; then
            RESUME=true
        else
            echo -e "  ${WHITE}Clearing existing session...${NC}"
            rm -rf "$STM_DIR"
        fi
    fi
fi

# Validate inputs
if [[ ! -f "$STATE_FILE" ]] && [[ -z "$TASK" ]]; then
    echo -e "  ${RED}Usage: $0 \"Your development task\"${NC}"
    echo -e "  ${RED}       $0 --resume${NC}"
    exit 1
fi

# Initialize if needed
if [[ ! -f "$STATE_FILE" ]]; then
    initialize_stm "$TASK"
fi

# Set initial prompt
if [[ -n "$TASK" ]] && ! $RESUME; then
    prompt="$TASK"
else
    prompt="Continue the development task"
fi

# Main loop
iteration=0
max_iterations=100

while true; do
    ((iteration++))
    
    # Read current state
    phase=$(json_get "$STATE_FILE" "phase")
    status=$(json_get "$STATE_FILE" "status")
    phase_id=$(json_get_num "$STATE_FILE" "phase_id")
    
    # Check completion
    if [[ "$status" == "complete" ]] || [[ "$phase" == "complete" ]]; then
        break
    fi
    
    # Check iteration limit
    if [[ $iteration -ge $max_iterations ]]; then
        echo ""
        echo -e "  ${RED}Maximum iterations reached. Something may be wrong.${NC}"
        echo -e "  ${YELLOW}STM preserved for debugging at $STM_DIR${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "  ${GRAY}─────────────────────────────────────────────────${NC}"
    echo -e "  ${WHITE}Iteration $iteration${NC}"
    write_phase $phase_id
    show_progress
    
    # Check for timeout
    if check_timeout; then
        echo -e "  ${YELLOW}⚠ Heartbeat timeout detected. Restarting agent...${NC}"
    fi
    
    # Handle user questions
    if handle_user_question; then
        continue
    fi
    
    # Handle approval phase
    if [[ "$status" == "waiting_for_user" ]] && [[ "$phase" == "approval" ]]; then
        handle_approval
        continue
    fi
    
    # Run the agent
    invoke_ralph "$prompt"
    
    # After first invocation, always use continue prompt
    prompt="Continue the development task"
    
    # Read updated state
    if [[ ! -f "$STATE_FILE" ]]; then
        echo -e "  ${RED}Error: State file missing after agent run${NC}"
        exit 1
    fi
    
    status=$(json_get "$STATE_FILE" "status")
    
    # Handle error status
    if [[ "$status" == "error" ]]; then
        error_msg=$(json_get "$STATE_FILE" "error")
        echo ""
        echo -e "  ${RED}⚠ Agent reported an error:${NC}"
        echo -e "    ${RED}$error_msg${NC}"
        
        read -p "  Retry? (yes/no): " choice
        if [[ ! "$choice" =~ ^(y|yes|Y|YES)$ ]]; then
            echo -e "  ${YELLOW}Exiting. STM preserved for debugging.${NC}"
            exit 1
        fi
    fi
    
    # Small delay between iterations
    sleep 0.5
done

# Completion
write_header "Task Complete!"

session_id=$(json_get "$STATE_FILE" "session_id")

echo -e "  ${GREEN}Ralph has completed the development task.${NC}"
echo ""
write_status "Session" "$session_id"
write_status "Total Iterations" "$iteration"
echo ""

# Check for PR description
if [[ -f "PR_DESCRIPTION.md" ]]; then
    echo -e "  ${WHITE}PR description saved to: PR_DESCRIPTION.md${NC}"
fi

echo ""
echo -e "  ${WHITE}The .ralph-stm directory can be safely removed.${NC}"
echo ""

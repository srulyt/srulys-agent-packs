# State Management Patterns

How to manage workflow state for multi-agent systems.

## Core Principles

1. **Filesystem-based**: State lives in files, not memory
2. **Session isolation**: Each session has its own directory
3. **Git-friendly**: State directories can be gitignored
4. **Recovery-capable**: Can resume from any state

## Standard Directory Structure

```
.{system-name}/
├── current-session.json        # Pointer to active session
├── sessions/                   # Active sessions
│   └── {session-id}/
│       ├── state.json          # Workflow state
│       ├── context/            # Input files
│       │   ├── user-request.md
│       │   └── decisions.md
│       └── artifacts/          # Output files
│           ├── design.md
│           └── manifest.json
└── history/                    # Archived sessions
    └── {old-session-id}/
```

## Session ID Format

Pattern: `{YYYY-MM-DD}-{8-char-hex}`

Examples:
- `2026-02-23-a1b2c3d4`
- `2026-02-23-deadbeef`

Generation:
- Date: Current UTC date
- Hex: Random 8-character hexadecimal

## State File Schemas

### current-session.json

```json
{
  "active_session": "2026-02-23-a1b2c3d4",
  "updated_at": "2026-02-23T09:00:00Z"
}
```

### state.json

```json
{
  "session_id": "2026-02-23-a1b2c3d4",
  "version": "1.0.0",
  "created_at": "2026-02-23T09:00:00Z",
  "updated_at": "2026-02-23T09:30:00Z",
  "phase": "intake|design|review|approval|build|complete",
  "mode": "creation|improvement",
  "iteration": 1,
  "target": {
    "platform": "roo|copilot",
    "name": "my-agent-pack"
  },
  "flags": {
    "user_approved": false,
    "review_passed": false
  },
  "deliverables": {
    "architecture": null,
    "artifacts": []
  },
  "errors": []
}
```

## State Transitions

```
intake → design → review → approval → build → complete
                    │          │
                    │          └── (changes requested)
                    │                    │
                    └────────────────────┘
```

**Transition Rules**:
- `intake → design`: Requirements captured
- `design → review`: Architecture written
- `review → approval`: Review passed
- `approval → build`: User approved
- `build → complete`: All artifacts created
- `approval → design`: Changes requested (increment iteration)

## Atomic Updates

Always write complete state files:

```javascript
// Read current
const state = JSON.parse(read("state.json"));

// Modify
state.phase = "build";
state.updated_at = new Date().toISOString();

// Write complete file
write("state.json", JSON.stringify(state, null, 2));
```

**Never** do partial updates to JSON files.

## Recovery Patterns

### Session Recovery

On startup:
1. Read `current-session.json`
2. Load active session's `state.json`
3. Resume from recorded phase

### Phase Recovery

For each phase, check preconditions:
- `design`: Has `context/user-request.md`?
- `review`: Has `artifacts/architecture.md`?
- `build`: Has approved architecture?
- `complete`: Has build manifest?

### Error Recovery

```json
{
  "errors": [
    {
      "timestamp": "2026-02-23T09:25:00Z",
      "phase": "build",
      "message": "File creation failed",
      "recoverable": true
    }
  ]
}
```

## Session Lifecycle

### Create Session
```
1. Generate session ID
2. Create session directory
3. Initialize state.json
4. Update current-session.json
```

### Archive Session
```
1. Move session dir to history/
2. Update current-session.json (clear or set new)
3. Optionally compress history
```

### Resume Session
```
1. Read current-session.json
2. Load state.json from sessions/{id}/
3. Continue from recorded phase
```

## Gitignore Patterns

Add to repository `.gitignore`:

```gitignore
# Agent system state directories
.{system-name}/
```

For agent packs repository:
```gitignore
agent-packs/**/.{system-name}/
```

## Multi-User Considerations

For systems with multiple concurrent users:

1. **User-prefixed sessions**: `{user}-{date}-{hex}`
2. **Lock files**: Prevent concurrent edits
3. **Separate state dirs**: One per user if needed

## Platform Differences

### Copilot CLI
- State in `.copilot-{system}/`
- Sessions auto-close on completion
- No explicit context continuity

### Roo Code
- State in `.{system}/` or `.factory/`
- Sessions can span multiple conversations
- Manual session management

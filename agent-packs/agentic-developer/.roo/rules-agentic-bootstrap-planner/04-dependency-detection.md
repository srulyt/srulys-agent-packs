# Dependency Detection

This document defines the dependency detection logic used in Phase 3 (Dependency Check) of the unified workflow.

## Purpose

Detect missing development tools BEFORE full planning begins, allowing users to install required dependencies in a single batch rather than encountering failures mid-execution.

## Detection Process

### Step 1: Parse PRD for Technology Stack

Scan the PRD for technology indicators:

| Indicator Pattern | Implies |
|-------------------|---------|
| "React", "Vue", "Angular", "Next.js" | Node.js |
| "TypeScript", "npm", "yarn", "pnpm" | Node.js |
| "Python", "Django", "Flask", "FastAPI" | Python |
| "Rust", "Cargo" | Rust |
| "Go", "Golang" | Go |
| "Docker", "container" | Docker |
| "Kubernetes", "k8s" | kubectl |
| ".NET", "C#", "ASP.NET" | dotnet |
| "Java", "Spring", "Maven", "Gradle" | Java (JDK) |
| "Ruby", "Rails" | Ruby |
| "PHP", "Laravel", "Composer" | PHP, Composer |

### Step 2: Build Required Tools List

Based on PRD analysis, build a list of required CLI tools:

```
required_tools = [
  { name: "git", required: true },  // Always required
  { name: "node", required: <from_prd> },
  { name: "python", required: <from_prd> },
  // ... etc
]
```

**Note**: Git is ALWAYS required for any project.

### Step 3: Execute Detection Commands

For each required tool, run the detection command and parse output.

---

## Tool Detection Matrix

| Tool | Detection Command (Windows) | Detection Command (Unix) | Expected Pattern | Min Version |
|------|----------------------------|--------------------------|------------------|-------------|
| Git | `git --version` | `git --version` | `git version \d+\.\d+` | 2.0 |
| Node.js | `node --version` | `node --version` | `v\d+\.\d+\.\d+` | 18.0 |
| npm | `npm --version` | `npm --version` | `\d+\.\d+\.\d+` | 8.0 |
| pnpm | `pnpm --version` | `pnpm --version` | `\d+\.\d+\.\d+` | 8.0 |
| yarn | `yarn --version` | `yarn --version` | `\d+\.\d+\.\d+` | 1.22 |
| Python | `python --version` | `python3 --version` | `Python \d+\.\d+` | 3.9 |
| pip | `pip --version` | `pip3 --version` | `pip \d+\.\d+` | 21.0 |
| Rust | `rustc --version` | `rustc --version` | `rustc \d+\.\d+` | 1.70 |
| Cargo | `cargo --version` | `cargo --version` | `cargo \d+\.\d+` | 1.70 |
| Go | `go version` | `go version` | `go\d+\.\d+` | 1.21 |
| Docker | `docker --version` | `docker --version` | `Docker version \d+\.\d+` | 20.0 |
| kubectl | `kubectl version --client` | `kubectl version --client` | `Client Version` | 1.25 |
| .NET | `dotnet --version` | `dotnet --version` | `\d+\.\d+\.\d+` | 6.0 |
| Java | `java -version` | `java -version` | `version "\d+` | 17 |
| Maven | `mvn --version` | `mvn --version` | `Apache Maven \d+\.\d+` | 3.8 |
| Gradle | `gradle --version` | `gradle --version` | `Gradle \d+\.\d+` | 8.0 |
| Ruby | `ruby --version` | `ruby --version` | `ruby \d+\.\d+` | 3.0 |
| PHP | `php --version` | `php --version` | `PHP \d+\.\d+` | 8.0 |
| Composer | `composer --version` | `composer --version` | `Composer version \d+` | 2.0 |

---

## Version Checking Patterns

### Extracting Version Numbers

Use regex to extract version from command output:

```javascript
// Node.js example
const output = "v18.17.0";
const match = output.match(/v(\d+)\.(\d+)\.(\d+)/);
const version = { major: 18, minor: 17, patch: 0 };

// Python example
const output = "Python 3.11.4";
const match = output.match(/Python (\d+)\.(\d+)/);
const version = { major: 3, minor: 11 };
```

### Version Comparison Logic

```
function meetsMinVersion(detected, minimum):
  if detected.major > minimum.major: return true
  if detected.major < minimum.major: return false
  if detected.minor >= minimum.minor: return true
  return false
```

---

## Detection Result Categories

After running all detection commands, categorize each tool:

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Installed | Tool found, meets minimum version | No action |
| ⚠️ Outdated | Tool found, below minimum version | Include in install script |
| ❌ Missing | Tool not found | Include in install script |
| ⏭️ Optional | Tool not required by PRD | Skip |

---

## Script Generation Trigger Conditions

Generate installation scripts when ANY of these conditions are met:

1. **Any required tool is missing** (status = ❌)
2. **Any required tool is outdated** (status = ⚠️)
3. **User explicitly requested script** (rare, via orchestrator flag)

### Do NOT Generate Scripts When:

- All required tools are installed and meet minimum versions
- No technology stack detected in PRD (edge case - return warning)

---

## Platform Detection

Determine the user's platform from environment details:

| Environment Indicator | Platform | Script Type |
|-----------------------|----------|-------------|
| `cmd.exe`, `PowerShell`, `Windows` | Windows | `.ps1` |
| `bash`, `zsh`, `/bin/`, `Darwin` | macOS | `.sh` |
| `bash`, `zsh`, `/bin/`, `Linux` | Linux | `.sh` |

---

## Output Artifacts

### 1. Dependency Report

Always generate: `.agent-memory/runs/<run-id>/dependency-report.md`

See template: [`.roo/templates/agentic-dependency-report.md`](../../templates/agentic-dependency-report.md)

### 2. Installation Script (Conditional)

Only if tools are missing/outdated:

- Windows: `.agent-memory/runs/<run-id>/install-dependencies.ps1`
- Unix: `.agent-memory/runs/<run-id>/install-dependencies.sh`

See templates:
- [`.roo/templates/agentic-install-deps-windows.ps1`](../../templates/agentic-install-deps-windows.ps1)
- [`.roo/templates/agentic-install-deps-unix.sh`](../../templates/agentic-install-deps-unix.sh)

---

## Error Handling

### Command Execution Failures

If a detection command fails (non-zero exit, timeout):

1. Assume tool is **missing** (not installed)
2. Log the error in events
3. Continue with next tool
4. Include in install script

### No Technology Stack Detected

If PRD contains no recognizable technology indicators:

1. Return warning to orchestrator
2. Include only Git in required tools (always needed)
3. Generate minimal dependency report

---

## Communication Protocol

After dependency detection completes, return to orchestrator via `attempt_completion`:

**All Tools Present**:
```
Dependency check complete.

Status: All required tools installed.
Report: .agent-memory/runs/<run-id>/dependency-report.md

No installation required. Ready for Phase 4.
```

**Tools Missing**:
```
Dependency check complete.

Status: Missing dependencies detected.
Report: .agent-memory/runs/<run-id>/dependency-report.md
Script: .agent-memory/runs/<run-id>/install-dependencies.{ps1|sh}

Missing tools: Node.js, Docker

Orchestrator should present options to user.
```

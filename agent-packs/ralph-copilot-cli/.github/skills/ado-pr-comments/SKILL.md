---
name: ralph-ado-pr-comments
description: Uses Azure CLI (az) to load Azure DevOps pull request comments and turn them into actionable task input. Use when tasks reference ADO review feedback, PR comments, or reviewer threads.
---

# Ralph ADO PR Comments Skill

Use this skill when the task requires incorporating Azure DevOps PR feedback into implementation work.

## Goal

- Retrieve PR comment threads from ADO using `az`.
- Extract actionable comments (ignore deleted/empty comments).
- Convert comments into a structured task input section.

## Preconditions

- Azure CLI installed (`az`).
- Azure DevOps extension installed:
  - `az extension add --name azure-devops`
- Authenticated session (`az login` and/or `az devops login`).

## Required Inputs

- `organization`: e.g. `https://dev.azure.com/contoso`
- `project`: ADO project name
- `repository`: repo name or ID
- `pull_request_id`: numeric PR ID

## Retrieval Command

```bash
az repos pr thread list \
  --organization "${organization}" \
  --project "${project}" \
  --repository "${repository}" \
  --id "${pull_request_id}" \
  --output json
```

## Extraction Rules

- Include only comments where:
  - `isDeleted != true`
  - `content` is present and non-empty
- Preserve author names and comment text.
- Keep original intent; do not paraphrase away technical details.

## Task Input Template

Use this exact structure as the injected task context:

```markdown
## Azure DevOps PR Comment Context

Source:
- Organization: {organization}
- Project: {project}
- Repository: {repository}
- Pull Request: {pull_request_id}

Comments:
- [Author A] {comment}
- [Author B] {comment}
```

## How to Use with Ralph Loop

PowerShell loop supports direct input wiring:

```powershell
.\ralph-loop.ps1 -Task "Address review feedback" \
  -IncludeAdoPrComments \
  -AdoOrganization "https://dev.azure.com/contoso" \
  -AdoProject "MyProject" \
  -AdoRepository "my-repo" \
  -AdoPullRequestId 123
```

This mode works with:
- `-Task`
- `-PromptFile`
- `-TaskListFile`

## Failure Handling

If retrieval fails:
- Surface the exact failure cause (auth/permissions/not found).
- Do not silently continue with partial results.
- Ask user to verify ADO parameters and CLI auth.

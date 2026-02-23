---
name: ralph-ado-pr-comments
description: Uses an ADO MCP server when available to load Azure DevOps pull request comments, and falls back to Azure CLI (az) when MCP is unavailable. Use when tasks reference ADO review feedback, PR comments, or reviewer threads.
---

# Ralph ADO PR Comments Skill

Use this skill when the task requires incorporating Azure DevOps PR feedback into implementation work.

## Goal

- Retrieve PR comment threads from ADO using MCP first, then `az` as fallback.
- Extract actionable comments (ignore deleted/empty comments).
- Convert comments into a structured task input section.

## Preconditions

- Preferred path: an Azure DevOps MCP server is configured and available in the current tool list.
- Fallback path (if MCP unavailable):
  - Azure CLI installed (`az`).
  - Azure DevOps extension installed: `az extension add --name azure-devops`
  - Authenticated session (`az login` and/or `az devops login`).

## Required Inputs

- `organization`: e.g. `https://dev.azure.com/contoso`
- `project`: ADO project name
- `repository`: repo name or ID
- `pull_request_id`: numeric PR ID

## Derive Inputs from ADO PR URL

If the user provides a PR URL, extract all required inputs directly from it.

Example URL:

`https://dev.azure.com/contoso/My%20Project/_git/myrepo/pullrequest/123456`

Extract as:
- `organization`: `https://dev.azure.com/contoso`
- `project`: `My Project` (URL-decoded from `My%20Project`)
- `repository`: `myrepo`
- `pull_request_id`: `123456`

Parsing rules:
1. Use the URL path pattern: `/{project}/_git/{repository}/pullrequest/{id}`
2. `organization` is scheme + host + first path segment after host (`https://dev.azure.com/{org}`)
3. URL-decode `project` and `repository` segments before using them
4. `pull_request_id` must be parsed as an integer
5. If URL does not match expected pattern, ask for explicit `organization`, `project`, `repository`, `pull_request_id`

## Retrieval Strategy (MCP First, CLI Fallback)

1. Check whether an Azure DevOps MCP server is available in the current environment.
  - Look for MCP server/tool names containing `ado`, `azure-devops`, or `devops`.
2. If available, retrieve PR threads using MCP tools.
3. If unavailable, or MCP retrieval fails, fall back to Azure CLI.
4. If both methods fail, surface the specific error and stop.

## Fallback Retrieval Command (Azure CLI)

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

## How to Use with Ralph

Ralph loop input should carry intent, not CLI wiring. To trigger this skill, include ADO PR context needs directly in the task prompt or prompt file, for example:

- "Use Azure DevOps PR comments from org/project/repo/PR 123 as planning input."

During planning/execution, Ralph should load this skill and retrieve PR comments via MCP first (or `az` fallback) per this skill's retrieval strategy.

## Failure Handling

If retrieval fails:
- Surface the exact failure cause (auth/permissions/not found).
- If MCP failed, explicitly note fallback to `az` was attempted.
- Do not silently continue with partial results.
- Ask user to verify ADO parameters and either MCP availability or CLI auth.

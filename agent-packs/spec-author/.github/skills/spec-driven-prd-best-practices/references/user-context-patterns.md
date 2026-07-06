# User-Context Patterns (embeddable reference templates)

Lightweight, spec-embeddable templates for the five user-context
concepts named in [`spec-driven-prd-best-practices` §11](../SKILL.md#11-user-context-weaving-personas-jtbd-journeys-roles).
The drafter **references** these shapes; it does not literal-copy
them. Every template is industry-neutral. Populate cells from the
context pack / interview answers — never fabricate a persona, job,
journey step, or role to fill a cell (leave it blank or raise an
`OQ-NN`).

Which of these appear in a spec depends on whether the
`experience-surface` axis fired:

- **Every spec (woven):** the Usage Context Block, the JTBD column
  on the mandatory `Users & Personas` table, and role-conditioned
  EARS FRs.
- **UI-forward specs only (dedicated section):** the expanded
  Persona Cards, the JTBD table with opportunity scores, the Journey
  Summary Table(s), and the Roles × Permissions matrix — all
  consolidated under "User Experience: Personas, Journeys & Roles".

---

## 1. Usage Context Block (woven into Problem Statement / Goals)

Ground the problem in observed usage. Cite verifiable sources.

```markdown
### Usage Context

| Signal type        | Finding                                                  | Source / date       |
|--------------------|----------------------------------------------------------|---------------------|
| Feature adoption   | Only 18% of activated accounts use CSV export today      | Amplitude, 2025-Q1  |
| Funnel drop-off    | 42% abandon onboarding at step 3 of 5                    | Mixpanel, 2025-03   |
| Support volume     | "Can't find my reports" is #2 ticket category (340/mo)   | Zendesk, 2025-04    |
| Qualitative signal | 6/8 interviews cite "too many clicks to download"        | UXR study #24, 2025 |

**Baseline metric this spec moves:** CSV export usage rate (18% → ≥35% within 90 days).
**Anti-goal:** do not introduce a net-new UI pattern — re-use the existing action menu.
```

> **Rule of thumb:** if a requirement traces to no usage signal,
> research finding, or strategic goal, it is a removal candidate.

Source: Cagan / SVPG — Product Discovery
(https://www.svpg.com/product-discovery/); Atlassian — PRD Guide
(https://www.atlassian.com/agile/product-management/requirements);
NNGroup — Analytics + Persona Segments
(https://www.nngroup.com/articles/analytics-persona-segment/).

---

## 2. Persona Card (dedicated section) / persona table row (woven)

Condensed, half-page card per persona; max 3–4 personas per spec.
Label proto-personas (assumption-only) explicitly.

```markdown
### Persona: "Maya the Marketing Analyst"

| Field            | Detail                                                        |
|------------------|---------------------------------------------------------------|
| Role / context   | Marketing Ops Manager, B2B SaaS; uses product 4–5×/week, desktop |
| Primary job(s)   | When it's Monday reporting time, I want to produce the weekly report without leaving the product, so I can spend time analysing not formatting |
| Top pains        | Manual CSV → Excel dance; no scheduling; no shareable link     |
| Expected outcome | Report in the CMO's inbox before the 9 AM stand-up             |
| Validated by     | 6 interviews (UXR #24, Feb 2025); Amplitude "frequent exporters" segment |
```

Omit irrelevant demographics. Distinguish **proto-persona**
(assumption), **qualitative** (5–30 interviews), **statistical**
(survey + cluster) — NNGroup persona types.

Source: NNGroup — Personas: Study Guide
(https://www.nngroup.com/articles/persona/) and Persona Types
(https://www.nngroup.com/articles/persona-types/); Roman Pichler —
10 Tips for Agile Personas
(https://www.romanpichler.com/blog/10-tips-agile-personas/).

---

## 3. JTBD table with opportunity score (dedicated) / JTBD column (woven)

Job-statement form: **When [situation], I want to [motivation], so I
can [outcome].** Keep the job solution-agnostic (distinct from a user
story).

```markdown
### Jobs To Be Done

| #  | Job statement                                                    | Persona     | Importance | Satisfaction | Opportunity |
|----|------------------------------------------------------------------|-------------|------------|--------------|-------------|
| J1 | When sharing results with leadership, I want one-click export…   | Maya        | 9/10       | 3/10         | HIGH        |
| J2 | When auditing user activity, I want a filterable audit log…      | Sam (Admin) | 8/10       | 5/10         | MEDIUM      |
```

> **Opportunity score (Ulwick ODI):**
> `Importance + max(Importance − Satisfaction, 0)`. Scores above ~10
> (1–10 scale) signal underserved jobs worth addressing. Annotate
> each FR with the job it addresses (`Addresses: J1`).

Source: Strategyn — JTBD Theory / ODI Process
(https://strategyn.com/jobs-to-be-done/jobs-to-be-done-theory/);
Ulwick — *Jobs to Be Done: Theory to Practice* (2016); Christensen —
*Competing Against Luck* (2016).

---

## 4. Journey Summary Table (dedicated section)

One table per primary affected journey. Highlight the phase this
spec addresses. Each step decomposes into an event-driven FR/AC.

```markdown
## User Journey: "Maya shares weekly results with leadership"
**Actor:** Maya (Marketing Analyst) — **Scenario:** Monday reporting cycle — **Goal:** report in CMO inbox before 9 AM

| Phase      | Actor / Role | Trigger                     | System response / action        | Success signal        | Pain / Opportunity            |
|------------|--------------|-----------------------------|---------------------------------|-----------------------|-------------------------------|
| Prepare    | Maya         | Opens product, Reports view | Shows last-used report          | Remembers last config | Save/remember filter state    |
| Configure  | Maya         | Applies filters + date range| Applies segment                 | Correct data shown    | One-click "last week" preset  |
| Export     | Maya         | Clicks Export               | Generates formatted file        | File downloaded ≤5s   | ← **this spec addresses here**|
| Share      | Maya         | Sends to CMO                | Produces shareable link         | CMO opens link        | Live source-of-truth link     |
```

Depth guidance: a micro-task touches only 2–3 phases; a full
workflow includes all phases. Keep the table to one printed page.
A macro **journey** (why it matters across the user's life) is
distinct from a micro **user flow** (exact screen steps) — link the
flow/wireflow rather than inlining it.

Source: NNGroup — Journey Mapping 101
(https://www.nngroup.com/articles/journey-mapping-101/) and User
Journeys vs. User Flows
(https://www.nngroup.com/articles/user-journeys-vs-user-flows/).

---

## 5. Roles × Permissions matrix + access-control rules (dedicated section)

Design to **deny-by-default, least-privilege, server-side
enforcement**. UI hiding of actions is cosmetic only.

```markdown
## Roles & permissions
**Access-control model:** RBAC (+ ReBAC rule ACR-01). **Posture:** deny by default; server-side enforcement.

### Role definitions
| Role   | Description                                          |
|--------|------------------------------------------------------|
| Owner  | Full control; billing; can delete workspace          |
| Admin  | Manage members, settings, integrations; cannot delete|
| Editor | Create/edit/publish content; no user management      |
| Viewer | Read-only; cannot export PII                          |

### Permissions × roles matrix
| Permission             | Owner | Admin | Editor | Viewer |
|------------------------|:-----:|:-----:|:------:|:------:|
| View dashboard         |  ✅   |  ✅   |   ✅   |   ✅   |
| Create/edit reports    |  ✅   |  ✅   |   ✅   |   ❌   |
| Export data (with PII) |  ✅   |  ✅   |   ❌   |   ❌   |
| Manage team members    |  ✅   |  ✅   |   ❌   |   ❌   |
| Delete workspace       |  ✅   |  ❌   |   ❌   |   ❌   |

### Access-control rules & exceptions
| Rule ID | Description                                                                 |
|---------|-----------------------------------------------------------------------------|
| ACR-01  | An Editor may edit only reports they created or that were shared with them (ReBAC) |
| ACR-02  | All permission checks are server-side; UI hiding is cosmetic only           |
```

Convention: ✅ = permitted; ❌ = denied by default; every ✅ must be
justifiable by a requirement. Express role-conditioned behaviour
ALSO as EARS optional-feature FRs ("Where <role> is included, the
<system> shall …") and pin the deny path in an AC ("Given a Viewer,
when they attempt PII export, then the system returns 403 and no data
is returned"). Choose **RBAC** for job-function access; add **ABAC**
for attribute/time/region rules; use **ReBAC** for
ownership/relationship access.

Source: OWASP — Authorization Cheat Sheet
(https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
and Top 10 A01:2021 Broken Access Control
(https://owasp.org/Top10/A01_2021-Broken_Access_Control/); NIST
SP 800-53 Rev.5 RBAC definition
(https://csrc.nist.gov/glossary/term/role_based_access_control).

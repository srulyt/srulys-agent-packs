# Section Catalogue (machine-readable)

This file is a YAML representation of the catalogue declared in
SKILL.md. The drafter and critic parse it to apply identical
inclusion logic.

```yaml
mandatory:
  - { name: "Document Information",        id_convention: null }
  - { name: "Problem Statement",           id_convention: null }
  - { name: "Goals & Success Metrics",     id_convention: null }
  - { name: "Users & Personas",            id_convention: null }
  - { name: "Solution Summary",            id_convention: null }
  - { name: "Functional Requirements",     id_convention: "FR-NN" }
  - { name: "Acceptance Criteria",         id_convention: "AC-NN" }
  - { name: "Risks & Mitigations",         id_convention: "R-NN" }
  - { name: "Open Questions",              id_convention: "OQ-NN" }
  - { name: "Out of Scope",                id_convention: null }

gated:
  - { name: "Stakeholders & Reviewers",       axis: "cross-team-scope" }
  - { name: "Dependencies & Assumptions",     axis: "cross-team-scope" }
  - { name: "Non-Functional Requirements",    axis: "infra-platform-change", id_convention: "NFR-NN" }
  - { name: "Capacity & Performance Targets", axis: "infra-platform-change" }
  - { name: "Security & Compliance",          axis: "security-surface" }
  - { name: "Threat Model Summary",           axis: "security-surface" }
  - { name: "Regulatory & Privacy",           axis: "regulatory-load" }
  - { name: "Data Model",                     axis: "persistence-data" }
  - { name: "Telemetry & Analytics",          axis: "persistence-data" }
  - { name: "API Contract",                   axis: "public-api-surface" }
  - { name: "Versioning & Deprecation Policy",axis: "public-api-surface" }
  - { name: "Rollout Plan",                   axis: "rollout-risk" }
  - { name: "Rollback Strategy",              axis: "rollout-risk" }
  - { name: "Test Scenarios",                 axis: "cross-team-scope|infra-platform-change", id_convention: "TS-NN" }
  - { name: "Appendix: Glossary",             axis: "optional" }
  - { name: "Appendix: NFR↔FR Traceability",  axis: "infra-platform-change" }
  - { name: "Appendix: Aliases & Deprecations", axis: "update-mode-rename" }

heuristic:
  cross-team-scope:
    high_when: "more than one engineering team owns delivery; named partner orgs; cross-org dependencies"
  security-surface:
    high_when: "auth flow change; new data egress; PII handling; supply-chain change; new trust boundary"
  infra-platform-change:
    high_when: "new service; new region; new datastore; breaking API; capacity-shaping change"
  regulatory-load:
    high_when: "any regulatory or compliance review is in scope; user names the regime"
    note: "Defer specifics to user-supplied instructions; never encode a specific regime's conventions in this catalogue."
  persistence-data:
    high_when: "new schema; retention-policy change; new analytics events"
  public-api-surface:
    high_when: "external consumers; SDK changes; webhooks; customer-visible API"
  rollout-risk:
    high_when: "phased release; feature flags; kill switch needed; customer migration"
```

## Decision rule (for both drafter and critic)

For each `gated` section:

1. If at least one signal in its axis fires given the inputs →
   `gated-included(<axis>)` with the matching signal as
   justification.
2. Otherwise → `gated-omitted` with a one-line reason
   (typically "no <axis> signal in inputs").

For ambiguous axes (the inputs neither confirm nor deny), default
to **omit** but list the ambiguity in `open-questions-json` so
Stop A surfaces it.

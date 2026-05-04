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
  - { name: "Functional Requirements",     id_convention: "FR-NN; ACs nested as AC-<FR>.<n>" }
  - { name: "Risks & Mitigations",         id_convention: "R-NN" }
  - { name: "Open Questions",              id_convention: "OQ-NN" }
  - { name: "Out of Scope",                id_convention: null }

# Note: "Acceptance Criteria" is NOT a separate top-level mandatory
# section. ACs live inside each FR with hierarchical IDs
# (AC-<FR>.<n>) — this eliminates FR↔AC traceability mismatches.

gated:
  - { name: "Stakeholders & Reviewers",        axis: "cross-team-scope",                     requires_spec_kind: "any" }
  - { name: "Dependencies & Assumptions",      axis: "cross-team-scope",                     requires_spec_kind: "any" }
  - { name: "Non-Functional Requirements",     axis: "infra-platform-change",                requires_spec_kind: "any", id_convention: "NFR-NN" }
  - { name: "Capacity & Performance Targets",  axis: "infra-platform-change",                requires_spec_kind: "technical|mixed" }
  - { name: "Security & Compliance",           axis: "security-surface",                     requires_spec_kind: "any" }
  - { name: "Threat Model Summary",            axis: "security-surface",                     requires_spec_kind: "technical|mixed" }
  - { name: "Regulatory & Privacy",            axis: "regulatory-load",                      requires_spec_kind: "any" }
  - { name: "Data Model",                      axis: "persistence-data",                     requires_spec_kind: "technical|mixed" }
  - { name: "Telemetry & Analytics",           axis: "persistence-data",                     requires_spec_kind: "any" }
  - { name: "API Contract",                    axis: "public-api-surface",                   requires_spec_kind: "technical|mixed" }
  - { name: "Versioning & Deprecation Policy", axis: "public-api-surface",                   requires_spec_kind: "technical|mixed" }
  - { name: "Rollout Plan",                    axis: "rollout-risk",                         requires_spec_kind: "any" }
  - { name: "Rollback Strategy",               axis: "rollout-risk",                         requires_spec_kind: "any" }
  - { name: "Test Scenarios",                  axis: "cross-team-scope|infra-platform-change", requires_spec_kind: "any", id_convention: "TS-NN" }
  - { name: "Technical Considerations",        axis: "any-technical-signal-in-mixed-mode",   requires_spec_kind: "mixed" }
  - { name: "Appendix: Glossary",              axis: "optional",                             requires_spec_kind: "any" }
  - { name: "Appendix: NFR↔FR Traceability",   axis: "infra-platform-change",                requires_spec_kind: "technical|mixed" }
  - { name: "Appendix: Aliases & Deprecations",axis: "update-mode-rename",                   requires_spec_kind: "any" }

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

1. If at least one signal in its axis fires given the inputs **AND**
   the user-chosen `spec_kind` satisfies the section's
   `requires_spec_kind` constraint → `gated-included(<axis>)` with
   the matching signal as justification.
2. If the axis fires but `spec_kind` does not satisfy
   `requires_spec_kind` → `gated-omitted-by-spec-kind` with a
   one-line reason.
3. Otherwise → `gated-omitted` with a one-line reason
   (typically "no <axis> signal in inputs").

For ambiguous axes (the inputs neither confirm nor deny), default
to **omit** but list the ambiguity in `open-questions-json` so
Stop A surfaces it.

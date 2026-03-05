# Assumptions and Open Questions

## Assumptions

- **Default capacity admin permissions include limited item visibility.** The speaker assumes capacity admins should see workspaces and items underneath for usage tracking, but this is his personal expectation — not a validated customer requirement.
- **Domain admins should not see data by default.** Stated as probable intent ("probably not"), not confirmed with customer research or product requirements.
- **Security admin is a viable vertical role.** The concept of a security-only admin (permissions, network security, CMK, policies) is proposed as an example but has not been validated as a real customer need.
- **Metadata maintainer is a viable vertical role.** Similarly proposed as an example (descriptions and tags only) without customer validation.
- **Every item-level permission should be assignable to admin roles.** The speaker states this as a design goal, but feasibility and scoping have not been discussed.
- **Workspace-to-item inheritance model is working correctly today and does not need changes.** Implied by the fact that only non-workspace admin roles are targeted for improvement.

## Open Questions

- **What specific permissions belong in each default admin role?** The transcript provides directional examples but no defined permission sets.
- **Will admin roles be fully customer-configurable or limited to predefined templates?** The speaker advocates for customer choice but does not specify the configuration model (custom roles vs. predefined role variants).
- **How will migration from hard-coded checks to the new RBAC model be executed?** Hundreds of hard-coded checks exist across the codebase; no migration strategy, sequencing, or timeline is discussed.
- **What is the expected scope, timeline, and resourcing for this work?** Not addressed in the transcript.
- **Will existing admin assignments be preserved during migration?** No backward-compatibility or transition plan is mentioned.
- **How does Entra ID integration constrain the RBAC design?** Fabric admin role originates from Entra ID; it is unclear how a new permission model would interact with external identity provider roles.
- **Are there performance or scale concerns with modeled permission checks replacing hard-coded checks?** Not discussed.

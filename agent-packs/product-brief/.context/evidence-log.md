# Evidence Log

| # | Claim | Source | Confidence | Notes |
|---|-------|--------|------------|-------|
| 1 | Only workspace admins have a modeled permission system; tenant, domain, and capacity admins lack any modeled permissions. | Admin roles transcript, 2026 | High | Core problem statement, repeated multiple times |
| 2 | Permissions for tenant, domain, and capacity admins are hard-coded throughout the codebase — tens if not hundreds of inline checks with no abstraction layer. | Admin roles transcript, 2026 | High | Technical root cause of all three business challenges |
| 3 | Admin roles are all-or-nothing with no granularity; there is no way to create vertical roles such as security admin or metadata maintainer. | Admin roles transcript, 2026 | High | |
| 4 | No permission inheritance exists from tenant, domain, or capacity containers down to items; Fabric only supports workspace-to-item inheritance today. | Admin roles transcript, 2026 | High | Contrasted with Azure's subscription-to-resource inheritance model |
| 5 | The proposed solution is a two-part RBAC model: (1) permissions on the container object itself, and (2) inherited permissions on items within the container. | Admin roles transcript, 2026 | High | |
| 6 | A capacity admin should by default be able to configure the capacity and have limited viewer permission on items underneath for usage tracking. | Admin roles transcript, 2026 | Medium | Stated as speaker's personal assumption, not a confirmed requirement |
| 7 | Domain admins should govern security and metadata but probably should not see data by default. | Admin roles transcript, 2026 | Medium | Stated as speaker's expectation, not validated with customers |
| 8 | The goal is to let customers decide what each admin type can do, replacing the current rigid system with configurable roles. | Admin roles transcript, 2026 | High | |
| 9 | Fabric admins inherit their role from Entra ID global admin and Power Apps admin roles; capacity admins originate from Azure; domain admins are delegated by tenant admins within Fabric. | Admin roles transcript, 2026 | High | Relevant for migration and integration constraints |

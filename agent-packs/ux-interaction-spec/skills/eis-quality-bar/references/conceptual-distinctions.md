# Conceptual distinctions — the 14 pairs (REQ-§44)

Many UX problems arise when these distinctions are accidentally collapsed.
Preserve them actively — in terminology, in section placement, and in review.

| # | Distinction | Collapsed when… | Keep them apart by… |
|---|---|---|---|
| 1 | requirement **vs** recommendation | a recommendation appears in EIS-§19 or as a `Status:`-bearing decision | recommendations live under `## Recommendations Awaiting Decision`; requirements carry a source |
| 2 | user role **vs** permission | the capability matrix has role columns but no `Conditions` column doing work | a role is *who someone is*; a permission is *what they may do under which conditions* |
| 3 | permission **vs** ownership | owners are given a role row instead of a derivation rule | ownership *derives* permissions; record the derivation in EIS-§7 `Inheritance / Overrides / Expiration` |
| 4 | discoverability **vs** access | one capability row covers "can see it exists" and "can use it" | two separate rows; a user who can discover but not access is the interesting case |
| 5 | access **vs** ability to administer | `Admin` column is `Yes` everywhere | administering a resource is not using it; say which admins may also use |
| 6 | object state **vs** user state | "user is pending" appears in an EIS-§8 model | objects have lifecycles; users have relationships to objects |
| 7 | user journey **vs** business workflow | EIS-§10 contains service names and internal steps | EIS-§10 is what the user experiences; EIS-§11 is what the system does |
| 8 | synchronous action **vs** asynchronous workflow | a flow ends at "access granted" with no pending state | async work needs a persistent, discoverable status and a return path |
| 9 | persistent state **vs** transient notification | EIS-§14 is the only place a status is recorded | a notification may be missed; state must survive it |
| 10 | conceptual model **vs** implementation model | EIS-§5 lists tables, services, or queues | EIS-§5 `User-facing vs implementation concepts` exists to sort exactly this |
| 11 | interaction specification **vs** visual design | a control type, layout, or colour appears | see `anti-requirements.md` |
| 12 | host-product convention **vs** competitor convention | RES-§5 merges the host column into the competitor columns | the host column is a *constraint*; competitor columns are *evidence* |
| 13 | evidence **vs** inference | a claim appears without an `EV-RS-###` or an explicit inference label | evidence has a source and a date; inference has a reasoning chain |
| 14 | error prevention **vs** error recovery | EIS-§15 lists only messages | prevention stops the state from arising; recovery gets the user out of it |

## Where the critic applies these

Check C-3 (anti-requirement lint) covers distinction 11. Check C-13 (layer
separation, REQ-§2) covers 7, 8, 10 and 11 together, reading `{out}/eis.md`.
Check C-12 covers 1. Check C-10 covers 13. The remainder are scored through
the Definition of Done and the quality bar by category.

## Terminology consequences (EIS-§6)

Where the input's vocabulary collapses a distinction, the glossary must say
so:

> **Access** — *(input uses "access" for both discoverability and use)*.
> In this specification, **discover** means a user can see the resource
> exists; **access** means the user holds an active entitlement to use it.
> Recommendation: adopt this split product-wide; `DEC-MD-002`.

Recording the split in the glossary is what stops the rest of the document
from silently re-collapsing it.

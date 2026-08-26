# Permissions and state (REQ-§11, §12)

## Permission and capability model — EIS-§7

Permission modeling is **mandatory** whenever access differs between users.
Do not stop at a role list.

Model at least: **actor/subject × resource/object × action × conditions**.

Actions to consider: discover · view metadata · view content · create · edit ·
delete · publish · share · request access · approve · reject · revoke ·
delegate · manage policy · administer · export · execute/use

### Six things to keep apart

Explicitly distinguish **discoverability**, **visibility**, **access**,
**use**, **modification**, and **administration**. These are six different
capabilities. A model that collapses them cannot express the most common
interesting case — a user who can see that something exists but cannot use it,
which is the entire premise of any access-request feature.

### Document when applicable

default permission · inherited permission · explicit permission ·
ownership-derived permission · organization-derived permission ·
group-derived permission · temporary permission · conditional permission ·
delegated authority · admin override · denial · precedence rules · revocation ·
expiration

These belong under `### Inheritance / Overrides / Expiration`. **Precedence
rules** are the ones most often omitted and most often needed: when an explicit
grant and an inherited denial collide, the specification must say which wins.

### The capability matrix

See the `eis-document-contracts` skill's `matrices.md` for the column
contract. Two rules bear repeating:

- **Do not invent permissions merely to fill the table.**
- **Unknown permission decisions must be explicitly flagged** —
  `Unknown — Q-MD-###`, never a guess, never a silent `No`.

## State models — EIS-§8

Identify every important object whose behavior changes over time and give each
an explicit state model.

```
Resource:  Draft → Published → Deprecated → Archived
Request:   Not requested → Pending → Approved → Provisioning → Active
```

with branches such as `Rejected`, `Cancelled`, `Failed`, `Expired`, `Revoked`.

For each state document:

| Field | Content |
|---|---|
| what it means | In user terms. |
| who can observe it | Which EIS-§4 actors, under which EIS-§7 conditions. |
| available actions | What can be done from here. |
| unavailable actions | What cannot, **and why** — probe 14 lives here. |
| entry conditions | What causes arrival. |
| exit conditions | What causes departure, and to where. |
| system behavior | What the system does while the object sits here. |
| relevant notifications | What is communicated on entry, per EIS-§14. |
| recovery behavior | Where applicable — how the object leaves a bad state. |

### Do not model only the happy path

Explicitly consider all fourteen:

pending · loading · processing · partial success · failure · retry ·
cancellation · expiration · revocation · stale state · concurrent
modification · duplicate actions · resource deletion · permission loss

Each either appears in the model, or is recorded in EIS-§16 as considered and
not applicable with a reason. A state model that goes
`Pending → Approved → Active` with no failure branch is not a state model; it
is a happy path with arrows.

Use Mermaid `stateDiagram-v2` where useful — supplementing the per-state
table, never replacing it. Every node in the diagram must be a state in the
table; every table state must be reachable in the diagram or explicitly
documented as terminal-on-entry.

## Object state versus user state

An object has a lifecycle. A user has a **relationship** to an object. "The
user is pending" is a category error — the *request* is pending, and the user
holds a pending request. Getting this wrong produces state models that cannot
express two simultaneous requests, or a user whose access differs per
resource.

## Async is a permission problem too

Model what happens when permissions change **while** an operation is in
flight: an approval granted by an approver who lost authority mid-flow, a
provisioning step that completes after the requester left the organization.
Each is an EIS-§8 transition, an EIS-§15 recovery, and usually an EIS-§16 edge
case.

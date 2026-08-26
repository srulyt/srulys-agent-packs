# Journeys, workflows, blueprints, entry points (REQ-§13, §14, §15, §17)

## User journeys — EIS-§10 (REQ-§13)

Define flows around **user goals**, not around screens.

Goals look like: Find a resource I can use · Request access · Approve
requests · Publish a product · Revoke a user's access · Transfer ownership ·
Understand why I cannot perform an action · Recover from a failed operation.

Each significant journey is a `###` block carrying all ten fields:

| Field | Content |
|---|---|
| Goal | What the actor is trying to achieve. |
| Actor | Who is performing it — an EIS-§4 name, verbatim. |
| Preconditions | What must already be true. |
| Entry points | How the journey can begin — see EIS-§9. |
| Primary path | The expected successful interaction. |
| Branches | Meaningful alternate paths. |
| Exit conditions | What constitutes completion. |
| Failure and recovery | What can go wrong and how the user recovers. |
| Resulting state | What changed, in EIS-§8 terms. |
| Cross-role consequences | What other actors now see or can do. |

`Cross-role consequences` is the field most often left empty and the one that
most often matters: an access request that changes nothing for the approver is
not modeled.

Use Mermaid flowcharts where useful.

## Never conflate journey with workflow — EIS-§11 (REQ-§14)

```
User experience:  Discover → Request → Pending → Notification → Open

Business/system:  Create request → determine approver → evaluate policy
                  → approve → provision entitlement → send notification
```

Both may be important. **Represent them separately.** EIS-§10 contains no
service names and no internal steps; EIS-§11 contains no claims about what the
user sees.

For multi-party workflows use swimlane-style representations or Mermaid
sequence diagrams.

### Asynchronous workflows (REQ-§19)

Do not represent an asynchronous operation as if it were a guaranteed
synchronous action. For every operation that may take time, document:

what happens immediately · what becomes pending · whether the user can leave ·
whether work continues · how completion is communicated · how the user can
find status later · whether cancellation is possible · what retry means · what
happens after partial success · what happens if permissions change while
processing

The last three are the ones inputs almost never specify and designers almost
always need.

## Service blueprint — EIS-§12 (REQ-§15)

Use a blueprint when the experience has meaningful backend workflow, multiple
systems, or asynchronous operations — not by default for trivial
interactions.

Four fixed layers:

| Layer | Content |
|---|---|
| `User actions` | What the human does. |
| `Frontstage experience` | What the user sees. |
| `Backstage process` | What the product does behind the visible interface. |
| `External/system dependencies` | What supporting services or systems do. |

Rendered as a stage × layer table (see the `eis-document-contracts` skill's
`diagrams.md`). When a blueprint genuinely does not help, EIS-§12's body reads
`Not applicable — <reason>`; the heading always renders.

## Entry points and experience surfaces — EIS-§9 (REQ-§17)

Identify where users can encounter or initiate the feature: global navigation ·
object detail page · list/table · search · contextual action · admin center ·
notification · deep link · onboarding · empty state · external integration.

**Do not prescribe exact layout.** For each entry point specify:

1. why the entry point exists;
2. which actors can encounter it;
3. what information must be available there;
4. what action it enables;
5. what state affects its behavior.

Point 5 is what connects EIS-§9 to EIS-§8: an entry point that renders
differently for a pending request than for no request is a behavioural
requirement, and saying so is not visual design.

An entry point with no journey referencing it, or a journey whose
`Entry points` field names a surface EIS-§9 does not list, is an internal
inconsistency the critic will find.

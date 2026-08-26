# Actors, concepts, terminology (REQ-§8, §9, §10)

## Actors and roles — EIS-§4

Identify the **functional** actors. Actors are not necessarily demographic
personas.

Candidates: consumer · creator · owner · editor · reviewer · approver ·
administrator · organization administrator · resource administrator · guest ·
unauthenticated visitor · service account · external system

For each actor document: goals · responsibilities · relevant resources ·
capabilities · restrictions · relationships to other actors.

Distinguish, and never use interchangeably: **identity** · **role** ·
**ownership** · **permission** · **entitlement** · **organizational
membership**.

Actor names in EIS-§4 are the canonical strings. The EIS-§7 capability matrix
columns, the EIS-§13 `Actor` fields, and the EIS-§10 journey actors all use
them verbatim. A different string means a different actor.

An actor with no capability row in EIS-§7 and no appearance in any journey is
not a modeled actor — either give it work or drop it.

## Conceptual / domain model — EIS-§5

Identify the concepts users must understand: Product · Workspace · Request ·
Approval · Policy · Subscription · Resource · Connection · Entitlement ·
Owner · Consumer, and whatever this feature adds.

For each object document: definition · relationship to other objects ·
ownership · lifecycle · visibility · important attributes · cardinality where
relevant.

The purpose is **not** an engineering database schema. The purpose is the
**user-visible conceptual model**.

### `### User-facing vs implementation concepts`

This sub-heading exists to sort exactly this, and it is load-bearing. For each
concept, decide which side it belongs on:

| User-facing | Implementation |
|---|---|
| The user must understand it to use the feature correctly. | The system needs it; the user does not. |
| It appears in EIS-§6's glossary. | It appears here and nowhere else. |
| Its states appear in EIS-§8. | Its states are invisible. |

Actively look for opportunities to **hide unnecessary implementation
complexity**. When an input exposes an implementation concept to users, say so
and recommend hiding it — that is discovery probe 14 in action.

> `Entitlement grant record` is an implementation concept. Users experience
> "access", not the record that carries it. The EIS refers to access
> throughout; the record appears only in EIS-§11 where its creation is the
> backstage step that makes access real.

An object listed under `### Objects` with no lifecycle in EIS-§8 and no
appearance in a journey is either an implementation concept in the wrong
column, or a concept nobody needs.

## Terminology model — EIS-§6

Terminology is part of UX. Build a glossary for the important concepts. For
each term:

| Field | Content |
|---|---|
| Preferred term | The word this specification uses. |
| Definition | One or two sentences, in product language. |
| Alternative terms found in existing materials | Every competing string, with where it came from. |
| Host-product precedent | What the host product calls it (`EV-RS-###`). |
| Competitor precedent where relevant | What competitors call it. |
| Recommendation | Adopt / rename / split, with a reason. |

**Identify conflicting vocabulary.** Where the input uses two words for one
concept, or one word for two concepts, the glossary is where that gets
resolved — and where the resolution is recorded so the rest of the document
cannot re-collapse it.

Recommend terminology that, in order:

1. matches the host product where possible;
2. aligns with established customer mental models;
3. avoids implementation terminology;
4. distinguishes genuinely different concepts.

Rule 4 outranks rule 1 when they conflict: if the host product uses one word
for discoverability and access, and this feature depends on the difference,
split the term and say that you are deviating from host precedent and why.
That is a `DEC-MD-###` and a RES-§9 implication, not a silent choice.

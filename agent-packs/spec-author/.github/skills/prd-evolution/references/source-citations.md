# prd-evolution — Source citations

The rules in `SKILL.md` are grounded in these public conventions.
Cited URLs are representative; the skill does not require live
network at runtime to function.

| # | Source | Where applied |
|---|--------|----------------|
| 1 | **IETF RFC 7322 — RFC Style Guide.** "Updates: NNNN" / "Obsoletes: NNNN" headers. <https://www.rfc-editor.org/rfc/rfc7322> | Rule 2 — header annotations on the revised spec. |
| 2 | **Architecture Decision Records — Michael Nygard's original (2011).** <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions> + **MADR** <https://adr.github.io/madr/> | Rule 3 — superseded ADRs are not deleted; status changes from `Accepted` → `Superseded by NNNN`. Same pattern applied to deprecated requirement IDs. |
| 3 | **Semantic Versioning 2.0.** <https://semver.org/> | Rule 1 — semver-for-specs MAJOR / MINOR / PATCH. |
| 4 | **Keep a Changelog 1.1.0.** <https://keepachangelog.com/en/1.1.0/> — Added / Changed / Deprecated / Removed / Fixed / Security. | Rule 6 — literal categories in `CHANGELOG.md`. |
| 5 | **GitHub spec-kit changelog conventions.** <https://github.com/github/spec-kit> | Rule 5 — living-document preamble; rule 6 — diff-friendly output the critic reviews. |
| 6 | **Notion docs versioning + Linear "project updates" cadence.** Living-document patterns. | Rule 5 — `## Changes since vN` block at top of every revised spec. |

These citations are referenced solely in the abstract. The skill's
operational rules do not depend on any specific organisation's
practice; they capture the convergent conventions across the
sources above.

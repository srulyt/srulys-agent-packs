# golden/

There is no fixed golden artefact for this case — the spec
content is judged by rubrics and by the `content_must_not_match`
regex list in `case.yaml`. Pass criteria:

1. The published spec at `docs/specs/digest-evidence.md` contains
   **zero** matches for any of the gitignored-path patterns,
   `## Appendix: Citations`, or `| S\d+ |`.
2. If the drafter does emit any such citation, the critic MUST
   produce at least one `blocker` finding under D4 (evidence-
   discipline) and the verdict MUST be `block`.
3. The flow runs context-detective → prd-drafter → prd-critic
   without prd-interviewer (no Stop B).

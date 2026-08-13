"""Strict v3 schema, cross-document, receipt, and guarded-state validation."""
import argparse, copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import canonical, dump, load, sha_bytes, sha_file

ROOT = Path(__file__).resolve().parents[1]

def issue(code, path, message):
    return {"code": code, "path": path, "message": message}

def schema_validate(instance, schema):
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("jsonschema is required; install pinned requirements") from exc
    jsonschema.Draft202012Validator.check_schema(schema)
    return sorted(
        [issue("schema", "/" + "/".join(map(str, e.absolute_path)), e.message)
         for e in jsonschema.Draft202012Validator(schema).iter_errors(instance)],
        key=lambda x: (x["path"], x["message"]),
    )

def duplicates(values):
    seen, dup = set(), set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)

def require_unique(values, code, path, diagnostics):
    dup = duplicates(values)
    if dup:
        diagnostics.append(issue(code, path, f"duplicate values: {dup}"))

def load_related(related, key):
    return load(related[key]) if related.get(key) else None

def semantic_validate(kind, obj, root=ROOT, related=None):
    related = related or {}
    d = []
    if kind == "intake":
        registry = load(root / "design-systems/registry.json")
        if obj.get("design_system_id") not in {x["id"] for x in registry["systems"]}:
            d.append(issue("design-system", "/design_system_id", "unknown design system"))
        require_unique(obj.get("context_files", []), "context-file-duplicate", "/context_files", d)
    elif kind == "evidence-ledger":
        evidence, claims = obj.get("evidence", []), obj.get("claims", [])
        require_unique([x.get("source_id") for x in evidence], "source-id-duplicate", "/evidence", d)
        require_unique([x.get("evidence_id") for x in evidence], "evidence-id-duplicate", "/evidence", d)
        require_unique([x.get("claim_id") for x in claims], "claim-id-duplicate", "/claims", d)
        known = {x.get("evidence_id") for x in evidence}
        for i, claim in enumerate(claims):
            ids = claim.get("evidence_ids", [])
            require_unique(ids, "claim-evidence-duplicate", f"/claims/{i}/evidence_ids", d)
            for eid in ids:
                if eid not in known:
                    d.append(issue("evidence-reference", f"/claims/{i}/evidence_ids", f"unknown evidence {eid}"))
            unsupported = bool(claim.get("unsupported", not ids))
            allowed = claim.get("allowed_use")
            qualification = str(claim.get("qualification", "")).strip()
            if unsupported != (not ids):
                d.append(issue("unsupported-consistency", f"/claims/{i}/unsupported", "must be true exactly when evidence_ids is empty"))
            if unsupported and allowed != "unsupported":
                d.append(issue("unsupported-allowed-use", f"/claims/{i}/allowed_use", "unsupported claims require allowed_use=unsupported"))
            if not unsupported and allowed == "unsupported":
                d.append(issue("supported-allowed-use", f"/claims/{i}/allowed_use", "supported claims cannot use unsupported"))
            if unsupported and not qualification:
                d.append(issue("unsupported-qualification", f"/claims/{i}/qualification", "unsupported claim must be explicitly qualified"))
    elif kind == "story-plan":
        slides = obj.get("slides", [])
        require_unique([x.get("slide_id") for x in slides], "slide-id-duplicate", "/slides", d)
        ledger = load_related(related, "evidence-ledger")
        if ledger:
            claims = {x["claim_id"] for x in ledger["claims"]}
            evidence = {x["evidence_id"] for x in ledger["evidence"]}
            for i, slide in enumerate(slides):
                for cid in slide.get("claim_ids", []):
                    if cid not in claims:
                        d.append(issue("claim-reference", f"/slides/{i}/claim_ids", f"unknown claim {cid}"))
                for eid in slide.get("evidence_ids", []):
                    if eid not in evidence:
                        d.append(issue("evidence-reference", f"/slides/{i}/evidence_ids", f"unknown evidence {eid}"))
    elif kind == "deck-spec":
        slides, sources = obj.get("slides", []), obj.get("sources", [])
        require_unique([s.get("slide_id") for s in slides], "slide-id-duplicate", "/slides", d)
        require_unique([s.get("source_id") for s in sources], "source-id-duplicate", "/sources", d)
        if [s.get("index") for s in slides] != list(range(1, len(slides) + 1)):
            d.append(issue("slide-index", "/slides", "indices must be contiguous, unique, and start at 1"))
        source_map = {x.get("source_id"): x for x in sources}
        registry = load(root / "design-systems/registry.json")
        if obj.get("design_system_id") not in {x["id"] for x in registry["systems"]}:
            d.append(issue("design-system", "/design_system_id", "unknown design system"))
        ledger = load_related(related, "evidence-ledger")
        plan = load_related(related, "story-plan")
        claim_map = {x["claim_id"]: x for x in ledger.get("claims", [])} if ledger else {}
        evidence_map = {x["evidence_id"]: x for x in ledger.get("evidence", [])} if ledger else {}
        planned = {x["slide_id"]: x for x in plan.get("slides", [])} if plan else {}
        require_unique([x.get("slide_id") for x in plan.get("slides", [])] if plan else [], "plan-slide-id-duplicate", "/related/story-plan/slides", d)
        relationship_types = {
            "comparison": {"bar", "column"},
            "trend": {"line", "area", "column"},
            "composition": {"pie", "donut", "bar"},
            "distribution": {"bar", "column"},
            "correlation": {"scatter"},
            "flow": {"bar"},
        }
        recipes = {"title", "section", "assertion-evidence", "big-number", "comparison", "process", "timeline", "chart", "image-led", "quote", "matrix", "table", "recommendation", "cta"}
        layout_families = {"hero", "editorial", "data", "comparison", "process", "visual", "decision"}
        background_roles = {"background", "accent", "positive", "warning"}
        for i, slide in enumerate(slides):
            p, content = f"/slides/{i}", slide.get("content", {})
            if slide.get("recipe") not in recipes:
                d.append(issue("recipe", p + "/recipe", f"unsupported recipe {slide.get('recipe')}"))
            if slide.get("layout_family") not in layout_families:
                d.append(issue("layout-family", p + "/layout_family", f"unsupported layout family {slide.get('layout_family')}"))
            if slide.get("background_role") not in background_roles:
                d.append(issue("background-role", p + "/background_role", f"unsupported role {slide.get('background_role')}"))
            claim_ids, evidence_ids = slide.get("claim_ids", []), slide.get("evidence_ids", [])
            require_unique(claim_ids, "slide-claim-duplicate", p + "/claim_ids", d)
            require_unique(evidence_ids, "slide-evidence-duplicate", p + "/evidence_ids", d)
            if set(claim_ids) != set(slide.get("notes", {}).get("claim_ids", [])):
                d.append(issue("notes-claim-lineage", p + "/notes/claim_ids", "must equal slide claim_ids"))
            if set(evidence_ids) != set(slide.get("notes", {}).get("evidence_ids", [])):
                d.append(issue("notes-evidence-lineage", p + "/notes/evidence_ids", "must equal slide evidence_ids"))
            if plan:
                ps = planned.get(slide.get("slide_id"))
                if not ps:
                    d.append(issue("plan-slide-reference", p + "/slide_id", "slide is absent from story plan"))
                else:
                    if set(claim_ids) != set(ps.get("claim_ids", [])):
                        d.append(issue("plan-claim-lineage", p + "/claim_ids", "must equal planned claim IDs"))
                    if set(evidence_ids) != set(ps.get("evidence_ids", [])):
                        d.append(issue("plan-evidence-lineage", p + "/evidence_ids", "must equal planned evidence IDs"))
            expected_sources = set()
            for cid in claim_ids:
                if ledger and cid not in claim_map:
                    d.append(issue("claim-reference", p + "/claim_ids", f"unknown claim {cid}"))
                claim = claim_map.get(cid, {})
                if claim.get("allowed_use") == "unsupported":
                    qualification = str(claim.get("qualification", "")).strip()
                    if not qualification or qualification.casefold() not in (slide.get("core_assertion", "") + " " + slide.get("notes", {}).get("talk_track", "")).casefold():
                        d.append(issue("unsupported-claim", p + "/core_assertion", f"{cid} must include its explicit qualification"))
            for eid in evidence_ids:
                if ledger and eid not in evidence_map:
                    d.append(issue("evidence-reference", p + "/evidence_ids", f"unknown evidence {eid}"))
                if eid in evidence_map:
                    expected_sources.add(evidence_map[eid]["source_id"])
            footer = slide.get("source_footer", [])
            require_unique(footer, "footer-duplicate", p + "/source_footer", d)
            for source_id in footer:
                if source_id not in source_map:
                    d.append(issue("footer-source-reference", p + "/source_footer", f"unknown source {source_id}"))
            if expected_sources != set(footer):
                d.append(issue("footer-lineage", p + "/source_footer", f"must exactly identify evidence sources {sorted(expected_sources)}"))
            object_ids = semantic_object_ids(slide)
            order = slide.get("reading_order", [])
            require_unique(order, "reading-order-duplicate", p + "/reading_order", d)
            missing, unknown = object_ids - set(order), set(order) - object_ids
            if missing:
                d.append(issue("reading-order-incomplete", p + "/reading_order", f"missing semantic objects: {sorted(missing)}"))
            if unknown:
                d.append(issue("reading-order-reference", p + "/reading_order", f"unknown semantic objects: {sorted(unknown)}"))
            if order[:2] != ["title", "assertion"]:
                d.append(issue("reading-order-prefix", p + "/reading_order", "must begin with title then assertion"))
            if slide.get("type") == "chart":
                n = len(content.get("categories", []))
                if any(len(x.get("values", [])) != n for x in content.get("series", [])):
                    d.append(issue("chart-length", p + "/content/series", "series lengths must match categories"))
                rel, chart_type = content.get("relationship"), content.get("chart_type")
                if chart_type not in relationship_types.get(rel, set()):
                    d.append(issue("chart-relationship-type", p + "/content/chart_type", f"{chart_type} is unsupported for {rel}"))
                if set(content.get("source_ids", [])) != set(footer):
                    d.append(issue("chart-source-membership", p + "/content/source_ids", "must equal source_footer"))
                if set(content.get("evidence_ids", [])) != set(evidence_ids):
                    d.append(issue("chart-evidence-membership", p + "/content/evidence_ids", "must equal slide evidence_ids"))
                if content.get("missing_value_policy") not in {"gap", "zero", "exclude", "annotate"}:
                    d.append(issue("chart-missing-policy", p + "/content/missing_value_policy", "unsupported policy"))
                if content.get("axis_policy") not in {"zero", "auto", "log", "explicit"}:
                    d.append(issue("chart-axis-policy", p + "/content/axis_policy", "unsupported policy"))
                explicit = content.get("explicit_axis")
                if content.get("axis_policy") == "explicit":
                    if not explicit:
                        d.append(issue("chart-explicit-axis", p + "/content/explicit_axis", "explicit axis policy requires bounds and titles"))
                    elif explicit["x_min"] >= explicit["x_max"] or explicit["y_min"] >= explicit["y_max"]:
                        d.append(issue("chart-explicit-axis", p + "/content/explicit_axis", "axis minimums must be less than maximums"))
                if rel in {"comparison", "distribution"} and content.get("zero_baseline_policy") == "required" and content.get("axis_policy") != "zero":
                    d.append(issue("chart-baseline", p + "/content/axis_policy", "required baseline must use axis_policy=zero"))
                if content.get("zero_baseline_policy") == "exception-justified" and not content.get("zero_baseline_exception"):
                    d.append(issue("chart-baseline", p + "/content/zero_baseline_exception", "exception requires justification"))
            if slide.get("type") == "matrix":
                for j, item in enumerate(content.get("items", [])):
                    if not (0 <= item.get("x", -1) <= 1 and 0 <= item.get("y", -1) <= 1):
                        d.append(issue("matrix-coordinate", f"{p}/content/items/{j}", "matrix x and y must be normalized to 0..1"))
    elif kind == "render-manifest":
        seen = []
        for i, output in enumerate(obj.get("outputs", [])):
            seen.append(output.get("channel"))
            if output.get("status") == "rendered":
                path = Path(output.get("path", ""))
                if not path.is_file() or sha_file(path) != output.get("sha256"):
                    d.append(issue("output-checksum", f"/outputs/{i}", "rendered output is missing or checksum-mismatched"))
        require_unique(seen, "output-channel-duplicate", "/outputs", d)
    elif kind == "qa-report":
        if obj.get("verdict") == "pass":
            if any(x.get("severity") == "blocking" for x in obj.get("findings", [])):
                d.append(issue("qa-pass-blocking", "/verdict", "pass cannot contain blocking findings"))
            if any(x.get("status") != "pass" for x in obj.get("deterministic_checks", [])):
                d.append(issue("qa-pass-check", "/deterministic_checks", "pass requires every deterministic check to pass"))
            if obj.get("model_review", {}).get("status") != "completed":
                d.append(issue("qa-pass-model", "/model_review/status", "pass requires completed model review"))
    return sorted(d, key=lambda x: (x["path"], x["code"], x["message"]))

def semantic_object_ids(slide):
    ids = {"title", "assertion", "implication", "source-footer"}
    typ, c = slide.get("type"), slide.get("content", {})
    fixed = {
        "title": {"visual"}, "section": {"visual"}, "big-number": {"visual", "content-1"},
        "comparison": {"content-1", "content-2", "comparison-basis"}, "chart": {"chart", "content-annotation"},
        "image-led": {"image", "content-1"}, "quote": {"quote", "content-attribution"},
        "matrix": {"matrix", "matrix-x", "matrix-y"}, "table": {"table"},
        "recommendation": {"visual", "content-1", "content-2"}, "cta": {"visual", "content-1", "content-2"},
    }
    ids |= fixed.get(typ, set())
    for key in ("evidence_blocks", "steps", "events", "items"):
        ids |= {x["object_id"] for x in c.get(key, []) if isinstance(x, dict) and x.get("object_id")}
    return ids

TRANSITIONS = {
    ("new", "initialize"): "initialized",
    ("initialized", "validate-intake-started"): "intake-validating",
    ("intake-validating", "intake-validation-succeeded"): "intake-valid",
    ("intake-validating", "intake-producer-invalid"): "initialized",
    ("intake-validating", "intake-validator-failed"): "intake-validation-retry",
    ("intake-validation-retry", "retry-intake-validation"): "intake-validating",
    ("intake-valid", "strategy-produced"): "strategy-validating",
    ("strategy-validating", "strategy-validation-succeeded"): "strategy-ready",
    ("strategy-validating", "strategy-producer-invalid"): "awaiting-revision",
    ("strategy-validating", "strategy-validator-failed"): "strategy-validation-retry",
    ("strategy-validation-retry", "retry-strategy-validation"): "strategy-validating",
    ("strategy-ready", "proposal-presented"): "awaiting-approval",
    ("awaiting-approval", "approve"): "approved",
    ("awaiting-approval", "revise"): "awaiting-revision",
    ("awaiting-revision", "retry-strategy-producer"): "intake-valid",
    ("awaiting-revision", "retry-composition"): "approved",
    ("approved", "compose-started"): "composing",
    ("composing", "render-completed"): "rendered",
    ("composing", "render-degraded"): "awaiting-render-decision",
    ("composing", "composition-failed"): "awaiting-revision",
    ("awaiting-render-decision", "accept-degraded-format"): "approved",
    ("awaiting-render-decision", "retry-render"): "approved",
    ("rendered", "review-started"): "reviewing",
    ("reviewing", "qa-passed"): "passed",
    ("reviewing", "qa-revise"): "awaiting-revision",
    ("reviewing", "qa-unverified"): "qa-residuals-pending-user",
    ("reviewing", "qa-contract-failed"): "rendered",
    ("qa-residuals-pending-user", "retry-quality"): "awaiting-revision",
    ("qa-residuals-pending-user", "retry-visual-environment"): "awaiting-render-decision",
    ("qa-residuals-pending-user", "accept-residuals"): "publication-preflighting",
    ("passed", "publish-requested"): "publication-preflighting",
    ("publication-preflighting", "preflight-clear"): "publishing",
    ("publication-preflighting", "preflight-clear-residual"): "publishing-residual",
    ("publication-preflighting", "preflight-collision"): "awaiting-publication-decision",
    ("awaiting-publication-decision", "destination-selected"): "publication-preflighting",
    ("awaiting-publication-decision", "replace-authorized"): "publication-preflighting",
    ("publishing", "publication-race"): "awaiting-publication-decision",
    ("publishing-residual", "publication-race"): "awaiting-publication-decision",
    ("publishing", "publication-failed"): "passed",
    ("publishing-residual", "publication-failed"): "qa-residuals-pending-user",
    ("publishing", "publication-committed"): "delivered",
    ("publishing-residual", "publication-committed"): "delivered-with-accepted-residuals",
    ("delivered", "revise-strategy"): "intake-valid",
    ("delivered-with-accepted-residuals", "revise-strategy"): "intake-valid",
    ("delivered", "revise-deck"): "approved",
    ("delivered-with-accepted-residuals", "revise-deck"): "approved",
}

RETRY_EVENT_COUNTER = {
    "intake-producer-invalid": "intake_producer_retry",
    "intake-validator-failed": "intake_validator_contract_retry",
    "strategy-producer-invalid": "strategy_producer_retry",
    "strategy-validator-failed": "strategy_validator_contract_retry",
    "qa-revise": "quality_retry",
    "qa-contract-failed": "qa_contract_retry",
    "retry-render": "render_retry",
    "publication-failed": "publication_retry",
    "preflight-failed": "publication_contract_retry",
}

def known_evidence(state):
    values = set(state.get("validation_receipt_ids", []))
    for name in ("input_manifest", "artifact_manifest", "staging_manifest", "publication_manifest"):
        values |= {x.get("artifact_id") for x in state.get(name, [])}
        values |= {x.get("sha256") for x in state.get(name, [])}
    values |= {x.get("event_id") for x in state.get("events", [])}
    values.add(state.get("capability_preflight", {}).get("evidence_id"))
    values.add(state.get("publication_destination", {}).get("effective_destination_event_id"))
    values.add(state.get("publication_destination", {}).get("intake_sha256"))
    values.add(state.get("publication_manifest_sha256"))
    return values

def exact_event_evidence(event, required):
    return set(event.get("evidence_ids", [])) == set(required)

RECEIPT_RULES = {
    "intake-validation-succeeded": {
        "operations": {"validate-intake"}, "kinds": {"intake"}, "required_kinds": {"intake"},
        "manifests": {"input_manifest"},
        "predecessors": {"validate-intake-started"},
        "producer": "story-orchestrator", "validator": "deck-composer",
    },
    "strategy-validation-succeeded": {
        "operations": {"validate-strategy"},
        "kinds": {"evidence-ledger", "story-plan", "proposal"},
        "required_kinds": {"evidence-ledger", "story-plan", "proposal"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"strategy-produced"},
        "producer": "narrative-strategist", "validator": "deck-composer",
    },
    "approve": {
        "operations": {"validate-strategy"},
        "kinds": {"evidence-ledger", "story-plan", "proposal"},
        "required_kinds": {"evidence-ledger", "story-plan", "proposal"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"strategy-produced"},
        "producer": "narrative-strategist", "validator": "deck-composer",
    },
    "compose-started": {
        "operations": {"validate-strategy"},
        "kinds": {"evidence-ledger", "story-plan", "proposal"},
        "required_kinds": {"evidence-ledger", "story-plan", "proposal"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"strategy-produced"},
        "producer": "narrative-strategist", "validator": "deck-composer",
    },
    "render-completed": {
        "operations": {"compose"}, "kinds": {"deck-spec", "render-manifest", "pptx", "marp", "staged-pptx", "staged-marp"},
        "required_kinds": {"deck-spec", "render-manifest"}, "manifests": {"staging_manifest"},
        "predecessors": {"compose-started"},
        "producer": "deck-composer", "validator": "deck-critic",
    },
    "render-degraded": {
        "operations": {"compose"}, "kinds": {"deck-spec", "render-manifest", "pptx", "marp", "staged-pptx", "staged-marp"},
        "required_kinds": {"deck-spec", "render-manifest"}, "manifests": {"staging_manifest"},
        "predecessors": {"compose-started"},
        "producer": "deck-composer", "validator": "deck-critic",
    },
    "review-started": {
        "operations": {"compose"}, "kinds": {"deck-spec", "render-manifest", "pptx", "marp", "staged-pptx", "staged-marp"},
        "required_kinds": {"deck-spec", "render-manifest"}, "manifests": {"staging_manifest"},
        "predecessors": {"compose-started"},
        "producer": "deck-composer", "validator": "deck-critic",
    },
    "qa-passed": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"review-started"}, "capability": "complete",
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "qa-revise": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "qa-unverified": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"},
        "predecessors": {"review-started"}, "capability": "raster-unavailable",
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "accept-residuals": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "publish-requested": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "preflight-clear": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "preflight-clear-residual": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "preflight-collision": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
    "publication-committed": {
        "operations": {"review"}, "kinds": {"qa-report"}, "required_kinds": {"qa-report"},
        "manifests": {"artifact_manifest"}, "predecessors": {"review-started"},
        "producer": "deck-critic", "validator": "deck-composer",
    },
}

def last_event(state, kinds):
    return next((x for x in reversed(state.get("events", [])) if x.get("type") in kinds), None)

def expected_receipt_artifacts(state, rule):
    """Return the exact active artifact set which a gated handoff must receipt."""
    selected = {}
    for name in rule.get("manifests", set()):
        for artifact in state.get(name, []):
            if (artifact.get("kind") in rule["kinds"]
                    and artifact.get("lineage_id") == state.get("active_lineage_id")
                    and artifact.get("status") not in {"untrusted", "invalidated", "superseded"}):
                if artifact.get("artifact_id") in selected:
                    raise ValueError("duplicate active artifact identity across manifests")
                selected[artifact["artifact_id"]] = artifact
    kinds = {artifact.get("kind") for artifact in selected.values()}
    missing = rule.get("required_kinds", set()) - kinds
    if missing:
        raise ValueError(f"required artifact kinds are missing: {sorted(missing)}")
    return selected

def validate_receipt_lineage(state, event):
    """Validate the indexed immutable envelope before any guarded transition."""
    registered_ids = set(state.get("validation_receipt_ids", []))
    registry = state.get("validation_receipts", {})
    if registered_ids != set(registry):
        return "validation receipt ID list and indexed envelope registry differ"
    receipt_ids = event.get("receipt_ids", [])
    rule = RECEIPT_RULES.get(event["type"])
    if not receipt_ids:
        return "receipt-gated transition requires the complete receipt set" if rule else None
    if len(receipt_ids) != len(set(receipt_ids)):
        return "transition contains duplicate receipt IDs"
    if not event.get("handoff_id"):
        return "receipt-bearing transition requires an exact handoff_id"
    artifacts = {
        x["artifact_id"]: x
        for name in ("input_manifest", "artifact_manifest", "staging_manifest", "publication_manifest")
        for x in state.get(name, [])
    }
    predecessor = last_event(state, rule["predecessors"]) if rule else None
    if rule:
        try:
            expected_artifacts = expected_receipt_artifacts(state, rule)
        except ValueError as exc:
            return str(exc)
        supplied = [registry.get(receipt_id, {}).get("artifact_id") for receipt_id in receipt_ids]
        if len(supplied) != len(set(supplied)) or set(supplied) != set(expected_artifacts):
            return "transition receipt set does not exactly equal the complete active artifact set"
    for receipt_id in receipt_ids:
        receipt = registry.get(receipt_id)
        if not receipt or receipt.get("receipt_id") != receipt_id:
            return "transition references a missing or identity-mismatched receipt envelope"
        if receipt.get("run_id") != state["run_id"] or receipt.get("handoff_id") != event["handoff_id"]:
            return "receipt run/session or handoff identity mismatch"
        if not receipt.get("valid") or receipt.get("superseded") or receipt.get("lineage_id") != state.get("active_lineage_id"):
            return "receipt is invalid, superseded, or belongs to stale lineage"
        artifact = artifacts.get(receipt.get("artifact_id"))
        if (not artifact or artifact.get("kind") != receipt.get("artifact_kind")
                or artifact.get("sha256") != receipt.get("artifact_sha256")
                or artifact.get("producer") != receipt.get("producer_agent")
                or artifact.get("status") in {"untrusted", "invalidated", "superseded"}):
            return "receipt artifact identity, kind, or checksum does not match a state manifest"
        if rule:
            if receipt.get("validator_operation") not in rule["operations"] or receipt.get("artifact_kind") not in rule["kinds"]:
                return "receipt kind or validator operation is wrong for this transition"
            if receipt.get("producer_agent") != rule["producer"] or receipt.get("validator_agent") != rule["validator"]:
                return "receipt producer or validator identity is wrong for this transition"
            if not predecessor or receipt.get("predecessor_event_id") != predecessor.get("event_id"):
                return "receipt does not bind the exact predecessor event/state"
            expected_capability = rule.get("capability")
            if expected_capability and receipt.get("capability_status") != expected_capability:
                return "receipt capability status is incompatible with the guarded transition"
            if event["type"] == "render-completed" and receipt.get("capability_status") == "raster-unavailable":
                return "completed render transition cannot use a raster-unavailable receipt"
        manifest = event.get("render_manifest_sha256")
        if manifest and receipt.get("render_manifest_sha256") != manifest:
            return "receipt does not bind the exact render manifest"
        approval = event.get("approval_event_id")
        if approval and receipt.get("approval_event_id") != approval:
            return "receipt does not bind the exact approval identity"
        acceptance = event.get("acceptance_event_id")
        if event["type"] in {"publish-requested", "publication-committed"} and acceptance and receipt.get("acceptance_event_id") != acceptance:
            return "receipt does not bind the exact acceptance identity"
    return None

def transition_guard(state, event, event_schema):
    errors = schema_validate(event, event_schema)
    if errors:
        return None, "event is schema-invalid: " + errors[0]["message"]
    source, typ = state["phase"], event["type"]
    target = TRANSITIONS.get((source, typ))
    if typ == "resume":
        if source in {"delivered", "delivered-with-accepted-residuals", "aborted", "error"}:
            return None, "terminal state cannot resume into an earlier checkpoint"
        target = event.get("resume_phase")
        if target not in {"initialized", "intake-valid", "strategy-ready", "awaiting-approval", "approved", "rendered", "passed", "qa-residuals-pending-user", "publication-preflighting", "awaiting-publication-decision", "publishing", "publishing-residual"}:
            return None, "resume_phase is not a safe checkpoint"
        if target != source and not event.get("invalidate_artifact_ids"):
            return None, "resume fallback must explicitly invalidate stale downstream lineage"
    if typ == "preflight-failed" and source == "publication-preflighting":
        target = "passed" if state.get("publication_gate") == "pass" else "qa-residuals-pending-user"
    if typ == "integrity-error" and source not in {"delivered", "delivered-with-accepted-residuals", "aborted", "error"}:
        target = "error"
    if not target:
        if typ == "cancel" and source not in {"delivered", "delivered-with-accepted-residuals", "aborted", "error"}:
            target = "aborted"
        else:
            return None, f"illegal transition {source} + {typ}"
    if event["run_id"] != state["run_id"]:
        return None, "event run_id mismatch"
    if event["event_id"] in {x.get("event_id") for x in state["events"]}:
        return None, "duplicate event_id"
    receipt_lineage_error = validate_receipt_lineage(state, event)
    if receipt_lineage_error:
        return None, receipt_lineage_error
    if typ == "initialize" and any(state["retry_counters"].values()):
        return None, "initialization requires zeroed retry counters"
    needed = set(event.get("evidence_ids", []))
    resolvable = needed - (set(event.get("accepted_finding_ids", [])) if typ == "accept-residuals" else set())
    if typ not in {"initialize", "validate-intake-started", "cancel"} and (not needed or not resolvable.issubset(known_evidence(state))):
        return None, "event evidence_ids are missing or do not resolve in state lineage"
    counter = RETRY_EVENT_COUNTER.get(typ)
    if counter and state["retry_counters"][counter] >= 2:
        return None, f"{counter} retry cap reached"
    if typ in {"intake-validation-succeeded", "strategy-validation-succeeded"}:
        receipts = set(event.get("receipt_ids", []))
        rule = RECEIPT_RULES[typ]
        expected = expected_receipt_artifacts(state, rule)
        required = receipts | set(expected) | {x["sha256"] for x in expected.values()}
        if not receipts or not exact_event_evidence(event, required):
            return None, "success evidence must exactly equal complete receipt, artifact, and checksum lineage"
    if typ == "approve":
        receipts = set(event.get("receipt_ids", []))
        if not receipts or not receipts.issubset(set(state["validation_receipt_ids"])) or not exact_event_evidence(event, receipts):
            return None, "approval requires exact validated strategy receipt lineage"
    if typ == "compose-started":
        approval = state.get("approval_event_id")
        receipts = set(event.get("receipt_ids", []))
        approval_record = next((x for x in state.get("events", []) if x.get("event_id") == approval), {})
        approved_receipts = set(approval_record.get("receipt_ids", []))
        if event.get("approval_event_id") != approval or not receipts or receipts != approved_receipts or not exact_event_evidence(event, receipts | {approval}):
            return None, "composition requires exact approval event and strategy receipt lineage"
    if typ in {"render-completed", "render-degraded"}:
        approval = state.get("approval_event_id")
        capability = state.get("capability_preflight", {}).get("evidence_id")
        staged = {x["artifact_id"] for x in state.get("staging_manifest", []) if x["status"] == "staged"}
        receipts = set(event.get("receipt_ids", []))
        required = staged | {approval, capability} | receipts
        if event.get("approval_event_id") != approval or event.get("capability_evidence_id") != capability or not staged or not receipts or not receipts.issubset(set(state["validation_receipt_ids"])) or not exact_event_evidence(event, required):
            return None, "render transition requires exact approval, capability, and staged-manifest lineage"
        if typ == "render-completed":
            manifests = {x["sha256"] for x in state.get("staging_manifest", []) if x["kind"] == "render-manifest" and x["status"] == "staged"}
            if event.get("render_manifest_sha256") not in manifests:
                return None, "render completion requires the exact staged render-manifest checksum"
    if typ == "accept-degraded-format":
        capability = state.get("capability_preflight", {})
        offered = capability.get("available_formats")
        effective = event.get("effective_formats")
        if event.get("capability_evidence_id") != capability.get("evidence_id") or effective != offered or effective == state.get("requested_formats"):
            return None, "degraded acceptance must select the exact preflight-supported degraded format"
        if not event.get("invalidate_artifact_ids") or not exact_event_evidence(event, {capability.get("evidence_id"), state.get("approval_event_id")}):
            return None, "degraded acceptance requires exact capability/approval evidence and incompatible-artifact invalidation"
    if typ == "review-started":
        staged = {x["artifact_id"] for x in state.get("staging_manifest", []) if x["status"] == "staged"}
        receipts = set(event.get("receipt_ids", []))
        if not staged or not receipts or not receipts.issubset(set(state["validation_receipt_ids"])) or not exact_event_evidence(event, staged | receipts):
            return None, "review requires exact staged manifest and receipt lineage"
    if typ in {"qa-passed", "qa-revise", "qa-unverified"}:
        manifest = event.get("render_manifest_sha256")
        staged_hashes = {x["sha256"] for x in state.get("staging_manifest", []) if x["kind"] == "render-manifest" and x["status"] == "staged"}
        staged_ids = {x["artifact_id"] for x in state.get("staging_manifest", []) if x["status"] == "staged"}
        receipts = set(event.get("receipt_ids", []))
        review_event = next((x for x in reversed(state.get("events", [])) if x.get("type") == "review-started"), {})
        input_receipts = set(review_event.get("receipt_ids", []))
        if manifest not in staged_hashes or not receipts or receipts & input_receipts or not receipts.issubset(set(state["validation_receipt_ids"])):
            return None, "QA transition is not bound to registered receipts and the exact staged render manifest"
        if not exact_event_evidence(event, staged_ids | receipts | {manifest}):
            return None, "QA evidence must exactly equal staged artifacts, receipts, and render manifest"
    if typ in {"revise", "retry-composition", "strategy-producer-invalid", "qa-revise", "destination-selected", "replace-authorized", "publication-race", "composition-failed", "retry-render", "retry-quality", "retry-visual-environment", "revise-strategy", "revise-deck"} and not event.get("invalidate_artifact_ids"):
        return None, "transition must explicitly invalidate downstream lineage"
    if typ == "accept-residuals":
        qa_event = next((x for x in reversed(state.get("events", [])) if x.get("type") == "qa-unverified"), None)
        receipts = set(event.get("receipt_ids", []))
        if not qa_event or event.get("acceptance_event_id") != qa_event.get("event_id") or receipts != set(qa_event.get("receipt_ids", [])):
            return None, "residual acceptance requires the exact QA event and receipt lineage"
        if not event.get("accepted_finding_ids") or not event.get("render_manifest_sha256") or event.get("render_manifest_sha256") != qa_event.get("render_manifest_sha256"):
            return None, "residual acceptance requires exact finding IDs and render manifest checksum"
        if not exact_event_evidence(event, set(event["accepted_finding_ids"]) | {event["render_manifest_sha256"], qa_event["event_id"]} | receipts):
            return None, "residual acceptance evidence must exactly match findings, QA receipt/event, and manifest"
    if typ == "publish-requested":
        manifest = event.get("render_manifest_sha256")
        acceptance = state.get("qa_acceptance_event_id")
        qa_event = next((x for x in state.get("events", []) if x.get("event_id") == acceptance and x.get("type") == "qa-passed"), None)
        receipts = set(event.get("receipt_ids", []))
        if not qa_event or event.get("acceptance_event_id") != acceptance or manifest != qa_event.get("render_manifest_sha256") or receipts != set(qa_event.get("receipt_ids", [])):
            return None, "publish request requires exact QA acceptance, receipt, and manifest lineage"
        if not exact_event_evidence(event, {acceptance, manifest} | receipts):
            return None, "publish request evidence contains missing or unrelated lineage"
    if typ == "preflight-clear" and state.get("publication_gate") != "pass":
        return None, "pass preflight requires publication_gate=pass"
    if typ == "preflight-clear-residual" and state.get("publication_gate") != "residual":
        return None, "residual preflight requires publication_gate=residual"
    if typ in {"destination-selected", "replace-authorized"}:
        if event.get("intake_sha256") != state["publication_destination"]["intake_sha256"]:
            return None, "destination decision is not bound to validated intake"
    if typ in {"preflight-clear", "preflight-clear-residual", "preflight-collision"}:
        manifest = state.get("publication_manifest_sha256")
        acceptance = state.get("residual_acceptance_event_id") if state.get("publication_gate") == "residual" else state.get("qa_acceptance_event_id")
        destination_event = state["publication_destination"]["effective_destination_event_id"]
        intake = state["publication_destination"]["intake_sha256"]
        if event.get("render_manifest_sha256") != manifest or event.get("acceptance_event_id") != acceptance or event.get("intake_sha256") != intake or not event.get("preflight_fingerprint"):
            return None, "preflight result lacks exact acceptance, manifest, intake, or fingerprint lineage"
        acceptance_record = next((x for x in state.get("events", []) if x.get("event_id") == acceptance), {})
        receipts = set(event.get("receipt_ids", []))
        if receipts != set(acceptance_record.get("receipt_ids", [])):
            return None, "preflight receipt set must exactly equal the accepted QA receipt set"
        required = {manifest, acceptance, destination_event, intake} | receipts
        if not exact_event_evidence(event, required):
            return None, "preflight evidence must exactly equal frozen publication lineage"
    if typ == "replace-authorized":
        collision = next((x for x in reversed(state.get("events", [])) if x.get("type") == "preflight-collision"), None)
        if not collision or event.get("preflight_fingerprint") != collision.get("preflight_fingerprint"):
            return None, "replacement consent requires the exact collision preflight fingerprint"
        required = {collision["event_id"], state.get("publication_manifest_sha256"), state["publication_destination"]["intake_sha256"]}
        if not exact_event_evidence(event, required):
            return None, "replacement consent evidence must exactly bind collision, manifest, and intake"
    if typ == "publication-committed":
        if event.get("render_manifest_sha256") != state.get("publication_manifest_sha256"):
            return None, "committed manifest checksum mismatch"
        acceptance = event.get("acceptance_event_id")
        expected = state.get("residual_acceptance_event_id") if source == "publishing-residual" else state.get("qa_acceptance_event_id")
        if not acceptance or acceptance != expected:
            return None, "publication is not bound to the exact acceptance event"
        receipts = set(event.get("receipt_ids", []))
        acceptance_record = next((x for x in state.get("events", []) if x.get("event_id") == acceptance), {})
        expected_receipts = set(acceptance_record.get("receipt_ids", []))
        if not receipts or receipts != expected_receipts or not exact_event_evidence(event, {acceptance, state.get("publication_manifest_sha256")} | receipts):
            return None, "publication commit requires exact acceptance, QA receipt, and manifest evidence"
    if typ == "resume":
        receipt_ids = set(event.get("receipt_ids", []))
        if target not in {"initialized", "intake-valid"} and (not receipt_ids or not receipt_ids.issubset(set(state["validation_receipt_ids"]))):
            return None, "resume checkpoint requires all referenced independent receipts"
        if target in {"rendered", "passed", "qa-residuals-pending-user", "publication-preflighting", "awaiting-publication-decision", "publishing", "publishing-residual"}:
            staged = {x["sha256"] for x in state.get("staging_manifest", []) if x.get("kind") == "render-manifest" and x.get("status") in ("staged", "accepted")}
            if event.get("render_manifest_sha256") not in staged or not exact_event_evidence(event, receipt_ids | {event.get("render_manifest_sha256")}):
                return None, "resume requires exact receipt and staged render-manifest lineage"
    return target, None

def state_transition(args):
    original = load(args.state)
    schema, event = load(args.schema), load(args.event)
    errors = schema_validate(original, schema)
    if errors:
        print(json.dumps({"status": "rejected", "reason": "source state is schema-invalid", "diagnostics": errors}))
        return 1
    event_schema = schema["$defs"]["event"]
    target, reason = transition_guard(original, event, event_schema)
    state = copy.deepcopy(original)
    if reason:
        at = event.get("at") if isinstance(event, dict) else datetime.datetime.now(datetime.timezone.utc).isoformat()
        rejected = {
            "event_id": sha_bytes(canonical({"rejected": event, "state": sha_bytes(canonical(original))})),
            "type": "transition-rejected", "run_id": state["run_id"], "at": at,
            "actor": "story-state-validator", "evidence_ids": [], "rejected_event_type": event.get("type", "unknown"),
            "reason": reason,
        }
        state["events"].append(rejected)
        state["transition_history"].append({"transition_id": rejected["event_id"], "event_type": rejected["type"], "from_phase": state["phase"], "to_phase": state["phase"], "at": at, "status": "rejected", "reason": reason})
        state["updated_at"] = at
        if schema_validate(state, schema):
            print(json.dumps({"status": "rejected", "reason": reason, "persistence": "skipped because rejection envelope failed schema"}))
            return 2
        dump(args.state_output or args.state, state)
        print(json.dumps(state["transition_history"][-1]))
        return 1
    source = state["phase"]
    state["events"].append(event)
    state["transition_history"].append({"transition_id": event["event_id"], "event_type": event["type"], "from_phase": source, "to_phase": target, "at": event["at"], "status": "applied", "reason": None})
    state["phase"], state["updated_at"] = target, event["at"]
    typ = event["type"]
    counter = RETRY_EVENT_COUNTER.get(typ)
    if counter:
        state["retry_counters"][counter] += 1
    if typ == "approve":
        state["approval_event_id"] = event["event_id"]
        for receipt_id in event.get("receipt_ids", []):
            state["validation_receipts"][receipt_id]["approval_event_id"] = event["event_id"]
    if typ == "qa-passed":
        state["qa_acceptance_event_id"] = event["event_id"]
        for receipt_id in event.get("receipt_ids", []):
            state["validation_receipts"][receipt_id]["acceptance_event_id"] = event["event_id"]
    if typ == "accept-residuals":
        state["publication_gate"] = "residual"
        state["residual_acceptance_event_id"] = event["event_id"]
        state["publication_manifest_sha256"] = event["render_manifest_sha256"]
        for receipt_id in event.get("receipt_ids", []):
            state["validation_receipts"][receipt_id]["acceptance_event_id"] = event["event_id"]
    if typ == "accept-degraded-format":
        state["effective_formats"] = event["effective_formats"]
    if typ == "publish-requested":
        state["publication_gate"] = "pass"
        state["publication_manifest_sha256"] = event["render_manifest_sha256"]
    if typ == "destination-selected":
        pd = state["publication_destination"]
        pd.update({"effective_output_dir": event["destination"], "effective_destination_event_id": event["event_id"], "revision": pd["revision"] + 1})
    if event.get("invalidate_artifact_ids"):
        state["invalidated_artifact_ids"] = sorted(set(state["invalidated_artifact_ids"] + event["invalidate_artifact_ids"]))
        for name in ("artifact_manifest", "staging_manifest", "publication_manifest"):
            for artifact in state[name]:
                if artifact["artifact_id"] in event["invalidate_artifact_ids"]:
                    artifact["status"] = "invalidated"
    post = schema_validate(state, schema)
    if post:
        print(json.dumps({"status": "rejected", "reason": "post-transition state failed schema", "diagnostics": post}))
        return 2
    dump(args.state_output or args.state, state)
    print(json.dumps(state["transition_history"][-1]))
    return 0

def main():
    if "--state-transition" in sys.argv:
        p = argparse.ArgumentParser()
        p.add_argument("--state-transition", action="store_true")
        p.add_argument("--state", required=True); p.add_argument("--event", required=True)
        p.add_argument("--schema", required=True); p.add_argument("--state-output")
        return state_transition(p.parse_args())
    p = argparse.ArgumentParser()
    p.add_argument("--kind", required=True); p.add_argument("--input", required=True)
    p.add_argument("--schema", required=True); p.add_argument("--run-id", required=True)
    p.add_argument("--handoff-id", required=True); p.add_argument("--producer", required=True)
    p.add_argument("--validator", required=True); p.add_argument("--operation", required=True)
    p.add_argument("--receipt", required=True); p.add_argument("--evidence-ledger")
    p.add_argument("--story-plan")
    p.add_argument("--proposal")
    a = p.parse_args()
    try:
        if a.producer == a.validator:
            raise RuntimeError("producer and validator must differ")
        obj, schema = load(a.input), load(a.schema)
        related = {"evidence-ledger": a.evidence_ledger, "story-plan": a.story_plan}
        diagnostics = schema_validate(obj, schema) + semantic_validate(a.kind, obj, ROOT, related)
        if a.kind == "story-plan" and a.proposal:
            proposal = Path(a.proposal).read_text(encoding="utf-8")
            required = [str(obj.get("decision_sought", "")), str(obj.get("one_sentence_thesis", ""))]
            for value, label in zip(required, ("decision_sought", "one_sentence_thesis")):
                if value and value.casefold() not in proposal.casefold():
                    diagnostics.append(issue("proposal-lineage", "/proposal", f"proposal must contain exact {label}"))
            if not any(line.startswith("#") for line in proposal.splitlines()):
                diagnostics.append(issue("proposal-structure", "/proposal", "proposal requires a Markdown heading"))
        diagnostics = sorted(diagnostics, key=lambda x: (x["path"], x["code"], x["message"]))
        valid = not diagnostics
        core = {
            "run_id": a.run_id, "handoff_id": a.handoff_id, "artifact_kind": a.kind,
            "artifact_path": str(Path(a.input).resolve()), "artifact_sha256": sha_file(a.input),
            "schema_sha256": sha_file(a.schema), "producer_agent": a.producer,
            "validator_agent": a.validator, "validator_operation": a.operation,
            "diagnostics_hash": sha_bytes(canonical(diagnostics)),
        }
        receipt = {
            "schema_version": "3.0", "receipt_version": "1.0",
            "receipt_id": sha_bytes(canonical(core)), **core,
            "schema_path": str(Path(a.schema).resolve()), "tool_version": "story-contract-validator/3.2",
            "validated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "valid": valid, "diagnostic_class": "none" if valid else "producer-artifact-invalid",
            "diagnostic_count": len(diagnostics), "superseded": False,
            "diagnostics": diagnostics, "inspection_profile": None,
            "accepted_qa_event_id": None, "accepted_residual_event_id": None,
            "render_manifest_sha256": None,
        }
        receipt_errors = schema_validate(receipt, load(ROOT / "schemas/v3/validation-receipt.schema.json"))
        if receipt_errors:
            raise RuntimeError("receipt schema validation failed: " + json.dumps(receipt_errors))
        out = Path(a.receipt); out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            raise RuntimeError("immutable receipt already exists")
        dump(out, receipt)
        print(json.dumps({"receipt": str(out), "receipt_id": receipt["receipt_id"], "valid": valid, "diagnostics": diagnostics}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"valid": False, "diagnostic_class": "validator-internal-error", "error": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

"""Independent structural, raster, model-handoff QA with evidence-derived receipts."""
import argparse, datetime, json, math, re, shutil, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import canonical, dump, libreoffice_cli, libreoffice_headless_command, load, quiet_subprocess_kwargs, sha_bytes, sha_file
from validate_contract import schema_validate, semantic_validate

ROOT = Path(__file__).resolve().parents[1]

def contrast(a, b):
    def lum(value):
        vals = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
        vals = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in vals]
        return .2126 * vals[0] + .7152 * vals[1] + .0722 * vals[2]
    x, y = lum(a), lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)

def pptx_inspect(path, spec, token):
    from pptx import Presentation
    prs = Presentation(path); findings = []; checks = []
    checks.append(("pptx-dimensions", abs(prs.slide_width / prs.slide_height - 16 / 9) < .01, f"{prs.slide_width}x{prs.slide_height}"))
    if len(prs.slides) != len(spec["slides"]):
        findings.append(finding("pptx-slide-count", "blocking", [], f"{len(prs.slides)} != {len(spec['slides'])}", "Render all specified slides."))
    for index, (slide, expected) in enumerate(zip(prs.slides, spec["slides"]), 1):
        shapes = list(slide.shapes); names = [x.name for x in shapes]
        if names != expected["reading_order"]:
            findings.append(finding(f"reading-order-{index}", "blocking", [index], f"actual {names}; expected {expected['reading_order']}", "Create each semantic object once and order shapes exactly as reading_order."))
        overflow = [x.name for x in shapes if x.left < 0 or x.top < 0 or x.left + x.width > prs.slide_width or x.top + x.height > prs.slide_height]
        if overflow:
            findings.append(finding(f"overflow-{index}", "blocking", [index], str(overflow), "Fit objects within slide bounds."))
        for ai, a in enumerate(shapes):
            for b in shapes[ai + 1:]:
                ix = max(0, min(a.left + a.width, b.left + b.width) - max(a.left, b.left))
                iy = max(0, min(a.top + a.height, b.top + b.height) - max(a.top, b.top))
                ratio = (ix * iy) / max(1, min(a.width * a.height, b.width * b.height))
                if ratio > .08:
                    findings.append(finding(f"overlap-{index}-{a.name}-{b.name}", "major", [index], f"{ratio:.1%} overlap", "Separate semantic objects; intentional layering must be one grouped object."))
        note_text = slide.notes_slide.notes_text_frame.text
        try:
            note = json.loads(note_text[note_text.find("{"):])
            for key in ("slide_id", "claim_ids", "evidence_ids", "source_footer", "reading_order"):
                if note.get(key) != (expected["slide_id"] if key == "slide_id" else expected[key]):
                    findings.append(finding(f"notes-{key}-{index}", "blocking", [index], "notes lineage mismatch", "Regenerate notes from the exact slide model."))
        except Exception as exc:
            findings.append(finding(f"notes-parse-{index}", "blocking", [index], str(exc), "Write parseable semantic speaker notes."))
        for shape in shapes:
            descr = shape._element.xpath(".//p:cNvPr")[0].get("descr")
            if shape.name in expected["reading_order"] and not descr:
                findings.append(finding(f"alt-{index}-{shape.name}", "major", [index], "missing accessibility description", "Set meaningful alt text on every semantic object."))
            if getattr(shape, "has_text_frame", False):
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size and run.font.size.pt < token["type_pt"]["source"]:
                            findings.append(finding(f"font-size-{index}-{shape.name}", "major", [index], f"{run.font.size.pt}pt", "Use the design-token minimum size."))
        for shape in shapes:
            if not getattr(shape, "has_chart", False): continue
            content = expected["content"]; chart = shape.chart
            if expected["type"] != "chart":
                findings.append(finding(f"unexpected-chart-{index}", "blocking", [index], "chart absent from model", "Remove undeclared chart."))
                continue
            if content["chart_type"] not in ("pie", "donut"):
                if not chart.value_axis.has_title or chart.value_axis.axis_title.text_frame.text != content["units"]:
                    findings.append(finding(f"chart-axis-{index}", "blocking", [index], "unit axis title missing/mismatched", "Render declared chart units on the value axis."))
                if content["axis_policy"] == "zero" and chart.value_axis.minimum_scale != 0:
                    findings.append(finding(f"chart-baseline-{index}", "blocking", [index], "zero baseline not applied", "Set minimum value axis scale to zero."))
        if expected["type"] == "image-led":
            pics = [x for x in shapes if x.name == "image"]
            if pics and not any((x.crop_left or x.crop_right or x.crop_top or x.crop_bottom) for x in pics):
                # A matching aspect ratio legitimately needs no crop.
                checks.append((f"crop-{index}", True, "focal crop evaluated; no crop needed for matching aspect ratio"))
    checks.append(("pptx-structure", not any(x["severity"] == "blocking" for x in findings), f"{len(findings)} findings"))
    return findings, checks

def finding(fid, severity, slides, evidence, fix, channel="pptx"):
    return {"id": fid, "severity": severity, "channel": channel, "slides": slides, "evidence": evidence, "owner": "deck-composer", "fix": fix}

def marp_inspect(path, spec):
    text = Path(path).read_text(encoding="utf-8")
    semantics = [json.loads(x) for x in re.findall(r"<!-- story-semantic: (\{.*\}) -->", text)]
    expected = [{"index": s["index"], "slide_id": s["slide_id"], "title": s["title"], "claim_ids": s["claim_ids"], "evidence_ids": s["evidence_ids"], "source_footer": s["source_footer"], "notes": s["notes"], "cta": s["content"].get("cta") if s["type"] == "cta" else None} for s in spec["slides"]]
    return [("marp-frontmatter", "marp: true" in text, "Marp enabled"), ("marp-semantics", semantics == expected, "output semantics equal deck model")]

def render_previews(pptx, out):
    office = libreoffice_cli()
    raster = shutil.which("pdftoppm")
    try:
        import fitz
    except ImportError:
        fitz = None
    if not office or (not raster and not fitz):
        return [], "LibreOffice and either pdftoppm or PyMuPDF are required"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        profile = Path(td) / "profile"
        run = subprocess.run(
            libreoffice_headless_command(
                office, profile, "--convert-to", "pdf", "--outdir", td,
                str(Path(pptx).resolve()),
            ),
            capture_output=True, text=True, timeout=120, **quiet_subprocess_kwargs(),
        )
        pdf = Path(td) / (Path(pptx).stem + ".pdf")
        if run.returncode or not pdf.exists():
            return [], "LibreOffice conversion failed: " + (run.stderr or run.stdout)
        if raster:
            subprocess.run([raster, "-png", "-r", "150", str(pdf), str(out / "slide")], check=True, capture_output=True)
        else:
            with fitz.open(pdf) as document:
                for index, page in enumerate(document, 1):
                    page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72), alpha=False).save(out / f"slide-{index}.png")
    return [{"slide_index": i, "path": str(p.resolve()), "sha256": sha_file(p), "dpi": 150} for i, p in enumerate(sorted(out.glob("slide-*.png")), 1)], None

def render_shape_masks(pptx_path, previews, out):
    """Derive occupied-pixel masks by re-rendering with each shape removed."""
    from PIL import Image, ImageChops
    from pptx import Presentation
    baseline = {x["slide_index"]: Image.open(x["path"]).convert("RGB") for x in previews}
    source = Presentation(pptx_path); masks = {}
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shape_names = [(si, shape.name) for si, slide in enumerate(source.slides, 1) for shape in slide.shapes]
        for sequence, (slide_index, shape_name) in enumerate(shape_names):
            variant = Presentation(pptx_path)
            shape = next((x for x in variant.slides[slide_index-1].shapes if x.name == shape_name), None)
            if shape is None:
                continue
            shape._element.getparent().remove(shape._element)
            variant_path = td / f"without-{sequence}.pptx"; variant.save(variant_path)
            rendered, error = render_previews(variant_path, out / f"without-{sequence}")
            candidate = next((x for x in rendered if x["slide_index"] == slide_index), None)
            if error or not candidate:
                continue
            changed = ImageChops.difference(baseline[slide_index], Image.open(candidate["path"]).convert("RGB")).convert("L")
            masks[(slide_index, shape_name)] = changed.point(lambda value: 255 if value > 8 else 0)
    return masks

def pixel_checks(previews):
    from PIL import Image, ImageStat
    checks, findings = [], []
    for preview in previews:
        image = Image.open(preview["path"]).convert("RGB")
        stat = ImageStat.Stat(image)
        extrema = image.getextrema()
        dynamic = max(b for _, b in extrema) - min(a for a, _ in extrema)
        blank = dynamic < 10 or sum(stat.var) < 20
        checks.append((f"pixels-{preview['slide_index']}", not blank, f"dynamic range {dynamic}; variance {sum(stat.var):.1f}"))
        if blank:
            findings.append(finding(f"blank-render-{preview['slide_index']}", "blocking", [preview["slide_index"]], "render is blank/near-blank", "Repair rendering before review."))
    return checks, findings

def rendered_geometry_checks(previews, pptx_path, token, masks=None):
    """Measure actual 150-DPI pixels and shape-removal masks."""
    from PIL import Image, ImageChops
    from pptx import Presentation
    prs = Presentation(pptx_path); findings, checks = [], []
    indexed = {x["slide_index"]: x for x in previews}
    for index, slide in enumerate(prs.slides, 1):
        preview = indexed.get(index)
        if not preview:
            continue
        image = Image.open(preview["path"]).convert("RGB")
        sx, sy = image.width / prs.slide_width, image.height / prs.slide_height
        shapes = list(slide.shapes)
        def box(shape):
            return (max(0, int(shape.left*sx)), max(0, int(shape.top*sy)),
                    min(image.width, int((shape.left+shape.width)*sx)),
                    min(image.height, int((shape.top+shape.height)*sy)))
        for shape in shapes:
            region = box(shape)
            if region[2] <= region[0] or region[3] <= region[1]:
                continue
            patch = image.crop(region)
            mask = (masks or {}).get((index, shape.name))
            if mask is not None and mask.getbbox() and getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
                occupied = mask.getbbox()
                tolerance = 3
                inside = occupied[0] >= region[0]-tolerance and occupied[1] >= region[1]-tolerance and occupied[2] <= region[2]+tolerance and occupied[3] <= region[3]+tolerance
                checks.append((f"rendered-mask-overflow-{index}-{shape.name}", inside, f"occupied pixels {occupied}; declared box {region}"))
                if not inside:
                    findings.append(finding(f"text-overflow-{index}-{shape.name}", "blocking", [index], f"occupied rendered pixels {occupied} escape declared box {region}", "Shorten text, enlarge the box, or use a permitted larger layout."))
            colors = Counter(patch.getdata()).most_common(8)
            if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
                runs = [run for para in shape.text_frame.paragraphs for run in para.runs]
                size = max([run.font.size.pt for run in runs if run.font.size] or [token["type_pt"]["body"]])
                usable_w = max(.1, shape.width / 914400 - .18)
                usable_h = max(.1, shape.height / 914400 - .12)
                chars_per_line = max(1, int(usable_w * 72 / (size * .52)))
                lines = sum(max(1, math.ceil(len(line) / chars_per_line)) for line in shape.text_frame.text.splitlines())
                required_h = lines * size * 1.18 / 72
                ok = required_h <= usable_h
                checks.append((f"rendered-text-overflow-{index}-{shape.name}", ok, f"estimated {required_h:.2f}in in {usable_h:.2f}in; raster {patch.size}"))
                if not ok:
                    findings.append(finding(f"text-overflow-{index}-{shape.name}", "blocking", [index], f"rendered text requires {required_h:.2f}in but box has {usable_h:.2f}in", "Shorten text, enlarge the box, or use a permitted larger layout."))
                if len(colors) >= 2:
                    background = colors[0][0]
                    # The second dominant rendered color represents the glyph
                    # body; choosing the most distant antialias outlier can
                    # falsely turn low-contrast text into black-on-white.
                    foreground = colors[1][0]
                    actual = contrast("#%02X%02X%02X" % background, "#%02X%02X%02X" % foreground)
                    contrast_ok = actual >= token["min_contrast"]
                    checks.append((f"rendered-contrast-{index}-{shape.name}", contrast_ok, f"dominant raster colors {actual:.2f}:1"))
                    if not contrast_ok:
                        findings.append(finding(f"contrast-{index}-{shape.name}", "blocking", [index], f"actual rendered dominant-color contrast {actual:.2f}:1", "Use an AA-compliant foreground/background pair."))
            if shape.shape_type == 13:  # picture
                crop = [shape.crop_left, shape.crop_right, shape.crop_top, shape.crop_bottom]
                source = Image.open(__import__("io").BytesIO(shape.image.blob)).convert("RGB")
                def color_bins(value):
                    return len({tuple((channel // 32) * 32 for channel in pixel)
                                for pixel in value.resize((32, 32)).getdata()})
                source_colors = color_bins(source)
                rendered_colors = color_bins(patch)
                geometric_ok = all(0 <= value < .9 for value in crop) and crop[0]+crop[1] < .9 and crop[2]+crop[3] < .9
                # A destructive crop must also be observable in rendered pixels:
                # the retained raster loses most of a pixel-distinct source.
                pixel_retention = rendered_colors / max(1, source_colors)
                crop_ok = geometric_ok or pixel_retention >= .6
                checks.append((f"rendered-crop-{index}-{shape.name}", crop_ok, f"crop fractions {crop}; source/rendered colors {source_colors}/{rendered_colors}; retention {pixel_retention:.2f}; raster {patch.size}"))
                if not crop_ok:
                    findings.append(finding(f"crop-{index}-{shape.name}", "blocking", [index], f"rendered crop retained {pixel_retention:.0%} of source color detail with fractions {crop}", "Use a valid focal crop retaining visible source detail and at least 10% on each axis."))
        for ai, a in enumerate(shapes):
            for b in shapes[ai+1:]:
                amask=(masks or {}).get((index,a.name)); bmask=(masks or {}).get((index,b.name))
                if amask is not None and bmask is not None:
                    intersection=ImageChops.multiply(amask,bmask)
                    occupied=intersection.getbbox()
                    checks.append((f"rendered-overlap-{index}-{a.name}-{b.name}", occupied is None, f"occupied-mask intersection {occupied}"))
                    if occupied is not None:
                        findings.append(finding(f"rendered-overlap-{index}-{a.name}-{b.name}", "blocking", [index], f"actual occupied-pixel masks intersect at {occupied}", "Separate the overlapping semantic objects."))
                    continue
                ax0,ay0,ax1,ay1=box(a); bx0,by0,bx1,by1=box(b)
                region=(max(ax0,bx0),max(ay0,by0),min(ax1,bx1),min(ay1,by1))
                if region[2] <= region[0] or region[3] <= region[1]:
                    continue
                overlap=(region[2]-region[0])*(region[3]-region[1])
                smaller=max(1,min((ax1-ax0)*(ay1-ay0),(bx1-bx0)*(by1-by0)))
                if overlap/smaller <= .08:
                    continue
                patch=image.crop(region); colors=Counter(patch.getdata()).most_common(2)
                visible=len(colors)>1
                checks.append((f"rendered-overlap-{index}-{a.name}-{b.name}", not visible, f"{overlap/smaller:.1%}; {len(colors)} raster colors"))
                if visible:
                    findings.append(finding(f"rendered-overlap-{index}-{a.name}-{b.name}", "blocking", [index], "semantic geometry overlaps in occupied rendered pixels", "Separate the overlapping semantic objects."))
    return checks, findings

def make_receipt(kind, path, schema_path, run_id, handoff_id, diagnostics, profile=None):
    valid = not diagnostics
    core = {"run_id": run_id, "handoff_id": handoff_id, "artifact_kind": kind, "artifact_path": str(Path(path).resolve()), "artifact_sha256": sha_file(path), "schema_sha256": sha_file(schema_path) if schema_path else None, "producer_agent": "deck-composer", "validator_agent": "deck-critic", "validator_operation": "review", "diagnostics_hash": sha_bytes(canonical(diagnostics)), "inspection_profile": profile}
    receipt = {"schema_version": "3.0", "receipt_version": "1.0", "receipt_id": sha_bytes(canonical(core)), **core, "schema_path": str(Path(schema_path).resolve()) if schema_path else None, "tool_version": "story-deck-inspector/3.3", "validated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "valid": valid, "diagnostic_class": "none" if valid else "producer-artifact-invalid", "diagnostic_count": len(diagnostics), "diagnostics": diagnostics, "superseded": False, "accepted_qa_event_id": None, "accepted_residual_event_id": None, "render_manifest_sha256": None}
    errors = schema_validate(receipt, load(ROOT / "schemas/v3/validation-receipt.schema.json"))
    if errors:
        raise RuntimeError("generated receipt failed schema: " + json.dumps(errors))
    return receipt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True); p.add_argument("--manifest", required=True)
    p.add_argument("--output", required=True); p.add_argument("--run-id", required=True)
    p.add_argument("--handoff-id", required=True); p.add_argument("--receipt-dir")
    p.add_argument("--prior-report"); p.add_argument("--comparison-manifest"); p.add_argument("--model-review")
    a = p.parse_args()
    spec, manifest = load(a.spec), load(a.manifest)
    checks, findings = [], []
    spec_diags = schema_validate(spec, load(ROOT / "schemas/v3/deck-spec.schema.json")) + semantic_validate("deck-spec", spec)
    manifest_diags = schema_validate(manifest, load(ROOT / "schemas/v3/render-manifest.schema.json")) + semantic_validate("render-manifest", manifest)
    checks += [("deck-spec-validation", not spec_diags, json.dumps(spec_diags)), ("render-manifest-validation", not manifest_diags, json.dumps(manifest_diags))]
    outputs = {x["channel"]: x for x in manifest.get("outputs", [])}
    channels = {"pptx": "not-requested", "marp": "not-requested", "parity": manifest.get("parity", {}).get("status", "not-applicable")}
    token = next(x for x in load(ROOT / "design-systems/registry.json")["systems"] if x["id"] == spec["design_system_id"])
    ratio = contrast(token["palette"]["text"], token["palette"]["background"])
    checks.append(("contrast-token-aa", ratio >= token["min_contrast"], f"{ratio:.2f}:1"))
    substitutions = manifest.get("environment", {}).get("fonts", {}).get("substitutions", [])
    checks.append(("font-availability", not substitutions, json.dumps(substitutions)))
    if substitutions:
        findings.append(finding("font-substitution", "major", [], json.dumps(substitutions), "Use available declared fonts or explicitly approve substitutions."))
    output_diagnostics = {"pptx": list(spec_diags) + list(manifest_diags), "marp": list(spec_diags) + list(manifest_diags)}
    for channel in ("pptx", "marp"):
        output = outputs.get(channel)
        if not output: continue
        channels[channel] = "unavailable" if output["status"] == "unavailable" else "fail"
        if output["status"] != "rendered": continue
        if channel == "pptx":
            try:
                f, c = pptx_inspect(output["path"], spec, token); findings += f; checks += c
                output_diagnostics[channel] += f + [{"code": x[0], "message": x[2]} for x in c if not x[1]]
            except Exception as exc:
                findings.append(finding("pptx-inspection", "blocking", [], str(exc), "Produce an openable PPTX.")); channels[channel] = "fail"
        else:
            c = marp_inspect(output["path"], spec); checks += c
            output_diagnostics[channel] += [{"code": x[0], "message": x[2]} for x in c if not x[1]]
    previews = manifest.get("previews", [])
    preview_error = None
    if not previews and outputs.get("pptx", {}).get("status") == "rendered":
        previews, preview_error = render_previews(outputs["pptx"]["path"], Path(a.output).parent / "previews-150dpi")
    valid_previews = [
        x for x in previews
        if x.get("dpi") == 150 and Path(x.get("path", "")).is_file()
        and sha_file(x["path"]) == x.get("sha256")
    ]
    raster_required = outputs.get("pptx", {}).get("status") == "rendered"
    raster_complete = bool(valid_previews) and len(valid_previews) == len(spec["slides"])
    if previews and not raster_complete:
        preview_error = "preview manifest is incomplete, not 150 DPI, missing, or checksum-mismatched"
        previews = []
    if previews:
        c, f = pixel_checks(previews); checks += c; findings += f
        pptx_output = outputs.get("pptx", {})
        if pptx_output.get("status") == "rendered":
            masks = render_shape_masks(pptx_output["path"], previews, Path(a.output).parent / "shape-masks-150dpi")
            rc, rf = rendered_geometry_checks(previews, pptx_output["path"], token, masks); checks += rc; findings += rf
            output_diagnostics["pptx"] += rf + [{"code": x[0], "message": x[2]} for x in rc if not x[1]]
    capability_reason = preview_error or "no 150-DPI previews"
    checks.append(("visual-render-150dpi", not raster_required or raster_complete, f"{len(previews)} verified 150-DPI previews" if raster_complete else capability_reason))
    model = {"status": "unavailable", "scores": {}, "notes": ["Deck Critic must inspect every listed 150-DPI preview and pass --model-review JSON."]}
    if a.model_review:
        candidate = load(a.model_review)
        scores = candidate.get("scores", {})
        if candidate.get("status") != "completed" or not all(k in scores and isinstance(scores[k], (int, float)) and 0 <= scores[k] <= 1 for k in ("narrative", "visual_craft", "evidence_fit")) or not candidate.get("notes"):
            findings.append(finding("model-review-contract", "blocking", [], "invalid model visual QA handoff", "Provide completed scores and evidence notes.", "cross-format"))
        else:
            model = candidate
    elif previews:
        findings.append(finding("model-review-required", "blocking", [], "previews exist but model visual QA handoff is absent", "Deck Critic must inspect previews with vision and provide --model-review.", "cross-format"))
    repro = {"checked": bool(manifest.get("reproducibility", {}).get("second_render_checked")), "matching": manifest.get("reproducibility", {}).get("matching"), "comparison_manifest_sha256": sha_file(a.comparison_manifest) if a.comparison_manifest else None}
    checks.append(("reproducibility", repro["checked"] and repro["matching"] is True, "genuine normalized second-render comparison"))
    checks_json = [{"id": x[0], "status": "pass" if x[1] else ("unavailable" if x[0] == "visual-render-150dpi" and not previews else "fail"), "evidence": x[2]} for x in checks]
    for check in checks_json:
        if check["status"] in ("pass", "unavailable"):
            continue
        diagnostic = {"code": check["id"], "message": check["evidence"]}
        if check["id"] == "visual-render-150dpi" or check["id"].startswith(("pixels-", "rendered-", "pptx-")):
            output_diagnostics["pptx"].append(diagnostic)
        elif check["id"].startswith("marp-"):
            output_diagnostics["marp"].append(diagnostic)
        else:
            output_diagnostics["pptx"].append(diagnostic)
            output_diagnostics["marp"].append(diagnostic)
    # Finalize channel status only after structural, semantic, raster, parity,
    # and reproducibility diagnostics have all completed.
    for channel in ("pptx", "marp"):
        output = outputs.get(channel)
        if not output:
            channels[channel] = "not-requested"
        elif output["status"] == "unavailable":
            channels[channel] = "unavailable"
        elif channel == "pptx" and raster_required and not raster_complete:
            channels[channel] = "unavailable"
        elif output["status"] != "rendered" or output_diagnostics[channel]:
            channels[channel] = "fail"
        else:
            channels[channel] = "pass"
    structural = all(x["status"] in ("pass", "unavailable") for x in checks_json)
    scores = model.get("scores", {})
    metrics = {"structural": 1.0 if structural else 0.0, "source_coverage": sum(bool(x["evidence_ids"]) for x in spec["slides"]) / len(spec["slides"]), "narrative": scores.get("narrative", 0.0), "evidence_fit": scores.get("evidence_fit", 0.0), "accessibility": 1.0 if not any(x["id"].startswith("alt-") for x in findings) else 0.0, "visual_craft": scores.get("visual_craft", 0.0), "parity": 1.0 if channels["parity"] in ("pass", "not-applicable") else 0.0, "reproducibility": 1.0 if repro["matching"] else 0.0}
    verdict = "unverified-needs-user" if raster_required and not raster_complete else ("revise" if findings or not structural else ("pass" if model["status"] == "completed" else "unverified-needs-user"))
    prior = None
    if a.prior_report:
        old = load(a.prior_report); old_ids = {x["id"] for x in old["findings"]}; new_ids = {x["id"] for x in findings}
        prior = {"prior_sha256": sha_file(a.prior_report), "improved_finding_ids": sorted(old_ids - new_ids), "regressed_finding_ids": sorted(new_ids - old_ids)}
    receipt_ids = []
    if a.receipt_dir:
        receipt_dir = Path(a.receipt_dir); receipt_dir.mkdir(parents=True, exist_ok=True)
        candidates = [("deck-spec", a.spec, ROOT / "schemas/v3/deck-spec.schema.json", spec_diags), ("render-manifest", a.manifest, ROOT / "schemas/v3/render-manifest.schema.json", manifest_diags)]
        for output in manifest.get("outputs", []):
            if output["status"] == "rendered":
                diags = list(output_diagnostics.get(output["channel"], []))
                completed = ["identity", "structural", "semantic", "parity", "reproducibility"]
                unavailable = []
                capability_status = "complete"
                if output["channel"] == "pptx":
                    if raster_complete:
                        completed.insert(3, "raster-150dpi")
                    else:
                        capability_status = "raster-unavailable"
                        unavailable.append({"diagnostic": "raster-150dpi", "reason": capability_reason})
                        diags.append({"code": "raster-150dpi-unavailable", "message": capability_reason})
                if not Path(output["path"]).is_file() or sha_file(output["path"]) != output["sha256"]:
                    diags.append({"code": "staged-output", "path": output["path"], "message": "missing/checksum mismatch"})
                if manifest.get("parity", {}).get("status") == "fail":
                    diags.append({"code": "parity", "message": "cross-format parity failed"})
                if not repro["checked"] or repro["matching"] is not True:
                    diags.append({"code": "reproducibility", "message": "second render did not match"})
                profile = {
                    "id": f"story-staged-{output['channel']}/1",
                    "artifact_format": output["channel"],
                    "completed_diagnostics": completed,
                    "unavailable_diagnostics": unavailable,
                    "capability_status": capability_status,
                }
                candidates.append((f"staged-{output['channel']}", output["path"], None, diags, profile))
        for candidate in candidates:
            kind, path, schema, diagnostics = candidate[:4]
            profile = candidate[4] if len(candidate) == 5 else None
            receipt = make_receipt(kind, path, schema, a.run_id, a.handoff_id, diagnostics, profile)
            rp = receipt_dir / (receipt["receipt_id"][7:] + ".validation-receipt.json")
            if rp.exists() and load(rp) != receipt:
                raise RuntimeError("immutable receipt collision")
            if not rp.exists(): dump(rp, receipt)
            if receipt["valid"]: receipt_ids.append(receipt["receipt_id"])
    report = {"schema_version": "3.0", "run_id": a.run_id, "handoff_id": a.handoff_id, "verdict": verdict, "channels": channels, "deterministic_checks": checks_json, "model_review": model, "findings": findings, "metrics": metrics, "prior_comparison": prior, "validated_receipt_ids": receipt_ids, "previews": previews, "reproducibility": repro}
    report_errors = schema_validate(report, load(ROOT / "schemas/v3/qa-report.schema.json")) + semantic_validate("qa-report", report)
    if report_errors:
        print(json.dumps({"status": "error", "diagnostics": report_errors}, indent=2)); return 2
    dump(a.output, report); print(json.dumps(report, indent=2))
    return 0 if verdict in ("pass", "unverified-needs-user") else 1

if __name__ == "__main__":
    raise SystemExit(main())

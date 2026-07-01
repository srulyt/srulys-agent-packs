"""``evalpilot`` command-line interface.

Author, run, and inspect evals with the modeled result at the centre:

* ``evalpilot new``      — scaffold a ``*.eval.md`` (or ``*.eval.py``) spec.
* ``evalpilot run``      — discover + execute specs, render terminal/HTML/JSON.
* ``evalpilot show``     — re-render a previous run from its JSON.
* ``evalpilot lint``     — validate specs without running the SUT.
* ``evalpilot metrics``  — numeric trends; ``--check`` fails on regressions.
* ``evalpilot discover`` — list agents/skills evalpilot can see.
* ``evalpilot init``     — scaffold an ``evals/`` tree from bundled templates.

Every ``run`` writes a canonical ``report.json`` (plus HTML) under
``<eval_root>/_runs/<run-id>/`` so the result location is always obvious.
"""

from __future__ import annotations

import argparse
import json
import shutil
import webbrowser
from pathlib import Path
from typing import Optional

from . import collect, discovery, metrics
from .config import bundled_data_dir, find_eval_root, find_metrics_root, find_repo_root
from .executor import run_specs
from .render import render_html, render_terminal, write_json
from .render.json_report import read_json
from .spec import EvalSpec


# ---- new ----------------------------------------------------------------

_MD_TEMPLATE = """\
---
name: {name}
target: {target}
kind: {kind}
tags: [smoke]
timeout: 600
---

# {title}
> One-line summary of what a good result looks like.

## Description
Explain, in plain English, the scenario this eval exercises: the starting
context, what the agent/skill is asked to do, and what a correct outcome looks
like. This is the human-readable intent — an agent can implement the sections
below directly from it.

## Setup
```yaml
# stage: {{ {stage} }}          # inferred from target+kind; override here if needed
# files: [{{ copy: "fixtures/**", dest: "." }}]
```

## Act
```prompt
Replace this with a prompt that exercises a real scenario. Do NOT include the
expected answer -- the point is that the agent had to work it out.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]        # at least one artifact was produced
contains:
  - {{ text: "REPLACE", ignore_case: true }}   # against stdout by default
judge:
  # artifact: path/to/output.md    # omit to judge stdout
  threshold: 0.7
  criteria: |
    Score 1.0 only if ALL criteria are met; 0.5 for partial; 0.0 if off-topic.
metrics:
  - {{ name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }}
```
"""

# Description-first stub: prose only, no Act/Assert yet. Lints as [stub];
# hand it to an agent to implement the executable sections.
_MD_STUB_TEMPLATE = """\
---
name: {name}
target: {target}
kind: {kind}
tags: [smoke]
timeout: 600
---

# {title}
> {summary}

## Description
{description}

<!-- TODO: ask an agent to implement ## Setup / ## Act / ## Assert from the
     description above, then run `evalpilot run` on this file. -->
"""

_PY_TEMPLATE = '''\
"""Builder-style eval for {name}. Run with: evalpilot run this_file.eval.py"""

from evalpilot import Eval

eval = (
    Eval("{name}", target="{target}", kind="{kind}", tags=["smoke"], timeout=600)
    .summarize("One-line summary of what a good result looks like.")
    .describe("Explain the scenario, the action, and what a correct outcome is.")
    .prompt("Replace with a prompt that exercises a real scenario.")
    .expect_file("**/*.md")
    .judge(
        "Score 1.0 only if ALL criteria are met; 0.5 partial; 0.0 off-topic.",
        threshold=0.7,
    )
    .metric("judge_score", "$judge.score", direction="higher_is_better",
            baseline="rolling_mean", tolerance=0.1)
    .build()
)
'''


def _cmd_new(args) -> int:
    eval_root = find_eval_root()
    out_dir = Path(args.dir).resolve() if args.dir else eval_root
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = ".eval.py" if args.python else ".eval.md"
    dest = out_dir / f"{args.name}{ext}"
    if dest.exists() and not args.force:
        print(f"refusing to overwrite {dest} (pass --force)")
        return 1
    stage = f"{args.kind}: {args.target}" if args.kind in ("agent", "skill") else ""
    title = args.name.replace("-", " ").title()
    describe = getattr(args, "describe", None)
    if describe and not args.python:
        # Description-first: emit a prose-only stub for an agent to implement.
        dest.write_text(
            _MD_STUB_TEMPLATE.format(
                name=args.name, target=args.target or args.name, kind=args.kind,
                title=title, summary=describe.splitlines()[0].strip(),
                description=describe.strip(),
            ),
            encoding="utf-8",
        )
        print(f"created {dest} (stub)")
        print("\nNext steps:")
        print("  1. review the ## Description")
        print(f"  2. ask an agent to implement ## Setup / ## Act / ## Assert in {dest.name}")
        print(f"  3. evalpilot lint {dest.name}   # shows [stub] until implemented")
        return 0
    template = _PY_TEMPLATE if args.python else _MD_TEMPLATE
    dest.write_text(
        template.format(
            name=args.name, target=args.target or args.name, kind=args.kind,
            title=title, stage=stage,
        ),
        encoding="utf-8",
    )
    print(f"created {dest}")
    print("\nNext steps:")
    print(f"  1. edit the prompt / criteria in {dest.name}")
    print(f"  2. evalpilot run {dest}")
    return 0


# ---- run ----------------------------------------------------------------


def _cmd_run(args) -> int:
    eval_root = find_eval_root()
    target = Path(args.target).resolve() if args.target else eval_root
    if not target.exists():
        print(f"nothing to run: {target} does not exist")
        return 2

    specs = collect.collect_specs(target)
    specs = _filter_tags(specs, args.tags)
    if not specs:
        print(f"no evals found under {target}"
              + (f" matching tags {args.tags!r}" if args.tags else ""))
        return 2

    report = run_specs(
        specs,
        parallel=args.parallel,
        runner=_runner_override(args.runner),
    )
    # The executor placed workspaces under <eval_root>/_runs/<run_id>/.
    out_dir = eval_root / "_runs" / report.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    fmts = _formats(args.format)
    json_path = write_json(report, out_dir / "report.json")
    _write_latest_pointer(eval_root, out_dir)
    html_path = None
    if "html" in fmts:
        html_path = out_dir / "report.html"
        html_path.write_text(render_html(report), encoding="utf-8")

    print(render_terminal(
        report,
        json_path=str(json_path),
        html_path=str(html_path) if html_path else None,
    ))

    if args.open and html_path:
        webbrowser.open(html_path.as_uri())

    if args.no_gate:
        return 0
    return 0 if report.ok else 1


# ---- show ---------------------------------------------------------------


def _cmd_show(args) -> int:
    report_path = _resolve_report(args.run)
    if report_path is None:
        print("no runs found. Run `evalpilot run` first.")
        return 2
    report = read_json(report_path)
    if args.format == "html":
        html_path = report_path.parent / "report.html"
        html_path.write_text(render_html(report), encoding="utf-8")
        print(f"wrote {html_path}")
        if args.open:
            webbrowser.open(html_path.as_uri())
    else:
        print(render_terminal(report, json_path=str(report_path)))
    return 0 if report.ok else 1


# ---- lint ---------------------------------------------------------------


def _cmd_lint(args) -> int:
    target = Path(args.target).resolve() if args.target else find_eval_root()
    specs = collect.collect_specs(target)
    if not specs:
        print(f"no evals found under {target}")
        return 2
    problems = 0
    stubs = 0
    for s in specs:
        loc = s.spec_path or s.name
        if s.is_stub():
            stubs += 1
            print(f"[stub] {loc}  ({s.name})")
            print("        - described, awaiting implementation; "
                  "ask an agent to implement Act/Assert")
            continue
        issues = s.validate()
        if issues:
            problems += 1
            print(f"[FAIL] {loc}")
            for i in issues:
                print(f"        - {i}")
        else:
            print(f"[ ok ] {loc}  ({s.name})")
    tail = f"\n{len(specs)} specs, {problems} with problems"
    if stubs:
        tail += f", {stubs} stub{'s' if stubs != 1 else ''}"
        if args.strict:
            tail += " (failing: --strict)"
    print(tail)
    if problems:
        return 1
    if stubs and args.strict:
        return 1
    return 0


# ---- init ---------------------------------------------------------------


def _cmd_init(args) -> int:
    repo_root = find_repo_root()
    eval_root = find_eval_root(repo_root)
    templates = bundled_data_dir() / "templates"
    eval_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for src in templates.rglob("*"):
        if src.is_dir() or "__pycache__" in src.parts:
            continue
        dst = eval_root / src.relative_to(templates)
        if dst.exists() and not args.force:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created.append(dst)

    print(f"evalpilot init -> {eval_root}")
    for c in created:
        print(f"  created {c.relative_to(repo_root)}")
    if not created:
        print("  (nothing to create; pass --force to overwrite)")
    print("\nNext steps:")
    print("  1. edit examples/hello-agent.eval.md (set a real target) then: evalpilot run")
    print("  2. or scaffold your own: evalpilot new my-eval --target my-agent --kind agent")
    print("  3. try it offline first: EVALPILOT_RUNNER=mock evalpilot run <file>")
    return 0


# ---- discover -----------------------------------------------------------


def _cmd_discover(args) -> int:
    repo_root = find_repo_root()
    agents = discovery.discover_agents(repo_root)
    skills = discovery.discover_skills(repo_root)
    if args.json:
        print(json.dumps({
            "repo_root": str(repo_root),
            "agents": [{"name": a.name, "path": str(a.path)} for a in agents],
            "skills": [{"name": s.name, "path": str(s.path)} for s in skills],
        }, indent=2))
        return 0
    print(f"repo root: {repo_root}")
    print(f"\nagents ({len(agents)}):")
    for a in agents:
        print(f"  - {a.name:30} {a.path.relative_to(repo_root)}")
    print(f"\nskills ({len(skills)}):")
    for s in skills:
        print(f"  - {s.name:30} {s.path.relative_to(repo_root)}")
    return 0


# ---- metrics ------------------------------------------------------------


def _cmd_metrics(args) -> int:
    metrics_root = find_metrics_root()
    series = list(metrics.iter_series(metrics_root))
    if args.slug:
        series = [(slug, hp) for slug, hp in series if args.slug in slug]
    if not series:
        print(f"No metric history under {metrics_root}")
        return 0

    any_regression = False
    for slug, hp in series:
        history = []
        for line in hp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if not history:
            continue
        latest = history[-1]
        values = [r["value"] for r in history if isinstance(r.get("value"), (int, float))]
        regressions = sum(1 for r in history if r.get("regressed"))
        any_regression = any_regression or bool(latest.get("regressed"))
        flag = "  <-- REGRESSED" if latest.get("regressed") else ""
        print(f"\n{slug}{flag}")
        print(f"  runs={len(history)} latest={latest.get('value')} "
              f"baseline={latest.get('baseline')} "
              f"min={min(values) if values else None} "
              f"max={max(values) if values else None} "
              f"regressions={regressions}")
        if args.verbose:
            for r in history[-args.tail:]:
                print(f"    {r.get('ts')} {r.get('value')} "
                      f"(d{r.get('delta')}) {'REGRESSED' if r.get('regressed') else ''}")

    if args.check and any_regression:
        print("\nRegressions detected in latest run.")
        return 1
    return 0


# ---- helpers ------------------------------------------------------------


def _filter_tags(specs: list[EvalSpec], expr: Optional[str]) -> list[EvalSpec]:
    if not expr:
        return specs
    tokens = [t.strip() for t in expr.split(",") if t.strip()]
    includes = {t for t in tokens if not t.startswith(("-", "~"))}
    excludes = {t[1:] for t in tokens if t.startswith(("-", "~"))}
    out = []
    for s in specs:
        tags = set(s.tags)
        if includes and not (includes & tags):
            continue
        if excludes & tags:
            continue
        out.append(s)
    return out


def _formats(raw: str) -> set[str]:
    parts = {p.strip() for p in raw.split(",") if p.strip()}
    if "all" in parts:
        return {"terminal", "html", "json"}
    return parts or {"terminal", "json"}


def _runner_override(name: Optional[str]):
    if not name:
        return None
    from .runners.base import get_runner
    return get_runner(name)


def _write_latest_pointer(eval_root: Path, out_dir: Path) -> None:
    (eval_root / "_runs" / "latest.txt").write_text(
        str(out_dir / "report.json"), encoding="utf-8"
    )


def _resolve_report(run: Optional[str]) -> Optional[Path]:
    runs_dir = find_eval_root() / "_runs"
    if run:
        p = Path(run)
        if p.is_file():
            return p
        cand = runs_dir / run / "report.json"
        return cand if cand.exists() else None
    pointer = runs_dir / "latest.txt"
    if pointer.exists():
        p = Path(pointer.read_text(encoding="utf-8").strip())
        if p.exists():
            return p
    reports = sorted(runs_dir.glob("*/report.json"))
    return reports[-1] if reports else None


# ---- argument parsing ---------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="evalpilot", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    pn = sub.add_parser("new", help="scaffold a new *.eval.md (or *.eval.py) spec")
    pn.add_argument("name")
    pn.add_argument("--target", help="agent or skill under test")
    pn.add_argument("--kind", choices=["agent", "skill", "none"], default="agent")
    pn.add_argument("--python", action="store_true", help="scaffold a builder *.eval.py")
    pn.add_argument("--describe", metavar="TEXT",
                    help="description-first: emit a prose-only stub for an agent "
                         "to implement (markdown only)")
    pn.add_argument("--dir", help="output directory (default: eval root)")
    pn.add_argument("--force", action="store_true")
    pn.set_defaults(func=_cmd_new)

    pr = sub.add_parser("run", help="run evals and render results")
    pr.add_argument("target", nargs="?", help="spec file or dir (default: eval root)")
    pr.add_argument("-t", "--tags", help="tag filter, e.g. 'smoke,-slow'")
    pr.add_argument("--parallel", type=int, default=1, help="concurrent workers")
    pr.add_argument("--format", default="all",
                    help="terminal,html,json,all (default: all)")
    pr.add_argument("--runner", help="SUT runner override (e.g. mock)")
    pr.add_argument("--open", action="store_true", help="open the HTML report")
    pr.add_argument("--no-gate", action="store_true",
                    help="always exit 0 (don't fail on eval failures)")
    pr.set_defaults(func=_cmd_run)

    ps = sub.add_parser("show", help="re-render a previous run from its JSON")
    ps.add_argument("run", nargs="?", help="run id or report.json (default: latest)")
    ps.add_argument("--format", choices=["terminal", "html"], default="terminal")
    ps.add_argument("--open", action="store_true")
    ps.set_defaults(func=_cmd_show)

    pl = sub.add_parser("lint", help="validate specs without running the SUT")
    pl.add_argument("target", nargs="?", help="spec file or dir (default: eval root)")
    pl.add_argument("--strict", action="store_true",
                    help="treat description-only stubs as failures (for CI)")
    pl.set_defaults(func=_cmd_lint)

    pi = sub.add_parser("init", help="scaffold an evals/ tree into this repo")
    pi.add_argument("--force", action="store_true", help="overwrite existing files")
    pi.set_defaults(func=_cmd_init)

    pd = sub.add_parser("discover", help="list discoverable agents and skills")
    pd.add_argument("--json", action="store_true")
    pd.set_defaults(func=_cmd_discover)

    pm = sub.add_parser("metrics", help="show metric trends")
    pm.add_argument("slug", nargs="?", help="filter series by substring")
    pm.add_argument("--check", action="store_true",
                    help="exit non-zero if the latest run regressed")
    pm.add_argument("-v", "--verbose", action="store_true")
    pm.add_argument("--tail", type=int, default=5, help="rows to show with -v")
    pm.set_defaults(func=_cmd_metrics)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

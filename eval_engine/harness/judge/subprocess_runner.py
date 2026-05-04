"""Non-interactive judge invocation.

Replaces the human-paste step that ``judge-plan`` documents. For each
:class:`JudgeRequest` in a manifest, we spawn the Copilot CLI in
non-interactive (``-p``) mode targeting the ``eval-judge`` agent, wait
for it to exit, extract the judge's JSON object from stdout, and write
it to ``request.response_file`` so the existing ``score`` / replay
pipeline can pick it up unchanged.

The judge is asked to emit ``{"score": float, "rationale": str, ...}``.
We accept three extraction strategies, in order of preference:

  1. The full stdout parses as a JSON object that has ``score`` and
     ``rationale`` keys.
  2. A fenced ``json`` code block (``\`\`\`json ... \`\`\``) parses
     and has the required keys.
  3. The last balanced ``{...}`` blob in stdout parses and has the
     required keys.

If extraction fails on the first attempt we retry once. After that we
write a structured ``{"error": "..."}`` payload to ``response_file`` so
``load_responses`` reports a judge error rather than a missing file.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .orchestration import JudgeManifest, JudgeRequest


_FENCED_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


@dataclass
class JudgeRunResult:
    request_id: str
    response_file: str
    success: bool
    error: str | None = None
    stdout_excerpt: str = ""


class CopilotBinNotFound(RuntimeError):
    """Raised when the configured ``copilot`` binary is not on PATH."""


def _resolve_copilot_bin(copilot_bin: str) -> str:
    """Resolve the binary path; raise CopilotBinNotFound if missing."""
    if Path(copilot_bin).exists():
        return str(Path(copilot_bin).resolve())
    found = shutil.which(copilot_bin)
    if found is None:
        raise CopilotBinNotFound(
            f"copilot binary {copilot_bin!r} not found on PATH"
        )
    return found


def _extract_json_object(text: str) -> dict | None:
    """Try the three strategies in order. Returns None on failure."""
    text = text.strip()
    if not text:
        return None

    def _ok(obj: object) -> dict | None:
        if not isinstance(obj, dict):
            return None
        if "score" not in obj or "rationale" not in obj:
            return None
        return obj

    # Strategy 1: whole stdout is the JSON object.
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        obj = None
    out = _ok(obj)
    if out is not None:
        return out

    # Strategy 2: last fenced ```json block.
    fenced = _FENCED_JSON_RE.findall(text)
    for blob in reversed(fenced):
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        out = _ok(obj)
        if out is not None:
            return out

    # Strategy 3: last balanced {...} blob.
    blob = _last_balanced_object(text)
    if blob is not None:
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            obj = None
        out = _ok(obj)
        if out is not None:
            return out

    return None


def _last_balanced_object(text: str) -> str | None:
    """Return the last top-level balanced ``{...}`` blob, or None.

    Quick scanner that ignores braces inside string literals. Not a full
    JSON parser, but good enough to isolate a JSON candidate from
    arbitrary surrounding prose.
    """
    end = text.rfind("}")
    while end != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(end, -1, -1):
            c = text[i]
            if esc:
                esc = False
                continue
            if c == "\\":
                esc = True
                continue
            if c == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if c == "}":
                depth += 1
            elif c == "{":
                depth -= 1
                if depth == 0:
                    return text[i : end + 1]
        end = text.rfind("}", 0, end)
    return None


def _build_argv(
    *,
    copilot_bin: str,
    prompt: str,
    name: str,
    judge_agent: str = "eval-judge",
) -> list[str]:
    return [
        copilot_bin,
        "-p",
        prompt,
        "--agent",
        judge_agent,
        "--allow-all-tools",
        "--allow-all-paths",
        "--no-ask-user",
        "--name",
        name,
    ]


def run_one_judge_request(
    req: JudgeRequest,
    *,
    copilot_bin: str,
    run_id: str,
    request_index: int,
    timeout_seconds: float = 600.0,
    judge_seed: str | None = None,
    judge_agent: str = "eval-judge",
    retry_on_malformed: bool = True,
) -> JudgeRunResult:
    """Run a single judge request and write the response file.

    Always writes ``req.response_file`` — either the parsed judge JSON
    on success, or a small ``{"error": ...}`` blob on failure. Returns
    a JudgeRunResult describing what happened.
    """
    Path(req.response_file).parent.mkdir(parents=True, exist_ok=True)
    prompt = req.prompt
    if judge_seed:
        prompt = (
            f"# Judge seed for reproducibility: {judge_seed}\n"
            f"# Incorporate this exact seed string into your reasoning so "
            f"that prompt-side state is stable across re-runs.\n\n"
            + prompt
        )
    name = f"{run_id}-judge-{request_index:03d}"
    argv = _build_argv(
        copilot_bin=copilot_bin, prompt=prompt, name=name,
        judge_agent=judge_agent,
    )
    last_error = ""
    last_stdout = ""
    attempts = 2 if retry_on_malformed else 1
    for attempt in range(attempts):
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            last_error = f"timeout after {timeout_seconds}s"
            continue
        except FileNotFoundError as exc:
            # Bubble up: this is a hard infrastructure error.
            raise CopilotBinNotFound(str(exc)) from exc
        last_stdout = proc.stdout or ""
        if proc.returncode != 0:
            last_error = (
                f"copilot exited {proc.returncode}: "
                f"{(proc.stderr or '').strip()[:400]}"
            )
            continue
        obj = _extract_json_object(last_stdout)
        if obj is None:
            last_error = "could not extract a {score, rationale} JSON object from stdout"
            continue
        Path(req.response_file).write_text(
            json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8",
        )
        return JudgeRunResult(
            request_id=req.request_id,
            response_file=req.response_file,
            success=True,
            stdout_excerpt=last_stdout[:400],
        )

    # All attempts failed — write a structured error payload.
    payload = {
        "error": last_error or "unknown judge subprocess failure",
        "score": None,
        "rationale": "",
    }
    Path(req.response_file).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    return JudgeRunResult(
        request_id=req.request_id,
        response_file=req.response_file,
        success=False,
        error=last_error,
        stdout_excerpt=last_stdout[:400],
    )


def run_manifest(
    manifest: JudgeManifest,
    *,
    copilot_bin: str = "copilot",
    timeout_seconds: float = 600.0,
    judge_seed: str | None = None,
    judge_agent: str = "eval-judge",
    progress: callable = None,
) -> list[JudgeRunResult]:
    """Run every request in a manifest, in order. See module docstring."""
    bin_path = _resolve_copilot_bin(copilot_bin)
    out: list[JudgeRunResult] = []
    for i, req in enumerate(manifest.requests):
        if progress is not None:
            progress(i, len(manifest.requests), req.request_id)
        out.append(
            run_one_judge_request(
                req,
                copilot_bin=bin_path,
                run_id=manifest.run_id,
                request_index=i + 1,
                timeout_seconds=timeout_seconds,
                judge_seed=judge_seed,
                judge_agent=judge_agent,
            )
        )
    return out

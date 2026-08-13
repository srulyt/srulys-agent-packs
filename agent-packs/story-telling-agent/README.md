# Story Telling Agent v3

An evidence-led GitHub Copilot plugin that plans once, renders deterministic PPTX and Marp siblings from one strict model, performs structural and 150-DPI visual QA, then atomically publishes an immutable accepted version.

## Install and invoke

Install `story-telling-agent` from this repository's Copilot plugin marketplace, or install this plugin directory directly using current Copilot CLI plugin commands. Then invoke:

```text
@story-orchestrator Build an executive decision deck from docs/brief.md. Audience: ELT. Decision: approve Q4 investment. Formats: both.
```

The four agents are Story Orchestrator (user-facing), Narrative Strategist, Deck Composer, and Deck Critic (delegation-only). The plugin contains exactly 12 canonical skills. `agents/` and `skills/` are canonical; no hand-maintained `.github` copy ships.

## Workflow and outputs

The v3 pipeline is `intake → evidence ledger → story plan → deck spec → output.pptx/output.md → render manifest → QA report`. Stable claim/evidence IDs flow into slides, sources, and notes. Proposal approval, degraded-mode acceptance, residual acceptance, and replacement consent use structured events. State is under `.story-telling-stm/runs/<id>/`; its indexed receipt lineage binds every guarded transition to exact handoff, artifact checksum, operation, predecessor, capability, manifest, and approval/acceptance identities. Resume validates independent receipts and invalidates downstream lineage when inputs change.

Composition writes only to immutable staging. QA must pass, or the user must explicitly accept enumerated residuals. Publication preflights collisions, verifies frozen checksums, creates `versions/<publication-id>/`, and atomically updates `current.json`; interrupted or failed revisions leave the last good version in place.

## Dependencies and degraded modes

Create an environment and install pinned requirements explicitly:

```powershell
python -m pip install -r agent-packs/story-telling-agent/requirements.txt
python agent-packs/story-telling-agent/scripts/preflight.py --json
```

Scripts never install or use the network. Missing PPTX or Marp dependencies can offer a user-approved available channel. Missing LibreOffice prevents visual verification and yields `unverified-needs-user`, never pass. Font substitutions and unavailable capabilities are recorded.

LibreOffice conversion is always non-interactive: each invocation uses an
isolated temporary user profile, disables synchronous printer detection, and
passes headless/no-default/no-restore flags. It must never display a console,
printer, recovery, or profile dialog.

On Windows, automated LibreOffice conversion is disabled because LibreOffice
26.x can still display printer dialogs despite headless flags and isolated
profiles. PPTX generation continues, but raster visual QA reports
`unverified-needs-user`. Run visual QA in Linux/WSL or another non-interactive
environment instead; installing LibreOffice again will not change this policy.

Supported external tools are **Marp CLI 4.x** (with Node.js 20 or 22 LTS) and
**LibreOffice 24.2+**. Install them before starting Copilot; both executables must be on
`PATH` (`marp` and `soffice`/`libreoffice`). The PPTX source renderer requires
Python 3.10+ and pinned `python-pptx`; contract validation requires pinned `jsonschema`.
At 150 DPI, visual QA additionally requires either `pdftoppm` (Poppler) or
the pinned PyMuPDF fallback. Preflight returns:

- `ok`: requested channels and requested visual QA are available.
- `degraded`: at least one sibling channel or visual QA is unavailable, but a usable
  channel remains. The orchestrator must ask for explicit degraded-mode acceptance.
- `error`: validation or all requested rendering capabilities are unavailable. Composition
  stops with actionable missing-tool diagnostics.

Run `preflight.py --formats both --require-visual-qa --json`; a nonzero exit is deliberate
(`1` degraded, `2` error). It never installs, downloads, or silently changes formats.

## Privacy, accessibility, and provenance

Public-web research requires intake approval and must never disclose supplied/private context. Unsupported claims remain explicit. Meaningful images require source/license, focal crop and alt text; charts require units, source, axis policy, focal annotation and non-color encoding.

## Legacy and migration

Generate compatibility files in a consuming repository:

```powershell
python agent-packs/story-telling-agent/scripts/install-legacy-layout.py --target .
python agent-packs/story-telling-agent/scripts/install-legacy-layout.py --target . --check
```

The generator records checksums and refuses overwrite unless `--force`. See [MIGRATION.md](MIGRATION.md). v2 state is exported for context/assets but restarted under v3 validation receipts.

## Marketplace maintainer update

The durable updater is `scripts/update-marketplace.py`. It is dry-run by
default, preserves unknown entry fields and ordering conventions, rejects
source collisions, deduplicates the plugin name, supports an expected-hash
race guard, fsyncs the replacement and parent directory where supported, and
verifies the persisted bytes after atomic replacement with `--apply`:

```powershell
python agent-packs/story-telling-agent/scripts/update-marketplace.py
python agent-packs/story-telling-agent/scripts/update-marketplace.py --expected-sha256 sha256:<live-hash> --apply
```

Applying `.github/plugin/marketplace.json` is intentionally a repository-level
maintainer action; plugin runtime agents never mutate the live registry.

## Evals

```powershell
evalpilot lint evals/packs/story-telling-agent/
evalpilot run evals/packs/story-telling-agent/
node scripts/run-evals.mjs story-telling-agent
```

Limitations: visual quality varies by installed fonts/office renderer; PPTX and Marp have different native capabilities; prompt path boundaries are policy rather than an OS sandbox.

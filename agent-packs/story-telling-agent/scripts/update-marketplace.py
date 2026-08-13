"""Safely register this plugin in a repository marketplace registry.

Dry-run is the default. Use --apply only from a repository-level workflow that
is authorized to mutate the live registry.
"""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

NAME = "story-telling-agent"
SOURCE = "agent-packs/story-telling-agent"

def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()

def fsync_parent(path):
    """Make a completed rename durable when the host supports directory fsync."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        fd = os.open(path, flags)
    except (OSError, NotImplementedError) as exc:
        return {"status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"}
    try:
        os.fsync(fd)
        return {"status": "completed", "reason": None}
    except (OSError, NotImplementedError) as exc:
        return {"status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"}
    finally:
        os.close(fd)

def update(registry):
    if not isinstance(registry, dict) or not isinstance(registry.get("plugins"), list):
        raise ValueError("marketplace root must be an object with a plugins array")
    plugins = registry["plugins"]
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str) or not isinstance(plugin.get("source"), str):
            raise ValueError(f"plugins[{index}] must contain string name and source")
        if plugin["source"] == SOURCE and plugin["name"] != NAME:
            raise ValueError(f"source collision: {SOURCE} is owned by {plugin['name']}")
    matches = [i for i, plugin in enumerate(plugins) if plugin["name"] == NAME]
    canonical = {"name": NAME, "source": SOURCE}
    if matches:
        canonical = {**plugins[matches[0]], **canonical}
        registry["plugins"] = [
            canonical if i == matches[0] else plugin
            for i, plugin in enumerate(plugins)
            if i == matches[0] or i not in matches
        ]
        action = "replace" if len(matches) == 1 else "replace-and-deduplicate"
    else:
        names = [plugin["name"] for plugin in plugins]
        if names == sorted(names):
            at = next((i for i, value in enumerate(names) if value > NAME), len(plugins))
            plugins.insert(at, canonical)
            action = f"insert-sorted:{at}"
        else:
            plugins.append(canonical)
            action = "append"
    final = [plugin for plugin in registry["plugins"] if plugin["name"] == NAME]
    if len(final) != 1 or final[0]["source"] != SOURCE:
        raise AssertionError("marketplace registration postcondition failed")
    return registry, action

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".github/plugin/marketplace.json")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    before = target.read_bytes()
    before_hash = digest(before)
    if args.expected_sha256 and args.expected_sha256 != before_hash:
        raise SystemExit(f"refusing stale update: expected {args.expected_sha256}, live {before_hash}")
    updated, action = update(json.loads(before.decode("utf-8")))
    after = (json.dumps(updated, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    parsed = json.loads(after)
    matches = [plugin for plugin in parsed["plugins"] if plugin["name"] == NAME]
    if len(matches) != 1 or matches[0]["source"] != SOURCE:
        raise SystemExit("serialized postcondition failed")
    result = {
        "target": str(target), "action": action, "before_sha256": before_hash,
        "after_sha256": digest(after), "changed": before != after, "applied": False,
        "post_replace_verified": False,
        "parent_directory_fsync": {"status": "not-required", "reason": None},
    }
    if args.apply and before != after:
        fd, temp_name = tempfile.mkstemp(prefix="marketplace-", suffix=".json", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(after)
                handle.flush()
                os.fsync(handle.fileno())
            if target.read_bytes() != before:
                raise RuntimeError("marketplace changed during update")
            os.replace(temp_name, target)
            result["parent_directory_fsync"] = fsync_parent(target.parent)
            persisted = target.read_bytes()
            if persisted != after or digest(persisted) != result["after_sha256"]:
                raise RuntimeError("marketplace post-replace durability verification failed")
            result["post_replace_verified"] = True
            result["applied"] = True
        finally:
            Path(temp_name).unlink(missing_ok=True)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

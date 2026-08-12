import path from "node:path";
import { fileURLToPath } from "node:url";

const PACK = /^[a-z0-9][a-z0-9-]*$/;
const ABSOLUTE_OR_URI = /^(?:[A-Za-z]:[\\/]|\\\\|\/\/|\/|[a-z][a-z0-9+.-]*:)/i;

function safeSegments(value) {
  if (typeof value !== "string" || value.length === 0) return false;
  if (ABSOLUTE_OR_URI.test(value) || value.includes("\\") || /[*?[\]]/.test(value)) {
    return false;
  }
  const parts = value.split("/");
  return !parts.some((part) => part === "" || part === "." || part === "..");
}

export function validateFixablePath(value, pack) {
  if (!PACK.test(pack) || !safeSegments(value)) return false;
  const prefix = `agent-packs/${pack}/`;
  if (!value.startsWith(prefix) || value === prefix.slice(0, -1)) return false;

  const relative = value.slice(prefix.length);
  if (!relative.startsWith(".github/")) return false;

  // Verify without using normalization as a substitute for pre-validation.
  const root = path.resolve("agent-packs", pack);
  const resolved = path.resolve(value);
  const rel = path.relative(root, resolved);
  return rel !== "" && !rel.startsWith(`..${path.sep}`) && rel !== ".." &&
    !path.isAbsolute(rel) && value.split("/").join(path.sep) ===
      path.relative(path.resolve("."), resolved);
}

export function validateEvalTarget(value, pack) {
  if (!PACK.test(pack) || value === "all") return value === "all";
  if (!safeSegments(value)) return false;
  const prefix = `evals/packs/${pack}/`;
  if (!value.startsWith(prefix)) return false;
  const root = path.resolve("evals", "packs", pack);
  const resolved = path.resolve(value);
  const rel = path.relative(root, resolved);
  return rel !== "" && !rel.startsWith(`..${path.sep}`) && rel !== ".." &&
    !path.isAbsolute(rel);
}

function main(argv) {
  const [kind, pack, ...values] = argv.slice(2);
  const validator = kind === "fixable" ? validateFixablePath
    : kind === "target" ? validateEvalTarget
      : null;
  if (!validator || !pack || values.length === 0) {
    console.error("usage: validate-factory-paths.mjs fixable|target <pack> <path>...");
    return 2;
  }
  const invalid = values.filter((value) => !validator(value, pack));
  if (invalid.length) {
    console.error(JSON.stringify({ valid: false, invalid }));
    return 1;
  }
  console.log(JSON.stringify({ valid: true, values }));
  return 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = main(process.argv);
}

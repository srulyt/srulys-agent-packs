/**
 * Shared assertion helpers for evals.
 *
 * {@link assertProseContains} normalises whitespace (collapsing all runs of
 * whitespace to a single space) before comparing, so wrapping-induced newlines
 * don't break the match. Use this for **prose** assertions. Do NOT use it for
 * **structural** assertions where exact formatting matters.
 */

/** Collapse all whitespace runs to single spaces. */
export function normalise(text: string): string {
  return text.split(/\s+/).filter(Boolean).join(" ");
}

/** Assert `needle` appears in `text` after whitespace normalisation. */
export function assertProseContains(
  text: string,
  needle: string,
  opts: { logPath?: string; extra?: string } = {},
): void {
  const normText = normalise(text);
  const normNeedle = normalise(needle);
  if (normText.includes(normNeedle)) return;
  const prefix = opts.extra ? `${opts.extra}\n` : "";
  const logHint = opts.logPath ? `\n  log: ${opts.logPath}` : "";
  throw new Error(
    `${prefix}prose substring not found (after whitespace normalisation):` +
      `\n  needle: ${JSON.stringify(normNeedle)}${logHint}`,
  );
}

/** Mirror of {@link assertProseContains} for the negative case. */
export function assertProseNotContains(
  text: string,
  needle: string,
  opts: { logPath?: string; extra?: string } = {},
): void {
  const normText = normalise(text);
  const normNeedle = normalise(needle);
  if (!normText.includes(normNeedle)) return;
  const prefix = opts.extra ? `${opts.extra}\n` : "";
  const logHint = opts.logPath ? `\n  log: ${opts.logPath}` : "";
  throw new Error(
    `${prefix}prose substring unexpectedly present ` +
      `(after whitespace normalisation):` +
      `\n  needle: ${JSON.stringify(normNeedle)}${logHint}`,
  );
}

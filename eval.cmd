@echo off
rem Convenience wrapper: `eval <pack> [flags]`  (or `eval --all`)
rem Forwards to the TypeScript eval engine via scripts\run-evals.mjs
node "%~dp0scripts\run-evals.mjs" %*

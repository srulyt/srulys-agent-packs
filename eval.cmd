@echo off
rem Convenience wrapper: `eval <pack> [tests...]`
rem Forwards everything to scripts\run_evals.py
python "%~dp0scripts\run_evals.py" %*

# Copilot Instructions for XMD ToolBox

These instructions apply to all code created for this project.

## General

- Follow clean code principles.
- Prefer clarity over cleverness.
- Minimize side effects and shared global state.
- Keep functions focused and small.

## Python

- Use type hints for public functions.
- Use docstrings for functions and classes.
- Keep line length at or under 120 characters when practical.
- Avoid modifying shared module state (sys, math, random).

## JavaScript or TypeScript (If Used)

- Add JSDoc comments for all functions.
- Prefer named functions for clarity.
- Keep modules small and purpose-driven.

## ZBrush SDK Constraints

- Assume a shared, persistent Python VM.
- Do not use multiprocessing.
- Do not spawn subprocesses using sys.executable.
- Do not override sys.stdin/stdout/stderr.
- Do not change the working directory.
- Clean up any sys.path modifications.

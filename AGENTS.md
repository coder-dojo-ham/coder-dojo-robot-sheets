# AI Agent Guidelines

The term contributors also means agents. These guidelines apply to all agents working on this project.

## Required Reading

Before making any contributions, review the following documents:

- [README.md](./README.md) — Project overview
- **Folder-specific READMEs** — If a folder containing a file you are editing has a README.md, read it first.

## Code Style

- Favour brevity, clarity, and readability over verbose prose
- Keep documentation concise and actionable
- Use clear, direct language in code comments and documentation
- Follow existing patterns and conventions in the codebase

## Documentation Conventions

- **Date format**: always `yyyy-mm-dd` for datestamped files and entries
- Keep documentation focused and actionable

## Memory

Memory does not live in this repo. Unless otherwise instructed, it goes in the orionrobots
memories repo (`~/ai/orionrobots_memories`), in this project's PARA project folder under
`10-projects/`. If no project folder exists yet, create one with that repo's
`new-memory-project` skill and link it here.

Read the project folder's seed file first — it is the router, holds the log, and ends with
the Next Session bridge. Put decisions in `decisions.md`, other notes in dated
`YYYY-MM-DD-<topic>.md` files, and follow that repo's README.md and AGENTS.md. Do not use
Claude Code's built-in auto memory.

Capture decisions, context, and things to remember. Skip secrets unless explicitly asked to
keep them. Apply progressive summarisation when reading from memories.

### Write It Down

Memory does not survive session restarts. Files do.

- When someone says "remember this" → update the project's orionrobots memories folder (see Memory above)
- When you learn a lesson → update `AGENTS.md` or the relevant file
- When you make a mistake → document it so future-you doesn't repeat it
- Working code with notes beats regenerating similar code from scratch later

## Red Lines

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

## Python Preferences

- Use `uv` to manage virtual environments: `uv run python <script>.py`
- Use `ruff` to keep Python code tidy

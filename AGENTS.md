# Agent Instructions

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `workflows/*/*.md`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read workflow directives, call colocated scripts in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. You should route to the correct workflow, then use its `scripts/` folder rather than improvising the implementation from scratch.

**Layer 3: Execution (Doing the work)**
- Deterministic scripts live in `workflows/<workflow>/scripts/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check the target workflow's `scripts/` directory per its directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

**4. Always read `SKILL_SETUP.md` for any skills-related request**
If the user asks about skills in any form (usage, discovery, installation, setup, identification, search, or operational workflow), read `SKILL_SETUP.md` first and follow it as the source of truth for how skills should be found, installed, set up, used etc.

**5. Skill Usage**
Always check the `SKILLS.md` file in the `docs/` folder to see what specialized capabilities are available to you. Use these skills whenever applicable to the user's request.

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `workflows/` - Active workflow source of truth (directives + scripts + workflow docs)
- `runtime/` - Generated artifacts, working directories, outputs and temp data. Never commit.
- `skills-local/` - Project-specific local skills that are not already covered by global Codex skills.
- `archive/do-usuniecia/` - Staging area for retired, duplicate, or suspicious files pending final removal.
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Repo holds workflow source-of-truth. Runtime output should go to `runtime/`, not to workflow source directories.

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

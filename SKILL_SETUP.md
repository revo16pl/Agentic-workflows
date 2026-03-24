# Skill Management Setup Guide

Use this guide to initialize skills for any new project if asked about using, finding, or installing skills.

## 1. Global Skills Repository
The master library of all available skills is located here:
`/Users/revo/.agents/skills`

## 2. Setup Procedure
When starting a project or adding skills, follow these steps:

### Step A: Identify Needed Skills
1. Analyze the project requirements (e.g., "React frontend", "Python backend", "Browser automation").
2. Browse the Global Skills Repository to find matching skills.
   - *Example:* If the project uses React, look for `react-patterns`, `feature-sliced-design`, etc.

### Step B: Decide if a Local Copy Is Actually Needed
Default rule: do **not** duplicate global Codex skills into the repo unless the skill contains project-specific instructions, references, or agent config that are not available globally.

Use a local repo copy only for specialized assets under `./skills-local/`.

### Step C: Create/Update SKILLS.md
1. Create or update `docs/SKILLS.md`.
2. List active workflows and only the project-local skills that are actually maintained in-repo.
   - *Format:*
     ```markdown
     # Project Skills
     
     - **[skill-name]**: [Short description of what it does]
     - **[another-skill]**: [Short description of what it does]
     ```

### Step D: Configure Agents
1. Update `AGENTS.md`.
2. Append the following instruction to the "Operating Principles" or "Instructions" section:
   > **Skill Usage**: Always check the `SKILLS.md` file in the `docs/` folder to see what specialized capabilities are available to you. Use these skills whenever applicable to the user's request.

## 3. Maintenance
- If you add a new project-local skill later, place it in `./skills-local/` and repeat **Step C**.

## 4. Discover and Install Skills via `find-skills`
If you need to discover skills for a specific task, use the helper skill located at:
`/Users/revo/.agents/skills/find-skills`

Important order for new skills:
1. First install skill into the global skills directory: `/Users/revo/.agents/skills`
2. Only create a project-local copy if the repo needs a customized variant or bundled references
3. If you create a project-local copy, store it in `./skills-local/`
4. Then register it in `docs/SKILLS.md` and, if needed, in `AGENTS.md`

Recommended workflow:

1. Search by intent/domain:
   - `npx skills find react performance`
   - `npx skills find pr review`
   - `npx skills find changelog`
2. Review results and pick the package in format `<owner/repo@skill>`.
3. Install selected skill globally first:
   - `npx skills add <owner/repo@skill> -g -y`
4. If needed, copy/install into current project local `./skills-local/` (from `/Users/revo/.agents/skills`).
5. Verify and maintain:
   - Check updates: `npx skills check`
   - Update installed skills: `npx skills update`

Reference catalog: `https://skills.sh/`

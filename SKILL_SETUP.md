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

### Step B: Install Skills Locally
1. Create a `skills/` directory in the project root if it doesn't exist.
2. Copy the selected skill folders from the Global Repository to `./skills/`.
   - *Example Command:* `cp -r ~/.agents/skills/<skill_name> ./skills/`

### Step C: Create/Update SKILLS.md
1. Create a file named `SKILLS.md` in the `DOCS/` folder. If the `DOCS/` folder doesn't exist, create it.
2. List all installed skills with a brief description.
   - *Format:*
     ```markdown
     # Project Skills
     
     - **[skill-name]**: [Short description of what it does]
     - **[another-skill]**: [Short description of what it does]
     ```

### Step D: Configure Agents
1. Update **ALL** agent configuration files present in the project (e.g., `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).
2. Append the following instruction to the "Operating Principles" or "Instructions" section:
   > **Skill Usage**: Always check the `SKILLS.md` file in the `DOCS/` folder to see what specialized capabilities are available to you. Use these skills whenever applicable to the user's request.

## 3. Maintenance
- If you add a new skill later, repeat **Step B** and **Step C**.

## 4. Discover and Install Skills via `find-skills`
If you need to discover skills for a specific task, use the helper skill located at:
`/Users/revo/.agents/skills/find-skills`

Important order for new skills:
1. First install skill into global skills directory: `/Users/revo/.agents/skills`
2. Then copy skill into project-local `./skills/`
3. Only after that, register/use it in project docs and agent configs

Recommended workflow:

1. Search by intent/domain:
   - `npx skills find react performance`
   - `npx skills find pr review`
   - `npx skills find changelog`
2. Review results and pick the package in format `<owner/repo@skill>`.
3. Install selected skill globally first:
   - `npx skills add <owner/repo@skill> -g -y`
4. Copy/install into current project local `./skills/` (from `/Users/revo/.agents/skills`).
5. Verify and maintain:
   - Check updates: `npx skills check`
   - Update installed skills: `npx skills update`

Reference catalog: `https://skills.sh/`

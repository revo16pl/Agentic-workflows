# Notes: Turn Claude Code into Your Own INCREDIBLE UI Designer (using Playwright MCP Subagents)

## 🚀 Core Concept: The "Missing 90%"
The core thesis is that LLMs (like Claude Opus/Sonnet) have massive "visual intelligence" trained on images, but standard coding agents only use the text/code modality ("blindfolded").
**The Unlock**: Use **Playwright MCP** to give the agent "eyes" (screenshots), enabling it to see its own work, compare it to designs, and iteratively self-correct.

## 🛠️ Actionable Methods & Workflows

### 1. The Iterative Agentic Loop (Front-end Engineering)
Instead of one-shot prompting, set up a loop where the agent:
1.  **Reads Spec**: Looks at a UI mockup, style guide, or prompt.
2.  **Implements**: Writes the code.
3.  **Verifies**: Uses Playwright to **take a screenshot** of the localhost page.
4.  **Compares**: Analyzes the screenshot against the original spec.
5.  **Fixes**: Self-corrects visual discrepancies (padding, colors, alignment) that are hard to spot in code but obvious in images.

### 2. "Design Reviewer" Sub-Agent
Create a dedicated "Sub-Agent" (can be a slash command or conditioned context) specifically for design reviews.
*   **Persona**: "Principal Designer".
*   **Task**: Navigate to the page, take screenshots, check mobile responsiveness, check console errors.
*   **Output**: A structured report with an "A-F" grade and specific fix requests.
*   **Chaining**: The Design Reviewer can call a "Mobile Specialist" sub-agent for focused mobile testing.

### 3. Git Worktrees for Parallel "Abundance"
Don't rely on one attempt. Use **Git Worktrees** to spawn 3 separate instances of the repo.
*   **Command**: `git worktree add ...`
*   **Workflow**: Run Claude Code in all 3 worktrees simultaneously with the same prompt (or slight variations).
*   **Result**: You get 3 different design approaches. Pick the best one, or merge the best parts.

### 4. Reference Scraping
Use Playwright to visit *other* websites (inspiration) and scrape/screenshot them to use as context for your own design.
*   **Prompt**: "Go to [URL], take a screenshot, and use that header layout as inspiration for my site."

### 5. Automated "Monkey Testing"
Ask the agent to "navigate the site like a user":
*   Click buttons, fill forms, submit data.
*   **Goal**: Catch red console errors or broken flows that static analysis misses.

## 🔧 Configuration & Setup Specifics

### Playwright MCP Config
*   **Headless vs. Headed**: Run `headless: false` (in `mcp_config.json`) to watch the agent work. It builds trust and lets you spot issues faster.
*   **Mobile Emulation**: Configure Playwright to emulate specific devices (e.g., "iPhone 15") for mobile-first testing.

### "Memory" Files (`.claude/config.json` / `claude.md`)
*   Treat configuration files as "Long-term Memory".
*   **Include**:
    *   **Style Guides**: Hex codes, typography, spacing rules.
    *   **Design Principles**: "We prefer clean, minimal UI", "Always use consistent padding".
    *   **Tech Stack Rules**: "Use Tailwind, avoiding arbitrary values".
*   **Benefit**: This context is injected into *every* session, preventing the "generic shadcn/ui" look.

## 💡 Key Insights
*   **Orchestration vs. Prompting**: Success isn't about the perfect prompt; it's about the **environment** (Tools + Context + Validation).
*   **Visual Circuits**: You are paying for a multimodal model (Opus/Sonnet)—use the visual processing circuits!
*   **Sub-Agents as Packageable Expertise**: You can "package" your Senior Engineer's code review process into a prompt/sub-agent and distribute it to the whole team.

## 🔗 Tools Mentioned
*   **Playwright MCP**: The core tool for browser automation.
*   **Claude Code**: The agentic CLI.
*   **Git Worktrees**: For parallelizing experiments.

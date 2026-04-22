---
name: create-skill
user-invocable: true
description: "Workflow skill for converting a conversational request into a reusable/replicable SKILL.md in the repository. Includes extraction of steps, decision points, and quality criteria."

# Create Skill Workflow

This skill codifies the multi-step process used in the current conversation to build a `SKILL.md` from scratch.

## 1) Extract and formalize the pattern
- Review conversation history for explicit workflow instructions and goals.
- Find any repeating sequence of tasks and decision branches.
- Capture acceptance criteria (validation checks).

## 2) Clarify ambiguous points
- Ask what output is expected (file vs. plan vs. template).
- Ask if scope is workspace-scoped or user-scoped.
- Determine if a quick checklist is enough or full multi-step instructions are needed.

## 3) Draft the artifact
- Choose file type: skill, instruction, prompt, agent, hook.
- Pick path and naming conventions (workspace: `.github/skills/<name>/SKILL.md`; user: `{{VSCODE_USER_PROMPTS_FOLDER}}/` for prompts/instructions).
- Add YAML frontmatter: name, displayName, description, applyTo, triggers.
- Add body sections: purpose, when to use, steps, examples.

## 4) Validate and iterate
- Confirm path and file creation.
- Validate YAML syntax and required fields.
- Ask for explicit review points where ambiguity remains.

## 5) Finalize
- Summarize produced artifact and next actions.
- Provide sample invocation prompts.

## Checklist (completion criteria)
- [x] Workflow has been extracted and documented
- [x] File created in repository path
- [x] Frontmatter includes name/displayName/description
- [x] Trigger phrases make the skill discoverable
- [x] User is asked for any remaining ambiguities

## Quick start
- In Copilot Chat, use `/create-skill-agent` to launch the workflow.
- Then follow prompts to generate or update `SKILL.md` files.

## Example prompts
- "Use this skill to turn my conversation about agent customizations into a shareable SKILL.md."
- "Create a workspace skill that explains when to use `.instructions.md` versus `SKILL.md`."
- "Generate a compact skill checklist for this repo’s naming conventions."

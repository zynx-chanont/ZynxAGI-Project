---
name: create-skill-agent
description: "Agent for building and validating SKILL.md workflows in the repository. Focus on agent-customization best practices, template patterns and safe incremental edits."
user-invocable: true
---

# Create Skill Agent

Use this agent when the user wants to define a reusable workflow for generating VS Code agent customization files in this repo.

## When to use
- Building `SKILL.md` for team onboarding, checklist automation, or repo-specific processes.
- Converting an ad hoc interaction into structured process documentation.

## When not to use
- General conversation that does not produce a persisted agent or skill file.
- Cases requiring per-developer personal settings only (use `*.prompt.md` in user folder instead).
# Zynx AGI - System Agents

This document provides an overview of the agents operating within the Zynx AGI ecosystem. Each agent is a modular component designed for a specific function, and they collaborate through the **Model Context Protocol (MCP)**.

**Last Updated:** June 23, 2025

---

## Agent Template

Each agent is defined by the following structure:

- **Status:** Current development stage (e.g., 🟢 Live, 🟡 Planned).
- **Core Function:** A one-sentence summary of the agent's primary purpose.
- **Key Capabilities:** A list of its specific functions and abilities.
- **MCP Command:** The primary slash command used to interact with the agent.
- **Notes:** Additional context or important information.

---

## 1. Deeja (ดีจ้า)

- **Status:** 🟢 **Live**
- **Core Function:** To serve as the primary emotional AI, facilitating empathetic, ethical, and culturally aware human-computer interactions.
- **Key Capabilities:**
    - Empathy Scoring & Calibration (`self-reflect` process)
    - Ethical Reasoning based on a core Knowledge Base
    - Cultural Sensitivity (specializing in Thai/Global contexts)
    - Natural Language Processing & Translation
    - User well-being analysis
- **MCP Command:** `/deeja`
- **Notes:** Deeja is the heart of the Zynx AGI "Empathy-First" philosophy. It is the most mature agent and serves as the primary interface for many user-facing tasks. It embodies the "Thai Tech with Heart" principle.

## 2. CodeD

- **Status:** 🟡 **Planned**
- **Core Function:** To act as a specialized coding assistant for generating, analyzing, and debugging code.
- **Key Capabilities:**
    - Code generation from natural language prompts.
    - Error analysis and debugging suggestions.
    - Creation of technical documentation and docstrings.
    - Optimizing code for performance and readability.
- **MCP Command:** `/coded`
- **Notes:** CodeD is designed to streamline the development workflow for both internal Zynx developers and external users on the AaaP platform.

## 3. Verifier

- **Status:** 🟡 **Planned**
- **Core Function:** To fact-check, validate information, and review outputs from other agents for accuracy and ethical compliance.
- **Key Capabilities:**
    - Cross-referencing information against trusted sources.
    - Validating the logical consistency of agent outputs.
    - Flagging potential misinformation, bias, or ethical breaches.
    - Ensuring all outputs adhere to the Zynx ethical framework.
- **MCP Command:** `/verifier`
- **Notes:** Verifier acts as a critical quality control and safety layer within the multi-agent system. It can be invoked in a workflow to check the output of another agent (e.g., `/deeja:summarize [text] | /verifier:check`).

## 4. Dispatcher

- **Status:** 🟢 **Live** (Core System Component)
- **Core Function:** To parse user prompts and route tasks to the appropriate agent based on MCP commands and contextual cues.
- **Key Capabilities:**
    - Parsing Slash Prompts (`/agent:action`) and @mentions (`@context`).
    - Managing the execution queue for all agents.
    - Orchestrating complex, multi-step workflows that involve several agents.
- **MCP Command:** Not directly invoked by users.
- **Notes:** The Dispatcher is the central nervous system of the MCP. It operates transparently in the background to ensure seamless communication and task delegation across the entire platform.

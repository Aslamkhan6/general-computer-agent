# Reliability-First General Computer Agent

> **Reliable Long-Horizon Computer Task Execution Through Hybrid State-Grounded Tool Orchestration and Continuous Verification**

An autonomous agent system designed to accomplish complex, long-horizon computer tasks by dynamically orchestrating APIs, CLI, browser DOM, accessibility metadata, and visual GUI controls. Built with continuous state verification, dynamic failure recovery, skill abstraction, and a policy-driven security engine.

---

## 📑 Table of Contents
- [1. Executive Summary & Vision](#1-executive-summary--vision)
- [2. System Architecture](#2-system-architecture)
  - [2.1 Core System Pipeline](#21-core-system-pipeline)
  - [2.2 State-First Interface Preference Hierarchy](#22-state-first-interface-preference-hierarchy)
- [3. Key Architectural Components](#3-key-architectural-components)
  - [3.1 Intent Engine & Context Builder](#31-intent-engine--context-builder)
  - [3.2 Supervisor & Task Planner](#32-supervisor--task-planner)
  - [3.3 Tool Router & Executor](#33-tool-router--executor)
  - [3.4 Observer, State Estimator & Verifier](#34-observer-state-estimator--verifier)
  - [3.5 Diagnoser, Recovery Engine & Replanner](#35-diagnoser-recovery-engine--replanner)
  - [3.6 Memory Architecture (Episodic, Semantic, Procedural)](#36-memory-architecture)
  - [3.7 Skill Learning System](#37-skill-learning-system)
  - [3.8 Security, Policy Engine & Audit System](#38-security-policy-engine--audit-system)
- [4. End-to-End Task Execution Workflow](#4-end-to-end-task-execution-workflow)
- [5. Project Directory Structure](#5-project-directory-structure)
- [6. Installation & Prerequisites](#6-installation--prerequisites)
- [7. Quickstart & Usage](#7-quickstart--usage)
- [8. Evaluation & Benchmarking Strategy](#8-evaluation--benchmarking-strategy)
- [9. Tech Stack](#9-tech-stack)
- [10. License & Citation](#10-license--citation)

---

## 1. Executive Summary & Vision

Existing computer-use systems focus primarily on visual interaction ("can the AI click around the desktop?"). However, research shows that frontier agents struggle with long-horizon workflows due to lost constraints, hidden application states, poor verification, and premature stopping.

This project shifts the paradigm from **Computer Use** to **Reliable Computer Task Completion**.

### Core Pillars
1. **Hybrid Interface Intelligence**: Prioritizes fast, deterministic state interactions (APIs, CLI, DOM) over raw pixel manipulation.
2. **Dynamic Task Graphs**: Breaks down high-level intent into adaptive execution graphs capable of branching during runtime failures.
3. **Continuous Verification**: Evaluates actual computer state transitions after every action rather than trusting raw model outputs.
4. **Self-Healing & Skill Extraction**: Diagnoses execution bottlenecks, retries via fallback interfaces, and synthesizes repeated successful patterns into procedural skills.
5. **Deterministic Policy Control**: Enforces strict policy-based execution guardrails (SAFE / REVIEW / BLOCK) to protect user environments.

---

## 2. System Architecture

### 2.1 Core System Pipeline

                            USER
                             │
                     Text / Voice / API
                             │
                             ▼
                   ┌───────────────────┐
                   │   INTENT ENGINE   │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │    SUPERVISOR     │
                   └─────────┬─────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
               ▼             ▼             ▼
            MEMORY        POLICY        CONTEXT
               │          ENGINE           │
               └─────────────┬─────────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │   TASK PLANNER    │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │    TASK GRAPH     │
                   └─────────┬─────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │   TOOL ROUTER     │
                   └─────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    STATE TOOLS         EXECUTION TOOLS     GUI TOOLS
         │                   │                   │
         │              ┌────┼────┐        ┌────┼────┐
         │              │    │    │        │    │    │
         ▼              ▼    ▼    ▼        ▼    ▼    ▼
     APIs/DB          CLI   Code Docker   DOM  A11Y Vision
         │              │    │    │        │    │    │
         └──────────────┴────┴────┴────────┴────┴────┘
                                │
                                ▼
                          POLICY ENGINE
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                      Allowed       Approval
                         │             │
                         │          USER / AUDIT
                         │             │
                         └──────┬──────┘
                                ▼
                          TOOL EXECUTOR
                                │
                                ▼
                           OBSERVATION
                                │
                                ▼
                         STATE ESTIMATOR
                                │
                                ▼
                            VERIFIER
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
               SUCCESS                     FAILURE
                  │                           │
                  ▼                           ▼
              CONTINUE                    DIAGNOSER
                  │                           │
                  │                           ▼
                  │                       RECOVERY
                  │                           │
                  │                           ▼
                  │                        REPLAN
                  │                           │
                  └───────────────────────────┘

---

### 2.2 State-First Interface Preference Hierarchy

To maximize speed, accuracy, and efficiency while reducing token costs, the **Tool Router** executes operations using the highest available level in the hierarchy:

                  ┌───────────────────────────┐
                  │  Level 1: Structured      │  APIs, Databases, Filesystem
                  └─────────────┬─────────────┘
                                │ (Fallback)
                                ▼
                  ┌───────────────────────────┐
                  │  Level 2: Programmatic    │  CLI (PowerShell, Bash), Git, Docker
                  └─────────────┬─────────────┘
                                │ (Fallback)
                                ▼
                  ┌───────────────────────────┐
                  │  Level 3: Semantic UI     │  Browser DOM, Windows Accessibility (A11y)
                  └─────────────┬─────────────┘
                                │ (Fallback)
                                ▼
                  ┌───────────────────────────┐
                  │  Level 4: Visual GUI      │  Vision Models, OCR, Mouse/Keyboard Control
                  └───────────────────────────┘

---

## 3. Key Architectural Components

### 3.1 Intent Engine & Context Builder
- **Intent Engine**: Parses free-form user requests (text, voice, API triggers) into precise programmatic goals and constraints.
- **Context Builder**: Gathers local state environment details, working directories, active user session data, and relevant system hardware parameters.

### 3.2 Supervisor & Task Planner
- **Supervisor**: High-level coordinator that monitors overall task progression, resource usage, and security policies.
- **Task Planner**: Constructs a **Dynamic Task Graph** (Directed Acyclic Graph) defining dependencies, parallel workflows, and target state criteria.

### 3.3 Tool Router & Executor
- **Tool Router**: Dynamically matches sub-tasks to interface layers (API, CLI, DOM, GUI) based on reliability ratings and application availability.
- **Tool Executor**: Encapsulates atomic calls into deterministic functions (e.g., `filesystem.create_directory()`, `terminal.run_command()`) with standardized structured responses.

### 3.4 Observer, State Estimator & Verifier
- **Observer**: Captures actual post-execution telemetry (exit codes, DOM tree changes, snapshot buffers, terminal output).
- **State Estimator**: Reconstructs the updated system state model.
- **Verifier**: Independent evaluation engine that inspects state transformations against expected outcome criteria (e.g., verifying `file.size > 0` or checking HTTP status codes) before marking a step as complete.

### 3.5 Diagnoser, Recovery Engine & Replanner
- **Diagnoser**: Triggered when verification fails. Analyzes error outputs, missing windows, or unmet conditions.
- **Recovery Engine**: Attempts localized self-healing actions (e.g., refocusing application windows, clearing temp files, changing tool fallback interface).
- **Replanner**: Modifies the remaining Task Graph dynamically if recovery requires a different sequence of operations.

### 3.6 Memory Architecture
The agent utilizes a segmented tri-part memory engine:

                            memory_engine/
                                  │
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
    episodic_memory        semantic_memory       procedural_memory
           │                      │                      │
     [Past Tasks]           [Environment]          [Reusable Skills]
     [Trajectories]         [User Prefs]           [Workflow Macros]
     [Failure Logs]         [System Specs]         [Automated Graphs]

### 3.7 Skill Learning System
Automates procedural skill synthesis:
1. Identifies successfully completed long-horizon trajectories.
2. Extracts macro-steps, parameterizing variables (e.g., paths, URLs, options).
3. Compiles the workflow into a reusable procedural skill stored in memory for instant retrieval.

### 3.8 Security, Policy Engine & Audit System
Guarantees deterministic control over system operations via a policy matrix:

| Operation Category | Default Policy | Action / Behavior |
| :--- | :--- | :--- |
| Read public/local files | `AUTOMATIC` | Execute immediately without prompt |
| Web Search / API Fetch | `AUTOMATIC` | Execute immediately |
| Directory creation / temp build | `AUTOMATIC` | Execute immediately |
| Dependency Installation (`npm install`, `pip install`) | `CONFIGURABLE` | Automatic if in sandboxed path |
| Git Commit / Branch Creation | `CONFIGURABLE` | Prompt or execute based on profile |
| File Deletion / Modification | `ASK` | Require user explicit approval |
| Email Dispatch / Data Upload | `ASK` | Require user explicit approval |
| Financial / Credential Access | `EXPLICIT APPROVAL` | Mandatory approval with 2FA/Confirmation |

All actions, policy checks, observations, and state transitions are logged to immutable JSON audit trajectories.

---

## 4. End-to-End Task Execution Workflow

┌───┐   1. User Request    ┌────────────────┐   2. Resolve Goal & Context   ┌────────────┐
│ 👤│ ───────────────────> │ INTENT ENGINE  │ ────────────────────────────> │ SUPERVISOR │
└───┘                      └────────────────┘                               └─────┬──────┘
│
┌────────────────┐   5. Policy Check OK   ┌──────────────┐   3. Generate Graph    │
│ TOOL ROUTER    │ <───────────────────── │ TASK PLANNER │ <──────────────────────┘
└──────┬─────────┘                        └──────────────┘
│
│ 4. Route to Interface (API/CLI/DOM/GUI)
▼
┌────────────────┐   6. Execute Command   ┌──────────────┐   7. Collect Output    ┌────────────┐
│ TOOL EXECUTOR  │ ─────────────────────> │   OBSERVER   │ ─────────────────────> │ ESTIMATOR  │
└────────────────┘                        └──────────────┘                        └─────┬──────┘
│
┌────────────────┐                        ┌──────────────┐   8. Verify Transition       │
│   CONTINUE     │ <── [SUCCESS = TRUE] ─ │   VERIFIER   │ <────────────────────────┘
└──────┬─────────┘                        └──────┬───────┘
│                                         │
▼                                         │ [SUCCESS = FALSE]
┌────────────────┐                               ▼
│ TASK COMPLETE  │                        ┌──────────────┐   9. Analyze Root Cause
└────────────────┘                        │  DIAGNOSER   │
└──────┬───────┘
│
▼
┌──────────────┐  10. Fallback Interface / Replan
│   RECOVERY   │ ───────────────────┐
└──────────────┘                    │
▲                            │
└────────────────────────────┘


---

## 5. Installation & Prerequisites

### Prerequisites
- Python 3.10+
- Node.js 18+ (for DOM/Playwright browser automation)
- Docker Desktop (optional, for isolated container execution)
- System Permissions: Accessibility access enabled (macOS/Windows)

### Setup

```bash
# Clone the repository
git clone [https://github.com/Aslamkhan6/general-computer-agent.git](https://github.com/Aslamkhan6/general-computer-agent.git)
cd general-computer-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser drivers (for DOM/Browser automation)
playwright install chromium

# Set up environment configuration
cp .env.example .env
7. Quickstart & Usage
Running the Agent
Start the agent CLI dashboard:

Bash
python main.py
Pass a direct complex task via CLI argument:

Bash
python main.py --task "Build and deploy my portfolio site, verify production URL, and commit changes to Git"
Inspected Trajectory Output Example
JSON
{
  "task_id": "TASK-82F9",
  "goal": "Build and deploy portfolio",
  "status": "SUCCESS",
  "metrics": {
    "steps_completed": 14,
    "retries": 1,
    "verification_rate": 1.0,
    "total_time_seconds": 42.5
  },
  "trajectory": [
    {
      "step": 1,
      "action": "terminal.execute",
      "interface": "CLI",
      "command": "npm run build",
      "result": { "exit_code": 0, "output_dir": "./dist" },
      "verification": { "verified": true, "check": "dist directory exists and populated" }
    }
  ]
}
8. Evaluation & Benchmarking Strategy
The system features a benchmark evaluator designed after WeaveBench and OSWorld 2.0 standards, measuring real performance over outcome bias.

Evaluated Metrics
Success Rate: Binary task completion rate based on real state inspection.

Trajectory Accuracy: Ratio of steps correctly verified vs false positives.

Recovery Rate: Percentage of encountered errors successfully recovered from automatically.

Interface Cost Metric: Ratio of low-cost (CLI/API) calls vs high-cost (Vision/GUI) calls.

Run benchmarking suite:

Bash
python -m tests.benchmark.run_eval --suite long_horizon_hybrid
9. Tech Stack
Core Orchestration: Python 3.10+, LangChain / LangGraph (Task Graphs)

State & CLI Execution: Subprocess, Asyncio, Docker SDK

Browser & DOM Controls: Playwright, Accessibility API Integration

GUI & Computer Vision: OpenCV, Pillow, PyAutoGUI

Verification Engine: Pydantic validation schemas, Custom State Assertions

UI & Telemetry: Rich / Textual (CLI Dashboard), Structured JSON Logging

10. License & Citation
Distributed under the MIT License. See LICENSE for details.

Citation
If using this project in research or academic work, please cite as:

Code snippet
@software{general_computer_agent_2026,
  title = {Reliability-First General Computer Agent: State-Grounded Tool Orchestration and Continuous Verification},
  author = {Software Developer},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub Repository}

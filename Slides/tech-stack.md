---
marp: true
theme: default
class: text-center
---

# 🛠️ QR Training Manager
### Tech Stack, AI Workflow & Methodology
**By Ye' Naung**

---

## 💻 1. Tech Stack
A full-stack QR-based event management system for HR:
- **Frontend:** PWA (Progressive Web App) UI
- **Backend:** Flask backend
- **Database:** Local SQLite (`attendance.db`) accessed via `mcp-server-sqlite`
- **Integrations:** Telegram bot (for QR delivery) and SMTP Email reporting

---

## 🧠 2. AI Workflow (Agent & Skill)
System built and guided using specialized Claude AI workflows:

- **Subagent (`.claude/agents/HR_Trainer.md`):** 
  Orchestrates isolated QR generation and CSV reporting dispatch.
  
- **Skill (`.claude/skills/attendance_manager/SKILL.md`):** 
  Defines rules to manage QR lists and strict event statuses.

---

## 🎯 3. Trigger & Commands
How the AI workflow is activated for this project:

- **Trigger:** 
  When setting up a new training event, generating QRs for attendees, or finalizing reports.
  
- **Command:**
  Run the following exactly in the terminal:
  `claude -p .claude/agents/HR_Trainer.md`

---

## 🏗️ 4. Methodology
**Get-Shit-Done (GSD) Project-Based Approach**
Iteratively built the system through the following phases:
1. PWA UI and Flask backend setup.
2. Telegram bot integration for QR generation.
3. Strict Event State Management to gate Check-ins.
4. Centralized dropdown UI for SMTP email reporting.
5. Rigorous security audit (protecting `.env` and `.gitignore` for database) and generating Marp presentation.

---

# Thank You!
**Any Questions?**
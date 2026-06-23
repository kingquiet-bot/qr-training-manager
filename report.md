# ch-3 Personal Project — Report

github_username: kingquiet-bot
personal_repo_url: https://github.com/kingquiet-bot/qr-training-manager
project_summary: A full-stack QR-based event management system for HR. It features a PWA frontend, a Python Flask/SQLite backend, strict Event State Management (Upcoming/Live/Closed), a centralized Email Reporting dashboard, and a Telegram Bot for automated self-service QR distribution.
slides_url: slides.md

## Methodology
I adopted a Get-Shit-Done (GSD) project-based approach. My git workflow consists of small, frequent commits pushed to a public GitHub repo. I iteratively built the system: starting with the PWA UI and Flask backend, integrating the Telegram bot for QR generation, advancing to strict Event State Management to gate Check-ins, and concluding with a centralized dropdown UI for SMTP email reporting.

## Evidence — Claude Code usage

### MCP
- path: .mcp.json
- what: Configured the `mcp-server-sqlite` to allow Claude Code to connect directly to our local `attendance.db` database for schema management, testing queries, and verifying event states.

### Skill
- path: .claude/skills/attendance_manager/SKILL.md
- what: Provides the contextual rules and database schema instructions for managing the `active_qr_list`, enforcing the `status` column logic ('upcoming', 'live', 'closed') in the events table, and handling SMTP credentials securely.

### Agent
- path: .claude/agents/HR_Trainer.md
- what: An agent instruction set that defines the core logic: isolating event-specific QR generation, ensuring only one event is 'live' at a time to prevent data mix-ups, gating the check-in endpoint, and managing the centralized dropdown workflow for automated final CSV report dispatch.
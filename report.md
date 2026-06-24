# ch-4 Personal Project — Report

github_username: kingquiet-bot
personal_repo_url: https://github.com/kingquiet-bot/qr-training-manager
live_url: https://github.com/kingquiet-bot/qr-training-manager/releases/tag/v1.0.0
project_summary: A full-stack QR-based event management system for HR. It features a PWA frontend, a Python Flask/SQLite backend, strict Event State Management (Upcoming/Live/Closed), a centralized Email Reporting dashboard, and a Telegram Bot for automated self-service QR distribution.
slides_url: presentation.md
license: MIT

## Methodology
I adopted a Get-Shit-Done (GSD) project-based approach. My git workflow consists of small, frequent commits pushed to a public GitHub repo. I iteratively built the system: starting with the PWA UI and Flask backend, integrating the Telegram bot for QR generation, advancing to strict Event State Management to gate Check-ins, and concluding with a centralized dropdown UI for SMTP email reporting. Finally, for this release, I performed a rigorous security audit (moving sensitive API keys into an `.env` file, adding a `.gitignore` to protect the database) and generated a Marp presentation.

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

## Screenshots
![Dashboard](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Dashboard.jpg)
![Setup Event](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Setup_Event.jpg)
![Event Detail](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Event_Detail.jpg)
![Import Attendance.png](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/import_attendance.png)
![Generate QR](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/Generate_QR.jpg)
![Telegram bot](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Telegram_bot.jpg)
![Scanner](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Scanner.jpg)
![Self-Check-In](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/self-check-in.jpg)
![Download Report](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Download_Report.jpg)
![Send_Report](https://raw.githubusercontent.com/kingquiet-bot/qr-training-manager/main/assets/Send_Report.jpg)
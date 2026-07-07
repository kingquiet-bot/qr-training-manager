---
marp: true
paginate: true
transition: fade
auto-advance: 20
---

<!-- slide 1 -->
# 📱 QR Training Manager
**A full-stack QR-based event management system for HR**

Setup an event → Deliver QRs via Telegram → Scan & auto-generate reports

---

<!-- slide 2 -->
# The Problem
HR and training coordinators waste valuable time because:
- Manual paper sign-in sheets are slow and outdated
- Requires tedious manual data entry after every session
- Missing records and unverified attendance are common for internal branch manager and staff trainings

---

<!-- slide 3 -->
# What I Built
A fully responsive web app designed for internal bank colleagues:
- **Telegram Bot** — delivers QR codes directly to staff phones instantly
- **Flask Backend & SQLite** — robust data handling and storage
- **PWA Frontend** — accessible via both Mobile and Browser Web View
- **SMTP Email Integration** — immediate attendance report delivery

---

<!-- slide 4 -->
# How I Built It
- **MCP**: `mcp-server-sqlite` — allows AI to connect directly to the local `attendance.db`
- **Skill**: `attendance_manager` — enforces strict event states (Live/Close) to gate check-ins
- **Agent**: `HR_Trainer` — orchestrates isolated QR generation and CSV reporting dispatch
- **Methodology**: Iterative GSD approach with AI-assisted debugging

---

<!-- slide 5 -->
# Why It Matters
- **Saves hours** — immediate attendance CSV reports the moment class ends
- **Frictionless** — direct self-check-in links and fast Telegram QRs
- **Reliable** — built-in scan delay time prevents duplicate records
- **User-friendly** — includes comprehensive End-User and Technical Installation Guides

---

<!-- slide 6 -->
# Done Checklist
- [x] PWA Frontend & Flask Backend deployed
- [x] Telegram bot integration for instant QR delivery
- [x] Strict Event State Management (Live/Close gating)
- [x] Scan delay timer to prevent duplicate check-ins
- [x] Desktop Browser Web View & Mobile UI adjustments
- [x] 6-slide Marp presentation
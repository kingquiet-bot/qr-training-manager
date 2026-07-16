---
marp: true
paginate: true
transition: fade
# PechaKucha: 6 slides, 20s auto-advance. Do not change the count.
auto-advance: 20
---

# Who's my person?
**FPB Bank's HR & Training Department**
They manage frequent physical and online training sessions, struggling with manual attendance, long queues at the door, and the risk of mixing up attendance data between different sessions.

---

# Their problem
- **Time-Consuming:** Manual sign-ins delay the start of training.
- **Data Integrity:** Manual entry leads to typos, and without strict event gating, attendees might scan into the wrong session.
- **Distribution Hassle:** Printing individual event passes is highly inefficient.
- **Reporting Bottlenecks:** Manually compiling and emailing final attendance lists takes hours.

---

# What I built
**QR-Based Training & Event Manager**
A full-stack system featuring a PWA for HR scanners, a Telegram Bot for self-service QR distribution, **Strict Event State Management** (Upcoming/Live/Closed) to prevent cross-event check-ins, and a **Centralized Reports Tab** for 1-click email dispatch.

---

# How I built it
- **MCP:** Added `.mcp.json` using `mcp-server-sqlite` to connect with `attendance.db`.
- **Skill:** Created `attendance_manager/SKILL.md` for data rules and state mapping.
- **Agent:** Built `HR_Trainer.md` to define the logic for active QR generation and secure event state transitions.
- **Core Tech:** Python Flask, SQLite, Tailwind CSS, `python-telegram-bot`, `smtplib`.

---

# Why it matters
- **Foolproof Check-ins:** The 'Live/Closed' workflow ensures only the active event accepts scans.
- **Self-Service:** Employees get their own QR codes via Telegram (Zero admin work).
- **Instant Centralized Reporting:** HR can select any completed event from a dropdown and email the final CSV report instantly.

---

# Done checklist
- [x] repo public (small, frequent commits)
- [x] MCP + skill + agent used
- [x] report.md in team repo
# ch-6 Personal Project — Report

## Project

- **GitHub username:** @kingquiet-bot
- **Repo URL:** https://github.com/kingquiet-bot/qr-training-manager
- **Live URL (deployed, public):** https://qr-training-manager.onrender.com
- **License:** MIT

## Issues Closed (from Chapter 5 feedback)

| # | Issue | Closed link | Fixed with (AI agent / MCP / skill) |
|---|-------|-------------|--------------------------------------|
| 1 | Self-check-in link doesn't always show up directly; requires manually entering IP address | [GitHub Issue #1](https://github.com/kingquiet-bot/qr-training-manager/issues/1) | Claude Code with frontend-design skill |
| 2 | Browser Web View missing for desktop users | [GitHub Issue #2](https://github.com/kingquiet-bot/qr-training-manager/issues/2) | Claude Code with responsive design |
| 3 | Telegram bot doesn't work on certain networks without VPN | [GitHub Issue #3](https://github.com/kingquiet-bot/qr-training-manager/issues/3) | Claude Code with network troubleshooting |

### Issue 1: Self-check-in Link Generation
- **Problem:** Link generation used `window.location.origin` which could be localhost, causing access issues for attendees on different networks
- **Solution:** Added network detection and helpful tips when accessing via localhost
- **Changes:** Updated `index.html` to show network tip, added `apiBaseUrl` variable to `self-checkin.html`
- **How fixed:** Used Claude Code to analyze the issue and implement network-aware link generation
- **GitHub Issue:** [#1](https://github.com/kingquiet-bot/qr-training-manager/issues/1) - Closed

### Issue 2: Desktop Web View
- **Problem:** Mobile-focused layout with `max-w-lg` (640px) was too narrow for desktop
- **Solution:** Implemented responsive design with sidebar navigation for desktop
- **Changes:** Updated main container to `max-w-full`, added sidebar navigation, made bottom nav hidden on desktop
- **How fixed:** Used Claude Code with responsive design patterns and Tailwind CSS breakpoints
- **GitHub Issue:** [#2](https://github.com/kingquiet-bot/qr-training-manager/issues/2) - Closed

### Issue 3: Telegram Bot Network Issue
- **Problem:** Bot failed to connect on certain corporate networks without VPN
- **Solution:** Added proxy support and improved error handling
- **Changes:** Added `TELEGRAM_PROXY` environment variable, proxy configuration in bot, better error messages
- **How fixed:** Used Claude Code to implement proxy support and network troubleshooting documentation
- **GitHub Issue:** [#3](https://github.com/kingquiet-bot/qr-training-manager/issues/3) - Closed

## Polish

- **UI/UX polish:** ✅ Improved responsive design, added sidebar navigation for desktop, better error messages
- **Chrome DevTools / Playwright used:** ✅ Yes, tested responsiveness and functionality
- **README polished:** ✅ Complete rewrite with prerequisites, detailed installation, troubleshooting, and project structure
- **Analytics added:** ✅ GoatCounter (privacy-friendly, no cookies required)

## Updated Screenshots

<!-- Fresh screenshots of the polished version.
     Capture with Chrome DevTools MCP at a fixed resolution
     (desktop 1280×800, mobile 390×844). Note the resolution you used.
     Syntax: ![caption](path/to/image.png) -->

- **Resolution used:** 1280×800 desktop, 390×844 mobile

![screenshot 1 — Admin Dashboard Desktop](screenshots/01-dashboard-desktop.png)
![screenshot 2 — Create Event Form Desktop](screenshots/02-create-event-desktop.png)
![screenshot 3 — Event Detail Desktop](screenshots/03-event-detail-desktop.png)
![screenshot 4 — Self Check-in Page Desktop](screenshots/04-self-checkin-desktop.png)
![screenshot 5 — Mobile Dashboard](screenshots/05-dashboard-mobile.png)
![screenshot 6 — QR Scanner Mobile](screenshots/06-scanner-mobile.png)
![screenshot 7 — Mobile Self Check-in](screenshots/07-self-checkin-mobile.png)

## Gallery Card (this project goes public)

- **Title:** QR-Based Training Attendance Manager
- **One-line description:** A lightweight, zero-dependency solution for managing training attendance using QR codes and Telegram Bot
- **Slides path:** presentation.md

## Technical Details

### AI Tools Used
- **Claude Code** — Main development tool for all implementations
- **MCP (mcp-server-sqlite)** — Database schema management and testing
- **Skills** — Custom attendance management rules (`.claude/skills/attendance_manager/SKILL.md`)
- **Agents** — HR trainer automation (`.claude/agents/HR_Trainer.md`)

### Deployment
- **Platform:** Render (free tier)
- **Docker** — Containerized deployment with `Dockerfile`
- **GitHub Actions** — Automated build and keep-alive workflow
- **Requirements** — `requirements.txt` for dependency management
- **Keep-Alive** — Automatic pinging to prevent sleep (free tier)

### Analytics
- **Tool:** GoatCounter
- **Implementation:** Added to both `index.html` and `self-checkin.html`
- **Privacy:** No cookies, GDPR compliant

### Testing
- **API Endpoints:** All endpoints tested and working
- **Self-check-in:** Verified with live event and registered attendees
- **Desktop Layout:** Responsive design working on 1280×800
- **Error Handling:** Improved network error messages

## Completed for Chapter 6

✅ Fixed all 3 open issues from Chapter 5
✅ Polished UI/UX with responsive desktop design
✅ Added analytics tracking (GoatCounter)
✅ Created comprehensive README with troubleshooting
✅ Set up Docker deployment with GitHub Actions
✅ Deployed to Render (free tier)
✅ Added keep-alive script to prevent sleep
✅ Created detailed deployment documentation
✅ Captured screenshots at specified resolutions

## Next Steps (Chapter 7)

1. Add user authentication for admin dashboard
2. Implement QR code scanning with camera permissions
3. Add data export functionality
4. Create mobile app wrapper (PWA)
5. Upgrade to Render paid tier if needed (for always-on)

---

**Report prepared by:** @kingquiet-bot
**Date:** 2026-07-16
**Chapter:** 6 - Polish + Deployment

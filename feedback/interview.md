# User Interview — QR Based Training Manager

- **Who:** Ma Thandar (Bank Colleague / Training Coordinator)
- **When:** 2026-07-04
- **How:** In person — ~15 min

## What they do today (without your project)

Currently, she uses manual paper sign-in sheets for branch manager and staff training sessions, which takes time, requires manual data entry later, and sometimes causes missing records.

## What they liked

- She appreciated the Telegram bot integration for getting QR codes quickly and easily.
- She liked that the **End-User Guide** was provided alongside the Technical Installation Guide, making it much easier for non-technical staff to understand (Completed).
- She was happy that the initial scanning issue was quickly addressed by adding a **"Scan Delay Time"** to prevent the scanner from rapidly capturing duplicate records (Completed).

## What confused them / what's missing

- During the initial test, the QR scanner was too fast and registered "Duplicate" records repeatedly (Now fixed).
- The self-check-in link doesn't always show up directly; it occasionally requires manually entering an IP address, adding an annoying extra step.
- When running `tele.py`, it doesn't work on certain local networks unless a VPN is turned on.
- The system is currently focused on Mobile View, but a proper Browser Web View is missing for managing events smoothly on a computer.

## What would make them actually use it

- A direct, click-and-go self-check-in link without needing any manual IP configurations.
- A fully responsive Browser Web View for desktop users to manage the dashboard.
- Clear instructions or a proxy workaround for the Telegram bot network/VPN issue.

## What I'll change (next steps)

- [x] Add a "Scan Delay Time" to prevent the scanner from registering duplicate entries too quickly.
- [x] Create and include an End-User Guide for non-technical users.
- [ ] Refactor the self-check-in link generation to automatically resolve the correct IP without manual entry.
- [ ] Develop a proper Browser Web View layout alongside the existing Mobile View.
- [ ] Investigate the `qr_bot.py` network issue and implement a proxy workaround or document the VPN requirement clearly.

# QR-Based Training Attendance Manager

A lightweight, zero-dependency, full-stack solution for managing training attendance using QR codes and a Telegram Bot. Perfect for HR departments, training coordinators, and event organizers who need a simple, efficient way to track attendance.

![Dashboard](assets/Dashboard.jpg)

## ✨ Features

- **📱 PWA Frontend** — Mobile-friendly dashboard and QR scanner that works offline
- **🤖 Telegram Bot Integration** — Auto-generates QR codes for registered attendees
- **💾 Offline-capable Database** — Uses SQLite for easy setup, no external database needed
- **📧 Email Reporting** — Sends attendance CSV reports directly via email
- **🔗 Self-Check-in** — Employees can check themselves in using a shared link
- **📊 Real-time Dashboard** — Live tracking of attendance with instant updates

## 📋 Prerequisites

- **Python 3.7+** — [Download Python](https://www.python.org/downloads/)
- **pip** — Python package manager (comes with Python)
- **Telegram Bot Token** — Get one from [@BotFather](https://t.me/BotFather) on Telegram
- **Gmail App Password** (optional) — For email reporting feature

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/kingquiet-bot/qr-training-manager.git
cd qr-training-manager
```

### 2. Install Dependencies

```bash
pip install python-telegram-bot qrcode[pil] Pillow python-dotenv flask
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# Required: TELEGRAM_BOT_TOKEN=your_token_here
# Optional: SMTP_EMAIL=your_email@gmail.com
# Optional: SMTP_PASSWORD=your_app_password
# Optional: TELEGRAM_PROXY=socks5://user:pass@proxy:1080
```

### 4. Start the Application

```bash
# Terminal 1: Start the web server
python3 app.py

# Terminal 2: Start the Telegram bot
python3 qr_bot.py
```

### 5. Access the Application

Open your browser and go to: **http://localhost:5000**

## 📖 Usage Guide

### For Attendees & Staff

1. **Get Your QR Code**
   - Open Telegram and search for the Training Bot
   - Send `/start` and follow the prompts
   - Receive your unique QR code

2. **Check-In**
   - Open the Check-in URL provided by admin
   - Tap "Scan QR" and scan your code from Telegram
   - See "Check-in Successful" confirmation

### For Admin / Trainers

1. **Setup Event**
   - Log into Admin Dashboard
   - Click "Create New Event"
   - Enter training name, date, and time

2. **Import Attendees**
   - Prepare Excel/CSV with attendee list
   - Go to Import Attendance section
   - Upload your file

3. **Manage Check-ins**
   - Change event status to "Live" to open check-ins
   - Change to "Closed" when training ends
   - Only one event can be "Live" at a time

4. **Send Reports**
   - Navigate to Email Reporting
   - Select completed event
   - Click Send to email CSV report

## 🔧 Troubleshooting

### Telegram Bot Network Issues

If the bot fails to connect or only works with VPN:

1. **Check your network** — Some corporate networks block Telegram API
2. **Use a proxy** — Add to your `.env` file:
   ```
   TELEGRAM_PROXY=socks5://user:password@proxy.example.com:1080
   ```
3. **VPN workaround** — Connect to VPN before starting the bot
4. **Firewall rules** — Ensure outbound connections to `api.telegram.org:443` are allowed

### Self-Check-in Link Issues

If attendees can't access the self-check-in link:

1. **Use your computer's IP** — Instead of `http://localhost:5000`, use `http://192.168.x.x:5000`
   - Find your IP: Windows (`ipconfig`), Mac/Linux (`ifconfig`)
2. **Same network** — Ensure admin and attendees are on the same WiFi/network
3. **Firewall** — Check that port 5000 is not blocked

### Common Errors

| Error | Solution |
|-------|----------|
| `TELEGRAM_BOT_TOKEN not set` | Add token to `.env` file |
| `python-telegram-bot not installed` | Run `pip install python-telegram-bot` |
| `Could not connect to backend` | Ensure `python3 app.py` is running |
| `Event has not started yet` | Change event status to "Live" |

## 📁 Project Structure

```
qr-training-manager/
├── app.py              # Flask web server & API
├── qr_bot.py           # Telegram bot for QR generation
├── index.html          # Admin dashboard (PWA)
├── self-checkin.html   # Employee self-check-in page
├── assets/             # Screenshots and images
├── feedback/           # User feedback and interviews
├── .claude/            # Claude Code skills and agents
│   ├── skills/         # Custom skills
│   └── agents/         # Custom agents
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🤖 AI Tools Used

This project was built using Claude Code with:

- **Skills** — Custom attendance management rules
- **Agents** — HR trainer automation
- **MCP** — SQLite database integration
- **GSD Methodology** — Get-Shit-Done approach

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Built with ❤️ using Claude Code
- QR code generation: [qrcode](https://pypi.org/project/qrcode/)
- Telegram integration: [python-telegram-bot](https://python-telegram-bot.org/)
- Frontend: Tailwind CSS, HTML5 QR Scanner

---

**Need help?** Open an issue or contact the developer.

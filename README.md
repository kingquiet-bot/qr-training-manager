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
- **🔐 Google Sign-in** — One-click sign in with your Google account (optional)

## 📋 Prerequisites

- **Python 3.7+** — [Download Python](https://www.python.org/downloads/)
- **pip** — Python package manager (comes with Python)
- **Telegram Bot Token** — Get one from [@BotFather](https://t.me/BotFather) on Telegram
- **Gmail App Password** (optional) — For email reporting feature
- **Google Cloud OAuth Client ID** (optional) — For Google sign-in feature

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
# Optional: GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
# Optional: TELEGRAM_PROXY=socks5://user:pass@proxy:1080
```

## 🌐 Deploy to Render (Free)

### Quick Deploy:

1. **Click the button below:**
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

2. **Or follow manual steps:**
   - Go to https://render.com
   - Sign up with GitHub
   - Create new "Web Service"
   - Connect repository: `kingquiet-bot/qr-training-manager`
   - Select "Docker" runtime
   - Add environment variables
   - Deploy!

### Detailed Guide:

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step instructions.

### Your Live URL (after deployment):

```
https://qr-training-manager.onrender.com
```

### Keep-Alive (Prevent Sleep):

Render free tier sleeps after 15 min of inactivity. Use the keep-alive script:

```bash
# Run locally (keeps app awake)
python3 keep_alive.py

# Or use GitHub Actions (automatic)
# See keep-alive.yml workflow
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

## 🔐 Google Sign-in Setup (Optional)

Add one-click Google sign-in so users can skip email/password registration.

### Step 1: Create Google Cloud Project

1. Go to **https://console.cloud.google.com**
2. Click the project dropdown → **New Project**
3. Name it `QR Training Manager` → Click **Create**
4. Select the new project from the dropdown

### Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → Click **Create**
3. Fill in:
   - **App name:** `QR Training Manager`
   - **User support email:** your email
   - **Developer contact:** your email
4. Click **Save and Continue**
5. **Scopes:** Click **Add or Remove Scopes** → select `email` and `profile` → **Update** → **Save and Continue**
6. **Test users:** Add any Google accounts that need access during testing → **Save**

### Step 3: Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. **Application type:** `Web application`
4. **Name:** `QR Training Manager Web Client`
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:5000
   https://qr-training-manager.onrender.com
   ```
6. Click **Create**
7. **Copy the Client ID**

### Step 4: Add to Environment Variables

```bash
# In your .env file
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
```

For **Render**: Go to Environment tab → Add `GOOGLE_CLIENT_ID`

### Step 5: Test

1. Restart the server: `python3 app.py`
2. Open `http://localhost:5000`
3. You'll see **"Sign in with Google"** on the login page
4. Click it → select your Google account → you're in

> **Note:** While unverified, only test users (added in Step 2.6) can sign in. For internal use, no Google verification needed.

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
├── app.py              # Python HTTP server & API (stdlib, no Flask)
├── qr_bot.py           # Telegram bot for QR generation
├── crypto_utils.py     # Encryption for stored credentials
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

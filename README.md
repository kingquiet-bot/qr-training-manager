# QR-Based Training Attendance Manager

A lightweight, zero-dependency, full-stack solution for managing training attendance using QR codes and a Telegram Bot. 

## Features
* **PWA Frontend:** Mobile-friendly dashboard and QR scanner.
* **Telegram Bot Integration:** Auto-generates QR codes for registered attendees.
* **Offline-capable Database:** Uses SQLite for easy setup.
* **Email Reporting:** Sends attendance CSV reports directly via email.

## How to Run Locally
1. Clone this repository.
2. Ensure you have Python 3 installed.
3. Install dependencies for the bot: `pip install python-telegram-bot qrcode[pil] Pillow python-dotenv`
4. Run the Web Server: `python3 app.py`
5. Run the Telegram Bot: `python3 qr_bot.py`
6. Open your browser and go to `http://localhost:5000`
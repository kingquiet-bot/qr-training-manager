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
4. Rename `.env.example` to `.env`.
5. Open the `.env` file and replace the placeholder values with your actual Telegram Bot Token and Gmail App Password.
6. When you run `python3 app.py` for the first time, a fresh `attendance.db` will be created automatically.
7. Run the Web Server: `python3 app.py`
8. Run the Telegram Bot: `python3 qr_bot.py`
9. Open your browser and go to `http://localhost:5000`

## Screenshots
![Dashboard](assets/Dashboard.jpg)
![Setup Event](assets/Setup_Event.jpg)
![Event Detail](assets/Event_Detail.jpg)
![Import Attendance.png](assets/import_attendance.png)
![Generate QR](Generate_QR.jpg)
![Telegram bot](assets/Telegram_bot.jpg)
![Scanner](assets/Scanner.jpg)
![Self-Check-In](assets/self-check-in.jpg)
![Download Report](assets/Download_Report.jpg)
![Send_Report](assets/Send_Report.jpg)
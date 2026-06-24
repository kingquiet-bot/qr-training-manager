---
marp: true
paginate: true
size: 16:9
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Myanmar:wght@400;600;700&family=Inter:wght@400;600;800&display=swap');
:root { --bg:#fffdf9; --ink:#292524; --muted:#a8a29e; --accent:#d97706; --burnt:#9a3412; --line:#f1d9bf; --code:#1c1917; }
section {
  background:var(--bg); color:var(--ink);
  font-family:'Pyidaungsu','Noto Sans Myanmar','Inter',sans-serif;
  font-size:27px; line-height:1.7; padding:56px 72px;
}
h1 { color:var(--burnt); font-weight:700; border-bottom:4px solid var(--accent); padding-bottom:.2em; line-height:1.4; }
h2 { color:var(--accent); font-weight:600; line-height:1.5; }
h3 { color:var(--burnt); font-weight:600; }
strong { color:var(--burnt); }
a { color:#0369a1; text-decoration:none; }
ul,ol { line-height:1.7; }
code { background:#fff1e6; color:#be123c; padding:.06em .35em; border-radius:5px; font-family:'JetBrains Mono',ui-monospace,monospace; }
pre  { background:var(--code); border-radius:10px; }
pre code { background:none; color:#fde9d3; }
blockquote { border-left:4px solid var(--accent); background:#fffbeb; color:#57534e; padding:.5em 1em; }
table th { background:#fff1e6; color:var(--burnt); }
table td, table th { border-color:var(--line); }
header,footer,section::after { color:var(--muted); font-size:.5em; }
section.cover {
  background:linear-gradient(135deg,#7c2d12 0%, #b45309 50%, #d97706 100%);
  color:#fff7ed;
}
section.cover h1 { border-bottom:none; color:#fff7ed; font-size:2.1em; }
section.cover h2 { color:#ffedd5; font-weight:400; }
section.lead { background:linear-gradient(135deg,#fff7ed,#ffedd5); }
section.lead h1 { border-bottom:none; }
</style>

# QR-Based Training Manager

## Telegram Bot နှင့် ချိတ်ဆက်ထားသော QR အခြေခံ သင်တန်းတက်ရောက်မှု မှတ်တမ်းစနစ်

**Ye Naung** · vibecode.tours

---

# ဒါ ဘာလဲ

- **ဖြေရှင်းပေးတဲ့ ပြဿနာ:** သင်တန်းများတွင် လူကိုယ်တိုင် စာရင်းမှတ်ရသည့် အချိန်ကုန်လူပင်ပန်းသော ပြဿနာကို အလိုအလျောက်စနစ်ဖြင့် အစားထိုးဖြေရှင်းပေးသည်။
- **ဘယ်သူ့အတွက်လဲ:** ဘဏ်နှင့် ရုံးလုပ်ငန်းများမှ HR ဝန်ထမ်းများ၊ သင်တန်းပို့ချသူများ။
- **အကောင်းဆုံး လုပ်ပေးနိုင်တဲ့ အရာ:** ဝန်ထမ်းစာရင်းသွင်းလိုက်သည်နှင့် Telegram မှတစ်ဆင့် QR Code အလိုအလျောက် ထုတ်ပေးပြီး၊ ဖုန်းဖြင့် ဖတ်လိုက်ရုံဖြင့် Check-in ဝင်နိုင်သည်။

---

# ဘယ်လို အလုပ်လုပ်လဲ

```bash
# Web Server အား စတင်ရန်
python3 app.py

# Telegram Bot အား စတင်ရန်
python3 qr_bot.py

---

# Demo

Demo - Admin Dashboard,Scanner & Check-in
![w:860](assets/Dashboard.jpg)
![w:860](assets/Setup_Event.jpg)
![w:860](assets/import_attendance.png)
![w:860](Generate_QR.jpg)
![w:860](assets/Telegram_bot.jpg)
![w:860](assets/Scanner.jpg)
![w:860](assets/self-check-in.jpg)
![w:860](assets/Send_Report.jpg)

---

# Link များ

- **Live:** https://github.com/kingquiet-bot/qr-training-manager/releases/tag/v1.0.0
- **Repo:** https://github.com/kingquiet-bot/qr-training-manager
- **License:** MIT
---
marp: true
paginate: true
size: 16:9
theme: default
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

section {
  font-family: 'Inter', 'Pyidaungsu', sans-serif;
  background: #f8fafc;
  color: #1e293b;
  padding: 50px 60px;
}

h1 {
  color: #4f46e5;
  font-weight: 800;
  font-size: 2.2em;
  border-bottom: 3px solid #4f46e5;
  padding-bottom: 0.2em;
}

h2 {
  color: #4f46e5;
  font-weight: 700;
}

strong { color: #4f46e5; }

.cover {
  background: linear-gradient(135deg, #1e1b4b 0%, #4f46e5 100%);
  color: white;
}
.cover h1 { color: white; border-bottom: none; font-size: 2.8em; }
.cover h2 { color: #c7d2fe; font-weight: 400; font-size: 1.3em; }

.lead {
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
}
.lead h1 { border-bottom: none; }

table { font-size: 0.85em; }
table th { background: #eef2ff; color: #4338ca; }
ul { line-height: 1.8; }
img { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>

<!-- slide 1: Cover -->
![bg right:45%](assets/Dashboard.jpg)

# QR Training Manager

**Telegram Bot + QR Code အခြေပြု သင်တန်းတက်ရောက်မှု စီမံခန့်ခွဲရေးစနစ်**

- HR နှင့် Training Coordinator များအတွက်
- အလိုအလျောက် QR ထုတ်ပေးခြင်း၊ Check-in နှင့် Report ပို့ခြင်း

---

<!-- slide 2: Problem -->
![bg left:40%](assets/Setup_Event.jpg)

# 🚩 ပြဿနာ

**လက်ရှိကိုင်တွယ်နေရတဲ့အခက်အခဲများ**

- 📄 **စာရွက်စနစ်** — ခေတ်နောက်ကျနေပြီ၊ သင်တန်းပြီးတိုင်း ဒေတာပြန်ရိုက်ရ
- ❌ **မှားယွင်းမှုများ** — တက်ရောက်သူစာရင်းတွေ ပျောက်ဆုံး/မှားယွင်းတတ်
- ⏱️ **အချိန်ကုန်** — Management ကို အချိန်နဲ့တစ်ပြေးညီ အစီရင်ခံမပေးနိုင်
- 📊 **ဒေတာမရှိခြင်း** — ဌာနအလိုက် တက်ရောက်မှုနှုန်း ခွဲခြမ်းစိတ်ဖြာမရ

---

<!-- slide 3: Solution -->
![bg right:40%](assets/Telegram_bot.jpg)

# 💡 အဖြေရှာချက်

**QR Training Manager ၏ အဓိက အင်္ဂါရပ်များ**

- 🤖 **Telegram Bot** — QR Code များ အလိုအလျောက်ထုတ်ပေး
- 📱 **PWA Frontend** — Mobile & Browser နှစ်မျိုးလုံးသုံးရ
- 🔗 **Self-Check-In** — Link တစ်ခုတည်းနဲ့ အားလုံးဝင်နိုင်
- 📧 **Email Report** — သင်တန်းပြီးတာနဲ့ CSV Report ပို့

---

<!-- slide 4: How It Works -->
![bg left:40%](assets/import_attendance.png)

# ⚙️ အလုပ်လုပ်ပုံ

**ရိုးရှင်းသော အဆင့် ၅ ဆင့်**

| အဆင့် | လုပ်ဆောင်ချက် | အသေးစိတ် |
|:---:|:---|---|
| **၁** | Event ဖန်တီး | သင်တန်းအမည်၊ ရက်၊ အချိန်သတ်မှတ် |
| **၂** | Register လုပ် | CSV/Excel မှ Attendees တင်သွင်း |
| **၃** | Live ပြောင်း | QR ထုတ်ပြီး Check-in စတင် |
| **၄** | Check-in | QR Scan / Self-Check-In |
| **၅** | Report | Event ပိတ်တာနဲ့ အလိုအလျောက် Report ထုတ် |

---

<!-- slide 5: Features -->
![bg right:40%](assets/Scanner.jpg)

# 🎯 အဓိကအင်္ဂါရပ်များ

**တစ်နေရာတည်းမှ အကုန်စီမံနိုင်**

| အင်္ဂါရပ် | အကျိုးကျေးဇူး |
|:---|---|
| 🟢 **Event Status** | Upcoming → Live → Closed အလိုအလျောက်ထိန်း |
| 🚫 **Duplicate Protection** | တစ်ယောက်တစ်ခါပဲ Check-in ရ |
| 📊 **Dashboard** | Real-time Attendance စောင့်ကြည့်နိုင် |
| 📱 **QR Scanner** | Camera ကနေ QR တန်းဖတ် |
| 📧 **Email Report** | CSV Report ကို Management ဆီပို့ |

---

# 🙏 ကျေးဇူးတင်ပါတယ်

**မေးခွန်းများ ရှိပါက မေးမြန်းနိုင်ပါတယ်**

---

🌐 **Live URL:** https://qr-training-manager.onrender.com  
📂 **Repo:** https://github.com/kingquiet-bot/qr-training-manager  

Developed with ❤️ using Python, Telegram Bot & PWA  
*Claude Code — AI-Assisted Development*

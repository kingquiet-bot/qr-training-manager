# Render Deployment Guide

This guide will help you deploy the QR Training Manager to Render (free tier).

## 📋 Prerequisites

Before you begin, make sure you have:

- ✅ GitHub account with your repository pushed
- ✅ Telegram Bot Token (from @BotFather)
- ✅ Gmail App Password (optional, for email reports)
- ✅ Render account (free, no credit card required)

## 🚀 Step-by-Step Deployment

### Step 1: Create Render Account

1. **Go to Render:**
   - Open: https://render.com
   - Click "Get Started for Free"

2. **Sign up with GitHub:**
   - Click "GitHub"
   - Authorize Render to access your repositories
   - No credit card required!

3. **Verify your email:**
   - Check your email for verification link
   - Click the link to verify

### Step 2: Create New Web Service

1. **Dashboard:**
   - After login, you'll see the Render Dashboard
   - Click "New" (top right)

2. **Select Service Type:**
   - Choose "Web Service"

3. **Connect GitHub Repository:**
   - Click "Build and deploy from a Git repository"
   - Click "Next"

4. **Select Repository:**
   - Find and select: `kingquiet-bot/qr-training-manager`
   - Click "Connect"

### Step 3: Configure Service Settings

Fill in the following settings:

#### Basic Settings:
- **Name:** `qr-training-manager`
- **Region:** `Oregon (US West)` (or closest to your location)
- **Branch:** `main`
- **Runtime:** `Docker`

#### Docker Settings:
- **Dockerfile Path:** `./Dockerfile`
- **Docker Context:** `.` (leave as default)

#### Instance Type:
- **Free** (512 MB RAM, 0.5 CPU)

### Step 4: Add Environment Variables

Click "Advanced" → "Add Environment Variable" for each:

#### Required Variables:

```
Key: TELEGRAM_BOT_TOKEN
Value: your_telegram_bot_token_here
```

```
Key: PYTHON_VERSION
Value: 3.11.0
```

#### Optional Variables (for email reports):

```
Key: SMTP_EMAIL
Value: your_email@gmail.com
```

```
Key: SMTP_PASSWORD
Value: your_gmail_app_password
```

#### Optional Variables (if behind firewall):

```
Key: TELEGRAM_PROXY
Value: socks5://user:password@proxy:1080
```

### Step 5: Configure Build Settings

#### Build Command:
- Leave empty (Docker handles this)

#### Start Command:
- Leave empty (Dockerfile CMD handles this)

#### Health Check Path:
- `/` (root path)

### Step 6: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment:**
   - Build time: 2-5 minutes
   - You'll see build logs in real-time

3. **Monitor the build:**
   - Watch for "Build successful"
   - Watch for "Deploy live"

4. **Get your URL:**
   - Once deployed, you'll see: `https://qr-training-manager.onrender.com`
   - Click the URL to test your app!

## ✅ Post-Deployment Checklist

### Test Your Application:

1. **Open your Render URL:**
   - `https://qr-training-manager.onrender.com`

2. **Test the dashboard:**
   - Should see the Training Attendance Manager
   - Create a test event

3. **Test self-check-in:**
   - Create an event
   - Change status to "Live"
   - Open self-check-in link
   - Test check-in flow

4. **Test Telegram bot:**
   - Make sure bot token is correct
   - Test QR code generation

### Verify Environment Variables:

1. **Go to Render Dashboard**
2. **Select your service**
3. **Click "Environment" tab**
4. **Verify all variables are set correctly**

## 🔧 Troubleshooting

### Issue 1: Build Fails

**Symptoms:**
- Build logs show errors
- "Failed to build" message

**Solutions:**
1. **Check Dockerfile:**
   ```bash
   # Test locally first
   docker build -t qr-training-manager .
   docker run -p 5000:5000 qr-training-manager
   ```

2. **Check build logs:**
   - Click on the failed build
   - Read the error message
   - Fix the issue in your code

3. **Common fixes:**
   - Ensure all files are committed
   - Check `requirements.txt` is correct
   - Verify `Dockerfile` syntax

### Issue 2: App Won't Start

**Symptoms:**
- Build succeeds but app crashes
- "Application failed to respond" error

**Solutions:**
1. **Check start command:**
   - Render uses `Dockerfile` CMD
   - Ensure `app.py` runs on port 5000

2. **Check environment variables:**
   - `TELEGRAM_BOT_TOKEN` must be set
   - Check for typos

3. **Check logs:**
   - Go to "Logs" tab in Render
   - Look for error messages

### Issue 3: App Sleeps (Free Tier)

**Symptoms:**
- First request takes 30+ seconds
- Subsequent requests are fast

**This is normal!** Render free tier sleeps after 15 min of inactivity.

**Solutions:**

#### Option A: Keep-Alive Cron Job (Recommended)
Add a cron job to ping your app every 10 minutes:

```bash
# Add to your project
# Create keep_alive.py
```

I'll create this for you below.

#### Option B: Upgrade to Paid Tier
- $7/month for always-on
- No sleep

### Issue 4: Environment Variables Not Working

**Symptoms:**
- Telegram bot can't connect
- Email reports not sending

**Solutions:**
1. **Check variable names:**
   - Must be exact: `TELEGRAM_BOT_TOKEN` (case-sensitive)

2. **Check variable values:**
   - No extra spaces
   - No quotes around values

3. **Redeploy:**
   - After changing variables, click "Manual Deploy" → "Clear build cache & deploy"

## 🔄 Updating Your Application

### Automatic Deploys (Recommended):

1. **Enable auto-deploy:**
   - Go to your service settings
   - Under "Build & Deploy"
   - Enable "Auto Deploy" from `main` branch

2. **Push changes:**
   ```bash
   git add .
   git commit -m "Update"
   git push origin main
   ```

3. **Render auto-deploys:**
   - Render detects the push
   - Automatically rebuilds and redeploys
   - Takes 2-5 minutes

### Manual Deploy:

1. **Go to Render Dashboard**
2. **Select your service**
3. **Click "Manual Deploy"**
4. **Select "Clear build cache & deploy"**

## 📊 Monitoring Your Application

### View Logs:

1. **Go to your service**
2. **Click "Logs" tab**
3. **See real-time logs:**
   - Build logs
   - Runtime logs
   - Error messages

### View Metrics:

1. **Go to your service**
2. **Click "Metrics" tab**
3. **See:**
   - CPU usage
   - Memory usage
   - Request count

## 🌐 Custom Domain (Optional)

### Add Custom Domain:

1. **Go to service settings**
2. **Click "Settings" tab**
3. **Scroll to "Custom Domains"**
4. **Click "Add Custom Domain"**
5. **Enter your domain:** `yourdomain.com`

### Configure DNS:

1. **Go to your DNS provider**
2. **Add CNAME record:**
   ```
   Name: @ (or www)
   Value: qr-training-manager.onrender.com
   TTL: 3600
   ```

3. **Wait for DNS propagation:**
   - Takes 24-48 hours
   - Render auto-SSL once verified

## 💰 Cost Estimate

### Free Tier (Recommended):

| Resource | Limit | Your Usage |
|----------|-------|------------|
| **RAM** | 512 MB | ~100-200 MB |
| **CPU** | 0.5 | ~0.1-0.2 |
| **Bandwidth** | Unlimited | Low |
| **Sleep** | After 15 min | Normal |
| **Cost** | **$0** | **$0** |

### Paid Tier (If Needed):

| Tier | RAM | CPU | Cost |
|------|-----|-----|------|
| **Starter** | 512 MB | 0.5 | $7/month |
| **Standard** | 1 GB | 1 | $25/month |

**For your project:** Free tier is perfect!

## 🎯 Quick Reference

### Your Render URL:
```
https://qr-training-manager.onrender.com
```

### Key Files:
- `Dockerfile` - Docker configuration
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template

### Environment Variables:
```
TELEGRAM_BOT_TOKEN=your_token
SMTP_EMAIL=your_email (optional)
SMTP_PASSWORD=your_password (optional)
```

### Useful Commands:

```bash
# Test locally
docker build -t qr-training-manager .
docker run -p 5000:5000 qr-training-manager

# Deploy to Render
git push origin main

# Check Render logs
gh api repos/kingquiet-bot/qr-training-manager/actions/runs
```

## 🆘 Getting Help

### Render Documentation:
- https://render.com/docs

### Render Community:
- https://community.render.com

### Common Issues:
- Check build logs first
- Verify environment variables
- Test Docker locally before deploying

## ✅ Deployment Checklist

Before going live, ensure:

- [ ] GitHub repository is up to date
- [ ] `Dockerfile` works locally
- [ ] Environment variables are set in Render
- [ ] App loads at Render URL
- [ ] Telegram bot connects
- [ ] Self-check-in works
- [ ] Dashboard is responsive
- [ ] No errors in logs

## 🎉 You're Live!

Once deployed, your app will be available at:

```
https://qr-training-manager.onrender.com
```

### Share Your App:

1. **Add to README:**
   ```markdown
   ## Live Demo
   [QR Training Manager](https://qr-training-manager.onrender.com)
   ```

2. **Submit to Chapter 6:**
   - Use the Render URL as your live URL
   - Update `ch-6-report.md` with the URL

3. **Share with others:**
   - Send the URL to test users
   - Collect feedback

---

**Congratulations! Your QR Training Manager is now live!** 🚀

Need help? Check the troubleshooting section or ask in your team channel.

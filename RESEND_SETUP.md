# Setting Up Resend API for Email Delivery

This guide provides step-by-step instructions to configure the **Resend API** for secure, HTTPS-based OTP (One-Time Password) and report email delivery. 

> [!IMPORTANT]
> Render's free tier blocks outbound SMTP ports (587, 465, 25). If you are deploying the Training Attendance Manager on Render, you **must** use the Resend API (Option A) rather than standard SMTP (Option B) for email operations.

---

## Step 1: Create a Resend Account
1. Go to [Resend.com](https://resend.com) and click **Sign Up**.
2. Create your account and complete the registration.

---

## Step 2: Add and Verify Your Domain
Resend requires you to verify your custom domain to send emails to your users. 
1. In the Resend Dashboard, go to **Domains** from the left-hand sidebar.
2. Click **Add Domain**.
3. Enter your domain name (e.g., `yourcompany.com`) and choose your region.
4. Resend will generate a set of DNS records (DKIM, SPF, and MX/TXT records).
5. Go to your DNS provider (e.g., GoDaddy, Cloudflare, Namecheap) and add these records to your domain's DNS settings.
6. Once added, click **Verify** in the Resend dashboard. It may take a few minutes for the DNS changes to propagate.

> [!NOTE]
> Until your domain is verified, you can only send emails to the email address you signed up with (using Resend's default `onboarding@resend.dev` sender address).

---

## Step 3: Generate an API Key
1. Go to the Resend Dashboard and select **API Keys** from the sidebar.
2. Click **Create API Key**.
3. Give it a name (e.g., `Attendance Manager Production`).
4. Set the role to **Sending Access** (or Full Access).
5. Click **Add** and **copy** the generated API Key immediately. It will look like `re_123456789...`.

---

## Step 4: Configure the Application
You can configure Resend in one of two ways:

### Option A: Via the Web Dashboard (Recommended)
If your application is already running:
1. Log in to the application as a Platform Administrator (e.g., `superadmin@local` or your custom admin account).
2. Navigate to the **Settings** tab (the gear icon on the navbar).
3. Under the **Administration** section, click **Open Platform Admin**.
4. Scroll to **Platform Email Delivery**.
5. Under **Option A: Resend API (HTTPS)**:
   - Paste your **Resend API Key** (e.g., `re_xxxxxxxxx`).
   - Enter your **Sender Email** (e.g., `Training Manager <noreply@yourdomain.com>`).
     > [!WARNING]
     > The domain in the sender email **must** match the custom domain you verified in Step 2.
6. Click **Save Email Settings**.

### Option B: Via Environment Variables
You can pre-configure the credentials in your server environment (useful for Docker or Render deployment setup):
1. Open your `.env` file (local development) or go to the **Environment** tab in your Render dashboard (production).
2. Set the following environment variables:
   ```env
   RESEND_API_KEY=re_your_api_key_here
   OTP_FROM_EMAIL="Training Manager <noreply@yourdomain.com>"
   ```
3. Restart/redeploy your application.

---

## Troubleshooting

### Issue 1: Emails only arrive to the administrator's signup email
- **Cause**: You have not verified your custom domain in Resend (Step 2), so you are in sandbox mode.
- **Solution**: Complete domain verification in the Resend Dashboard under the **Domains** tab.

### Issue 2: Logs show `HTTP 401 Unauthorized`
- **Cause**: The API key is invalid or not copied completely.
- **Solution**: Generate a new API key in the Resend Dashboard and re-enter it.

### Issue 3: Logs show `OTP_FROM_EMAIL is required`
- **Cause**: You set the `RESEND_API_KEY` but did not provide a sender email address.
- **Solution**: Set both `RESEND_API_KEY` and `OTP_FROM_EMAIL` (or fill in both fields in the Platform Admin panel).

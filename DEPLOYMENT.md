# Deployment Guide

This guide explains how to deploy the QR Training Manager application.

## Option 1: Local Deployment (Recommended for Testing)

### Prerequisites
- Python 3.7+
- pip

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kingquiet-bot/qr-training-manager.git
   cd qr-training-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the application:**
   ```bash
   # Terminal 1: Web server
   python3 app.py

   # Terminal 2: Telegram bot
   python3 qr_bot.py
   ```

5. **Access the application:**
   - Open: http://localhost:5000

## Option 2: Docker Deployment

### Prerequisites
- Docker installed

### Steps

1. **Build the Docker image:**
   ```bash
   docker build -t qr-training-manager .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name qr-training \
     -p 5000:5000 \
     -e TELEGRAM_BOT_TOKEN=your_token_here \
     qr-training-manager
   ```

3. **Access the application:**
   - Open: http://localhost:5000

## Option 3: Docker Hub Deployment

### Prerequisites
- Docker installed
- Docker Hub account

### Steps

1. **Build and tag the image:**
   ```bash
   docker build -t yourusername/qr-training-manager:latest .
   ```

2. **Login to Docker Hub:**
   ```bash
   docker login
   ```

3. **Push to Docker Hub:**
   ```bash
   docker push yourusername/qr-training-manager:latest
   ```

4. **Run from Docker Hub:**
   ```bash
   docker run -d \
     --name qr-training \
     -p 5000:5000 \
     -e TELEGRAM_BOT_TOKEN=your_token_here \
     yourusername/qr-training-manager:latest
   ```

## Option 4: Cloud Deployment

### Railway (Easiest)
1. Go to https://railway.app
2. Connect your GitHub repository
3. Railway will automatically detect the Dockerfile
4. Add environment variables in the dashboard
5. Deploy!

### Render
1. Go to https://render.com
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Select "Docker" as the runtime
5. Add environment variables
6. Deploy!

### Fly.io
1. Go to https://fly.io
2. Install the Fly CLI
3. Run `fly launch` in your project directory
4. Follow the prompts
5. Deploy with `fly deploy`

### Heroku
1. Go to https://heroku.com
2. Create a new app
3. Connect your GitHub repository
4. Add a `heroku.yml` file:
   ```yaml
   build:
     docker:
       web: Dockerfile
   run:
     web: python3 app.py
   ```
5. Deploy

## Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token

Optional:
- `SMTP_EMAIL` - Gmail address for email reports
- `SMTP_PASSWORD` - Gmail app password
- `TELEGRAM_PROXY` - Proxy for Telegram bot (if behind firewall)

## Troubleshooting

### Docker Build Fails
- Ensure Docker is running
- Check if port 5000 is available
- Verify all files are present

### Application Won't Start
- Check environment variables are set correctly
- Ensure all dependencies are installed
- Verify port 5000 is not in use

### Telegram Bot Connection Issues
- Verify bot token is correct
- Check network connectivity
- Use proxy if behind firewall

## GitHub Actions Workflow

### Option A: Build Only (Current)
- Workflow: `deploy.yml`
- Builds Docker image to verify it works
- Does not push to any registry

### Option B: Push to Docker Hub
- Workflow: `deploy-dockerhub.yml`
- Requires Docker Hub credentials in GitHub Secrets
- Automatically pushes to Docker Hub

### Setting up Docker Hub Secrets
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add:
   - `DOCKERHUB_USERNAME` - Your Docker Hub username
   - `DOCKERHUB_TOKEN` - Your Docker Hub access token

## Quick Start Commands

```bash
# Local development
pip install -r requirements.txt
cp .env.example .env
python3 app.py

# Docker
docker build -t qr-training-manager .
docker run -d -p 5000:5000 -e TELEGRAM_BOT_TOKEN=your_token qr-training-manager

# Docker Hub
docker tag qr-training-manager:latest yourusername/qr-training-manager:latest
docker push yourusername/qr-training-manager:latest
```

## Need Help?

If you encounter issues:
1. Check the logs: `docker logs qr-training`
2. Verify environment variables
3. Ensure all ports are accessible
4. Check network connectivity

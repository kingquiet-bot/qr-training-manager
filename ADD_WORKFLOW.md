# How to Add GitHub Actions Workflow

Since the OAuth token doesn't have the `workflow` scope, you need to manually add the GitHub Actions workflow file to your repository.

## Steps:

### Option 1: Via GitHub Web Interface (Recommended)

1. **Go to your repository:** https://github.com/kingquiet-bot/qr-training-manager

2. **Create the workflow directory:**
   - Click on "Add file" → "Create new file"
   - In the file name field, type: `.github/workflows/deploy.yml`
   - This will automatically create the directory structure

3. **Copy the workflow content:**
   - Open the file `deploy.yml` in this repository (or copy from below)
   - Paste the content into the new file

4. **Commit the file:**
   - Add a commit message: "Add GitHub Actions workflow for Docker deployment"
   - Click "Commit changes"

### Option 2: Via Git Command Line

1. **Create the directory structure:**
   ```bash
   mkdir -p .github/workflows
   ```

2. **Copy the workflow file:**
   ```bash
   cp deploy.yml .github/workflows/deploy.yml
   ```

3. **Commit and push:**
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Add GitHub Actions workflow for Docker deployment"
   git push origin main
   ```

## Workflow File Content:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to GitHub Container Registry
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=ref,event=branch
          type=sha

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

## What This Workflow Does:

1. **Triggers on:**
   - Push to `main` branch
   - Pull requests to `main` branch

2. **Builds:**
   - Docker image from your `Dockerfile`
   - Uses GitHub Actions cache for faster builds

3. **Pushes to:**
   - GitHub Container Registry (ghcr.io)
   - Tags images with branch name and commit SHA

4. **After Setup:**
   - Your Docker image will be available at: `ghcr.io/kingquiet-bot/qr-training-manager`
   - You can deploy to any platform that supports Docker

## Deployment Platforms:

Once the workflow is set up, you can deploy to:

- **Railway:** https://railway.app
- **Render:** https://render.com
- **Fly.io:** https://fly.io
- **Heroku:** https://heroku.com
- **Google Cloud Run:** https://cloud.google.com/run
- **AWS ECS:** https://aws.amazon.com/ecs/

## Need Help?

If you have any issues, feel free to ask in the team channel!

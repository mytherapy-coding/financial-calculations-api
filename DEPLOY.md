# Quick Deployment Guide

## Deploy to Render (5 minutes)

1. **Go to**: https://dashboard.render.com/
2. **Sign up/Login** (use GitHub for easy connection)
3. **Click**: "New +" → "Web Service"
4. **Connect GitHub** and select: `financial-calculations-api`
5. **Render will auto-detect** `render.yaml` - just click "Create Web Service"
6. **Wait 2-3 minutes** for deployment
7. **Copy your URL**: `https://finance-api-xxx.onrender.com`

## After Getting Render URL

Once you have your Render URL, update `client/app.js`:
- Replace `YOUR-RENDER-URL.onrender.com` with your actual URL
- Commit and push
- Enable GitHub Pages (Settings → Pages → /client folder)

## Test Deployment

- Health: `https://your-url.onrender.com/v1/health`
- Docs: `https://your-url.onrender.com/docs`

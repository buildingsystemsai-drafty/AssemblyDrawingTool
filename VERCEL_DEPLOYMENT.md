# Vercel Deployment Guide

## ⚠️ Important Limitations

Vercel has strict limits for serverless functions:
- **Max function size**: 50MB (compressed)
- **Max execution time**: 10 seconds (Hobby plan) / 60 seconds (Pro plan)
- **Memory**: Limited for large PDF processing

Your app with pdfplumber + dependencies is **~200MB**, which exceeds Vercel's limits.

## ❌ Vercel is NOT recommended for this project because:
1. Dependencies too large (pdfplumber, PyPDF2, cryptography)
2. PDF processing takes more than 10 seconds
3. File uploads may exceed limits

---

## ✅ Better Alternatives (All FREE tiers available):

### 1. **Railway** (BEST - Easiest)
**Cost**: FREE tier - 500 hours/month

**Deploy in 2 minutes:**
1. Push code to GitHub
2. Go to https://railway.app
3. Click "Start a New Project" → "Deploy from GitHub"
4. Select your repo
5. Railway auto-detects Python and deploys
6. Add custom domain in settings

**Why Railway?**
- ✅ No size limits
- ✅ No timeout limits
- ✅ Handles large PDFs perfectly
- ✅ Super easy setup
- ✅ Free SSL/HTTPS
- ✅ Custom domains

---

### 2. **Render** (Good alternative)
**Cost**: FREE tier - 750 hours/month

1. Go to https://render.com
2. Create new "Web Service"
3. Connect GitHub repo
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
5. Deploy
6. Add custom domain

---

### 3. **Fly.io** (More technical)
**Cost**: FREE tier - 3 shared VMs

Uses the Dockerfile I already created:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

---

### 4. **Google Cloud Run** (Best for Firebase users)
See FIREBASE_DEPLOYMENT.md

---

## 🚀 Recommended: Railway (Easiest for your use case)

### Step-by-step:

1. **Push to GitHub** (if not already)
   ```bash
   cd C:\Users\ArmandLefebvre\AppData\Roaming\AssemblyDrawingTool
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Visit https://railway.app
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select AssemblyDrawingTool
   - Railway auto-deploys!

3. **Add Your Domain**
   - In Railway dashboard → Settings → Domains
   - Click "Add Domain"
   - Enter your domain (e.g., `app.yourdomain.com`)
   - Add CNAME record to your DNS:
     - Name: `app` (or whatever subdomain)
     - Value: `your-app.railway.app`

4. **Done!**
   Your app is live at your custom domain with FREE SSL!

---

## 📊 Comparison

| Feature | Vercel | Railway | Render | Cloud Run |
|---------|--------|---------|--------|-----------|
| Setup time | 2 min | 2 min | 5 min | 10 min |
| PDF support | ❌ Too limited | ✅ Perfect | ✅ Good | ✅ Perfect |
| Free tier | ❌ Won't work | ✅ 500 hrs | ✅ 750 hrs | ✅ 2M requests |
| Custom domain | ✅ Easy | ✅ Easy | ✅ Easy | ✅ Medium |
| Timeout | ❌ 10s | ✅ Unlimited | ✅ Unlimited | ✅ 300s |
| Deployment | Git push | Git push | Git push | Docker |

---

## 🎯 Final Recommendation

**Use Railway** - It's the easiest and works perfectly for your app:
1. No configuration needed
2. Handles large PDFs
3. No timeouts
4. Free SSL
5. Custom domains
6. Takes 2 minutes to deploy

Want me to help you set up Railway instead?

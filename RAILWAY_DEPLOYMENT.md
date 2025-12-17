# Railway Deployment Guide

Railway is the **easiest and best** platform for deploying this AssemblyDrawingTool app.

## Why Railway?
✅ No size limits (handles your ~200MB app with pdfplumber)
✅ No timeout limits (perfect for large PDF processing)
✅ Free tier: 500 hours/month
✅ Takes 2 minutes to deploy
✅ Custom domains with free SSL
✅ Auto-deploys on git push

---

## Step 1: Push Your Code to GitHub

Your code is already connected to GitHub at:
`https://github.com/buildingsystemsai-drafty/AssemblyDrawingTool`

Run these commands to push your latest changes:

```bash
cd C:\Users\ArmandLefebvre\AppData\Roaming\AssemblyDrawingTool
git add .
git commit -m "Add Railway deployment configuration"
git push origin arch-drawing-parser-paused
```

---

## Step 2: Deploy on Railway

### 2.1 Create Railway Account
1. Go to https://railway.app
2. Click "Login" (top right)
3. Sign in with your GitHub account
4. Authorize Railway to access your repositories

### 2.2 Create New Project
1. Click "New Project" button
2. Select "Deploy from GitHub repo"
3. Choose `buildingsystemsai-drafty/AssemblyDrawingTool`
4. Select branch: `arch-drawing-parser-paused`
5. Click "Deploy Now"

### 2.3 Wait for Build (2-3 minutes)
Railway will automatically:
- Detect Python project
- Install dependencies from requirements.txt
- Build your app
- Deploy it

You'll see a URL like: `https://assemblydrawingtool-production.up.railway.app`

---

## Step 3: Configure Environment (Optional)

If you need environment variables:
1. In Railway dashboard → Your project
2. Click "Variables" tab
3. Add any needed variables:
   - `FLASK_ENV=production`
   - `MAX_CONTENT_LENGTH=52428800` (50MB file uploads)

---

## Step 4: Add Custom Domain (Optional)

### 4.1 Generate Railway Domain
1. In Railway dashboard → Your project
2. Click "Settings" tab
3. Scroll to "Domains" section
4. Click "Generate Domain"
5. You'll get a URL like: `assemblydrawingtool.railway.app`

### 4.2 Add Your Own Domain
If you have a domain (e.g., `yourdomain.com`):

1. In Railway "Domains" section, click "Custom Domain"
2. Enter your domain: `app.yourdomain.com`
3. Railway will show DNS records to add
4. Go to your domain registrar (GoDaddy, Namecheap, etc.)
5. Add a CNAME record:
   - **Name**: `app`
   - **Value**: `your-app.up.railway.app`
   - **TTL**: 3600 (or automatic)
6. Wait 5-60 minutes for DNS propagation
7. Railway will automatically provision SSL certificate

---

## Step 5: Test Your Deployment

1. Visit your Railway URL
2. Upload some test PDFs
3. Verify parsing works correctly
4. Check logs in Railway dashboard if anything fails

---

## Monitoring & Logs

### View Logs
1. Railway dashboard → Your project
2. Click "Deployments" tab
3. Click latest deployment
4. View real-time logs

### Check Usage
1. Railway dashboard → Your project
2. Click "Metrics" tab
3. See CPU, memory, network usage
4. Free tier: 500 hours/month (about 20 days of 24/7 uptime)

---

## Automatic Deploys

Once connected, Railway auto-deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update parser logic"
git push origin arch-drawing-parser-paused

# Railway automatically rebuilds and deploys! 🚀
```

---

## Troubleshooting

### Build Fails
- Check logs in Railway dashboard
- Ensure `requirements.txt` is complete
- Verify `wsgi.py` exists

### App Crashes
- Check if `gunicorn` is in requirements.txt ✅ (already added)
- View runtime logs for errors
- Ensure PORT environment variable is used (Railway sets this automatically)

### File Uploads Fail
- Railway has generous limits (no issues expected)
- Check `MAX_CONTENT_LENGTH` in app.py

### Timeout Issues
- Railway has no timeout limits (perfect for PDF processing)

---

## Costs

**Free Tier**: 500 hours/month
- Perfect for development and testing
- About $0/month if you use less than 500 hours

**Starter Plan**: $5/month
- 500 hours included + $0.000231/hour for additional usage
- Priority support

**Pro Plan**: $20/month
- Better for production apps with high traffic

For your use case (occasional PDF processing), **free tier should be plenty**.

---

## Next Steps

1. ✅ Push code to GitHub (see Step 1 above)
2. ✅ Sign up for Railway (https://railway.app)
3. ✅ Deploy your app (takes 2 minutes)
4. ✅ Get your URL and share with colleagues
5. (Optional) Add custom domain

Need help? Railway has excellent docs: https://docs.railway.app

---

## Comparison with Other Platforms

| Feature | Railway | Render | Cloud Run | Vercel |
|---------|---------|--------|-----------|--------|
| Setup time | 2 min | 5 min | 10 min | N/A |
| PDF support | ✅ Perfect | ✅ Good | ✅ Perfect | ❌ Too limited |
| Free tier | ✅ 500 hrs | ✅ 750 hrs | ✅ 2M requests | ❌ Won't work |
| Timeout | ✅ Unlimited | ✅ Unlimited | ✅ 300s | ❌ 10s |
| Size limits | ✅ None | ✅ None | ✅ None | ❌ 50MB |
| Auto-deploy | ✅ Yes | ✅ Yes | ⚠️ Manual | ✅ Yes |
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Winner**: Railway - Best balance of ease-of-use and features for this app.

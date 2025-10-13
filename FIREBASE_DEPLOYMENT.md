# Firebase Deployment Guide

## Problem: Flask Backend + Firebase Hosting

Firebase Hosting only serves static files. Your Flask app needs a backend server.

## 🎯 Best Solutions for Firebase Users

### Option 1: Use Google Cloud Run (Recommended - Works with Firebase)

Cloud Run runs your Flask app as a container, works perfectly with Firebase.

#### Setup Steps:

1. **Install Google Cloud SDK**
   - Download from: https://cloud.google.com/sdk/docs/install
   - Run: `gcloud init`

2. **Create Dockerfile**
   (Already created - see Dockerfile in project)

3. **Deploy to Cloud Run**
   ```bash
   # Build and deploy
   gcloud run deploy assemblydrawing \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

4. **Connect your Firebase domain**
   ```bash
   # In Firebase Console:
   # Hosting → Add custom domain → Point to Cloud Run URL
   ```

**Cost**: Free tier: 2 million requests/month, 360,000 GB-seconds

---

### Option 2: Firebase Hosting + Cloud Functions (Python)

⚠️ **Limitation**: Cloud Functions has cold start delays and file size limits

#### Setup:

1. **Install Firebase CLI**
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

2. **Initialize Firebase**
   ```bash
   cd C:\Users\ArmandLefebvre\AppData\Roaming\AssemblyDrawingTool
   firebase init hosting
   firebase init functions
   # Choose Python when prompted
   ```

3. **Move Flask app to functions**
   ```bash
   # This is complex - better to use Cloud Run instead
   ```

**Not Recommended** because:
- Large dependencies (pdfplumber) may exceed size limits
- Cold starts are slow
- Complex setup

---

### Option 3: Hybrid - Firebase Hosting + External Backend

Keep your backend on Railway/Render, use Firebase for frontend only.

1. **Deploy backend to Railway**
   - Connect GitHub repo
   - Auto-deploys backend
   - Get URL: `https://your-app.railway.app`

2. **Update frontend to call Railway API**
   ```javascript
   // In static/js/app.js, change:
   const response = await fetch('/parse', { ... });
   // To:
   const response = await fetch('https://your-app.railway.app/parse', { ... });
   ```

3. **Deploy frontend to Firebase**
   ```bash
   firebase deploy --only hosting
   ```

---

## 🚀 Recommended: Cloud Run (Best for Firebase users)

Let me create the Dockerfile for you:


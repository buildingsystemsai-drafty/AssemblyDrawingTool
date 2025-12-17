#!/bin/bash
# Deploy to Google Cloud Run

# Configuration
PROJECT_ID="your-firebase-project-id"  # Replace with your Firebase project ID
SERVICE_NAME="assemblydrawing"
REGION="us-central1"

echo "🚀 Deploying Assembly Drawing Tool to Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --max-instances 10

echo "✅ Deployment complete!"
echo "🌐 Your app is now live at the URL shown above"
echo ""
echo "Next steps:"
echo "1. Go to Firebase Console → Hosting"
echo "2. Add custom domain or use the Cloud Run URL"
echo "3. Test your app!"

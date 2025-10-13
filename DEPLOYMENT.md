# Deployment Guide - Assembly Drawing Tool

## Prerequisites
- A server (Ubuntu 22.04 recommended)
- A domain name pointing to your server's IP
- SSH access to your server

## Quick Deploy Steps

### 1. Set up your server

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx -y
```

### 2. Upload your code

```bash
# On your local machine
cd C:\Users\ArmandLefebvre\AppData\Roaming\AssemblyDrawingTool
git add .
git commit -m "Prepare for deployment"
git push origin main

# On your server
cd /var/www
sudo git clone https://github.com/yourusername/AssemblyDrawingTool.git
cd AssemblyDrawingTool
```

### 3. Set up Python environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Nginx

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/assemblydrawing

# Update paths in the config file
sudo nano /etc/nginx/sites-available/assemblydrawing
# Replace:
#   - yourdomain.com with your actual domain
#   - /path/to/AssemblyDrawingTool with /var/www/AssemblyDrawingTool

# Enable site
sudo ln -s /etc/nginx/sites-available/assemblydrawing /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 5. Set up SSL (HTTPS) with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure SSL in nginx
```

### 6. Run the app with Gunicorn

```bash
# Test run
cd /var/www/AssemblyDrawingTool
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 wsgi:app

# If it works, set up systemd service (see below)
```

### 7. Create systemd service (Auto-start on boot)

```bash
# Create service file
sudo nano /etc/systemd/system/assemblydrawing.service
```

Paste this content:

```ini
[Unit]
Description=Assembly Drawing Tool
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/AssemblyDrawingTool
Environment="PATH=/var/www/AssemblyDrawingTool/venv/bin"
ExecStart=/var/www/AssemblyDrawingTool/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app --timeout 300

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable assemblydrawing
sudo systemctl start assemblydrawing

# Check status
sudo systemctl status assemblydrawing
```

### 8. Configure firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Verify Deployment

Visit your domain: `https://yourdomain.com`

## Useful Commands

```bash
# View app logs
sudo journalctl -u assemblydrawing -f

# Restart app
sudo systemctl restart assemblydrawing

# Restart nginx
sudo systemctl restart nginx

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# Update code
cd /var/www/AssemblyDrawingTool
git pull
sudo systemctl restart assemblydrawing
```

## Troubleshooting

### PDF uploads failing
Increase nginx max body size in `/etc/nginx/sites-available/assemblydrawing`:
```nginx
client_max_body_size 100M;
```

### Slow processing
Increase gunicorn workers:
```bash
sudo nano /etc/systemd/system/assemblydrawing.service
# Change --workers 3 to --workers 5 (or more)
sudo systemctl daemon-reload
sudo systemctl restart assemblydrawing
```

### Permission errors
```bash
sudo chown -R www-data:www-data /var/www/AssemblyDrawingTool
sudo chmod -R 755 /var/www/AssemblyDrawingTool
```

## Alternative: Deploy to Platform-as-a-Service

### Railway (Easiest)
1. Connect GitHub repo to Railway
2. Add environment variables if needed
3. Deploy automatically

### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn wsgi:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Render
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn wsgi:app`
4. Deploy

## Security Notes

- Change `debug=True` to `debug=False` in production
- Add authentication if needed
- Regularly update dependencies
- Set up backups for uploads folder
- Monitor logs for suspicious activity

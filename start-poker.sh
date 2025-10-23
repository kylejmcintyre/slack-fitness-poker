#!/bin/bash

# Slack Fitness Poker - Complete Startup Script
# This script configures nginx and starts both nginx and the poker app

# Set your environment variables here
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
export SLACK_CHANNEL="C1234567890"
export SITE_URL="bluebirdtech.duckdns.org"
export GAME_COMMAND="game"

# Server configuration
export PORT="5000"          # Change this to run on a different port
export HOST="127.0.0.1"     # Only listen on localhost (nginx will proxy)
export DEBUG="false"        # Set to "true" for debug mode

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🃏 Starting Slack Fitness Poker Bot${NC}"

# Change to app directory
cd /root/slack-fitness-poker

# Create nginx configuration
echo -e "${YELLOW}📝 Configuring nginx...${NC}"
cat > /etc/nginx/sites-available/slack-poker << EOF
server {
    listen 80;
    server_name bluebirdtech.duckdns.org;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bluebirdtech.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/bluebirdtech.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bluebirdtech.duckdns.org/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/slack-poker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
if nginx -t; then
    echo -e "${GREEN}✅ nginx configuration valid${NC}"
else
    echo -e "${RED}❌ nginx configuration error${NC}"
    exit 1
fi

# Start/restart nginx
systemctl restart nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ nginx started${NC}"
else
    echo -e "${RED}❌ nginx failed to start${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating Python environment...${NC}"
source poker-env/bin/activate

# Initialize database if needed
echo -e "${YELLOW}🗄️ Initializing database...${NC}"
python3 poker/local_db.py

# Function to handle cleanup
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    echo -e "${GREEN}✅ Thanks for playing! 🃏${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the application
echo -e "${GREEN}🚀 Starting poker app on ${HOST}:${PORT}${NC}"
echo -e "${GREEN}🌐 Available at: https://bluebirdtech.duckdns.org${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

exec python3 app.py
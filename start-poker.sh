#!/bin/bash

# Slack Fitness Poker - Simple Startup Script for systemd
# Edit the environment variables below with your actual values

# Set your environment variables here
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
export SLACK_CHANNEL="C1234567890"
export SITE_URL="your-domain.trycloudflare.com"
export GAME_COMMAND="game"

# Server configuration
export PORT="5000"          # Change this to run on a different port
export HOST="0.0.0.0"       # Listen on all interfaces
export DEBUG="false"        # Set to "true" for debug mode

# Activate virtual environment
cd /root/slack-fitness-poker
source poker-env/bin/activate

# Initialize database if needed
python3 poker/local_db.py

# Start the application
exec python3 app.py
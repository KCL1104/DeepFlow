#!/usr/bin/env python3
"""
Run the DeepFlow Slack Bot.
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from deepflow_agent.integrations.slack_bot import DeepFlowSlackBot

def main():
    if not os.environ.get("SLACK_BOT_TOKEN") or not os.environ.get("SLACK_APP_TOKEN"):
        print("Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in .env")
        sys.exit(1)
        
    print("Starting DeepFlow Slack Bot...")
    bot = DeepFlowSlackBot()
    bot.start()

if __name__ == "__main__":
    main()

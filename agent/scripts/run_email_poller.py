#!/usr/bin/env python3
"""
Run the DeepFlow Email Poller.
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from deepflow_agent.integrations.email_poller import EmailPoller

def main():
    if not os.environ.get("EMAIL_USER") or not os.environ.get("EMAIL_PASSWORD"):
        print("Error: EMAIL_USER and EMAIL_PASSWORD must be set in .env")
        print("Tip: For Gmail, use an App Password.")
        sys.exit(1)
        
    print("Starting DeepFlow Email Poller...")
    poller = EmailPoller()
    poller.start()

if __name__ == "__main__":
    main()

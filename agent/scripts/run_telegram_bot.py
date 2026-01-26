#!/usr/bin/env python
"""
Run the DeepFlow Telegram Bot

Usage:
    python scripts/run_telegram_bot.py

Or with uv:
    uv run python scripts/run_telegram_bot.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deepflow_agent.integrations.telegram_bot import DeepFlowTelegramBot


def main():
    print("=" * 60)
    print("🤖 DeepFlow Telegram Bot")
    print("=" * 60)
    print()
    print("Commands available:")
    print("  /start - Welcome message")
    print("  /link <user_id> - Link Telegram to DeepFlow")
    print("  /status - Check your state")
    print("  /queue - View task queue")
    print("  (text) - Analyze message with Agent")
    print()
    print("Press Ctrl+C to stop the bot.")
    print()
    
    bot = DeepFlowTelegramBot()
    bot.run()


if __name__ == "__main__":
    main()

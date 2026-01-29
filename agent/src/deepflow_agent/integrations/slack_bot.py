import os
import logging
import asyncio
from typing import Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from ..agents.react_agent import process_message, create_deepflow_agent
from ..tools.base import get_redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepFlowSlackBot:
    def __init__(self):
        self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.redis = get_redis_client()
        self._setup_handlers()

    def _setup_handlers(self):
        @self.app.message("")  # Listen to all messages
        def handle_message(message, say):
            # Run async handler in sync wrapper
            # Bolt's default handler is sync, but we need async for key lookups/agent
            # For simplicity in this POC, we'll use a blocking call or asyncio.run
            # Ideally Bolt async app should be used, but let's stick to simple implementation first or use async_app if needed.
            # actually, let's use the async handler pattern if we can, but Bolt sync is easier to setup without an async server.
            # We will use asyncio.run() for our agent calls.
            
            user_id = message["user"]
            text = message.get("text", "")
            
            # 1. Check Binding
            deepflow_user_id = self._get_deepflow_user(user_id)
            
            if not deepflow_user_id:
                # Simple linking logic for demo: "link <id>"
                if text.startswith("link "):
                    uid = text.split(" ")[1]
                    self._bind_user(user_id, uid)
                    say(f"✅ Linked Slack user <@{user_id}> to DeepFlow user `{uid}`")
                    return
                
                say(f"⚠️ Account not linked. Please reply with `link <your_deepflow_id>` used in your dashboard.")
                return

            # 2. Get User State
            user_state = self.redis.get(f"user_state:{deepflow_user_id}") or "FLOW"

            # 3. Process with Agent
            try:
                # We need to run the async agent process
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    process_message(
                        user_id=deepflow_user_id,
                        user_state=user_state,
                        message_content=text,
                        sender=f"SlackUser_{user_id}",
                        source="slack"
                    )
                )
                loop.close()
                
                # If agent returned a direct text output (not handled by tool), say it
                # Note: If valid tool calls happened (like send_auto_reply), result["output"] might be "Agent completed"
                # which we probably don't want to echo unless verbose.
                
                output = result.get("output", "")
                if output and output != "Agent completed":
                     say(output)
                     
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                say(f"❌ Error processing message: {str(e)}")

    def _get_deepflow_user(self, slack_user_id: str) -> Optional[str]:
        return self.redis.get(f"slack_binding:{slack_user_id}")

    def _bind_user(self, slack_user_id: str, deepflow_user_id: str):
        self.redis.set(f"slack_binding:{slack_user_id}", deepflow_user_id)
        # Verify by setting reverse binding if needed, or just logging
        logger.info(f"Bound Slack {slack_user_id} -> DeepFlow {deepflow_user_id}")

    def start(self):
        # Start Socket Mode
        app_token = os.environ.get("SLACK_APP_TOKEN")
        if not app_token:
            raise ValueError("SLACK_APP_TOKEN is required for Socket Mode")
            
        handler = SocketModeHandler(self.app, app_token)
        logger.info("⚡️ DeepFlow Slack Bot is running!")
        handler.start()

if __name__ == "__main__":
    bot = DeepFlowSlackBot()
    bot.start()

"""
DeepFlow Telegram Bot Integration

Long Polling mode for receiving messages and commands.
Integrates with ReAct Agent for message analysis and task management.
"""

import json
import logging
import os
from typing import Optional

import redis
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - DeepFlowBot - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

STATE_KEY_PREFIX = "user:state:"
QUEUE_KEY_PREFIX = "user:queue:"


def get_redis_client():
    """Get standard Redis client for user bindings."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.from_url(redis_url, decode_responses=True)


class DeepFlowTelegramBot:
    """DeepFlow Telegram Bot with Long Polling."""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        self.redis = get_redis_client()
        self.supabase = None
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if supabase_url and supabase_service_role_key:
            try:
                self.supabase = create_client(supabase_url, supabase_service_role_key)
            except Exception as exc:
                logger.warning(f"Supabase client initialization failed: {exc}")
        self.application = None
    
    # ==================== Binding Management ====================
    
    def get_user_binding(self, telegram_id: int) -> Optional[str]:
        """Get DeepFlow user ID bound to Telegram ID."""
        key = f"telegram_binding:{telegram_id}"
        return self.redis.get(key)
    
    def set_user_binding(self, telegram_id: int, deepflow_user_id: str):
        """Bind Telegram ID to DeepFlow user ID."""
        key = f"telegram_binding:{telegram_id}"
        self.redis.set(key, deepflow_user_id)
        
        # Also store reverse mapping
        reverse_key = f"deepflow_binding:{deepflow_user_id}"
        self.redis.set(reverse_key, str(telegram_id))
    
    def get_user_state(self, deepflow_user_id: str) -> str:
        """Get user's current state (FLOW/SHALLOW/IDLE)."""
        key = f"{STATE_KEY_PREFIX}{deepflow_user_id}"
        state = self.redis.get(key)
        return state if state else "IDLE"
    
    def set_user_state(self, deepflow_user_id: str, state: str):
        """Set user's current state."""
        key = f"{STATE_KEY_PREFIX}{deepflow_user_id}"
        self.redis.set(key, state)
        logger.info(f"Set state for {deepflow_user_id}: {state}")
    
    def add_task_to_queue(self, user_id: str, summary: str, category: str = "standard", source: str = "telegram") -> dict:
        """Add a task using the same toolchain as the Agent worker."""
        from deepflow_agent.tools.add_to_queue import add_to_queue as add_to_queue_tool

        urgency_map = {"critical": 10, "urgent": 7, "standard": 5, "low": 2}
        urgency = urgency_map.get(category, 5)

        result = add_to_queue_tool.invoke({
            "user_id": user_id,
            "task_summary": summary,
            "urgency_score": urgency,
            "category": category,
            "source": source,
            "source_id": f"telegram-manual-{user_id}",
        })
        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown error while adding task"))

        payload = result.get("result", {})
        logger.info(f"Added task {payload.get('task_id')} to {user_id}'s queue: {summary[:30]}...")
        return payload

    def _get_tasks_from_supabase(self, task_ids: list[str]) -> dict[str, dict]:
        """Fetch task details from Supabase in bulk."""
        if not self.supabase or not task_ids:
            return {}
        try:
            result = (
                self.supabase.table("tasks")
                .select("id,title,summary,urgency,status,created_at")
                .in_("id", task_ids)
                .execute()
            )
            rows = result.data or []
            return {row["id"]: row for row in rows}
        except Exception as exc:
            logger.warning(f"Failed to load tasks from Supabase: {exc}")
            return {}

    def _get_task_from_redis(self, task_id: str) -> dict:
        """Fallback task lookup from Redis."""
        task_data = self.redis.get(f"task:{task_id}")
        if not task_data:
            return {}
        try:
            return json.loads(task_data)
        except Exception:
            return {}
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        logger.info(f"/start from {user.id} ({user.username})")
        
        welcome_message = (
            "🌊 *Welcome to DeepFlow Sentinel!*\n\n"
            "I'm your AI-powered focus protection assistant. "
            "I help manage your communications and protect your deep work time.\n\n"
            "*Commands:*\n"
            "• `/link user_id` - Bind your Telegram to DeepFlow\n"
            "• `/add task` - Manually add a task to queue\n"
            "• `/flow` `/shallow` `/idle` - Switch your state\n"
            "• `/status` - Check your current state\n"
            "• `/queue` - View your task queue\n"
            "• `/help` - Show this help message\n\n"
            "*How it works:*\n"
            "When you're in FLOW state, I'll automatically handle low-priority "
            "messages and add important ones to your queue.\n\n"
            "Get started by linking your account with:\n"
            "`/link your-user-id`"
        )
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
    
    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link <user_id> command."""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide your DeepFlow user ID:\n"
                "`/link your-user-id`",
                parse_mode="Markdown"
            )
            return
        
        deepflow_user_id = context.args[0]
        
        # Check if already bound
        existing = self.get_user_binding(user.id)
        if existing:
            await update.message.reply_text(
                f"ℹ️ Your Telegram is already linked to: `{existing}`\n"
                "Updating to new user ID...",
                parse_mode="Markdown"
            )
        
        # Create binding
        self.set_user_binding(user.id, deepflow_user_id)
        
        logger.info(f"Linked Telegram {user.id} to DeepFlow {deepflow_user_id}")
        
        await update.message.reply_text(
            f"✅ *Successfully linked!*\n\n"
            f"Telegram: @{user.username or user.id}\n"
            f"DeepFlow: `{deepflow_user_id}`\n\n"
            "You can now send me messages, and I'll analyze them based on your current state.",
            parse_mode="Markdown"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user = update.effective_user
        deepflow_user_id = self.get_user_binding(user.id)
        
        if not deepflow_user_id:
            await update.message.reply_text(
                "❌ Your Telegram is not linked to DeepFlow.\n"
                "Use `/link your-user-id` first.",
                parse_mode="Markdown"
            )
            return
        
        state = self.get_user_state(deepflow_user_id)
        
        state_emoji = {
            "FLOW": "🎯",
            "SHALLOW": "💡",
            "IDLE": "☕"
        }
        
        state_desc = {
            "FLOW": "Deep Focus - Only critical interruptions",
            "SHALLOW": "Light Work - Important tasks allowed",
            "IDLE": "Available - All notifications enabled"
        }
        
        await update.message.reply_text(
            f"*Your DeepFlow Status*\n\n"
            f"{state_emoji.get(state, '❓')} *State:* {state}\n"
            f"📝 {state_desc.get(state, 'Unknown')}\n\n"
            f"🆔 User: `{deepflow_user_id}`",
            parse_mode="Markdown"
        )
    
    async def queue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /queue command."""
        user = update.effective_user
        deepflow_user_id = self.get_user_binding(user.id)
        
        if not deepflow_user_id:
            await update.message.reply_text(
                "❌ Your Telegram is not linked to DeepFlow.\n"
                "Use `/link your-user-id` first.",
                parse_mode="Markdown"
            )
            return
        
        # Get queue from Redis (member is task_id)
        queue_key = f"{QUEUE_KEY_PREFIX}{deepflow_user_id}"
        queue_items = self.redis.zrevrange(queue_key, 0, 4, withscores=True)
        
        if not queue_items:
            await update.message.reply_text(
                "📭 *Your queue is empty!*\n\n"
                "No pending tasks at the moment.",
                parse_mode="Markdown"
            )
            return
        
        queue_text = "*📋 Your Task Queue (Top 5)*\n\n"
        task_ids = [task_id for task_id, _ in queue_items]
        task_map = self._get_tasks_from_supabase(task_ids)

        for i, (task_id, score) in enumerate(queue_items, 1):
            task = task_map.get(task_id) or self._get_task_from_redis(task_id)
            if not task:
                queue_text += f"{i}. ⚪ Task `{task_id}` (Priority: {score:.1f})\n"
                continue

            urgency = int(task.get("urgency", task.get("urgency_score", 5)))
            emoji = "🔴" if urgency >= 9 else "🟠" if urgency >= 7 else "🟡" if urgency >= 4 else "🟢"
            summary = (task.get("summary") or task.get("title") or "Untitled task").strip()
            if len(summary) > 50:
                summary = f"{summary[:47]}..."
            queue_text += f"{i}. {emoji} {summary} (Priority: {score:.1f})\n"

        await update.message.reply_text(queue_text, parse_mode="Markdown")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await self.start_command(update, context)
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add <task description> command."""
        user = update.effective_user
        deepflow_user_id = self.get_user_binding(user.id)
        
        if not deepflow_user_id:
            await update.message.reply_text(
                "❌ Your Telegram is not linked to DeepFlow.\n"
                "Use `/link your-user-id` first.",
                parse_mode="Markdown"
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a task description:\n"
                "`/add Buy groceries`\n"
                "`/add --urgent Call client back`",
                parse_mode="Markdown"
            )
            return
        
        # Check for priority flag
        args = list(context.args)
        category = "standard"
        
        if args[0] in ["--critical", "-c"]:
            category = "critical"
            args.pop(0)
        elif args[0] in ["--urgent", "-u"]:
            category = "urgent"
            args.pop(0)
        elif args[0] in ["--low", "-l"]:
            category = "low"
            args.pop(0)
        
        task_summary = " ".join(args)
        
        if not task_summary:
            await update.message.reply_text("❌ Task description cannot be empty.")
            return
        
        # Add to queue
        task = self.add_task_to_queue(deepflow_user_id, task_summary, category, "telegram")
        
        category_emoji = {"critical": "🔴", "urgent": "🟠", "standard": "🟡", "low": "🟢"}
        
        await update.message.reply_text(
            f"✅ *Task added!*\n\n"
            f"{category_emoji.get(category, '⚪')} {task_summary}\n"
            f"Priority: {category.upper()}\n"
            f"ID: `{task.get('task_id', 'N/A')}`",
            parse_mode="Markdown"
        )
    
    async def flow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /flow command - switch to FLOW state."""
        await self._set_state_command(update, "FLOW")
    
    async def shallow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /shallow command - switch to SHALLOW state."""
        await self._set_state_command(update, "SHALLOW")
    
    async def idle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /idle command - switch to IDLE state."""
        await self._set_state_command(update, "IDLE")
    
    async def _set_state_command(self, update: Update, new_state: str):
        """Helper to set user state."""
        user = update.effective_user
        deepflow_user_id = self.get_user_binding(user.id)
        
        if not deepflow_user_id:
            await update.message.reply_text(
                "❌ Your Telegram is not linked to DeepFlow.\n"
                "Use `/link your-user-id` first.",
                parse_mode="Markdown"
            )
            return
        
        old_state = self.get_user_state(deepflow_user_id)
        self.set_user_state(deepflow_user_id, new_state)
        
        state_emoji = {"FLOW": "🎯", "SHALLOW": "💡", "IDLE": "☕"}
        state_desc = {
            "FLOW": "Deep Focus - Only critical interruptions",
            "SHALLOW": "Light Work - Important tasks allowed",
            "IDLE": "Available - All notifications enabled"
        }
        
        await update.message.reply_text(
            f"✅ *State changed!*\n\n"
            f"From: {state_emoji.get(old_state, '❓')} {old_state}\n"
            f"To: {state_emoji.get(new_state, '❓')} {new_state}\n\n"
            f"📝 {state_desc.get(new_state, '')}",
            parse_mode="Markdown"
        )
    
    # ==================== Message Handler ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages - analyze with Agent."""
        user = update.effective_user
        message_text = update.message.text
        
        # Check binding
        deepflow_user_id = self.get_user_binding(user.id)
        
        if not deepflow_user_id:
            await update.message.reply_text(
                "❌ Your Telegram is not linked to DeepFlow.\n"
                "Use `/link your-user-id` to get started.",
                parse_mode="Markdown"
            )
            return
        
        # Get user state
        user_state = self.get_user_state(deepflow_user_id)
        
        logger.info(f"Message from {user.id} ({deepflow_user_id}): {message_text[:50]}...")
        
        # Import and run agent (lazy import to avoid circular deps)
        try:
            from deepflow_agent.agents import process_message
            
            # Process message with agent
            result = await process_message(
                user_id=deepflow_user_id,
                user_state=user_state,
                message_content=message_text,
                sender=user.first_name or user.username or str(user.id),
                source="telegram"
            )
            
            # Get agent's response
            agent_response = result.get("output", "Message processed.")
            
            # Send response to user
            await update.message.reply_text(
                f"🤖 *DeepFlow Agent*\n\n{agent_response}",
                parse_mode="Markdown"
            )
            
            logger.info(f"Agent response sent to {user.id}")
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            await update.message.reply_text(
                f"⚠️ Error processing message: {str(e)[:100]}"
            )
    
    # ==================== Bot Lifecycle ====================
    
    def build_application(self) -> Application:
        """Build the Telegram application with handlers."""
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(CommandHandler("add", self.add_command))
        self.application.add_handler(CommandHandler("flow", self.flow_command))
        self.application.add_handler(CommandHandler("shallow", self.shallow_command))
        self.application.add_handler(CommandHandler("idle", self.idle_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("queue", self.queue_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Add message handler (for non-command text)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        return self.application
    
    def run(self):
        """Run the bot with Long Polling."""
        logger.info("Starting DeepFlow Telegram Bot (Long Polling)...")
        self.build_application()
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Entry point for running the bot."""
    bot = DeepFlowTelegramBot()
    bot.run()


if __name__ == "__main__":
    main()

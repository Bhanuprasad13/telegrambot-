from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import DatabaseManager

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: DatabaseManager, scheduler):
    command = update.message.text.split()[0].lower()
    
    if command == '/schedule':
        try:
            task = ' '.join(context.args)
            scheduler.schedule_task(task)
            await update.message.reply_text(f"Task scheduled: {task}")
        except IndexError:
            await update.message.reply_text("Usage: /schedule <task description>")
            
    elif command == '/notify':
        tasks = db.list_tasks(update.effective_user.id, status='pending')
        if not tasks:
            await update.message.reply_text("You have no upcoming tasks.")
            return
        
        upcoming_tasks = []
        now = datetime.now().timestamp()
        for task in tasks:
            scheduled_time = float(task[6])
            if now <= scheduled_time <= now + 3600:
                upcoming_tasks.append(task)
        
        if not upcoming_tasks:
            await update.message.reply_text("No tasks scheduled within the next hour.")
        else:
            response = "Upcoming tasks within the next hour:\n"
            for task in upcoming_tasks:
                response += f"\u2022 {task[3]} (ID: {task[0]})\n"
            await update.message.reply_text(response)
        
    elif command == '/help':
        help_text = """
Available commands:
/start - Welcome message
/add_task <time> <description> - Add timed task
/list_tasks - Show all tasks
/notify - Get notifications of tasks
/create_poll <question> | option1 | option2 | ... - Create a poll

You can also send:
- Documents (saved automatically)
- Photos (saved automatically)
- Links (saved automatically)
- Location (using the Share Location button)
- Group messages (monitored)
"""
        await update.message.reply_text(help_text)

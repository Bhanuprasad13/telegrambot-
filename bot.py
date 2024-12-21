from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Poll, PollOption, Location
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollHandler
import os
import logging
from commands import handle_command
from database import DatabaseManager
from scheduler import ScheduleManager

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.db = DatabaseManager('bot.db')
        self.scheduler = ScheduleManager(self.db)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    async def start(self, update: Update, context: ContextTypes):
        keyboard = [
            [KeyboardButton('Share Location', request_location=True)],
            [KeyboardButton('Create Poll')]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "Welcome! Available commands:\n"
            "/add_task <time> <description>\n"
            "/list_tasks\n"
            "/notify\n"
            "/create_poll <question> | option1 | option2 | ...\n"
            "/help\n"
            "You can also send:\n"
            "- Documents\n"
            "- Photos\n"
            "- Links\n"
            "- Location",
            reply_markup=reply_markup
        )

    async def add_task(self, update: Update, context: ContextTypes):
        try:
            time = int(context.args[0])
            description = ' '.join(context.args[1:])
            task_id = self.db.add_task(update.effective_user.id, 'scheduled', description, time)
            self.scheduler.schedule_task(task_id, time, description)
            await update.message.reply_text(f"Task added and scheduled: {description}")
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /add_task <time_in_seconds> <description>")

    async def list_tasks(self, update: Update, context: ContextTypes):
        tasks = self.db.list_tasks(update.effective_user.id)
        if not tasks:
            await update.message.reply_text("No tasks scheduled")
            return
        
        response = "Scheduled tasks:\n"
        for task in tasks:
            response += f"\u2022 ID: {task[0]} - {task[3]} (Status: {task[4]})\n"
        await update.message.reply_text(response)

    async def handle_document(self, update: Update, context: ContextTypes):
        try:
            doc = update.message.document
            file = await context.bot.get_file(doc.file_id)
            
            os.makedirs('documents', exist_ok=True)
            file_path = f"documents/{doc.file_name}"
            
            await file.download_to_drive(file_path)
            
            self.db.save_media('document', file_path, doc.file_name, update.effective_user.id)
            await update.message.reply_text(f"Document saved: {doc.file_name}")
            
        except Exception as e:
            await update.message.reply_text("Failed to process document. Please try again.")
            logging.error(f"Document handling error: {str(e)}")

    async def handle_photo(self, update: Update, context: ContextTypes):
        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
        
            os.makedirs('photos', exist_ok=True)
            file_path = f"photos/{photo.file_id}.jpg"
        
            await file.download_to_drive(file_path)
            caption = update.message.caption or "No caption"
            self.db.save_media('photo', file_path, caption, update.effective_user.id)
            await update.message.reply_text("Photo saved!")
            
        except Exception as e:
            await update.message.reply_text("Failed to process photo. Please try again.")
            logging.error(f"Photo handling error: {str(e)}")

    async def handle_location(self, update: Update, context: ContextTypes):
        try:
            location = update.message.location
            latitude = location.latitude
            longitude = location.longitude
            
            location_data = f"{latitude},{longitude}"
            self.db.save_media('location', location_data, '', update.effective_user.id)
            
            await update.message.reply_text(
                f"Location received!\nLatitude: {latitude}\nLongitude: {longitude}"
            )
            
        except Exception as e:
            await update.message.reply_text("Failed to process location. Please try again.")
            logging.error(f"Location handling error: {str(e)}")

    async def handle_text(self, update: Update, context: ContextTypes):
        message = update.message.text
        
        if any(prefix in message.lower() for prefix in ['http://', 'https://', 'www.']):
            self.db.save_media('link', message, '', update.effective_user.id)
            await update.message.reply_text("Link saved!")
            
        if update.message.chat.type in ['group', 'supergroup']:
            self.db.save_group_message(
                update.message.chat.id,
                update.effective_user.id,
                message
            )

    async def create_poll(self, update: Update, context: ContextTypes):
        try:
            content = ' '.join(context.args)
            parts = [part.strip() for part in content.split('|')]
            
            if len(parts) < 3:
                await update.message.reply_text(
                    "Usage: /create_poll Question | Option1 | Option2 | [Option3...]"
                )
                return
                
            question = parts[0]
            options = parts[1:]
            
            message = await context.bot.send_poll(
                update.effective_chat.id,
                question,
                options,
                is_anonymous=False,
                allows_multiple_answers=False
            )
            
            poll_data = {
                'question': question,
                'options': '|'.join(options),
                'message_id': message.message_id
            }
            self.db.save_poll(update.effective_user.id, poll_data)
            
        except Exception as e:
            await update.message.reply_text("Failed to create poll. Please try again.")
            logging.error(f"Poll creation error: {str(e)}")

    async def handle_poll_answer(self, update: Update, context: ContextTypes):
        try:
            answer = update.poll_answer
            self.db.save_poll_answer(
                answer.poll_id,
                update.effective_user.id,
                answer.option_ids
            )
        except Exception as e:
            logging.error(f"Poll answer handling error: {str(e)}")

    def run(self):
        app = Application.builder().token(self.token).build()
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("add_task", self.add_task))
        app.add_handler(CommandHandler("list_tasks", self.list_tasks))
        app.add_handler(CommandHandler("create_poll", self.create_poll))
        app.add_handler(CommandHandler("notify", lambda u, c: handle_command(u, c, self.db, self.scheduler)))
        app.add_handler(CommandHandler("help", lambda u, c: handle_command(u, c, self.db, self.scheduler)))
        
        # Media and message handlers
        app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        app.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        app.add_handler(PollHandler(self.handle_poll_answer))
        
        # Start the scheduler
        self.scheduler.start()

        try:
            app.run_polling()
        except Exception as e:
            print(f"Error occurred: {e}")
            logging.error(f"Bot runtime error: {str(e)}")

if __name__ == '__main__':
    # Remember to keep your token secret and not share it publicly
    bot = TelegramBot("7734796052:AAFuWD501VbIsuuTENL3nh_P5wL2APwg6qU")
    bot.run()
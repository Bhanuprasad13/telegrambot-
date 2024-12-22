# Automated Telegram Bot

A feature-rich Telegram bot built with python-telegram-bot that handles tasks, polls, media, and location tracking.

## Features

- **Task Management**
  - Schedule tasks with custom timers
  - Get notifications before task execution
  - List all pending and completed tasks
  - Automatic task status updates

- **Media Handling**
  - Save photos with captions
  - Store documents automatically
  - Track shared locations
  - Save links shared in chats

- **Interactive Features**
  - Create custom polls with multiple options
  - Track poll responses
  - Share location with one-click button
  - Group chat message monitoring

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Telegram bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

## Project Structure

```
├── bot.py              # Main bot implementation
├── commands.py         # Command handlers
├── database.py         # SQLite database management
├── scheduler.py        # Task scheduling system
├── test_bot.py        # Unit tests
└── requirements.txt    # Project dependencies
```

## Usage

1. Start the bot:
```bash
python bot.py
```

2. Available commands:
- `/start` - Welcome message and command list
- `/add_task <time> <description>` - Schedule a new task
- `/list_tasks` - View all tasks
- `/notify` - Check upcoming tasks
- `/create_poll <question> | option1 | option2 | ...` - Create a poll
- `/help` - Show help message

## Location Handling

The bot implements location tracking with the following features:
- One-click location sharing button
- Automatic storage of latitude and longitude
- Location data saved in SQLite database
- Privacy-focused handling of location data

## Polling System

The polling system includes:
- Custom poll creation with multiple options
- Anonymous/non-anonymous poll support
- Poll response tracking
- Results storage in database
- Poll answer analytics

## Database Schema

The bot uses SQLite with the following tables:
- `tasks`: Scheduled task management
- `media`: Store photos, documents, and locations
- `group_messages`: Track group chat activity
- `polls`: Store poll information
- `poll_answers`: Track poll responses

## Testing

Run the test suite:
```bash
python -m unittest test_bot.py
```

## License

[Add your license here]

## Security Notes

- The bot token has been removed from the source code
- Location data is stored securely
- Poll responses are handled privately
- Media files are stored in protected directories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

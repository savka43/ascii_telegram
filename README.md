# ASCII Telegram Bot

Telegram bot that converts user images into ASCII art and stores a small per-user history.

## MVP Features

- `/start` greeting
- image upload flow
- black-and-white or colored ASCII mode
- width selection: `80`, `100`, `120`
- PNG result rendering
- TXT result download
- user history via `/history` or `Мои арты`
- resend, repeat generation, and delete saved works
- async SQLite storage through SQLAlchemy 2

## Stack

- Python 3.12+
- aiogram 3
- ascii-art-converter from `our0boros/ascii-art-converter`
- Pillow
- SQLite
- SQLAlchemy 2 async
- pydantic-settings
- logging

## Architecture

```text
Telegram
  -> Handlers
  -> Services
  -> Repositories
  -> Database
```

`services/ascii_service.py` is the only place that imports and uses `ascii-art-converter`.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Put your Telegram token into `.env`:

```env
BOT_TOKEN=123456:telegram-token
```

Run the bot:

```bash
python main.py
```

SQLite database file defaults to `ascii_telegram.db`.

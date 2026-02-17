# Wellfound Job Automation MVP

🤖 Automated job discovery system that scrapes Wellfound, filters by your skills, and sends daily Telegram alerts with direct apply links.

## ✨ Features

- 🔍 **Smart Scraping**: Automatically scrapes latest Wellfound job listings
- 🎯 **Skill Matching**: Filters jobs based on your skills and preferences (0-100 relevance score)
- 📱 **Telegram Alerts**: Daily notifications with formatted job cards and apply links
- 💾 **SQLite Storage**: Tracks jobs and prevents duplicate notifications
- ✍️ **AI Cover Letters** (Optional): Generate tailored cover letters using OpenAI
- 🆓 **Zero Cost**: Uses only free/open-source tools

## 📋 Prerequisites

- Python 3.8+
- Telegram account
- (Optional) OpenAI API key for cover letter generation

## 🚀 Quick Start

### 1. Clone/Download Project

```bash
cd C:\Users\tembh\.gemini\antigravity\scratch\wellfound-job-automation
```

### 2. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

If you still see 403s, install stealth support:

```bash
pip install playwright-stealth
```

### 3. Set Up Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow instructions
3. Copy your **bot token** (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Get your **chat ID**:
   - Search for **@userinfobot** on Telegram
   - Send it any message
   - Copy the `Id` number

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
copy .env.example .env
```

Edit `.env` and add your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional - for cover letter generation
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Customize Your Profile

Edit `config/user_profile.json` with your skills:

```json
{
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "keywords": ["backend", "API", "startup"],
  "locations": ["Remote", "San Francisco"],
  "min_match_score": 50
}
```

### 6. Run the Automation

```bash
python main.py
```

You should receive Telegram notifications with matching jobs! 🎉

## 📅 Schedule Daily Runs

### Windows Task Scheduler

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Wellfound Job Automation"
4. Trigger: **Daily** at 9:00 AM
5. Action: **Start a program**
   - Program: `C:\Users\tembh\.gemini\antigravity\scratch\wellfound-job-automation\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\tembh\.gemini\antigravity\scratch\wellfound-job-automation`
6. Finish and test

## 🛠️ Configuration

### `config/config.json`

```json
{
  "scraper": {
    "max_pages": 3,        // Pages to scrape
    "delay_seconds": 2     // Delay between requests
  },
  "telegram": {
    "enabled": true,
    "batch_size": 5        // Jobs per message
  },
  "cover_letter": {
    "enabled": false       // Set to true if using OpenAI
  }
}
```

### `config/user_profile.json`

- **skills**: Your technical skills (used for matching)
- **keywords**: Job-related keywords (backend, startup, etc.)
- **locations**: Preferred locations
- **min_match_score**: Minimum score to notify (0-100)

## 📊 How Matching Works

Jobs are scored 0-100 based on:

- ✅ **Skill match**: +10 points per matched skill
- ✅ **Keyword match**: +5 points per keyword
- ✅ **Location match**: +15 points

Example: A job matching 3 skills + 2 keywords + location = ~70 score

## 📱 Telegram Message Format

```
🚀 New Job Match! (Score: 85/100)

📋 Title: Senior Python Developer
🏢 Company: TechCorp
📍 Location: Remote

💡 Matched Skills: Python, FastAPI, PostgreSQL

🔗 Apply Now
```

## 🧪 Testing Components

Test individual modules:

```bash
# Test database
python src/database.py

# Test scraper
python src/scraper.py

# Test matcher
python src/matcher.py

# Test Telegram notifications
python src/notifier.py
```

## 🐛 Troubleshooting

### No jobs found
- Wellfound's HTML structure may have changed
- Try adjusting `max_pages` in config
- Check internet connection

### Telegram not working
- Verify bot token and chat ID in `.env`
- Test by running `python src/notifier.py`
- Make sure you've started a chat with your bot

### Scraping errors
- Wellfound may block excessive requests
- Increase `delay_seconds` in config
- Use fewer `max_pages`

## 📁 Project Structure

```
wellfound-job-automation/
├── src/
│   ├── database.py       # SQLite operations
│   ├── scraper.py        # Wellfound scraper
│   ├── matcher.py        # Skill matching
│   ├── notifier.py       # Telegram alerts
│   └── cover_letter.py   # AI cover letters
├── config/
│   ├── user_profile.json # Your skills
│   └── config.json       # Settings
├── data/
│   └── jobs.db           # SQLite database
├── main.py               # Main script
├── requirements.txt      # Dependencies
└── .env                  # Credentials
```

## 🔒 Privacy & Ethics

- ⚠️ **Respect Wellfound's Terms of Service**
- Use reasonable scraping delays (2+ seconds)
- Don't scrape excessively
- This tool is for personal use only

## 🚀 Future Enhancements

- [ ] Email notifications
- [ ] Job application tracking
- [ ] Resume customization
- [ ] Multiple job board support
- [ ] Web dashboard

## 📝 License

MIT License - Free to use and modify

## 🤝 Contributing

Feel free to submit issues or pull requests!

---

**Happy job hunting! 🎯**

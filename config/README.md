
# Configuration Guide

This project uses two JSON configuration files:

- `config/config.json` — runtime configuration for scraping, notifications, cover-letter generation, storage, and logging.
- `config/user_profile.json` — your personal preferences used for job matching.

> Note: Some secrets (like API keys) should **not** be stored in JSON files. They are read from environment variables.

---

## How configuration flows through the app

```mermaid
flowchart TD
    A[main.py] --> B[load_config()]
    B --> C[config/config.json]
    B --> D[config/user_profile.json]
    C --> E[WellfoundScraper]
    D --> F[JobMatcher]
    C --> G[JobDatabase]
    C --> H[TelegramNotifier]
    C --> I[CoverLetterGenerator]
```

---

# `config/config.json`

## Top-level keys

### `scraper` (object)
Scraper settings for Wellfound.

#### `scraper.base_url` (string)
Base URL for Wellfound job search.
- Example: `"https://wellfound.com/jobs"`

#### `scraper.max_pages` (number)
Maximum number of result pages to scrape (keeps scraping bounded to reduce bans).
- Example: `3`

#### `scraper.delay_seconds` (number)
Delay between operations to reduce rate limiting / detection.
- Example: `2`

#### `scraper.timeout` (number)
Timeout (seconds) for page loads / waits.
- Example: `10`

#### `scraper.use_selenium` (boolean)
Whether to use Selenium browser automation for scraping.
- Example: `true`

#### `scraper.headless` (boolean)
Whether Chrome runs in headless mode.
- Example: `true`
- Tip: If debugging scraping, set `false` so you can see the browser.

#### `scraper.user_agents` (array of strings)
List of user-agent strings. The scraper randomly chooses one to reduce detection.
- Example: Chrome UA strings for Windows/Mac.

---

### `telegram` (object)
Telegram notification settings.

#### `telegram.enabled` (boolean)
Turns Telegram notifications on/off.
- Example: `true`

#### `telegram.batch_size` (number)
How many jobs to include per notification batch.
- Example: `5`

#### `telegram.message_format` (string)
Message parse mode used by Telegram.
- Typical values: `"Markdown"` / `"HTML"`
- Your config: `"markdown"` (note: Telegram parse mode is usually case-sensitive in many examples; if you see formatting issues, try `"Markdown"`)

**Required environment variables (when enabled):**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

### `cover_letter` (object)
Optional cover letter generation via OpenAI.

#### `cover_letter.enabled` (boolean)
Enables/disables cover letter generation.
- Example: `false`

#### `cover_letter.model` (string)
OpenAI model name to use.
- Example: `"gpt-3.5-turbo"`

#### `cover_letter.max_tokens` (number)
Maximum tokens for cover letter output (upper bound).
- Example: `500`

**Required environment variable (when enabled):**
- `OPENAI_API_KEY`

---

### `database` (object)
Database settings for storing job listings.

#### `database.path` (string)
SQLite DB file path.
- Example: `"data/jobs.db"`

Notes:
- The code ensures the directory exists (creates `data/` if needed).

---

### `logging` (object)
File logging configuration.

#### `logging.level` (string)
Log level.
- Example: `"INFO"` (common values: `DEBUG`, `INFO`, `WARNING`, `ERROR`)

#### `logging.file` (string)
Log file path.
- Example: `"data/automation.log"`

---

# `config/user_profile.json`

Used by the matcher to compute a match score and filter jobs.

## Keys

### `skills` (array of strings)
Your skills/tech keywords. Matching is done by checking if each skill appears in job text.
- Example: `["Python", "FastAPI", "Docker"]`

### `keywords` (array of strings)
General keywords representing job interests. Used similarly to skills but weighted differently.
- Example: `["backend", "startup", "remote"]`

### `locations` (array of strings)
Preferred locations. If a job location contains one of these strings, it gets a location bonus.
- Example: `["Remote", "San Francisco"]`

### `min_match_score` (number)
Threshold score for considering a job “good enough”.
- Example: `50`

### `job_types` (array of strings)
Preferred job types.
- Example: `["Full-time", "Contract"]`

> Note: If `job_types` is not currently used in matching logic, it can still be kept for future enhancements.

---

## Environment variables (recommended via `.env`)

Create a `.env` file in the project root (do not commit it):

```bash
OPENAI_API_KEY="..."
TELEGRAM_BOT_TOKEN="..."
TELEGRAM_CHAT_ID="..."
```

---

## Minimal config checklist

1. Confirm `config/config.json` exists.
2. Confirm `config/user_profile.json` exists.
3. If Telegram is enabled:
   - set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
4. If cover letters are enabled:
   - set `OPENAI_API_KEY`
```

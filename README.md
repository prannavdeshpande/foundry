# Project Overview

This project implements a Wellfound job scraper that matches job listings with user profiles, leveraging SQLite for database management and Telegram for notifications. Additionally, it offers an optional feature for generating cover letters using OpenAI.

## Architecture

```mermaid
graph TD;
    A[Job Scraper] --> B[Database];
    A --> C[Matcher];
    B --> D[Notifier];
    D --> E[Telegram];
    F[OpenAI] --> G[Cover Letter Generation];
    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style B fill:#ccf,stroke:#333,stroke-width:2px;
    style C fill:#cfc,stroke:#333,stroke-width:2px;
    style D fill:#ff0,stroke:#333,stroke-width:2px;
    style E fill:#f66,stroke:#333,stroke-width:2px;
    style F fill:#9cf,stroke:#333,stroke-width:2px;
    style G fill:#fcf,stroke:#333,stroke-width:2px;
```

## Features
- Job scraping from Wellfound
- User profile matching
- Database management with SQLite
- Telegram notifications
- Optional OpenAI cover letter generation

## Getting Started
1. Clone the repository
2. Install dependencies
3. Set up environment variables:  
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

For detailed setup instructions, refer to the [CONFIG.md](config/CONFIG.md).

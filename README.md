# Project Overview

This project implements a Wellfound job scraper that matches job listings with user profiles, leveraging SQLite for database management and Telegram for notifications. Additionally, it offers an optional feature for generating cover letters using OpenAI.

## Architecture

%% High-contrast styling for good visibility in both light and dark themes
flowchart TD
    A[Job Scraper] --> B[Database]
    A --> C[Matcher]
    B --> D[Notifier]
    D --> E[Telegram]
    F[OpenAI] --> G[Cover Letter Generation]

    %% Keep it monochrome and readable in any theme
    classDef node fill:#ffffff,stroke:#111111,color:#111111,stroke-width:2px;
    classDef external fill:#ffffff,stroke:#111111,color:#111111,stroke-dasharray: 6 4,stroke-width:2px;

    class A,B,C,D,G node;
    class E,F external;

    linkStyle default stroke:#111111,stroke-width:2px;

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

"""
Main orchestration script for Wellfound job automation.
Runs the complete workflow: scrape (visit detail pages) -> filter -> notify.
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path if your folder structure requires it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Assuming these modules exist in your src/ folder
# If you don't have database/matcher/notifier files yet, you'll need those too.
# For now, I'm importing assuming the structure exists.
try:
    from database import JobDatabase
    from scraper import WellfoundScraper
    from notifier import TelegramNotifier
    from matcher import JobMatcher
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure required modules are in the 'src' folder or same directory.")
    sys.exit(1)

def load_config():
    """Load configuration files."""
    load_dotenv()
    
    # Simple default config if file missing
    default_config = {
        "scraper": {
            "base_url": "https://wellfound.com/jobs",
            "max_pages": 1,
            "delay_seconds": 3,
            "use_selenium": True,
            "headless": False
        },
        "database": {"path": "data/jobs.db"},
        "telegram": {"enabled": True, "batch_size": 5},
        "cover_letter": {"enabled": False}
    }

    # Try loading config.json, else use default
    if os.path.exists('config/config.json'):
        with open('config/config.json', 'r') as f:
            config = json.load(f)
    else:
        config = default_config
        
    # Mock user profile if missing
    if os.path.exists('config/user_profile.json'):
        with open('config/user_profile.json', 'r') as f:
            user_profile = json.load(f)
    else:
        user_profile = {"keywords": ["Software Engineer"], "locations": ["Remote"]}

    return config, user_profile

def main():
    """Main automation workflow."""
    print("="*60)
    print("🚀 Wellfound Job Automation - Starting")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config, user_profile = load_config()
    
    # Initialize components
    print("🔧 Initializing components...")
    
    # Initialize DB (Mock class if not present for testing this script)
    try:
        db = JobDatabase(config['database']['path'])
    except:
        print("⚠️  JobDatabase not found. Printing results to console only.")
        db = None

    scraper = WellfoundScraper(config['scraper'])
    
    # Step 1: Scrape jobs
    print("\n🔍 Scraping Wellfound jobs (List -> Detail View)...")
    
    # Build search query from user keywords
    search_query = " ".join(user_profile.get('keywords', [])[:2])
    location = user_profile.get('locations', ['Remote'])[0]
    
    # This now visits each page individually to get the skills/stipend
    jobs = scraper.scrape_jobs(search_query=search_query, location=location)
    
    print(f"\n✅ Extraction Complete. Found {len(jobs)} jobs.")
    
    if not jobs:
        print("❌ No jobs found. Exiting.")
        return
    
    # Step 2: Match jobs against user profile (score must be > 0)
    matcher = JobMatcher(user_profile)
    matched_jobs = []
    for job in jobs:
        score = matcher.calculate_match_score(job)
        job['match_score'] = score
        if score > 0:
            matched_jobs.append(job)

    if not matched_jobs:
        print("❌ No matching jobs (score > 0). Exiting.")
        return

    # Step 3: Display Results (Top 2)
    print("\n📊 Sample Matched Data (Top 2):")
    for job in matched_jobs[:2]:
        print("-" * 40)
        print(f"Title:    {job.get('title', 'N/A')}")
        print(f"Company:  {job.get('company', 'N/A')}")
        print(f"Location: {job.get('location', 'N/A')}")
        skills = job.get('skills', []) or []
        print(f"Skills:   {', '.join(skills) if skills else 'N/A'}")
        print(f"Score:    {job.get('match_score', 0)}")
        print(f"URL:      {job.get('apply_url', 'N/A')}")
    
    # Step 4: Save to database (if DB module exists)
    if db:
        print("\n💾 Saving jobs to database...")
        new_jobs_count = db.save_jobs(matched_jobs)
        print(f"   Saved {new_jobs_count} new jobs")
        print("   (Database saving commented out for safety until DB schema matches new fields)")

    # Step 5: Send Telegram notifications
    telegram_cfg = config.get('telegram', {})
    if telegram_cfg.get('enabled', False):
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            print("⚠️  Telegram credentials missing in .env (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)")
        else:
            notifier = TelegramNotifier(bot_token, chat_id)
            batch_size = telegram_cfg.get('batch_size', 5)

            # Ensure fields expected by notifier exist
            for job in matched_jobs:
                job.setdefault('match_score', 0)
                job.setdefault('location', 'Not specified')
                job['matched_skills'] = job.get('matched_skills') or job.get('skills', [])

            sent = notifier.send_job_alerts(matched_jobs, batch_size=batch_size)
            if sent == 0:
                notifier.send_message("⚠️ No job alerts were sent. Check logs for details.")
            else:
                notifier.send_summary({
                    'scraped': len(jobs),
                    'matched': len(matched_jobs),
                    'sent': len(matched_jobs),
                    'avg_score': sum(j.get('match_score', 0) for j in matched_jobs) / len(matched_jobs)
                })
    else:
        print("ℹ️  Telegram is disabled in config")

    print("\n✅ Automation complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
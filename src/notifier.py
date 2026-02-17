"""
Telegram notification module.
Sends formatted job alerts via Telegram Bot API.
"""

import requests
from typing import List, Dict
import os


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram.
        
        Args:
            text: Message text
            parse_mode: "Markdown" or "HTML"
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def format_job_message(self, job: Dict) -> str:
        """
        Format a job as a Telegram message.
        
        Args:
            job: Job dictionary
        
        Returns:
            Formatted message string
        """
        # Escape special characters for Markdown
        def escape_md(text: str) -> str:
            if not text:
                return ""
            # Escape special markdown characters
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        score = job.get('match_score', 0)
        title = escape_md(job.get('title', 'Unknown'))
        company = escape_md(job.get('company', 'Unknown'))
        location = escape_md(job.get('location', 'Not specified'))
        apply_url = job.get('apply_url', '')
        
        # Build matched skills string
        matched_skills = job.get('matched_skills', [])
        if matched_skills:
            skills_str = escape_md(', '.join(matched_skills[:5]))
        else:
            skills_str = "See description"
        
        message = f"""🚀 *New Job Match\\!* \\(Score: {score}/100\\)

📋 *Title:* {title}
🏢 *Company:* {company}
📍 *Location:* {location}

💡 *Matched Skills:* {skills_str}

🔗 [Apply Now]({apply_url})

───────────────────
"""
        
        return message
    
    def send_job_alerts(self, jobs: List[Dict], batch_size: int = 5) -> int:
        """
        Send job alerts to Telegram.
        
        Args:
            jobs: List of job dictionaries
            batch_size: Max jobs per message
        
        Returns:
            Number of successfully sent messages
        """
        if not jobs:
            print("No jobs to send")
            return 0
        
        sent_count = 0
        
        # Send header message
        header = f"📬 *Daily Job Alert* \\- {len(jobs)} new matches\\!\n\n"
        
        # Batch jobs into groups
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            
            # Build batch message
            message = header if i == 0 else ""
            
            for job in batch:
                message += self.format_job_message(job)
            
            # Send message
            if self.send_message(message):
                sent_count += 1
                print(f"Sent batch {i // batch_size + 1} ({len(batch)} jobs)")
            else:
                print(f"Failed to send batch {i // batch_size + 1}")
        
        return sent_count
    
    def send_summary(self, stats: Dict):
        """Send automation summary statistics."""
        message = f"""📊 *Automation Summary*

🔍 Total jobs scraped: {stats.get('scraped', 0)}
✅ Jobs matched: {stats.get('matched', 0)}
📨 Alerts sent: {stats.get('sent', 0)}
⭐ Avg match score: {stats.get('avg_score', 0)}

_Next run scheduled for tomorrow\\._
"""
        self.send_message(message)


if __name__ == "__main__":
    # Test notifier (requires environment variables)
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        # Test with sample job
        sample_job = {
            'title': 'Senior Python Developer',
            'company': 'TechCorp',
            'location': 'Remote',
            'match_score': 85,
            'matched_skills': ['Python', 'FastAPI', 'PostgreSQL'],
            'apply_url': 'https://wellfound.com/job/example'
        }
        
        message = notifier.format_job_message(sample_job)
        print("Sending test message...")
        print(message)
        notifier.send_message(message)
    else:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")

"""
AI-powered cover letter generation module (optional).
Uses OpenAI API to generate tailored cover letters.
"""

import os
from typing import Dict, Optional


class CoverLetterGenerator:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize cover letter generator.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-3.5-turbo or gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self.enabled = bool(api_key)
    
    def generate(self, job: Dict, user_profile: Dict) -> Optional[str]:
        """
        Generate a cover letter for a job.
        
        Args:
            job: Job dictionary
            user_profile: User profile with skills and experience
        
        Returns:
            Generated cover letter text or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Build prompt
            prompt = self._build_prompt(job, user_profile)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional career coach helping write concise, compelling cover letters."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content.strip()
            return cover_letter
        
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return None
    
    def _build_prompt(self, job: Dict, user_profile: Dict) -> str:
        """Build prompt for cover letter generation."""
        skills = ', '.join(user_profile.get('skills', []))
        
        prompt = f"""Generate a professional cover letter for this job application:

Job Title: {job.get('title')}
Company: {job.get('company')}
Job Description: {job.get('description', '')[:300]}

My Skills: {skills}
Matched Skills: {', '.join(job.get('matched_skills', []))}

Requirements:
- Keep it concise (3-4 paragraphs)
- Highlight relevant skills and experience
- Show enthusiasm for the role
- Professional but friendly tone
- Do NOT include placeholders like [Your Name]

Generate only the cover letter body, no subject line or signature.
"""
        return prompt


if __name__ == "__main__":
    # Test cover letter generation
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        generator = CoverLetterGenerator(api_key)
        
        sample_job = {
            'title': 'Senior Python Developer',
            'company': 'TechCorp',
            'description': 'We are looking for an experienced Python developer to build scalable backend systems using FastAPI and PostgreSQL.',
            'matched_skills': ['Python', 'FastAPI', 'PostgreSQL']
        }
        
        user_profile = {
            'skills': ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS']
        }
        
        print("Generating cover letter...")
        letter = generator.generate(sample_job, user_profile)
        
        if letter:
            print("\n" + "="*50)
            print(letter)
            print("="*50)
    else:
        print("Please set OPENAI_API_KEY in .env file to test")

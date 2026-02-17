"""
Job matching and filtering module.
Calculates relevance scores based on user skills and preferences.
"""

from typing import List, Dict
import json


class JobMatcher:
    def __init__(self, user_profile: Dict):
        """
        Initialize matcher with user profile.
        
        Args:
            user_profile: Dict containing skills, keywords, locations, etc.
        """
        self.skills = [s.lower() for s in user_profile.get('skills', [])]
        self.keywords = [k.lower() for k in user_profile.get('keywords', [])]
        self.locations = [l.lower() for l in user_profile.get('locations', [])]
        self.min_score = user_profile.get('min_match_score', 50)
    
    def calculate_match_score(self, job: Dict) -> int:
        """
        Calculate relevance score (0-100) for a job.
        
        Scoring:
        - Direct skill match: +10 points each
        - Keyword in description: +5 points each
        - Location match: +15 points
        - Normalized to 0-100 scale
        """
        score = 0
        
        # Prepare job text for matching
        job_text = (
            job.get('title', '') + ' ' +
            job.get('description', '') + ' ' +
            ' '.join(job.get('skills', []))
        ).lower()
        
        # Skill matching
        matched_skills = []
        for skill in self.skills:
            if skill in job_text:
                score += 10
                matched_skills.append(skill)
        
        # Keyword matching
        matched_keywords = []
        for keyword in self.keywords:
            if keyword in job_text:
                score += 5
                matched_keywords.append(keyword)
        
        # Location matching
        job_location = job.get('location', '').lower()
        location_match = False
        for location in self.locations:
            if location in job_location:
                score += 15
                location_match = True
                break
        
        # Normalize to 0-100 scale
        # Max possible: (len(skills) * 10) + (len(keywords) * 5) + 15
        max_possible = (len(self.skills) * 10) + (len(self.keywords) * 5) + 15
        if max_possible > 0:
            score = min(100, int((score / max_possible) * 100))
        
        # Store matched items for reporting
        job['matched_skills'] = matched_skills
        job['matched_keywords'] = matched_keywords
        job['location_match'] = location_match
        
        return score
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs based on match score threshold.
        
        Args:
            jobs: List of job dictionaries
        
        Returns:
            Filtered and scored jobs, sorted by score
        """
        scored_jobs = []
        
        for job in jobs:
            score = self.calculate_match_score(job)
            job['match_score'] = score
            
            if score >= self.min_score:
                scored_jobs.append(job)
        
        # Sort by score (highest first)
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_jobs
    
    def get_match_summary(self, job: Dict) -> str:
        """Generate human-readable match summary."""
        summary_parts = []
        
        if job.get('matched_skills'):
            skills_str = ', '.join(job['matched_skills'][:5])
            summary_parts.append(f"Skills: {skills_str}")
        
        if job.get('matched_keywords'):
            keywords_str = ', '.join(job['matched_keywords'][:3])
            summary_parts.append(f"Keywords: {keywords_str}")
        
        if job.get('location_match'):
            summary_parts.append(f"Location: {job.get('location', 'N/A')}")
        
        return " | ".join(summary_parts) if summary_parts else "General match"


if __name__ == "__main__":
    # Test matcher
    user_profile = {
        'skills': ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
        'keywords': ['backend', 'API', 'startup'],
        'locations': ['Remote', 'San Francisco'],
        'min_match_score': 50
    }
    
    sample_jobs = [
        {
            'title': 'Senior Python Backend Engineer',
            'company': 'TechCorp',
            'description': 'We are looking for a backend engineer with Python and FastAPI experience to build scalable APIs.',
            'skills': ['Python', 'FastAPI', 'PostgreSQL'],
            'location': 'Remote',
            'apply_url': 'https://example.com/job1'
        },
        {
            'title': 'Frontend React Developer',
            'company': 'WebCo',
            'description': 'Build beautiful UIs with React and TypeScript.',
            'skills': ['React', 'TypeScript'],
            'location': 'New York',
            'apply_url': 'https://example.com/job2'
        }
    ]
    
    matcher = JobMatcher(user_profile)
    filtered = matcher.filter_jobs(sample_jobs)
    
    print(f"Filtered {len(filtered)} jobs:")
    for job in filtered:
        print(f"\n{job['title']} - Score: {job['match_score']}")
        print(f"  {matcher.get_match_summary(job)}")

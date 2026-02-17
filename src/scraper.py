"""
Wellfound job scraper module.
Scrapes job listings by gathering links from the search page 
and visiting each job page individually for full details.
"""

from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import hashlib
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WellfoundScraper:
    def __init__(self, config: Dict):
        """Initialize scraper with configuration."""
        self.base_url = config.get('base_url', 'https://wellfound.com/jobs')
        self.max_pages = config.get('max_pages', 1) # Limit pages to avoid bans
        self.delay = config.get('delay_seconds', 3)
        self.timeout = config.get('timeout', 15)
        self.use_selenium = config.get('use_selenium', True)
        self.headless = config.get('headless', False) 
        self.user_agents = config.get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ])
    
    def _get_chrome_driver(self):
        """Create and return Chrome WebDriver instance with anti-detection options."""
        options = Options()
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Anti-bot detection flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        return driver

    def scrape_jobs(self, search_query: str = "", location: str = "") -> List[Dict]:
        """Main scraping orchestration."""
        params = []
        if search_query:
            params.append(f"q={search_query.replace(' ', '+')}")
        if location:
            params.append(f"l={location.replace(' ', '+')}")
        
        search_url = self.base_url
        if params and '?' not in search_url:
            search_url += "?" + "&".join(params)
        
        logger.info(f"Starting scrape on: {search_url}")
        
        driver = None
        all_jobs = []

        try:
            driver = self._get_chrome_driver()
            
            # 1. Collect Job Links from the Search List
            job_links = self._collect_job_links(driver, search_url)
            logger.info(f"Collected {len(job_links)} job links. Visiting details...")

            # 2. Visit each link and parse details
            for index, link in enumerate(job_links):
                logger.info(f"Processing ({index+1}/{len(job_links)}): {link}")
                try:
                    driver.get(link)
                    
                    # Random sleep to behave like a human
                    time.sleep(self.delay + random.uniform(1, 3))
                    
                    # Wait for the H1 title to ensure page load
                    try:
                        WebDriverWait(driver, self.timeout).until(
                            EC.presence_of_element_located((By.TAG_NAME, "h1"))
                        )
                    except:
                        logger.warning(f"Timeout waiting for page load: {link}")
                        continue

                    job_data = self._parse_job_detail_page(driver.page_source, link)
                    if job_data:
                        all_jobs.append(job_data)
                
                except Exception as e:
                    logger.error(f"Error processing link {link}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Fatal scraper error: {e}")
        finally:
            if driver:
                driver.quit()
        
        return all_jobs

    def _collect_job_links(self, driver, search_url) -> List[str]:
        """Navigates the search page and extracts URLs of job cards."""
        driver.get(search_url)
        time.sleep(self.delay + 2)
        
        # Scroll logic for infinite scroll (limited by max_pages roughly)
        for _ in range(self.max_pages):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = []
        
        # Find all anchors that look like job links
        # Wellfound job links usually start with /jobs/ and are inside the main feed
        anchors = soup.find_all('a', href=re.compile(r'^/jobs/\d+'))
        
        for a in anchors:
            href = a['href']
            if not href.startswith('http'):
                href = f"https://wellfound.com{href}"
            
            # Deduplicate and basic filter (exclude signup links masked as jobs)
            if href not in links and "signup" not in href:
                links.append(href)
        
        return list(set(links)) # Return unique links

    def _parse_job_detail_page(self, html: str, url: str) -> Optional[Dict]:
        """
        Parses the detailed job page HTML (the format provided in your prompt).
        Extracts: Skills pills, Description keywords, Stipend/Salary, Short Desc.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

        # 2. Company
        # Usually in the header next to logo or "About the job" section
        # Strategy: Look for the link /company/name
        company = "Unknown"
        company_link = soup.find('a', href=re.compile(r'^/company/'))
        if company_link:
            # Often contains an image or text. Try to find text within or near.
            # Based on your HTML: <a ...><span class="text-sm font-semibold text-black">ecoLong</span></a>
            company_span = soup.find('span', class_=re.compile(r'font-semibold'))
            if company_span:
                company = company_span.get_text(strip=True)

        # 3. Stipend / Salary
        # Based on HTML: <li class="md:flex-none">$90k – $115k • No equity</li>
        # We look for a list item containing '$'
        stipend = "Not disclosed"
        equity = "None"
        
        # Look in the header list
        header_ul = soup.find('ul', class_=re.compile(r'flex'))
        if header_ul:
            for li in header_ul.find_all('li'):
                text = li.get_text(strip=True)
                if '$' in text or '€' in text or '£' in text:
                    # Split into salary and equity if dot exists
                    if '•' in text:
                        parts = text.split('•')
                        stipend = parts[0].strip()
                        if len(parts) > 1:
                            equity = parts[1].strip()
                    else:
                        stipend = text
                    break

        # 4. Description & Short Description
        desc_div = soup.find(id='job-description')
        full_description = ""
        short_description = ""
        
        if desc_div:
            full_description = desc_div.get_text(separator='\n', strip=True)
            # Create short description (first 200 chars)
            short_description = full_description[:200].replace('\n', ' ') + "..."

        # 5. Skills (Explicit Tags from UI)
        # HTML: <div class="mr-2 mt-2 rounded-3xl border ... bg-accent-persian-100 ...">Python</div>
        ui_skills = []
        skill_tags = soup.find_all('div', class_=re.compile(r'rounded-3xl.*bg-accent-persian-100'))
        for tag in skill_tags:
            ui_skills.append(tag.get_text(strip=True))

        # 6. Keywords (Extracted from Description text)
        extracted_keywords = self._extract_keywords_from_text(full_description)
        
        # Combine unique skills
        all_skills = list(set(ui_skills + extracted_keywords))

        # 7. Location
        # HTML: <a href="/location/...">New York City</a>
        location = "Remote" # Default
        loc_tag = soup.find('a', href=re.compile(r'/location/'))
        if loc_tag:
            location = loc_tag.get_text(strip=True)

        return {
            'id': self._generate_job_id(title, company),
            'title': title,
            'company': company,
            'location': location,
            'stipend': stipend,
            'equity': equity,
            'skills': all_skills, # Combined list
            'ui_skills': ui_skills, # Just the tags
            'short_description': short_description,
            'full_description': full_description,
            'apply_url': url,
            'match_score': 0 
        }

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract tech keywords from text."""
        # Add your specific tech stack keywords here
        keywords = [
            'Python', 'Django', 'Flask', 'FastAPI', 'React', 'Next.js', 'Vue', 
            'Node.js', 'TypeScript', 'JavaScript', 'AWS', 'Docker', 'Kubernetes',
            'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Go', 'Rust', 'C++',
            'Machine Learning', 'AI', 'LLM', 'DevOps', 'CI/CD'
        ]
        
        found = []
        text_lower = text.lower()
        for kw in keywords:
            # Use word boundary regex to avoid partial matches (e.g. 'Go' in 'Google')
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
                found.append(kw)
        return found

    def _generate_job_id(self, title: str, company: str) -> str:
        unique_str = f"{title}_{company}".lower()
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
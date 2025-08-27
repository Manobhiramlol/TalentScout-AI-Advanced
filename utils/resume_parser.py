"""
Advanced resume parsing utilities for TalentScout AI
Extract skills, experience, and qualifications from resume text with NLP techniques
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ParsedResume:
    """Structured resume data"""
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = None
    experience_years: int = 0
    education: List[str] = None
    certifications: List[str] = None
    previous_roles: List[str] = None
    summary: str = ""

class ResumeParser:
    """Advanced resume parser with comprehensive skill extraction"""
    
    def __init__(self):
        self.tech_skills = {
            'languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'swift',
                'kotlin', 'php', 'ruby', 'scala', 'typescript', 'html', 'css', 'r'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'express',
                'spring', 'rails', 'laravel', 'codeigniter', 'symfony', 'nextjs',
                'nuxt', 'gatsby', 'svelte', 'ember'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite',
                'oracle', 'sql server', 'cassandra', 'dynamodb', 'neo4j', 'influxdb'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'jenkins', 'ci/cd', 'devops', 'serverless', 'lambda', 'heroku'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'jira', 'confluence', 'slack',
                'figma', 'photoshop', 'illustrator', 'sketch', 'webpack', 'npm'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
                'jupyter', 'matplotlib', 'plotly', 'spark', 'hadoop', 'kafka'
            ]
        }
        
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'diploma', 'certificate', 'degree',
            'university', 'college', 'institute', 'school', 'education', 'mba'
        ]
        
        self.experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'(\d+)\+?\s*yrs',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*year\s*experience'
        ]
        
        self.job_title_patterns = [
            'software engineer', 'senior software engineer', 'lead developer',
            'full stack developer', 'frontend developer', 'backend developer',
            'data scientist', 'data analyst', 'machine learning engineer',
            'devops engineer', 'system administrator', 'project manager',
            'product manager', 'business analyst', 'qa engineer', 'tester',
            'ui/ux designer', 'product designer', 'scrum master', 'architect'
        ]
    
    def parse_resume_text(self, text: str) -> ParsedResume:
        """Parse resume text and extract structured data"""
        
        if not text or not text.strip():
            return ParsedResume()
        
        logger.info("Starting comprehensive resume parsing...")
        
        resume = ParsedResume()
        text_lines = text.split('\n')
        
        # Extract basic contact information
        resume.name = self._extract_name(text_lines[:5])
        resume.email = self._extract_email(text)
        resume.phone = self._extract_phone(text)
        
        # Extract technical skills
        resume.skills = self._extract_skills(text)
        
        # Extract years of experience
        resume.experience_years = self._extract_experience_years(text)
        
        # Extract education
        resume.education = self._extract_education(text)
        
        # Extract previous job titles
        resume.previous_roles = self._extract_job_titles(text)
        
        # Extract certifications
        resume.certifications = self._extract_certifications(text)
        
        # Generate professional summary
        resume.summary = self._generate_summary(resume)
        
        logger.info(f"Resume parsing completed: {len(resume.skills)} skills, {resume.experience_years} years experience")
        
        return resume
    
    def parse_resume_file(self, filepath: str) -> ParsedResume:
        """Parse resume from file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            return self.parse_resume_text(text)
        except Exception as e:
            logger.error(f"Failed to parse resume file {filepath}: {e}")
            return ParsedResume()
    
    def _extract_name(self, first_lines: List[str]) -> str:
        """Extract candidate name from first few lines"""
        for line in first_lines:
            line = line.strip()
            if 2 <= len(line.split()) <= 4:
                # Check if it looks like a name (only letters, spaces, dots)
                if re.match(r'^[A-Za-z\s\.]+$', line) and not any(
                    keyword in line.lower() for keyword in ['email', 'phone', 'address', 'resume']
                ):
                    return line.title()
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\+?1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US with country code
            r'\b\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'  # International
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills using comprehensive matching"""
        text_lower = text.lower()
        found_skills = []
        
        # Check each skill category
        for category, skills in self.tech_skills.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill.title())
        
        # Additional pattern matching for common skill formats
        skill_section_patterns = [
            r'(?:skills?|technologies?|tools?)[\s:]*([^\n]+)',
            r'(?:programming|technical)\s+(?:languages?|skills?)[\s:]*([^\n]+)',
            r'(?:proficient|experienced)\s+(?:in|with)[\s:]*([^\n]+)'
        ]
        
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common separators and clean
                potential_skills = re.split(r'[,;|\n•·]', match)
                for skill in potential_skills:
                    skill = skill.strip().title()
                    if 2 <= len(skill) <= 30 and skill not in found_skills:
                        # Check if it's a known technology
                        if any(skill.lower() in category_skills 
                              for category_skills in self.tech_skills.values()):
                            found_skills.append(skill)
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of professional experience"""
        text_lower = text.lower()
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    years = max(int(match.replace('+', '')) for match in matches)
                    return min(years, 50)  # Cap at reasonable maximum
                except ValueError:
                    continue
        
        return 0
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        text_lower = text.lower()
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(bachelor[\'s]?\s+(?:of\s+)?(?:science|arts|engineering|technology|computer science))',
            r'(master[\'s]?\s+(?:of\s+)?(?:science|arts|engineering|technology|business administration))',
            r'(phd|doctorate)\s+(?:in\s+)?(\w+)',
            r'(diploma)\s+(?:in\s+)?(\w+)',
            r'(certificate)\s+(?:in\s+)?(\w+)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    degree_text = ' '.join(filter(None, match))
                else:
                    degree_text = match
                education.append(degree_text.title())
        
        return list(set(education))
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract previous job titles"""
        text_lower = text.lower()
        found_titles = []
        
        for title in self.job_title_patterns:
            if title in text_lower:
                found_titles.append(title.title())
        
        # Look for common job title patterns
        title_patterns = [
            r'(?:worked as|served as|position as)\s+([a-zA-Z\s]+)',
            r'(?:role|title)[\s:]+([a-zA-Z\s]+)',
            r'(?:current|previous)\s+(?:role|position)[\s:]+([a-zA-Z\s]+)'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                title = match.strip().title()
                if 5 <= len(title) <= 50 and title not in found_titles:
                    found_titles.append(title)
        
        return list(set(found_titles))
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract professional certifications"""
        cert_keywords = [
            'aws certified', 'azure certified', 'google cloud certified',
            'cisco certified', 'microsoft certified', 'oracle certified',
            'certified scrum master', 'pmp', 'cissp', 'ceh', 'comptia',
            'salesforce certified', 'red hat certified'
        ]
        
        text_lower = text.lower()
        certifications = []
        
        for cert in cert_keywords:
            if cert in text_lower:
                certifications.append(cert.title())
        
        # Look for certification section
        cert_patterns = [
            r'(?:certifications?|certificates?)[\s:]*([^\n]+)',
            r'(?:certified|licensed)\s+(?:in|as)[\s:]*([^\n]+)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert_items = re.split(r'[,;|\n•·]', match)
                for item in cert_items:
                    item = item.strip().title()
                    if 5 <= len(item) <= 100:
                        certifications.append(item)
        
        return list(set(certifications))
    
    def _generate_summary(self, resume: ParsedResume) -> str:
        """Generate professional summary based on extracted data"""
        parts = []
        
        if resume.experience_years > 0:
            parts.append(f"{resume.experience_years} years of professional experience")
        
        if resume.skills:
            skill_count = len(resume.skills)
            if skill_count > 8:
                parts.append(f"proficient in {skill_count}+ technologies including {', '.join(resume.skills[:4])}")
            elif skill_count > 3:
                parts.append(f"skilled in {', '.join(resume.skills[:5])}")
            else:
                parts.append(f"experienced with {', '.join(resume.skills)}")
        
        if resume.education:
            parts.append(f"educational background in {resume.education[0].lower()}")
        
        if resume.previous_roles:
            parts.append(f"experience as {resume.previous_roles[0].lower()}")
        
        if resume.certifications:
            parts.append(f"certified in {resume.certifications[0].lower()}")
        
        if parts:
            summary = ". ".join(parts).capitalize() + "."
        else:
            summary = "Professional with diverse technical background."
        
        return summary
    
    def extract_key_metrics(self, resume: ParsedResume) -> Dict[str, Any]:
        """Extract key metrics from parsed resume"""
        skill_categories = self._categorize_skills(resume.skills or [])
        
        return {
            "total_skills": len(resume.skills) if resume.skills else 0,
            "experience_years": resume.experience_years,
            "education_count": len(resume.education) if resume.education else 0,
            "certification_count": len(resume.certifications) if resume.certifications else 0,
            "job_titles_count": len(resume.previous_roles) if resume.previous_roles else 0,
            "has_contact_info": bool(resume.email and resume.phone),
            "skill_categories": skill_categories,
            "seniority_level": self._determine_seniority(resume.experience_years),
            "completeness_score": self._calculate_completeness_score(resume)
        }
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, int]:
        """Categorize skills by type"""
        categories = {category: 0 for category in self.tech_skills.keys()}
        
        if not skills:
            return categories
        
        skills_lower = [skill.lower() for skill in skills]
        
        for category, category_skills in self.tech_skills.items():
            for skill in category_skills:
                if skill in skills_lower:
                    categories[category] += 1
        
        return categories
    
    def _determine_seniority(self, years: int) -> str:
        """Determine seniority level based on experience"""
        if years == 0:
            return "Entry Level"
        elif years <= 2:
            return "Junior"
        elif years <= 5:
            return "Mid-Level"
        elif years <= 10:
            return "Senior"
        else:
            return "Expert/Lead"
    
    def _calculate_completeness_score(self, resume: ParsedResume) -> float:
        """Calculate resume completeness score (0-1)"""
        score = 0.0
        max_score = 7.0
        
        # Basic contact info (2 points)
        if resume.name:
            score += 1.0
        if resume.email:
            score += 1.0
        
        # Skills (2 points)
        if resume.skills:
            if len(resume.skills) >= 5:
                score += 2.0
            elif len(resume.skills) >= 2:
                score += 1.0
            else:
                score += 0.5
        
        # Experience (1 point)
        if resume.experience_years > 0:
            score += 1.0
        
        # Education (1 point)
        if resume.education:
            score += 1.0
        
        # Job titles (1 point)
        if resume.previous_roles:
            score += 1.0
        
        return round(score / max_score, 2)

# Global instance
resume_parser = ResumeParser()

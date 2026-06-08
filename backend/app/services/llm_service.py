import logging
import os
from typing import Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from backend/.env
import pathlib
env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class LLMService:
    """Service for Groq LLM integration."""

    def __init__(self):
        """Initialize Groq LLM client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            logger.info("✓ Groq LLM client initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Groq client: {e}")
            raise

    def extract_skills_via_llm(self, resume_text: str) -> Dict:
        """
        Extract skills from resume using Groq LLM.
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Dictionary with extracted skills
        """
        logger.info("🔄 Extracting skills using Groq LLM...")
        
        prompt = f"""Analyze this resume and extract ONLY the technical and professional skills.
Return ONLY a JSON object with no additional text.
Format: {{"skills": ["skill1", "skill2", ...], "proficiency": ["beginner", "intermediate", "expert", ...]}}

Resume:
{resume_text[:2000]}

Return ONLY valid JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✓ LLM Skills Extraction Response:\n{response_text[:200]}")
            
            # Parse response
            import json
            try:
                skills_data = json.loads(response_text)
                logger.info(f"✓ Extracted {len(skills_data.get('skills', []))} skills via LLM")
                for skill in skills_data.get('skills', [])[:5]:
                    logger.info(f"  - {skill}")
                return skills_data
            except json.JSONDecodeError:
                logger.warning("Could not parse LLM response as JSON, returning raw text")
                return {"skills": response_text.split('\n'), "proficiency": []}
                
        except Exception as e:
            logger.error(f"✗ Error in skill extraction: {e}")
            return {"skills": [], "proficiency": [], "error": str(e)}

    def analyze_experience_via_llm(self, resume_text: str) -> Dict:
        """
        Analyze work experience level using Groq LLM.
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Dictionary with experience analysis
        """
        logger.info("🔄 Analyzing experience using Groq LLM...")
        
        prompt = f"""Analyze this resume and provide:
1. Total years of experience (estimate)
2. Seniority level (Junior/Mid/Senior/Lead)
3. Industry/domain expertise
4. Key achievements (2-3 bullet points)

Resume:
{resume_text[:2000]}

Provide response as JSON: {{"years": X, "level": "...", "domains": [...], "achievements": [...]}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✓ LLM Experience Analysis Response:\n{response_text[:200]}")
            
            # Parse response
            import json
            try:
                exp_data = json.loads(response_text)
                logger.info(f"✓ Analyzed experience - Level: {exp_data.get('level', 'Unknown')}, Years: {exp_data.get('years', '?')}")
                return exp_data
            except json.JSONDecodeError:
                logger.warning("Could not parse experience analysis as JSON")
                return {"years": 0, "level": "Unknown", "domains": [], "achievements": []}
                
        except Exception as e:
            logger.error(f"✗ Error in experience analysis: {e}")
            return {"years": 0, "level": "Unknown", "domains": [], "achievements": [], "error": str(e)}

    def generate_recommendations(
        self, 
        resume_text: str,
        job_description: str,
        matching_sections: list,
        alignment_score: float,
        extracted_skills: list
    ) -> Dict:
        """
        Generate AI recommendations using Groq LLM.
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
            matching_sections: Top matching sections from RAG
            alignment_score: Overall alignment percentage
            extracted_skills: Extracted skills from resume
            
        Returns:
            Dictionary with recommendations
        """
        logger.info("🔄 Generating AI recommendations using Groq LLM...")
        
        matching_text = "\n".join([f"- {m['section_title']}: {m['content'][:100]}" for m in matching_sections[:3]])
        
        prompt = f"""You are a professional resume advisor. Analyze the resume and job description to provide actionable recommendations.

RESUME (excerpt):
{resume_text[:1000]}

JOB DESCRIPTION:
{job_description[:1000]}

MATCHING ANALYSIS:
Alignment Score: {alignment_score:.2f}%
Top Matching Sections:
{matching_text}

Candidate Skills: {', '.join(extracted_skills[:10])}

Please provide a JSON response with:
1. "missing_skills": [list of skills NOT in resume but required for job]
2. "strong_matches": [2-3 areas where resume aligns well]
3. "improvement_areas": [3-5 specific improvements to make]
4. "overall_recommendation": [2-3 sentence summary]
5. "priority_actions": [top 3 actions to take immediately]

Return ONLY valid JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✓ LLM Generated Recommendations")
            
            # Parse response
            import json
            try:
                recommendations = json.loads(response_text)
                logger.info(f"✓ Recommendations Summary:")
                logger.info(f"  Missing Skills: {len(recommendations.get('missing_skills', []))} identified")
                logger.info(f"  Improvement Areas: {len(recommendations.get('improvement_areas', []))} identified")
                logger.info(f"  Priority Actions: {len(recommendations.get('priority_actions', []))} actions")
                
                # Log details
                for skill in recommendations.get('missing_skills', [])[:3]:
                    logger.info(f"    - {skill}")
                for action in recommendations.get('priority_actions', []):
                    logger.info(f"    → {action}")
                
                return recommendations
            except json.JSONDecodeError:
                logger.warning("Could not parse recommendations as JSON, returning raw text")
                return {
                    "missing_skills": [],
                    "strong_matches": [],
                    "improvement_areas": [response_text],
                    "overall_recommendation": response_text[:200],
                    "priority_actions": []
                }
                
        except Exception as e:
            logger.error(f"✗ Error generating recommendations: {e}")
            return {
                "missing_skills": [],
                "strong_matches": [],
                "improvement_areas": [],
                "overall_recommendation": f"Error: {str(e)}",
                "priority_actions": [],
                "error": str(e)
            }

    def generate_tailored_resume(
        self,
        resume_text: str,
        job_description: str,
        recommendations: Dict
    ) -> Dict:
        """
        Generate tailored resume content suggestions.
        
        Args:
            resume_text: Original resume text
            job_description: Job description
            recommendations: Previously generated recommendations
            
        Returns:
            Dictionary with tailored content
        """
        logger.info("🔄 Generating tailored resume suggestions...")
        
        prompt = f"""Based on the job description, provide specific rewrites/improvements to the resume.

ORIGINAL RESUME (excerpt):
{resume_text[:800]}

JOB DESCRIPTION (excerpt):
{job_description[:800]}

Missing Skills to Highlight: {', '.join(recommendations.get('missing_skills', [])[:5])}
Priority Areas: {', '.join(recommendations.get('improvement_areas', [])[:3])}

Provide JSON with:
1. "headline_suggestion": improved professional headline
2. "summary_suggestion": 2-3 lines for professional summary tailored to job
3. "keywords_to_add": [list of keywords from JD to naturally incorporate]
4. "section_rewrites": {{"section_name": "improved text", ...}} for 2-3 key sections

Return ONLY valid JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✓ Generated tailored resume suggestions")
            
            # Parse response
            import json
            try:
                tailored = json.loads(response_text)
                logger.info(f"✓ Tailored suggestions:")
                logger.info(f"  Headline: {tailored.get('headline_suggestion', '')[:50]}")
                logger.info(f"  Keywords to add: {', '.join(tailored.get('keywords_to_add', [])[:5])}")
                return tailored
            except json.JSONDecodeError:
                logger.warning("Could not parse tailored suggestions as JSON")
                return {
                    "headline_suggestion": response_text[:100],
                    "summary_suggestion": response_text,
                    "keywords_to_add": [],
                    "section_rewrites": {}
                }
                
        except Exception as e:
            logger.error(f"✗ Error generating tailored resume: {e}")
            return {
                "headline_suggestion": "",
                "summary_suggestion": "",
                "keywords_to_add": [],
                "section_rewrites": {},
                "error": str(e)
            }

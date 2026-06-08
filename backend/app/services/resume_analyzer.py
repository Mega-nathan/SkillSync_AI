import logging
from typing import Dict, Optional, Callable
from .embedding_service import EmbeddingService
from .llm_service import LLMService
from .progress_manager import ProgressManager
from ..parsers.text_cleaner import clean_text

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """Main orchestrator for the resume analysis pipeline."""

    def __init__(self):
        """Initialize all services."""
        logger.info("\n" + "="*80)
        logger.info("INITIALIZING RESUME ANALYZER PIPELINE")
        logger.info("="*80)
        
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self.progress_manager = ProgressManager()
        
        logger.info("✓ All services initialized successfully\n")

    async def analyze(
        self,
        resume_text: str,
        job_description: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Main analysis pipeline orchestrator.
        
        Args:
            resume_text: Raw resume text from parsed document
            job_description: Job description text from user
            progress_callback: Optional callback for progress updates
            
        Returns:
            Complete analysis report
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING RESUME ANALYSIS PIPELINE")
        logger.info("="*80 + "\n")
        
        # Set progress callback
        self.progress_manager.callback = progress_callback
        
        try:
            # STEP 1: Resume Uploaded
            logger.info("\n[STEP 1/6] RESUME UPLOADED")
            logger.info("-" * 40)
            resume_stats = {
                "original_length": len(resume_text),
                "lines_count": len(resume_text.split('\n'))
            }
            self.progress_manager.log_data("Resume Stats", resume_stats)
            await self.progress_manager.update_step(
                "Resume Uploaded",
                "Resume file successfully received and loaded",
                resume_stats
            )
            
            # STEP 2: Resume Parsed
            logger.info("\n[STEP 2/6] RESUME PARSED")
            logger.info("-" * 40)
            cleaned_resume = clean_text(resume_text)
            cleaned_stats = {
                "cleaned_length": len(cleaned_resume),
                "reduction_percent": ((len(resume_text) - len(cleaned_resume)) / len(resume_text) * 100)
            }
            self.progress_manager.log_data("Cleaned Resume Stats", cleaned_stats)
            logger.info(f"Resume text cleaned. Size: {len(cleaned_resume)} chars")
            await self.progress_manager.update_step(
                "Resume Parsed",
                "Resume text extracted and cleaned",
                cleaned_stats
            )
            
            # STEP 3: Skills Extracted
            logger.info("\n[STEP 3/6] SKILLS EXTRACTED")
            logger.info("-" * 40)
            
            # Split resume into sections
            sections = self.embedding_service.split_into_sections(cleaned_resume)
            self.progress_manager.log_data("Resume Sections", [s['title'] for s in sections])
            
            # Extract skills via LLM
            skills_data = self.llm_service.extract_skills_via_llm(cleaned_resume)
            extracted_skills = skills_data.get('skills', [])
            self.progress_manager.log_data("Extracted Skills", extracted_skills)
            await self.progress_manager.update_step(
                "Skills Extracted",
                f"Identified {len(extracted_skills)} skills using AI",
                {
                    "skills_count": len(extracted_skills),
                    "skills_sample": extracted_skills[:5],
                    "skill_proficiencies": skills_data.get('proficiency', [])[:5]
                }
            )
            
            # STEP 4: Experience Analyzed
            logger.info("\n[STEP 4/6] EXPERIENCE ANALYZED")
            logger.info("-" * 40)
            
            # Extract skills/experience from sections
            extracted_info = self.embedding_service.extract_skills_and_experience(sections)
            
            # Analyze experience via LLM
            experience_data = self.llm_service.analyze_experience_via_llm(cleaned_resume)
            experience_stats = {
                "years_of_experience": experience_data.get('years', 0),
                "seniority_level": experience_data.get('level', 'Unknown'),
                "domains": experience_data.get('domains', []),
                "key_achievements": experience_data.get('achievements', [])
            }
            self.progress_manager.log_data("Experience Analysis", experience_stats)
            await self.progress_manager.update_step(
                "Experience Analyzed",
                f"Identified {experience_data.get('years', 0)} years of experience at {experience_data.get('level', 'Unknown')} level",
                experience_stats
            )
            
            # STEP 5: Matching Against Job Description
            logger.info("\n[STEP 5/6] MATCHING AGAINST JOB DESCRIPTION")
            logger.info("-" * 40)
            
            # Generate embeddings for sections
            sections_with_embeddings = self.embedding_service.embed_sections(sections)
            
            # Perform RAG retrieval
            rag_results = self.embedding_service.retrieve_relevant_sections(
                sections_with_embeddings,
                job_description,
                top_k=3
            )
            alignment_score = rag_results['alignment_score']
            
            matching_stats = {
                "alignment_score": f"{alignment_score:.2f}%",
                "top_matches": len(rag_results['top_matches']),
                "matching_sections": [m['section_title'] for m in rag_results['top_matches']]
            }
            self.progress_manager.log_data("Matching Results", matching_stats)
            await self.progress_manager.update_step(
                "Matching Against Job Description",
                f"Resume alignment score: {alignment_score:.2f}%",
                matching_stats
            )
            
            # STEP 6: Generating Recommendations
            logger.info("\n[STEP 6/6] GENERATING RECOMMENDATIONS")
            logger.info("-" * 40)
            
            # Generate recommendations
            recommendations = self.llm_service.generate_recommendations(
                cleaned_resume,
                job_description,
                rag_results['top_matches'],
                alignment_score,
                extracted_skills
            )
            
            # Generate tailored resume suggestions
            tailored = self.llm_service.generate_tailored_resume(
                cleaned_resume,
                job_description,
                recommendations
            )
            
            recommendation_stats = {
                "missing_skills_count": len(recommendations.get('missing_skills', [])),
                "improvement_areas_count": len(recommendations.get('improvement_areas', [])),
                "priority_actions_count": len(recommendations.get('priority_actions', []))
            }
            self.progress_manager.log_data("Recommendation Stats", recommendation_stats)
            await self.progress_manager.update_step(
                "Generating Recommendations",
                "AI-generated recommendations and tailored suggestions complete",
                recommendation_stats
            )
            
            # COMPILE FINAL REPORT
            logger.info("\n" + "="*80)
            logger.info("ANALYSIS COMPLETE - COMPILING FINAL REPORT")
            logger.info("="*80 + "\n")
            
            final_report = {
                "status": "success",
                "analysis_metadata": {
                    "resume_length": len(cleaned_resume),
                    "job_description_length": len(job_description),
                    "sections_analyzed": len(sections),
                    "total_steps": 6
                },
                "step_1_resume_upload": {
                    "filename_preview": "resume",
                    "size_chars": len(cleaned_resume)
                },
                "step_2_resume_parsed": {
                    "cleaned": True,
                    "sections_identified": len(sections)
                },
                "step_3_skills_extracted": {
                    "skills": extracted_skills,
                    "proficiency_levels": skills_data.get('proficiency', []),
                    "total_skills": len(extracted_skills)
                },
                "step_4_experience_analyzed": {
                    "years": experience_data.get('years', 0),
                    "seniority_level": experience_data.get('level', 'Unknown'),
                    "domains": experience_data.get('domains', []),
                    "key_achievements": experience_data.get('achievements', [])
                },
                "step_5_job_matching": {
                    "alignment_score": alignment_score,
                    "alignment_percentage": f"{alignment_score:.2f}%",
                    "top_matching_sections": rag_results['top_matches'],
                    "matching_strength": "Excellent" if alignment_score > 75 else "Good" if alignment_score > 50 else "Needs Improvement"
                },
                "step_6_recommendations": {
                    "missing_skills": recommendations.get('missing_skills', []),
                    "strong_matches": recommendations.get('strong_matches', []),
                    "improvement_areas": recommendations.get('improvement_areas', []),
                    "overall_recommendation": recommendations.get('overall_recommendation', ''),
                    "priority_actions": recommendations.get('priority_actions', []),
                    "tailored_resume": {
                        "headline_suggestion": tailored.get('headline_suggestion', ''),
                        "summary_suggestion": tailored.get('summary_suggestion', ''),
                        "keywords_to_add": tailored.get('keywords_to_add', []),
                        "section_rewrites": tailored.get('section_rewrites', {})
                    }
                },
                "progress_summary": self.progress_manager.get_summary()
            }
            
            logger.info("\n✓ FINAL REPORT GENERATED")
            logger.info(f"✓ Total processing: 6 steps completed")
            logger.info(f"✓ Final alignment score: {alignment_score:.2f}%")
            logger.info("\n" + "="*80)
            
            return final_report
            
        except Exception as e:
            logger.error(f"\n✗ ERROR IN PIPELINE: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_message": str(e),
                "progress_summary": self.progress_manager.get_summary()
            }

import logging
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings and performing RAG operations."""

    def __init__(self):
        """Initialize embedding service with sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✓ Embedding model loaded successfully: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"✗ Failed to load embedding model: {e}")
            raise

    def split_into_sections(self, text: str, max_length: int = 500) -> List[Dict]:
        """
        Split resume text into meaningful sections with overlap.
        
        Args:
            text: Full resume text
            max_length: Maximum length of each chunk
            
        Returns:
            List of section dictionaries with text and metadata
        """
        logger.info("🔄 Splitting text into sections...")
        
        # Define section patterns
        section_keywords = [
            'experience', 'skills', 'education', 'projects', 
            'certifications', 'qualifications', 'summary', 'objective'
        ]
        
        sections = []
        current_section = ""
        section_title = "HEADER"
        
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            is_header = any(keyword in line_lower for keyword in section_keywords)
            
            if is_header and current_section:
                # Save previous section
                sections.append({
                    "title": section_title,
                    "content": current_section.strip(),
                    "length": len(current_section)
                })
                current_section = ""
                section_title = line.strip()
            else:
                current_section += line + "\n"
        
        # Add last section
        if current_section.strip():
            sections.append({
                "title": section_title,
                "content": current_section.strip(),
                "length": len(current_section)
            })
        
        logger.info(f"✓ Created {len(sections)} sections from resume")
        for i, sec in enumerate(sections[:3]):
            logger.info(f"  [{i}] {sec['title']}: {sec['length']} chars")
        
        return sections

    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (numpy array)
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            logger.info(f"✓ Generated embedding of shape {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"✗ Error generating embedding: {e}")
            raise

    def embed_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for all sections.
        
        Args:
            sections: List of section dictionaries
            
        Returns:
            Sections with added embeddings
        """
        logger.info("🔄 Generating embeddings for all sections...")
        
        for i, section in enumerate(sections):
            embedding = self.embed_text(section['content'])
            section['embedding'] = embedding
            logger.info(f"  ✓ Section [{i}] '{section['title']}' embedded")
        
        logger.info(f"✓ Generated embeddings for {len(sections)} sections")
        return sections

    def retrieve_relevant_sections(
        self, 
        resume_sections: List[Dict], 
        job_description: str,
        top_k: int = 3
    ) -> Dict:
        """
        Retrieve resume sections most relevant to job description using RAG.
        
        Args:
            resume_sections: Resume sections with embeddings
            job_description: Full job description text
            top_k: Number of top matches to retrieve
            
        Returns:
            Dictionary with matching sections and scores
        """
        logger.info("🔄 Performing RAG retrieval against job description...")
        
        # Embed job description
        jd_embedding = self.embed_text(job_description)
        logger.info(f"✓ Job description embedded")
        
        # Calculate similarity scores
        similarities = []
        for section in resume_sections:
            if 'embedding' in section:
                # Cosine similarity
                score = cosine_similarity(
                    [jd_embedding], 
                    [section['embedding']]
                )[0][0]
                similarities.append({
                    "section_title": section['title'],
                    "content": section['content'],
                    "similarity_score": float(score),
                    "content_preview": section['content'][:100] + "..."
                })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_matches = similarities[:top_k]
        
        logger.info(f"✓ Retrieved top {top_k} matching sections")
        for i, match in enumerate(top_matches):
            logger.info(f"  [{i+1}] {match['section_title']}: {match['similarity_score']:.4f} similarity")
        
        # Calculate overall alignment score
        alignment_score = np.mean([m['similarity_score'] for m in top_matches]) * 100
        logger.info(f"✓ Overall alignment score: {alignment_score:.2f}%")
        
        return {
            "top_matches": top_matches,
            "alignment_score": alignment_score,
            "total_sections_analyzed": len(resume_sections),
            "jd_summary": job_description[:100] + "..."
        }

    def extract_skills_and_experience(
        self, 
        resume_sections: List[Dict]
    ) -> Dict:
        """
        Extract skills and experience information from sections.
        
        Args:
            resume_sections: Resume sections
            
        Returns:
            Extracted skills and experience
        """
        logger.info("🔄 Extracting skills and experience...")
        
        skills = []
        experience_items = []
        
        for section in resume_sections:
            title = section['title'].lower()
            content = section['content']
            
            # Extract skills from skills section
            if 'skill' in title:
                # Simple extraction: split by comma or newline
                items = [s.strip() for s in content.replace('\n', ',').split(',')]
                skills.extend([s for s in items if len(s) > 2 and len(s) < 50])
            
            # Extract experience from experience section
            if 'experience' in title or 'work' in title:
                lines = content.split('\n')
                for line in lines:
                    if len(line.strip()) > 10:
                        experience_items.append(line.strip())
        
        logger.info(f"✓ Extracted {len(skills)} skills")
        for skill in skills[:5]:
            logger.info(f"  - {skill}")
        if len(skills) > 5:
            logger.info(f"  ... and {len(skills) - 5} more skills")
        
        logger.info(f"✓ Extracted {len(experience_items)} experience items")
        
        return {
            "skills": skills,
            "experience_count": len(experience_items),
            "experience_sample": experience_items[:2] if experience_items else []
        }

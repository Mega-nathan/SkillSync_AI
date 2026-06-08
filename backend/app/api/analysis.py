import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import AsyncGenerator

from ..parsers.text_cleaner import clean_text
from ..parsers.docx_parser import extract_text_from_docx
from ..parsers.pdf_parser import extract_text_from_pdf
from ..services.resume_analyzer import ResumeAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])


async def event_generator(analyzer: ResumeAnalyzer, resume_text: str, job_description: str) -> AsyncGenerator:
    """Generate Server-Sent Events for progress updates."""
    
    async def send_progress(progress_data: dict):
        """Callback to send progress updates."""
        event_data = json.dumps(progress_data)
        yield f"data: {event_data}\n\n"
    
    # Run analysis with progress callback
    result = await analyzer.analyze(
        resume_text=resume_text,
        job_description=job_description,
        progress_callback=send_progress
    )
    
    # Send final result
    yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"


@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyze resume against job description using RAG pipeline.
    
    Args:
        file: Resume file (PDF or DOCX)
        job_description: Job description text
        
    Returns:
        StreamingResponse with progress updates and final analysis
    """
    logger.info("\n" + "="*80)
    logger.info("NEW ANALYSIS REQUEST RECEIVED")
    logger.info("="*80)
    logger.info(f"File: {file.filename}")
    logger.info(f"Job Description Length: {len(job_description)} chars")
    
    # Parse resume file
    try:
        logger.info("🔄 Parsing uploaded file...")
        content = await file.read()
        name = file.filename or "uploaded"
        
        if name.lower().endswith(".pdf"):
            logger.info(f"📄 Detected PDF file: {name}")
            txt = extract_text_from_pdf(content)
        elif name.lower().endswith(('.docx', '.doc')):
            logger.info(f"📄 Detected DOCX file: {name}")
            txt = extract_text_from_docx(content)
        else:
            logger.info(f"📄 Attempting to parse as text: {name}")
            try:
                txt = content.decode('utf8')
            except Exception:
                txt = ""
        
        if not txt:
            logger.error("✗ Could not extract text from file")
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        logger.info(f"✓ File parsed successfully. Text length: {len(txt)} chars")
        logger.info(f"Preview: {txt[:100]}...")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error parsing file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    # Validate job description
    if not job_description or len(job_description.strip()) < 10:
        logger.error("✗ Job description too short")
        raise HTTPException(status_code=400, detail="Job description must be at least 10 characters")
    
    logger.info(f"✓ Job description validated")
    
    # Initialize analyzer
    try:
        analyzer = ResumeAnalyzer()
    except Exception as e:
        logger.error(f"✗ Failed to initialize analyzer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize analysis services")
    
    # Return streaming response with progress updates
    logger.info("✓ Starting streaming analysis response...")
    return StreamingResponse(
        event_generator(analyzer, txt, job_description),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/analyze-simple")
async def analyze_resume_simple(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyze resume (non-streaming version for testing).
    
    Args:
        file: Resume file (PDF or DOCX)
        job_description: Job description text
        
    Returns:
        JSON with complete analysis result
    """
    logger.info("\n" + "="*80)
    logger.info("SIMPLE ANALYSIS REQUEST (NON-STREAMING)")
    logger.info("="*80)
    
    # Parse resume file
    try:
        logger.info("🔄 Parsing uploaded file...")
        content = await file.read()
        name = file.filename or "uploaded"
        
        if name.lower().endswith(".pdf"):
            txt = extract_text_from_pdf(content)
        elif name.lower().endswith(('.docx', '.doc')):
            txt = extract_text_from_docx(content)
        else:
            try:
                txt = content.decode('utf8')
            except Exception:
                txt = ""
        
        if not txt:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        logger.info(f"✓ File parsed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error parsing file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    # Validate job description
    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(status_code=400, detail="Job description must be at least 10 characters")
    
    # Initialize analyzer and run analysis
    try:
        analyzer = ResumeAnalyzer()
        result = await analyzer.analyze(txt, job_description)
        logger.info("\n✓ Simple analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"✗ Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

"""
Test script for the resume analysis pipeline
"""
import requests
import json
from pathlib import Path

# Create sample resume text
SAMPLE_RESUME = """
JOHN SMITH
Senior Software Engineer | Full Stack Developer
john.smith@email.com | (555) 123-4567 | LinkedIn.com/in/johnsmith

PROFESSIONAL SUMMARY
Experienced Full Stack Software Engineer with 7+ years of expertise in building scalable web applications.
Proficient in Python, JavaScript, React, and cloud technologies. Proven track record of delivering
high-quality solutions that improve user experience and business metrics.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, Java, SQL
Frontend: React, Vue.js, HTML5, CSS3, Tailwind CSS
Backend: FastAPI, Django, Node.js, Express
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Google Cloud, Docker, Kubernetes
Tools: Git, Jenkins, GitHub Actions, Jira

PROFESSIONAL EXPERIENCE

Senior Software Engineer | Tech Corp Inc. | 2021 - Present
- Led development of microservices architecture serving 1M+ users
- Implemented CI/CD pipelines reducing deployment time by 60%
- Mentored team of 5 junior developers
- Technologies: Python, FastAPI, PostgreSQL, Docker, Kubernetes

Software Engineer | WebSolutions Ltd. | 2018 - 2021
- Built RESTful APIs using Django and FastAPI
- Developed responsive frontend applications using React
- Optimized database queries improving application performance by 40%
- Technologies: Python, JavaScript, React, PostgreSQL

Junior Developer | StartupXYZ | 2016 - 2018
- Developed features for customer-facing web application
- Participated in code reviews and contributed to best practices
- Technologies: JavaScript, React, Node.js

EDUCATION
B.S. in Computer Science | State University | 2016
Relevant Coursework: Data Structures, Algorithms, Database Design, Web Development

CERTIFICATIONS
AWS Certified Solutions Architect - Associate (2022)
Google Cloud Professional Cloud Architect (2021)
"""

# Create sample job description
SAMPLE_JOB_DESCRIPTION = """
Job Title: Senior Full Stack Engineer

Company: Innovation Labs Inc.

About the Role:
We are seeking an experienced Senior Full Stack Engineer to join our team. You will be responsible for
designing and implementing scalable web applications, leading technical initiatives, and mentoring
junior developers.

Key Responsibilities:
- Design and develop full-stack web applications
- Build and maintain RESTful APIs
- Implement frontend solutions using modern frameworks
- Optimize application performance and scalability
- Lead code reviews and establish best practices
- Collaborate with product and design teams
- Mentor junior developers

Required Skills:
- 6+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React or Vue.js
- Backend framework experience (Django, FastAPI, Node.js)
- Database design and optimization (SQL)
- Cloud platforms (AWS, Google Cloud, or Azure)
- Docker and containerization
- Git and version control
- Strong communication and leadership skills

Preferred Skills:
- Kubernetes experience
- Microservices architecture
- Machine Learning basics
- DevOps practices
- GraphQL
- NoSQL databases

Nice to Have:
- Open source contributions
- Published technical articles
- Cloud certifications
- Agile/Scrum experience

Benefits:
- Competitive salary
- Health insurance
- Remote work options
- Professional development budget
"""


def test_simple_analysis():
    """Test the non-streaming analysis endpoint"""
    print("\n" + "="*80)
    print("TESTING SIMPLE ANALYSIS ENDPOINT")
    print("="*80 + "\n")
    
    url = "http://127.0.0.1:8000/analysis/analyze-simple"
    
    # Prepare form data
    files = {
        'file': ('sample_resume.txt', SAMPLE_RESUME, 'text/plain')
    }
    data = {
        'job_description': SAMPLE_JOB_DESCRIPTION
    }
    
    print("📤 Sending request to backend...")
    print(f"Resume length: {len(SAMPLE_RESUME)} characters")
    print(f"Job description length: {len(SAMPLE_JOB_DESCRIPTION)} characters\n")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print_analysis_results(result)
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout (300 seconds exceeded)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def print_analysis_results(result):
    """Pretty print the analysis results"""
    
    if result.get('status') == 'error':
        print(f"❌ Analysis Error: {result.get('error_message')}")
        return
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE - RESULTS")
    print("="*80 + "\n")
    
    # Step 1: Resume Upload
    print("📋 STEP 1: Resume Uploaded")
    step1 = result.get('step_1_resume_upload', {})
    print(f"   Size: {step1.get('size_chars', 'N/A')} characters\n")
    
    # Step 2: Resume Parsed
    print("📋 STEP 2: Resume Parsed")
    step2 = result.get('step_2_resume_parsed', {})
    print(f"   Cleaned: {step2.get('cleaned', False)}")
    print(f"   Sections Identified: {step2.get('sections_identified', 0)}\n")
    
    # Step 3: Skills Extracted
    print("📋 STEP 3: Skills Extracted")
    step3 = result.get('step_3_skills_extracted', {})
    skills = step3.get('skills', [])
    print(f"   Total Skills: {step3.get('total_skills', 0)}")
    print(f"   Top Skills: {', '.join(skills[:5])}")
    if len(skills) > 5:
        print(f"   ... and {len(skills) - 5} more skills\n")
    else:
        print()
    
    # Step 4: Experience Analyzed
    print("📋 STEP 4: Experience Analyzed")
    step4 = result.get('step_4_experience_analyzed', {})
    print(f"   Years of Experience: {step4.get('years', 'N/A')}")
    print(f"   Seniority Level: {step4.get('seniority_level', 'N/A')}")
    domains = step4.get('domains', [])
    if domains:
        print(f"   Domains: {', '.join(domains[:3])}")
    achievements = step4.get('key_achievements', [])
    if achievements:
        print(f"   Key Achievements: {achievements[0][:60]}...\n")
    else:
        print()
    
    # Step 5: Job Matching
    print("📋 STEP 5: Matching Against Job Description")
    step5 = result.get('step_5_job_matching', {})
    alignment = step5.get('alignment_score', 0)
    print(f"   ⭐ Alignment Score: {step5.get('alignment_percentage', 'N/A')}")
    print(f"   Matching Strength: {step5.get('matching_strength', 'N/A')}")
    matches = step5.get('top_matching_sections', [])
    if matches:
        print(f"   Top Matching Sections:")
        for match in matches[:3]:
            print(f"      - {match.get('section_title', 'N/A')}: {match.get('similarity_score', 0):.2f} similarity")
    print()
    
    # Step 6: Recommendations
    print("📋 STEP 6: Generating Recommendations")
    step6 = result.get('step_6_recommendations', {})
    missing = step6.get('missing_skills', [])
    improvements = step6.get('improvement_areas', [])
    actions = step6.get('priority_actions', [])
    
    print(f"   Missing Skills: {len(missing)} identified")
    if missing:
        print(f"      - {', '.join(missing[:3])}")
        if len(missing) > 3:
            print(f"      ... and {len(missing) - 3} more")
    print()
    
    print(f"   Improvement Areas: {len(improvements)} identified")
    if improvements:
        for i, area in enumerate(improvements[:2], 1):
            print(f"      {i}. {area[:70]}...")
    print()
    
    print(f"   Priority Actions: {len(actions)} actions")
    if actions:
        for i, action in enumerate(actions[:3], 1):
            print(f"      {i}. {action}")
    print()
    
    # Overall recommendation
    rec = step6.get('overall_recommendation', '')
    if rec:
        print(f"   Overall Recommendation:")
        print(f"   {rec[:100]}...")
    
    print("\n   Tailored Resume Suggestions:")
    tailored = step6.get('tailored_resume', {})
    headline = tailored.get('headline_suggestion', '')
    if headline:
        print(f"      Headline: {headline[:80]}")
    
    keywords = tailored.get('keywords_to_add', [])
    if keywords:
        print(f"      Keywords to Add: {', '.join(keywords[:5])}")
    
    print("\n" + "="*80)
    print("✅ END OF ANALYSIS REPORT")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🚀 SKILLSYNC RAG PIPELINE - TEST SCRIPT\n")
    success = test_simple_analysis()
    
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")

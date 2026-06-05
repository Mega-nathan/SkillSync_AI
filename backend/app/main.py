from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import resume

app = FastAPI(title="SkillSync AI")

@app.get('/')
async def root():
    return {"message":"Ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(resume.router)
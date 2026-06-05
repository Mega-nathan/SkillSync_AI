from fastapi import FastAPI

app = FastAPI(title="SkillSync AI")

@app.get('/')
async def root():
    return {"message":"Ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
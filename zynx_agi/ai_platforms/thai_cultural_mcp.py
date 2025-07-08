from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from ..config.settings import settings
from ..cultural.thai_cultural_engine import ThaiCulturalEngine

# Initialize FastAPI app
app = FastAPI(
    title="Thai Cultural MCP Server",
    description="Model Context Protocol Server for Thai Cultural Intelligence",
    version="1.0.0"
)

# Initialize Thai Cultural Engine
cultural_engine = ThaiCulturalEngine()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class CulturalAnalysisRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class CulturalAnalysisResponse(BaseModel):
    formality_level: float
    politeness_level: float
    cultural_elements: Dict[str, float]
    suggestions: List[str]
    detected_particles: List[str]
    cultural_patterns: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Authentication functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.exceptions.PyJWTError: # Corrected exception type
        raise credentials_exception
    return token_data

# MCP Endpoints
@app.post("/token")
async def login_for_access_token(username: str = Form(...), password: str = Form(...)): # Added Form(...)
    # In a real application, validate against a database
    if username != "admin" or password != "password":
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/cultural/analyze", response_model=CulturalAnalysisResponse)
async def analyze_cultural_context(
    request: CulturalAnalysisRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Analyze Thai cultural context of text"""
    try:
        # Analyze text using cultural engine
        formality = cultural_engine.analyze_formality(request.text)
        particles, politeness = cultural_engine.analyze_polite_particles(request.text)
        patterns = cultural_engine.detect_cultural_patterns(request.text)
        suggestions = cultural_engine.generate_cultural_suggestions(
            formality, politeness, patterns
        )
        
        return CulturalAnalysisResponse(
            formality_level=formality,
            politeness_level=politeness,
            cultural_elements=patterns,
            suggestions=suggestions,
            detected_particles=particles,
            cultural_patterns=list(patterns.keys())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/cultural/adjust")
async def adjust_cultural_context(
    request: CulturalAnalysisRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Adjust text based on cultural context"""
    try:
        adjusted_text = cultural_engine.adjust_response(
            request.text,
            target_formality=0.7,
            target_politeness=0.8
        )
        return {"adjusted_text": adjusted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP Resource endpoints
@app.get("/api/v1/cultural/resources", response_model=List[Dict[str, Any]])
async def get_cultural_resources(
    current_user: TokenData = Depends(get_current_user)
):
    """Get available cultural resources"""
    # Returning a list of dictionaries for more structured data
    resources = [
        {"type": "cultural_patterns", "data": cultural_engine.cultural_patterns},
        {"type": "formal_patterns", "data": cultural_engine.formal_patterns},
        {"type": "polite_particles", "data": cultural_engine.polite_particles}
    ]
    return resources

# MCP Prompt endpoints
@app.get("/api/v1/cultural/prompts", response_model=List[str])
async def get_cultural_prompts(
    current_user: TokenData = Depends(get_current_user)
):
    """Get available cultural prompts"""
    prompts = [
        "วิเคราะห์บริบททางวัฒนธรรมของข้อความ",
        "ปรับแต่งข้อความให้เหมาะสมกับบริบททางวัฒนธรรม",
        "ให้คำแนะนำในการปรับปรุงการสื่อสารทางวัฒนธรรม"
    ]
    return prompts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
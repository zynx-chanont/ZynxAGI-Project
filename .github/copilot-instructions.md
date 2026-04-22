# ZynxAGI - Universal AI Orchestration Platform

ZynxAGI is a Thai-English bilingual AI platform with cultural intelligence built using Python FastAPI backend and React TypeScript frontend. The system includes Deeja (ดีจ้า), a cultural-emotional AI agent that provides culturally-aware responses.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Agent Customization Workflow (onboarding)

- `AGENTS.md` describes system-level agent roles (Deeja, Dispatcher, Verifier, CodeD).
- `.github/agents/zynxagi-developer.agent.md` is the workspace agent used for code editing and internal tasks.
- For new agent customizations, create:
  - `.github/copilot-instructions.md` for global strategy and commands,
  - `.github/agents/<name>.agent.md` for context-aware behavior, or
  - `.github/skills/<name>/SKILL.md` for reusable workflows.
- Follow the “link, don’t embed” principle: reference existing docs (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`) in new instructions.
- Validate with `python -m pytest tests/ -v` and lints (`npx eslint` in frontend) after updates.

## Working Effectively

### Required Environment
- Python 3.8+ (validated with Python 3.12.3)
- Node.js 18+ (validated with Node.js 20.19.4) 
- npm 10+ (validated with npm 10.8.2)

### Bootstrap, Build, and Test the Repository
Run these commands in order, **NEVER CANCEL** long-running operations:

1. **Install Python dependencies** (takes ~3-4 minutes):
   ```bash
   pip install -r requirements.txt
   pip install pydantic-settings openai anthropic  # Additional required dependencies
   # Timeout: Use 5+ minutes for safety
   ```

2. **Install frontend dependencies** (takes ~10 seconds):
   ```bash
   cd frontend
   npm install
   npm install typescript-eslint @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/jest ts-jest
   # Timeout: Use 2+ minutes for safety
   ```

3. **Build frontend** (takes ~1-2 seconds):
   ```bash
   cd frontend
   npm run build
   # Timeout: Use 2+ minutes for safety
   ```

4. **Run Python tests** (takes ~1-2 seconds):
   ```bash
   python -m pytest tests/ -v
   # Timeout: Use 2+ minutes for safety
   # Expected: 10 tests should pass with some warnings
   ```

5. **Build everything with automation script** (takes ~8 seconds):
   ```bash
   chmod +x build.sh
   ./build.sh
   # Timeout: Use 2+ minutes for safety
   ```

### Run the Application

#### Start Backend Server:
```bash
# Start backend (takes ~2-3 seconds to start)
uvicorn zynx_agi.main:app --host 0.0.0.0 --port 8000 --reload
# Backend runs on: http://localhost:8000
# API Documentation: http://localhost:8000/docs
# Timeout: Use 2+ minutes for initial startup
```

#### Start Frontend Development Server:
```bash
# Start frontend (takes ~1-2 seconds to start)
cd frontend
npm run dev  
# Frontend runs on: http://localhost:5173
# Timeout: Use 2+ minutes for initial startup
```

## Validation Scenarios

**ALWAYS run through complete end-to-end scenarios after making changes:**

### Essential Test Scenarios:
1. **Backend Health Check**:
   ```bash
   curl -X GET "http://localhost:8000/health"
   # Expected: JSON response with status "healthy"
   ```

2. **English Chat Test**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   # Expected: English response from Deeja with cultural context
   ```

3. **Thai Cultural Intelligence Test**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Content-Type: application/json" \
     -d '{"message": "สวัสดีครับ"}'
   # Expected: Thai response with cultural markers and high politeness score
   ```

4. **Cultural Analysis Test**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/cultural/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Thank you very much", "context": {"formality": "casual"}}'
   # Expected: Cultural analysis with formality and politeness scores
   ```

5. **Frontend Access Test**:
   ```bash
   curl -X GET "http://localhost:5173/"
   # Expected: HTML response containing React application
   ```

## Linting and Code Quality

### Frontend Linting:
```bash
cd frontend
npx eslint .
# Known issues: Some unused variables in hooks and config files
# Always run before committing changes
```

### Fix Linting Issues:
The following lint warnings are expected and can be ignored:
- `useChat.ts`: Unused type imports (ChatRequest, ChatResponse, ChatError)
- `vite.config.ts`: Unused env variable

## Testing

### Python Backend Tests:
```bash
python -m pytest tests/ -v
# Expected: 10 tests pass (test_thai_cultural_mcp.py and test_universal_dispatcher.py)
# Runtime: ~1-2 seconds
# Some deprecation warnings are expected
```

### Frontend Tests:
```bash
cd frontend
npx jest
# Test framework is configured but may need test files updated
# Jest config includes coverage thresholds: 80% for all metrics
```

## Project Structure and Key Components

### Backend (Python FastAPI):
```
zynx_agi/
├── main.py              # FastAPI application entry point
├── config/settings.py   # Application configuration
├── api/                 # API endpoints
├── cultural/            # Cultural intelligence engine
├── ai_platforms/        # AI platform integrations (OpenAI, Claude)
├── security/            # Security and validation systems
└── agents/              # Agent framework (Deeja, CodeD, Verifier, Dispatcher)
```

### Frontend (React TypeScript):
```
frontend/
├── src/
│   ├── components/Chat/ # Chat interface components
│   └── hooks/useChat.ts # Chat functionality hook
├── package.json         # Dependencies and scripts
├── vite.config.ts       # Vite build configuration
└── jest.config.js       # Testing configuration
```

### Key Agent Architecture:
- **Deeja (ดีจ้า)**: Primary emotional AI with cultural intelligence (Live)
- **CodeD**: Coding assistant (Planned)
- **Verifier**: Fact-checking and validation (Planned)  
- **Dispatcher**: Central nervous system for agent coordination (Live)
- **Create Skill Agent Suite**: `/create-skill-agent` and `/create-skill` for generating and validating SKILL.md workflows (Live)

> NOTE: See `AGENTS.md` section "6. Create Skill Agent Suite" for details and example use cases.

## Environment Configuration

### Required Environment Variables:
Create `.env` file in root directory:
```env
# Optional API keys for AI platforms
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Cultural intelligence settings
THAI_CULTURAL_WEIGHT=0.8
DEFAULT_CULTURAL_THRESHOLD=0.7
```

## Common Issues and Solutions

### Missing Dependencies:
If you encounter import errors:
```bash
# Backend missing dependencies
pip install pydantic-settings openai anthropic

# Frontend missing dependencies  
cd frontend
npm install typescript-eslint @testing-library/react @testing-library/jest-dom
```

### Permission Issues:
```bash
# Make build script executable
chmod +x build.sh
```

### Build Failures:
- **CSS Import Warning**: Expected in Vite build process, does not affect functionality
- **ESLint Config Error**: Install `typescript-eslint` package
- **Test Collection Error**: Install missing AI platform dependencies

## Cultural Intelligence Features

### Supported Languages:
- **Thai**: Full cultural context including formality levels, politeness markers
- **English**: International communication style with cultural sensitivity

### Cultural Markers Detected:
- Thai: ครับ, ค่ะ, kreng_jai (consideration for others)
- Formality levels: formal, casual, friendly
- Politeness scoring: 0.0-1.0 scale

## API Endpoints Reference

### Core Endpoints:
- `GET /`: Welcome message and system status
- `GET /health`: Health check with component status
- `POST /api/v1/chat/message`: Chat with Deeja agent
- `POST /api/v1/cultural/analyze`: Analyze text for cultural context
- `GET /docs`: Swagger API documentation

### Expected Response Times:
- Health checks: < 50ms
- Chat messages: < 500ms  
- Cultural analysis: < 200ms

## Performance Expectations

### Build Times (with 50% safety buffer):
- Python dependency install: 5 minutes (actual ~3 minutes)
- Frontend dependency install: 2 minutes (actual ~10 seconds)
- Frontend build: 2 minutes (actual ~1 second)
- Complete build script: 2 minutes (actual ~8 seconds)
- Python tests: 2 minutes (actual ~1 second)

### Server Startup Times:
- Backend startup: 2 minutes (actual ~3 seconds)
- Frontend dev server: 2 minutes (actual ~2 seconds)

**CRITICAL: NEVER CANCEL builds or long-running commands. Always wait for completion and use the timeout values specified above.**

## Monitoring and Health

The application includes built-in monitoring:
- Component health tracking
- Cultural accuracy scoring
- Response time monitoring
- Thai language proficiency tracking

Monitor these during development to ensure cultural intelligence features are working correctly.
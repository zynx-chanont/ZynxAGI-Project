# ZynxAGI - สถาปัตยกรรมระบบโดยสมบูรณ์
# ZynxAGI - Complete System Architecture

**เวอร์ชั่น / Version:** 1.0.0  
**อัพเดทล่าสุด / Last Updated:** October 21, 2025  
**ผู้พัฒนา / Developer:** Chanont Wankaew

---

## สารบัญ / Table of Contents

1. [ภาพรวมระบบ / System Overview](#system-overview)
2. [หลักการออกแบบ / Design Principles](#design-principles)
3. [สถาปัตยกรรมระดับสูง / High-Level Architecture](#high-level-architecture)
4. [สถาปัตยกรรม Agent / Agent Architecture](#agent-architecture)
5. [สถาปัตยกรรม Backend / Backend Architecture](#backend-architecture)
6. [สถาปัตยกรรม Frontend / Frontend Architecture](#frontend-architecture)
7. [โครงสร้างข้อมูล / Data Architecture](#data-architecture)
8. [ความปลอดภัยและการเข้ารหัส / Security & Encryption](#security-encryption)
9. [การติดตามและตรวจสอบ / Monitoring & Observability](#monitoring-observability)
10. [การปรับใช้งาน / Deployment Architecture](#deployment-architecture)
11. [การไหลของข้อมูล / Data Flow](#data-flow)
12. [การบูรณาการ / Integration Points](#integration-points)
13. [ประสิทธิภาพและการปรับขนาด / Performance & Scalability](#performance-scalability)
14. [แผนงานอนาคต / Future Roadmap](#future-roadmap)

---

## 1. ภาพรวมระบบ / System Overview {#system-overview}

### ภาษาไทย

ZynxAGI เป็นแพลตฟอร์ม Universal AI Orchestration Platform ที่พัฒนาด้วย Python FastAPI (Backend) และ React TypeScript (Frontend) โดยมีจุดเด่นที่ระบบความฉลาดทางวัฒนธรรม (Cultural Intelligence) และความฉลาดทางอารมณ์ (Emotional Intelligence) โดยเฉพาะอย่างยิ่งการรองรับวัฒนธรรมไทยอย่างลึกซึ้ง

**วิสัยทัศน์หลัก:**
- สร้างสะพานเชื่อมระหว่างวัฒนธรรมไทยและสากลผ่าน AI
- พัฒนา AI ที่มีความเห็นอกเห็นใจ (Empathy-First Philosophy)
- รองรับการทำงานแบบ Multi-Agent Orchestration
- มุ่งเน้นความเป็นส่วนตัวและความปลอดภัยของข้อมูล

### English

ZynxAGI is a Universal AI Orchestration Platform developed with Python FastAPI (Backend) and React TypeScript (Frontend), featuring advanced Cultural Intelligence and Emotional Intelligence systems, with deep specialization in Thai cultural understanding.

**Core Vision:**
- Bridge Thai and international cultures through AI
- Develop AI with Empathy-First Philosophy
- Support Multi-Agent Orchestration
- Focus on privacy and data security

---

## 2. หลักการออกแบบ / Design Principles {#design-principles}

### ภาษาไทย

1. **Empathy-First (ความเห็นอกเห็นใจเป็นหลัก)**
   - ทุกการตอบสนองของระบบต้องมีความเข้าใจอารมณ์และบริบททางวัฒนธรรม
   - คำนวณคะแนนความเห็นอกเห็นใจ (Empathy Score) ในทุกการสื่อสาร

2. **Cultural Intelligence (ความฉลาดทางวัฒนธรรม)**
   - ตรวจจับและตอบสนองต่อ Cultural Markers ภาษาไทย (ครับ, ค่ะ, เกรงใจ, สนุก, ไม่เป็นไร)
   - ปรับระดับความสุภาพ (Formality Level) ตามบริบท
   - รักษาความเหมาะสมทางวัฒนธรรมในทุกการตอบสนอง

3. **Modular Agent System (ระบบ Agent แบบโมดูลาร์)**
   - Agent แต่ละตัวมีหน้าที่เฉพาะด้าน (Specialized Capabilities)
   - สื่อสารผ่าน Model Context Protocol (MCP)
   - Dispatcher ทำหน้าที่เป็นระบบประสาทกลาง (Central Nervous System)

4. **Privacy & Security First (ความเป็นส่วนตัวและความปลอดภัยเป็นลำดับแรก)**
   - เข้ารหัสข้อมูลสำคัญทั้งหมด
   - รองรับการทำงานแบบออฟไลน์
   - ไม่เก็บข้อมูลส่วนตัวโดยไม่ได้รับอนุญาต

5. **Ethical AI (AI ที่มีจริยธรรม)**
   - ตรวจสอบความเหมาะสมด้านจริยธรรมในทุกการตอบสนอง
   - รองรับค่านิยมทางพุทธศาสนาและวัฒนธรรมไทย
   - โปร่งใสและตรวจสอบได้

### English

1. **Empathy-First**
   - All system responses must demonstrate emotional and cultural understanding
   - Calculate Empathy Score in every interaction

2. **Cultural Intelligence**
   - Detect and respond to Thai cultural markers (ครับ, ค่ะ, kreng_jai, sanuk, mai_pen_rai)
   - Adjust formality levels based on context
   - Maintain cultural appropriateness in all responses

3. **Modular Agent System**
   - Each agent has specialized capabilities
   - Communication through Model Context Protocol (MCP)
   - Dispatcher acts as Central Nervous System

4. **Privacy & Security First**
   - Encrypt all sensitive data
   - Support offline operation
   - Never store personal data without consent

5. **Ethical AI**
   - Verify ethical appropriateness in all responses
   - Support Buddhist values and Thai culture
   - Transparent and auditable

---

## 3. สถาปัตยกรรมระดับสูง / High-Level Architecture {#high-level-architecture}

### ภาษาไทย

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│              React TypeScript + Vite (Port 5173)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Chat UI    │  │ Cultural UI  │  │  Admin UI    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / FastAPI                       │
│                        (Port 8000)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   /api/v1/   │  │   /health    │  │    /docs     │         │
│  │   chat       │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MCP Dispatcher (Central Router)                 │
│          Model Context Protocol - Central Nervous System         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Slash Command Parser: /agent:action                       │ │
│  │  Pipeline Parser: command1 | command2                      │ │
│  │  Capability Router: Maps requests to agents               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Deeja Agent     │ │  Zynx Main Agent │ │ Metadata Agent   │
│  (ดีจ้า)         │ │                  │ │                  │
│  🟢 Live         │ │  🟢 Live         │ │  🟢 Live         │
│                  │ │                  │ │                  │
│ - Cultural AI    │ │ - General Chat   │ │ - Compliance     │
│ - Emotional AI   │ │ - Orchestration  │ │ - Metadata Mgmt  │
│ - Empathy Score  │ │ - Session Mgmt   │ │ - Governance     │
│ - Translation    │ │ - Coordination   │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Cultural    │  │  Security    │  │   Storage    │         │
│  │  Engine      │  │  Encryption  │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  AI Platforms    │ │  Data Storage    │ │   Monitoring     │
│                  │ │                  │ │                  │
│ - OpenAI         │ │ - PostgreSQL     │ │ - Metrics        │
│ - Claude         │ │ - Redis          │ │ - Health Checks  │
│ - Thai MCP       │ │ - File Storage   │ │ - Dashboards     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### English

The architecture follows a layered approach with clear separation of concerns:

1. **Frontend Layer**: User interface built with React TypeScript
2. **API Gateway**: FastAPI handling REST endpoints
3. **Orchestration Layer**: MCP Dispatcher routing requests
4. **Agent Layer**: Specialized AI agents with distinct capabilities
5. **Core Services**: Shared services (Cultural Engine, Security, Storage)
6. **Integration Layer**: External AI platforms and data storage

---

## 4. สถาปัตยกรรม Agent / Agent Architecture {#agent-architecture}

### ภาษาไทย

ระบบ ZynxAGI ใช้สถาปัตยกรรม Multi-Agent โดยแต่ละ Agent มีความเชี่ยวชาญเฉพาะด้าน

#### 4.1 Deeja Agent (ดีจ้า) 🟢 Live

**บทบาท:** AI หลักที่มีความฉลาดทางอารมณ์และวัฒนธรรม

**ความสามารถหลัก (Capabilities):**
- `CULTURAL_ANALYSIS`: วิเคราะห์บริบททางวัฒนธรรม
- `EMOTIONAL_INTELLIGENCE`: ตรวจจับและตอบสนองอารมณ์
- `EMPATHY_SCORING`: คำนวณคะแนนความเห็นอกเห็นใจ
- `TRANSLATION`: แปลภาษาพร้อมรักษาบริบททางวัฒนธรรม
- `CHAT`: สนทนาแบบมีความเข้าใจทางอารมณ์

**Thai Cultural Intelligence:**
```python
# Thai Cultural Markers Detection
thai_cultural_markers = {
    "kreng_jai": ["เกรงใจ", "กรุณา", "ขอโทษ", "รบกวน"],
    "sanuk": ["สนุก", "เล่น", "สบาย", "ผ่อนคลาย"],
    "mai_pen_rai": ["ไม่เป็นไร", "ไม่มีปัญหา", "ช่างมัน"],
    "bun_khun": ["บุญคุณ", "ขอบคุณ", "ขอบใจ", "กตัญญู"]
}

# Empathy Score Calculation
empathy_score = (
    emotional_awareness * 0.3 +
    cultural_sensitivity * 0.3 +
    response_appropriateness * 0.2 +
    thai_cultural_context * 0.2
)
```

**Ethical Framework:**
- หลักการเคารพบุคคล (Respect for Persons)
- หลักการเมตตา (Beneficence)
- หลักการไม่ทำร้าย (Non-maleficence)
- หลักความยุติธรรม (Justice)
- ความเหมาะสมทางวัฒนธรรม (Cultural Sensitivity)

**Thai Values Integration:**
- Kreng Jai Respect (ความเกรงใจ)
- Sanuk Positivity (ความสนุกสนาน)
- Mai Pen Rai Acceptance (การยอมรับ)
- Family Harmony (ความสามัคคีในครอบครัว)
- Buddhist Compassion (ความเมตตาแบบพุทธ)

**File Location:** `/zynx_agi/agents/deeja_agent.py`

#### 4.2 MCP Dispatcher 🟢 Live

**บทบาท:** ระบบประสาทกลางที่จัดการการส่งต่อคำขอไปยัง Agent ที่เหมาะสม

**ความสามารถหลัก:**
- **Slash Command Parsing:** `/agent:action params`
  ```
  /deeja:analyze สวัสดีครับ
  /cultural:check ข้อความนี้
  ```

- **Pipeline Execution:** `command1 | command2`
  ```
  /deeja:analyze text | /verifier:check
  ```

- **Content-Based Routing:**
  - ตรวจจับภาษาไทย → Route to Deeja
  - ตรวจจับอารมณ์ → Route to Deeja
  - ตรวจจับคำถามเกี่ยวกับ compliance → Route to Metadata Agent

**Routing Table:**
```python
agent_routing = {
    "zynx": "zynx_main",
    "deeja": "deeja",
    "metadata": "zynx_metadata",
    "cultural": "deeja",
    "emotional": "deeja",
    "compliance": "zynx_metadata"
}
```

**Orchestration Types:**
- Single Agent Execution
- Multi-Agent Coordination
- Pipeline Processing
- Workflow Management

**File Location:** `/zynx_agi/agents/mcp_dispatcher.py`

#### 4.3 Zynx Main Agent 🟢 Live

**บทบาท:** Agent หลักสำหรับการสนทนาทั่วไปและการประสานงาน

**ความสามารถหลัก:**
- General conversation handling
- Session management
- Agent coordination
- System orchestration

**File Location:** `/zynx_agi/agents/zynx_main_agent.py`

#### 4.4 Metadata Agent 🟢 Live

**บทบาท:** จัดการ metadata, compliance และ governance

**ความสามารถหลัก:**
- Metadata management
- Compliance monitoring
- Data governance
- License verification

**File Location:** `/zynx_agi/agents/metadata_agent.py`

#### 4.5 Planned Agents 🟡

**CodeD** (Planned)
- Code generation
- Debugging assistance
- Technical documentation
- Code optimization

**Verifier** (Planned)
- Fact-checking
- Information validation
- Ethical compliance verification
- Output quality control

### English

The ZynxAGI system uses a Multi-Agent Architecture where each agent has specialized expertise.

**Key Agent Features:**
- **Modular Design:** Each agent is independent and reusable
- **MCP Communication:** Standardized communication protocol
- **Capability-Based Routing:** Requests routed based on capabilities
- **Collaborative Processing:** Agents can work together on complex tasks

**Base Agent Class:**
All agents inherit from `ZynxAgent` base class providing:
- Standard request/response handling
- Capability registration
- Storage integration
- Metrics tracking
- Health monitoring

---

## 5. สถาปัตยกรรม Backend / Backend Architecture {#backend-architecture}

### ภาษาไทย

#### 5.1 โครงสร้างหลัก (Core Structure)

```
zynx_agi/
├── main.py                    # FastAPI application entry point
├── config/
│   └── settings.py           # Configuration management
├── api/                       # API endpoints
│   ├── chat.py               # Chat endpoints
│   └── cultural.py           # Cultural analysis endpoints
├── agents/                    # Agent system
│   ├── base_agent.py         # Base agent class
│   ├── deeja_agent.py        # Deeja implementation
│   ├── mcp_dispatcher.py     # MCP dispatcher
│   ├── zynx_main_agent.py    # Main agent
│   └── metadata_agent.py     # Metadata agent
├── cultural/                  # Cultural intelligence
│   └── thai_cultural_engine.py
├── ai_platforms/             # AI platform integrations
│   ├── openai_client.py      # OpenAI integration
│   ├── claude_client.py      # Anthropic Claude
│   └── thai_cultural_mcp.py  # Thai cultural MCP
├── core/                      # Core services
│   ├── universal_dispatcher.py
│   └── session_manager.py
├── security/                  # Security layer
│   └── encryption.py
├── storage/                   # Storage management
│   ├── drivers.py
│   ├── artifact_manager.py
│   └── session_exporter.py
├── monitoring/               # Monitoring system
│   ├── integration.py
│   ├── middleware.py
│   └── api_endpoints.py
└── ecosystem/                # Ecosystem management
    ├── ecosystem_manager.py
    └── deployment_config.py
```

#### 5.2 API Endpoints

**Core Endpoints:**
```
GET  /                        # Welcome message
GET  /health                  # Health check
GET  /docs                    # Swagger API documentation
POST /api/v1/chat/message     # Chat with Deeja
POST /api/v1/cultural/analyze # Cultural analysis
```

**Response Format:**
```json
{
  "message": "สวัสดีค่ะ! ยินดีต้อนรับ",
  "aiPlatform": "deeja",
  "culturalContext": {
    "primaryCulture": "thai",
    "formalityLevel": "casual",
    "politenessLevel": 0.9,
    "culturalMarkers": ["ค่ะ", "kreng_jai"]
  },
  "culturalAccuracyScore": 0.95,
  "emotionalIntelligenceScore": 0.88,
  "processingTime": 0.5
}
```

#### 5.3 Cultural Intelligence Engine

**Thai Cultural Engine:**
- **Language Detection:** ตรวจจับอักขระไทย (U+0E00 - U+0E7F)
- **Formality Analysis:** วิเคราะห์ระดับความสุภาพจากคำอนุภาค
- **Cultural Marker Detection:** ตรวจจับเครื่องหมายทางวัฒนธรรม
- **Context Determination:** กำหนดบริบท (formal/casual/intimate)

**Politeness Scoring:**
```python
# Detect politeness particles
polite_particles = ["ครับ", "ค่ะ", "คะ", "จ้ะ"]
formal_pronouns = ["กระผม", "ดิฉัน", "ท่าน"]

# Calculate politeness level
politeness_score = (
    particle_count * 0.4 +
    pronoun_formality * 0.3 +
    cultural_marker_presence * 0.3
)
```

**File Location:** `/zynx_agi/cultural/thai_cultural_engine.py`

#### 5.4 AI Platform Integration

**Supported Platforms:**
1. **OpenAI GPT** - General purpose AI
2. **Anthropic Claude** - Advanced reasoning
3. **Thai Cultural MCP** - Thai-specific AI

**Integration Pattern:**
```python
class AIClientBase:
    async def send_message(self, message: str) -> dict
    async def stream_message(self, message: str)
    async def analyze_sentiment(self, text: str) -> dict
```

#### 5.5 Security & Encryption

**Encryption System:**
- AES-256 encryption for sensitive data
- JWT tokens for authentication
- Secure session management
- Data privacy compliance (PDPA/GDPR)

**File Location:** `/zynx_agi/security/encryption.py`

#### 5.6 Storage Architecture

**Storage Drivers:**
- **File System Driver:** Local storage
- **Database Driver:** PostgreSQL
- **Redis Driver:** Caching and sessions
- **Artifact Manager:** File artifact management

**Session Management:**
- Session creation and lifecycle
- Session export functionality
- Artifact storage and retrieval

**File Locations:**
- `/zynx_agi/storage/drivers.py`
- `/zynx_agi/storage/session_exporter.py`
- `/zynx_agi/storage/artifact_manager.py`

### English

#### Backend Technology Stack

**Core Framework:**
- **FastAPI:** Modern async web framework
- **Uvicorn:** ASGI server
- **Pydantic:** Data validation

**AI/ML Libraries:**
- OpenAI SDK
- Anthropic SDK
- Transformers (HuggingFace)
- NLTK/spaCy for NLP

**Data & Storage:**
- PostgreSQL: Primary database
- Redis: Caching and sessions
- SQLAlchemy: ORM

**Security:**
- python-jose: JWT tokens
- cryptography: Encryption
- passlib: Password hashing

---

## 6. สถาปัตยกรรม Frontend / Frontend Architecture {#frontend-architecture}

### ภาษาไทย

#### 6.1 โครงสร้าง Frontend

```
frontend/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main application component
│   ├── components/           # React components
│   │   └── Chat/             # Chat interface
│   │       ├── ChatContainer.tsx
│   │       ├── ChatMessage.tsx
│   │       └── ChatInput.tsx
│   ├── hooks/                # Custom React hooks
│   │   └── useChat.ts        # Chat functionality hook
│   ├── services/             # API services
│   │   └── api.ts            # API client
│   ├── types/                # TypeScript types
│   │   └── chat.ts           # Chat type definitions
│   └── assets/               # Static assets
├── public/                   # Public assets
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript config
└── package.json             # Dependencies
```

#### 6.2 Technology Stack

**Core Framework:**
- React 18.2.0 (Latest stable)
- TypeScript 5.2.2
- Vite 5.0.8 (Build tool)

**UI Components:**
- Custom React components
- react-hot-toast for notifications
- CSS3 for styling

**Development Tools:**
- ESLint for code quality
- TypeScript for type safety
- Jest & Testing Library for tests

#### 6.3 Chat Interface

**Features:**
- Real-time messaging
- Cultural context display
- Empathy score visualization
- Thai-English bilingual support
- Typing indicators
- Message history

**useChat Hook:**
```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  culturalContext?: CulturalContext;
  empathyScore?: number;
  timestamp: Date;
}

const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const sendMessage = async (content: string) => {
    // Send to backend API
    // Update message state
    // Handle cultural context
  };
  
  return { messages, sendMessage, isLoading };
};
```

#### 6.4 API Integration

**API Client:**
```typescript
class ZynxAPIClient {
  private baseURL = 'http://localhost:8000';
  
  async sendChatMessage(message: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  }
  
  async analyzeCulture(text: string): Promise<CulturalAnalysis> {
    const response = await fetch(`${this.baseURL}/api/v1/cultural/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return response.json();
  }
}
```

### English

#### Frontend Features

**Real-time Chat:**
- Instant messaging with AI agents
- WebSocket support (planned)
- Message streaming (planned)

**Cultural Intelligence Display:**
- Visual representation of cultural context
- Empathy score indicators
- Politeness level display
- Cultural marker highlighting

**Responsive Design:**
- Mobile-first approach
- Desktop optimization
- Cross-browser compatibility

**Performance Optimization:**
- Code splitting
- Lazy loading
- Optimized bundle size
- Fast initial load

---

## 7. โครงสร้างข้อมูล / Data Architecture {#data-architecture}

### ภาษาไทย

#### 7.1 Database Schema (PostgreSQL)

**Tables:**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    cultural_context JSONB,
    empathy_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cultural interactions log
CREATE TABLE cultural_interactions (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100),
    language_detected VARCHAR(10),
    cultural_markers JSONB,
    empathy_score FLOAT,
    formality_level FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent metrics
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100),
    capability VARCHAR(100),
    execution_count INTEGER,
    avg_processing_time FLOAT,
    success_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 7.2 Redis Data Structures

**Session Storage:**
```
session:{session_id} -> {
  "user_id": "uuid",
  "started_at": "timestamp",
  "last_activity": "timestamp",
  "context": {...}
}
```

**Cache:**
```
cache:cultural_analysis:{text_hash} -> {
  "analysis": {...},
  "expires_at": "timestamp"
}
```

**Rate Limiting:**
```
rate_limit:{user_id}:{endpoint} -> counter
```

#### 7.3 Data Models (Pydantic)

**Chat Request:**
```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
```

**Cultural Context:**
```python
class CulturalContext(BaseModel):
    primary_culture: str
    language: str
    formality_level: str
    politeness_level: float
    cultural_markers: List[str]
    communication_style: str
```

**Agent Response:**
```python
class AgentResponse(BaseModel):
    success: bool
    agent_id: str
    response_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str
    processing_time_ms: Optional[float] = None
```

### English

#### Data Flow

1. **User Input** → Frontend
2. **API Request** → FastAPI Backend
3. **Request Validation** → Pydantic Models
4. **Routing** → MCP Dispatcher
5. **Agent Processing** → Deeja/Other Agents
6. **Storage** → PostgreSQL/Redis
7. **Response** → Frontend

#### Data Retention

- **Session Data:** 30 days
- **Message History:** 90 days
- **Cultural Metrics:** 1 year
- **Agent Performance:** Indefinite

---

## 8. ความปลอดภัยและการเข้ารหัส / Security & Encryption {#security-encryption}

### ภาษาไทย

#### 8.1 Security Layers

**1. Transport Layer Security**
- HTTPS/TLS 1.3
- Certificate pinning (planned)
- Secure WebSocket (WSS)

**2. Authentication & Authorization**
- JWT tokens (HS256/RS256)
- OAuth2 support (planned)
- Session-based auth
- API key authentication

**3. Data Encryption**
- AES-256-GCM for data at rest
- End-to-end encryption (planned)
- Field-level encryption for sensitive data

**4. Input Validation**
- Pydantic data validation
- SQL injection prevention
- XSS protection
- CSRF tokens

**5. Privacy Protection**
- PDPA compliance (Thai law)
- GDPR compliance (EU law)
- Data anonymization
- Right to deletion

#### 8.2 Encryption Implementation

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class ZynxEncryption:
    def __init__(self, master_key: bytes):
        self.cipher_suite = Fernet(master_key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive user data"""
        decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()
```

#### 8.3 Security Best Practices

**Environment Variables:**
```bash
# .env file (never commit to git)
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

**CORS Configuration:**
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://zynxdata.com",
    "https://www.zynxdata.com"
]
```

### English

#### Security Features

**Rate Limiting:**
- Per-user rate limits
- Per-endpoint throttling
- DDoS protection

**Audit Logging:**
- All API requests logged
- Security events tracked
- Compliance monitoring

**Data Privacy:**
- No personal data stored without consent
- User data deletion on request
- Privacy-first architecture

---

## 9. การติดตามและตรวจสอบ / Monitoring & Observability {#monitoring-observability}

### ภาษาไทย

#### 9.1 Health Monitoring

**Health Check Endpoint:**
```json
GET /health

{
  "status": "healthy",
  "app": "ZynxAGI",
  "version": "1.0.0",
  "components": {
    "api": "healthy",
    "cultural_intelligence": "ready",
    "universal_dispatcher": "ready",
    "database": "connected",
    "redis": "connected"
  },
  "uptime": 3600,
  "timestamp": "2025-10-21T08:34:22Z"
}
```

#### 9.2 Metrics Collection

**Agent Performance Metrics:**
```python
agent_metrics = {
    "agent_id": "deeja",
    "total_requests": 1000,
    "successful_requests": 950,
    "failed_requests": 50,
    "avg_response_time_ms": 250,
    "empathy_score_avg": 0.85,
    "cultural_accuracy_avg": 0.92
}
```

**Cultural Intelligence Metrics:**
```python
cultural_metrics = {
    "thai_interactions": 600,
    "english_interactions": 400,
    "cultural_marker_detection_rate": 0.95,
    "formality_classification_accuracy": 0.88,
    "empathy_score_distribution": {
        "0.0-0.3": 50,
        "0.3-0.7": 200,
        "0.7-1.0": 750
    }
}
```

#### 9.3 Monitoring Dashboard

**Key Metrics Displayed:**
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate
- Agent success rate
- Cultural accuracy score
- Empathy score trends
- System resource usage

**Dashboard Technology:**
- Custom React dashboard
- Real-time metrics
- Historical trends
- Alert notifications

**File Location:** `/zynx_agi/monitoring/`

#### 9.4 Logging

**Log Levels:**
- DEBUG: Development debugging
- INFO: General information
- WARNING: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical failures

**Log Format:**
```json
{
  "timestamp": "2025-10-21T08:34:22.194Z",
  "level": "INFO",
  "logger": "zynx_agi.agents.deeja",
  "message": "Cultural analysis completed",
  "extra": {
    "session_id": "uuid",
    "empathy_score": 0.85,
    "cultural_context": "thai_casual"
  }
}
```

### English

#### Monitoring Features

**Real-time Monitoring:**
- Live request tracking
- Performance metrics
- Error tracking
- Cultural intelligence analytics

**Alerting:**
- High error rate alerts
- Performance degradation
- System health issues
- Cultural accuracy drops

**Analytics:**
- Usage patterns
- Cultural distribution
- Agent performance
- User behavior

---

## 10. การปรับใช้งาน / Deployment Architecture {#deployment-architecture}

### ภาษาไทย

#### 10.1 Deployment Options

**1. Docker Compose (Development/Staging)**
```yaml
version: '3.8'
services:
  zynx-agi:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: zynxagi
      POSTGRES_USER: zynx
      POSTGRES_PASSWORD: zynxpass
  
  redis:
    image: redis:7-alpine
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

**2. Kubernetes (Production)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zynx-agi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zynx-agi
  template:
    metadata:
      labels:
        app: zynx-agi
    spec:
      containers:
      - name: zynx-agi
        image: zynx-agi:1.0.0
        ports:
        - containerPort: 8000
```

#### 10.2 Infrastructure Components

**Load Balancer:**
- Nginx/HAProxy
- SSL termination
- Request routing
- Health check probes

**Database:**
- PostgreSQL 15
- Replication (master-slave)
- Automated backups
- Point-in-time recovery

**Cache Layer:**
- Redis cluster
- Session storage
- Cache invalidation
- Pub/Sub for events

**File Storage:**
- Local filesystem
- S3-compatible storage (planned)
- Artifact management
- Backup storage

#### 10.3 Scaling Strategy

**Horizontal Scaling:**
- Multiple backend instances
- Load balancing
- Stateless design
- Session stored in Redis

**Vertical Scaling:**
- Increased resources per instance
- Database optimization
- Cache tuning

**Auto-scaling:**
- CPU-based scaling
- Request rate scaling
- Scheduled scaling

#### 10.4 Environments

**Development:**
- Local Docker setup
- Hot reload enabled
- Debug logging
- Sample data

**Staging:**
- Production-like environment
- Integration testing
- Performance testing
- Security scanning

**Production:**
- High availability
- Monitoring enabled
- Automated backups
- Disaster recovery

### English

#### Deployment Workflow

1. **Code Push** → Git repository
2. **CI/CD Pipeline** → GitHub Actions
3. **Build** → Docker images
4. **Test** → Automated tests
5. **Deploy** → Kubernetes/Docker
6. **Monitor** → Health checks

#### Infrastructure Requirements

**Minimum Requirements:**
- 2 CPU cores
- 4 GB RAM
- 20 GB storage
- PostgreSQL 15+
- Redis 7+

**Recommended Production:**
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB storage
- Load balancer
- CDN for static files

---

## 11. การไหลของข้อมูล / Data Flow {#data-flow}

### ภาษาไทย

#### 11.1 Chat Message Flow

```
1. User Input
   ↓
2. Frontend (React)
   └─ Validation
   └─ State Update
   ↓
3. HTTP POST /api/v1/chat/message
   ↓
4. FastAPI Gateway
   └─ CORS Check
   └─ Request Validation
   └─ Authentication (if required)
   ↓
5. MCP Dispatcher
   └─ Parse Request
   └─ Detect Language (Thai/English)
   └─ Route to Appropriate Agent
   ↓
6. Deeja Agent
   └─ Cultural Analysis
   │  ├─ Language Detection
   │  ├─ Formality Level
   │  ├─ Thai Markers
   │  └─ Context Determination
   └─ Emotional Analysis
   │  ├─ Sentiment Detection
   │  ├─ Emotion Recognition
   │  └─ Empathy Requirements
   └─ Empathy Score Calculation
   └─ Ethical Reasoning
   └─ Response Generation
   ↓
7. Storage Layer
   └─ Save Message (PostgreSQL)
   └─ Update Session (Redis)
   └─ Log Interaction
   ↓
8. Response Processing
   └─ Format Response
   └─ Add Metadata
   └─ Cultural Context
   ↓
9. Return to Frontend
   ↓
10. UI Update
    └─ Display Message
    └─ Show Cultural Context
    └─ Empathy Score Visualization
```

#### 11.2 Cultural Analysis Flow

```
Input: "สวัสดีครับ ผมมีคำถามอยากถามค่ะ"
   ↓
1. Language Detection
   Result: Thai (detected U+0E00-U+0E7F characters)
   ↓
2. Cultural Marker Detection
   Found: ["ครับ", "ค่ะ"] - Polite particles
   ↓
3. Formality Analysis
   Formal indicators: ครับ, ค่ะ
   Result: Formality Level = 0.8 (Formal)
   ↓
4. Context Determination
   Context: "formal_business"
   ↓
5. Politeness Scoring
   Score: 0.9 (High politeness)
   ↓
6. Cultural Context Assembly
   {
     "primaryCulture": "thai",
     "formalityLevel": "formal",
     "politenessLevel": 0.9,
     "culturalMarkers": ["ครับ", "ค่ะ"],
     "communicationStyle": "thai_polite"
   }
   ↓
7. Empathy Score Calculation
   Base: 0.5
   + Cultural Sensitivity: 0.3
   + Thai Context Boost: 0.3
   = Final Score: 0.88
   ↓
8. Response Generation
   Generate culturally appropriate Thai response
   with matching formality level
```

### English

#### Agent Collaboration Flow

When multiple agents work together:

```
User Request: "Analyze this Thai text for cultural context and compliance"
   ↓
MCP Dispatcher
   ├─ Route to Deeja (Cultural Analysis)
   │  └─ Perform cultural analysis
   │  └─ Calculate empathy score
   │  └─ Return analysis
   └─ Route to Metadata Agent (Compliance)
      └─ Check compliance
      └─ Verify ethical standards
      └─ Return compliance report
   ↓
Orchestrate Responses
   └─ Combine results
   └─ Add coordination metadata
   ↓
Return Unified Response
```

---

## 12. การบูรณาการ / Integration Points {#integration-points}

### ภาษาไทย

#### 12.1 External AI Platforms

**OpenAI Integration:**
```python
from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def send_message(self, message: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
```

**Anthropic Claude Integration:**
```python
from anthropic import Anthropic

class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
    
    async def send_message(self, message: str) -> str:
        message = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}]
        )
        return message.content[0].text
```

#### 12.2 Database Integration

**PostgreSQL:**
- SQLAlchemy ORM
- Async support with asyncpg
- Connection pooling
- Migration management with Alembic

**Redis:**
- aioredis for async operations
- Session storage
- Cache management
- Pub/Sub messaging

#### 12.3 Frontend-Backend Integration

**REST API:**
```typescript
// Frontend API client
const apiClient = {
  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await fetch('/api/v1/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  }
};
```

**WebSocket (Planned):**
```typescript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

#### 12.4 Monitoring Integration

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram

# Request counter
request_counter = Counter(
    'zynx_requests_total',
    'Total requests',
    ['agent', 'endpoint']
)

# Response time histogram
response_time = Histogram(
    'zynx_response_time_seconds',
    'Response time',
    ['agent']
)
```

### English

#### Integration Patterns

**Service Layer Pattern:**
- Clear separation between API and business logic
- Reusable service components
- Easy testing

**Repository Pattern:**
- Abstract data access
- Multiple storage backends
- Consistent interface

**Factory Pattern:**
- Dynamic agent creation
- Configuration-based initialization
- Extensibility

---

## 13. ประสิทธิภาพและการปรับขนาด / Performance & Scalability {#performance-scalability}

### ภาษาไทย

#### 13.1 Performance Optimization

**Backend Optimization:**
- Async/await throughout
- Connection pooling
- Query optimization
- Caching strategy
- Lazy loading

**Frontend Optimization:**
- Code splitting
- Lazy component loading
- Memoization
- Virtual scrolling (planned)
- Service workers (planned)

**Database Optimization:**
- Indexed queries
- Query result caching
- Connection pooling
- Read replicas

**Caching Strategy:**
```python
# Multi-level caching
L1: In-memory cache (per instance)
L2: Redis cache (shared)
L3: Database query cache

# Cache invalidation
- Time-based expiration
- Event-based invalidation
- LRU eviction policy
```

#### 13.2 Performance Metrics

**Target Performance:**
- API Response Time: < 200ms (p95)
- Chat Response Time: < 500ms (p95)
- Cultural Analysis: < 100ms
- Empathy Scoring: < 50ms
- Database Query: < 50ms
- Page Load Time: < 2s

**Current Performance:**
- Health Check: < 50ms
- Chat Messages: < 500ms
- Cultural Analysis: < 200ms
- Frontend Load: < 2s

#### 13.3 Scalability Patterns

**Stateless Design:**
- No server-side session state
- All state in Redis/Database
- Easy horizontal scaling

**Load Distribution:**
- Round-robin load balancing
- Sticky sessions (if needed)
- Geographic distribution (planned)

**Database Scaling:**
- Read replicas
- Sharding (planned)
- Partitioning (planned)

**Cache Scaling:**
- Redis cluster
- Distributed caching
- Cache warming

#### 13.4 Resource Requirements

**Per Instance:**
```yaml
Development:
  CPU: 1 core
  Memory: 2 GB
  Storage: 10 GB

Production:
  CPU: 2-4 cores
  Memory: 4-8 GB
  Storage: 50-100 GB
```

**Expected Capacity:**
- 1000 concurrent users per instance
- 100 requests/second per instance
- 10,000 messages per day per instance

### English

#### Performance Monitoring

**Key Performance Indicators (KPIs):**
- Requests per second (RPS)
- Average response time
- Error rate
- Database connections
- Cache hit rate
- CPU/Memory usage

**Performance Testing:**
- Load testing with Locust
- Stress testing
- Endurance testing
- Spike testing

**Optimization Techniques:**
- Query optimization
- Index optimization
- Caching improvements
- Code profiling
- Resource monitoring

---

## 14. แผนงานอนาคต / Future Roadmap {#future-roadmap}

### ภาษาไทย

#### Phase 1: Foundation Enhancement (Q4 2025)
- ✅ Core agent system (Deeja, Dispatcher)
- ✅ Thai cultural intelligence
- ✅ Basic chat interface
- 🔄 Enhanced UI/UX
- 🔄 RAG integration
- 🔄 Timeline viewer

#### Phase 2: Agent Expansion (Q1 2026)
- 🟡 CodeD agent implementation
- 🟡 Verifier agent implementation
- 🟡 Advanced multi-agent workflows
- 🟡 Enhanced cultural markers
- 🟡 Voice input support (planned)
- 🟡 Multi-language support expansion

#### Phase 3: Platform Maturity (Q2 2026)
- 🟡 WebSocket support
- 🟡 Real-time collaboration
- 🟡 Advanced analytics dashboard
- 🟡 Mobile applications
- 🟡 Plugin system
- 🟡 Marketplace for agents

#### Phase 4: Ecosystem Growth (Q3-Q4 2026)
- 🟡 Third-party integrations
- 🟡 Developer API
- 🟡 Community agents
- 🟡 Enterprise features
- 🟡 White-label solution
- 🟡 Global expansion

### English

#### Technical Improvements

**Short Term:**
- Performance optimization
- Test coverage increase
- Documentation enhancement
- Bug fixes
- Security hardening

**Medium Term:**
- GraphQL API
- Streaming responses
- Advanced caching
- Microservices architecture
- Kubernetes native

**Long Term:**
- AI model fine-tuning
- Custom Thai language models
- Edge computing support
- Blockchain integration (for transparency)
- Advanced privacy features

---

## ภาคผนวก / Appendix

### A. Technology Stack Summary

**Backend:**
- Python 3.8+
- FastAPI
- PostgreSQL 15
- Redis 7
- SQLAlchemy
- Pydantic

**Frontend:**
- React 18.2
- TypeScript 5.2
- Vite 5.0
- Jest
- ESLint

**AI/ML:**
- OpenAI GPT
- Anthropic Claude
- HuggingFace Transformers
- NLTK/spaCy

**Infrastructure:**
- Docker
- Docker Compose
- Kubernetes (planned)
- Nginx
- GitHub Actions

### B. File Structure Reference

**Key Backend Files:**
```
zynx_agi/
├── main.py                     # FastAPI app entry
├── agents/
│   ├── deeja_agent.py         # Deeja implementation
│   ├── mcp_dispatcher.py      # MCP dispatcher
│   └── base_agent.py          # Base agent class
├── cultural/
│   └── thai_cultural_engine.py # Thai cultural engine
├── api/
│   ├── chat.py                # Chat endpoints
│   └── cultural.py            # Cultural endpoints
└── config/
    └── settings.py            # Configuration
```

**Key Frontend Files:**
```
frontend/src/
├── App.tsx                    # Main app component
├── components/Chat/           # Chat components
├── hooks/useChat.ts          # Chat hook
└── services/api.ts           # API client
```

### C. API Reference

**Chat API:**
```
POST /api/v1/chat/message
Request: { "message": "string" }
Response: {
  "message": "string",
  "aiPlatform": "string",
  "culturalContext": {...},
  "empathyScore": number
}
```

**Cultural Analysis API:**
```
POST /api/v1/cultural/analyze
Request: { "text": "string" }
Response: {
  "primaryCulture": "string",
  "formalityLevel": "string",
  "politenessLevel": number,
  "culturalMarkers": ["string"]
}
```

### D. Configuration Reference

**Environment Variables:**
```bash
# Application
APP_NAME=ZynxAGI
APP_VERSION=1.0.0
DEBUG=true

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Cultural Intelligence
THAI_CULTURAL_WEIGHT=0.8
DEFAULT_CULTURAL_THRESHOLD=0.7
```

### E. Testing Guidelines

**Backend Tests:**
```bash
pytest tests/ -v
pytest tests/test_thai_cultural_mcp.py
pytest tests/test_universal_dispatcher.py
```

**Frontend Tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

### F. Glossary

**Thai Terms:**
- **ดีจ้า (Deeja):** AI agent name meaning "good/well" with friendly particle
- **เกรงใจ (Kreng Jai):** Thai cultural concept of consideration for others
- **สนุก (Sanuk):** Fun, enjoyable
- **ไม่เป็นไร (Mai Pen Rai):** It's okay, no problem
- **บุญคุณ (Bun Khun):** Gratitude, indebtedness

**Technical Terms:**
- **MCP:** Model Context Protocol
- **AGI:** Artificial General Intelligence
- **RAG:** Retrieval-Augmented Generation
- **Empathy Score:** Quantified measure of empathetic response
- **Cultural Markers:** Language indicators of cultural context

---

## สรุป / Conclusion

ZynxAGI represents a unique approach to AI platform design, combining advanced technical architecture with deep cultural intelligence. The system is built on modern, scalable technologies while maintaining a focus on empathy, cultural sensitivity, and ethical AI practices.

**Key Strengths:**
- 🎯 Cultural Intelligence with Thai specialization
- 🤖 Modular Multi-Agent Architecture
- 💚 Empathy-First Philosophy
- 🔒 Privacy and Security Focus
- 🚀 Scalable and Modern Technology Stack

**เอกสารนี้ครอบคลุม / This Document Covers:**
- ✅ Complete system architecture
- ✅ Agent design and implementation
- ✅ Backend and Frontend architecture
- ✅ Data flow and integration
- ✅ Security and monitoring
- ✅ Deployment and scalability
- ✅ Future roadmap

**ติดต่อ / Contact:**
- Developer: Chanont Wankaew
- Repository: https://github.com/zynx-chanont/ZynxAGI-Project
- Documentation: /docs
- API Docs: http://localhost:8000/docs

---

**Last Updated:** October 21, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete and Comprehensive

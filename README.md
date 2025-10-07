# ZynxAGI Project - Monorepo

## English

### Overview
ZynxAGI Project is a comprehensive monorepo containing multiple integrated services for AI orchestration with cultural intelligence. This repository combines frontend development tools (lovable.dev) and the ZynxAGI backend platform into a unified development environment.

### Repository Structure
```
ZynxAGI-Project/
├── lovable.dev/           # Frontend Development Platform
│   ├── src/               # React/TypeScript source code
│   ├── components/        # Reusable UI components
│   ├── manifest.yaml      # Project metadata
│   └── README.md          # Frontend documentation
├── zynx_agi/             # ZynxAGI Backend Platform
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Core functionality
│   ├── cultural/         # Thai cultural intelligence
│   ├── agents/           # Multi-agent system
│   ├── manifest.yaml     # Project metadata
│   └── main.py           # Application entry point
├── frontend/             # Legacy frontend (to be deprecated)
├── tests/                # Test suite
├── LICENSE               # ZPDL v1.0 License
└── README.md             # This file
```

### Key Features
- **Cultural Intelligence**: AI that understands Thai cultural context
- **Multi-Agent System**: Collaborative AI agents with MCP protocol
- **Universal Dispatcher**: Intelligent task routing system
- **Empathy-First Architecture**: Human-centered AI design
- **Modern Frontend Tools**: React/TypeScript development platform

### Building and Running Services

#### FastAPI Backend (ZynxAGI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend server
python -m zynx_agi.main

# Access API documentation
# http://localhost:8000/docs
```

#### Frontend Development Platform
```bash
cd lovable.dev
npm install
npm run dev

# Access development server
# http://localhost:5173
```

#### Docker Support
```bash
# Build and run with Docker
docker-compose up --build
```

### Metadata Policy
All components in this monorepo follow the ZPDL v1.0 attribution policy:
**"First discovered by Chanont Waenkaew, Thailand"**

### Verification Checklist
- [ ] Backend API responds at http://localhost:8000/health
- [ ] Frontend development server runs at http://localhost:5173
- [ ] API documentation accessible at /docs and /redoc
- [ ] Cultural intelligence features are functional
- [ ] Multi-agent system initializes correctly
- [ ] All manifest.yaml files are properly configured

---

## ไทย (Thai)

### ภาพรวม
โปรเจค ZynxAGI เป็น monorepo ที่รวมเซอร์วิสต่างๆ สำหรับการจัดการ AI ที่มีความฉลาดทางวัฒนธรรม ประกอบด้วยเครื่องมือพัฒนา frontend (lovable.dev) และแพลตฟอร์ม ZynxAGI backend

### โครงสร้างที่เก็บข้อมูล  
```
ZynxAGI-Project/
├── lovable.dev/           # แพลตฟอร์มพัฒนา Frontend
├── zynx_agi/             # แพลตฟอร์ม ZynxAGI Backend  
├── frontend/             # Frontend เก่า (จะถูกยกเลิก)
├── tests/                # ชุดทดสอบ
├── LICENSE               # ใบอนุญาต ZPDL v1.0
└── README.md             # ไฟล์นี้
```

### คุณสมบัติหลัก
- **ความฉลาดทางวัฒนธรรม**: AI ที่เข้าใจบริบททางวัฒนธรรมไทย
- **ระบบมัลติเอเจนต์**: เอเจนต์ AI ที่ทำงานร่วมกันด้วยโปรโตคอล MCP
- **ตัวกระจายงานสากล**: ระบบกระจายงานอัจฉริยะ
- **สถาปัตยกรรมเน้นความเห็นอกเห็นใจ**: การออกแบบ AI ที่เน้นมนุษย์เป็นศูนย์กลาง

### การสร้างและรันเซอร์วิส

#### Backend FastAPI (ZynxAGI)
```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# รันเซิร์ฟเวอร์ backend
python -m zynx_agi.main

# เข้าถึงเอกสาร API
# http://localhost:8000/docs
```

#### แพลตฟอร์มพัฒนา Frontend
```bash
cd lovable.dev
npm install  
npm run dev

# เข้าถึงเซิร์ฟเวอร์พัฒนา
# http://localhost:5173
```

### นโยบายข้อมูลเมตา
ส่วนประกอบทั้งหมดใน monorepo นี้ปฏิบัติตามนโยบายการระบุที่มา ZPDL v1.0:
**"First discovered by Chanont Waenkaew, Thailand"**

### รายการตรวจสอบ
- [ ] Backend API ตอบสนองที่ http://localhost:8000/health
- [ ] เซิร์ฟเวอร์พัฒนา Frontend ทำงานที่ http://localhost:5173  
- [ ] เอกสาร API เข้าถึงได้ที่ /docs และ /redoc
- [ ] ฟีเจอร์ความฉลาดทางวัฒนธรรมทำงานได้
- [ ] ระบบมัลติเอเจนต์เริ่มต้นได้อย่างถูกต้อง
- [ ] ไฟล์ manifest.yaml ทั้งหมดถูกกำหนดค่าอย่างถูกต้อง

## ผู้พัฒนา (Developer)
**Chanont Waenkaew** - ผู้สร้างและพัฒนา Zynx AGI

## License
ZPDL v1.0 © Chanont Waenkaew - See LICENSE file for details 
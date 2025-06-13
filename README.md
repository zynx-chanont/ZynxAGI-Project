# Zynx AGI - Universal AI Orchestration Platform

## ภาพรวม (Overview)

Zynx AGI เป็นแพลตฟอร์ม AI ขั้นสูงที่สร้างขึ้นโดย Chanont Wankaew โดยเน้นที่ความสามารถในการทำงานแบบออฟไลน์ ความฉลาดทางวัฒนธรรม และการบูรณาการอารมณ์ ระบบนี้เป็น AGI แบบโมดูลาร์ที่ขับเคลื่อนด้วยพรอมต์ ซึ่งออกแบบมาเพื่อรันเครือข่ายของเอเจนต์อัจฉริยะ

Zynx AGI is an advanced AI platform created by Chanont Wankaew, focusing on offline capabilities, cultural intelligence, and emotional integration. The system is a prompt-driven modular AGI designed to run a network of intelligent agents.

## คุณสมบัติหลัก (Key Features)

- 🤖 **Avatar Deeja**: ตัวแทน AI ที่มีความฉลาดทางอารมณ์
- 🌐 **Universal Message Dispatcher**: ระบบจัดการข้อความแบบสากล
- 🎯 **Cultural Context Engine**: เครื่องยนต์ความฉลาดทางวัฒนธรรม
- 🔄 **Offline Operation**: การทำงานแบบออฟไลน์
- 📚 **RAG Integration**: การบูรณาการกับระบบ RAG
- 📊 **Timeline Viewer**: ระบบแสดงไทม์ไลน์

## โครงสร้างโปรเจค (Project Structure)

```
Zynx_AGI_Claude/
├── frontend/               # React + TypeScript frontend
├── zynx_agi/              # Python backend
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── cultural/          # Cultural intelligence
│   ├── models/            # Data models
│   ├── security/          # Security features
│   └── ai_platforms/      # AI platform integrations
├── memory_learning/       # Memory and learning systems
├── tests/                 # Test suite
└── Doc/                   # Documentation
```

## การติดตั้ง (Installation)

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## การใช้งาน (Usage)

1. Start the backend server:
```bash
python -m zynx_agi.main
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## แผนงาน (Roadmap)

### Phase 1: การเตรียมการเปิดตัว
- [ ] ปรับปรุง UI/UX
- [ ] เพิ่มระบบ RAG
- [ ] สร้าง Timeline Viewer

### Phase 2: การเปิดตัวและขยายตลาด
- [ ] จัดงานเปิดตัว
- [ ] กิจกรรมประชาสัมพันธ์
- [ ] การขยายฐานผู้ใช้

### Phase 3: การพัฒนาอย่างต่อเนื่อง
- [ ] เพิ่มคุณสมบัติใหม่
- [ ] ปรับปรุงประสิทธิภาพ
- [ ] ขยายความสามารถทางวัฒนธรรม

## ผู้พัฒนา (Developer)

- **Chanont Wankaew** - ผู้สร้างและพัฒนา Zynx AGI

## License

MIT License - See LICENSE file for details 
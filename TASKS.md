# Unified Implementation Roadmap
## Meeting Knowledge Hub (React + Node.js + Python Architecture)

---

## สถานะ Legend
| Symbol | ความหมาย |
|--------|-----------|
| `[ ]`  | ยังไม่เริ่มดำเนินงาน |
| `[~]`  | อยู่ระหว่างดำเนินการ / มีโครงสร้างพื้นฐาน (Scaffold) |
| `[x]`  | เสร็จสิ้นสมบูรณ์และผ่านการทดสอบภายในแล้ว |
| `[!]`  | พบปัญหาทางเทคนิค / ถูกบล็อก |

---

## Phase 0: Foundation & Microservices Setup
- [ ] ตั้งค่า Repository แบบ Monorepo หรือแบ่งแยกชัดเจน (`frontend/`, `backend-node/`, `worker-python/`)
- [ ] ตั้งค่าสภาพแวดล้อม Python AI Worker (RTX 4060, CUDA, PyTorch)
- [ ] ตั้งค่าสภาพแวดล้อม Node.js Core API และการเชื่อมต่อ DB (PostgreSQL, Qdrant)
- [ ] ตั้งค่า Network Firewall กั้นระบบภายนอก เปิดเฉพาะ MS Graph API Ingress

---

## Phase 1: Ingestion & Resilience (React & Node.js)
- [ ] พัฒนาระบบรับไฟล์ประชุมและเอกสารแบบ Batch (Node.js)
- [ ] พัฒนาระบบ Frontend `IndexedDB` Client Buffer สำหรับบันทึกเสียง Live Capture ค้างไว้เมื่อเน็ตหลุด (React)
- [ ] พัฒนา Ingress Endpoint รับ Audio Stream จาก MS Teams Bot (Node.js)

---

## Phase 2: AI Processing & VRAM Management (Python Worker)
- [ ] พัฒนา REST/gRPC Interface ให้ Python Worker รับงานจาก Node.js
- [ ] ติดตั้ง `faster-whisper` และระบบจัดการ VRAM (`torch.cuda.empty_cache()`) (Python)
- [ ] ติดตั้งระบบ Model Lifecycle จองคิวรันงานสลับกัน (Whisper, LLM) (Python)

---

## Phase 3: Speaker Identification & Pipeline
- [ ] พัฒนาโมดูลแกะตัวตนผู้พูดจาก MS Teams Account Stream ขาเข้า (Node.js)
- [ ] นำส่งข้อมูลเสียงที่แกะตัวตนแล้วไปให้ Python Worker ถอดความเป็นข้อความ
- [ ] จัดเก็บข้อมูลลงระบบ

---

## Phase 4: AI Intelligence & LLM Strategy (Node.js + Python)
- [ ] เชื่อมต่อ LLaMA 3.1 ผ่าน Ollama สำหรับสรุปการประชุม
- [ ] พัฒนา Logic หั่นเอกสารใหญ่ (Map) และสังเคราะห์รวม (Reduce) สำหรับ Executive Digest
- [ ] พัฒนา Prompt สกัดข้อมูลมติที่ประชุม (Resolutions) และงานค้าง (Pending Tasks)

---

## Phase 5: Knowledge Layer & Security
- [ ] พัฒนาระบบเชื่อมต่อ Qdrant และ PostgreSQL (Node.js)
- [ ] พัฒนา Atomic Transaction อัปเดตและลบ Vector ทันทีที่แก้ไขข้อความ
- [ ] เพิ่มเงื่อนไข Category-Based Security กรองสิทธิ์ JWT Role ในระดับ Database

---

## Phase 6: Application Layer (React UI)
- [ ] สร้าง Multi-Module Sidebar แบบ SPA บน React ครอบคลุม 5 หน้าต่างใช้งาน
- [ ] พัฒนาหน้าจอถามตอบ Knowledge Chat พร้อม Citation อ้างอิง
- [ ] เชื่อมต่อ API และ WebSockets เข้ากับ Node.js Backend

---

## Phase 7: Governance & Golden Vault
- [ ] พัฒนา Audit Logging และตัวลบไฟล์ดิบอัตโนมัติใน 30 วัน (Node.js)
- [ ] พัฒนา Data Sanitization (PII Masking) นำข้อความย้ายเข้า Anonymized Golden Vault

---

## Phase 8 & 9: Testing, QA & Feedback Loop
- [ ] ทำ End-to-End Integration Test ข้าม 3 Service (React → Node → Python)
- [ ] พัฒนาหน้าจอ Prompt Studio สำหรับแอดมิน ดึงข้อมูลจาก Golden Vault มาเทสทบทวนผล

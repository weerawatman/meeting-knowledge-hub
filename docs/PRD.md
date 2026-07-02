# Product Requirements Document (PRD)
## Meeting Knowledge Hub — Unified (Private AI Meeting & Knowledge Intelligence System)

> **Architecture Update:** ปรับปรุงสถาปัตยกรรมเป็น Microservices (React Frontend + Node.js Core API + Python AI Worker) เพื่อรองรับข้อจำกัดฮาร์ดแวร์ VRAM 8GB, การจัดการ Live Capture แบบ Non-blocking, และระบบความแม่นยำสูงระดับ Enterprise

---

## 1. Problem Statement
องค์กรเผชิญปัญหาการสูญเสียความรู้จากการประชุมและเอกสารที่กระจัดกระจาย:
- ข้อมูลสำคัญสูญหายทันทีหลังจบการประชุม
- การถอดเสียงและการระบุผู้พูดแบบเดิม (Audio Diarization) บนฮาร์ดแวร์ออนเปรมมีความคลาดเคลื่อนสูงและกินทรัพยากรมาก
- การประมวลผล AI และ Web API บน Process เดียวกันทำให้ระบบเกิดอาการคอขวด (Bottleneck) หรือ Out of Memory (OOM) ง่าย
- ข้อมูลความลับขององค์กรรั่วไหลหากส่งไปประมวลผลผ่านบริการ Cloud AI สาธารณะ

**กลุ่มผู้ใช้เป้าหมายต้องการ:**
"ระบบที่ช่วยบันทึกการประชุมและสรุปเอกสารอ้างอิงได้อย่างแม่นยำ ปลอดภัยสูงสุด ควบคุมข้อมูลภายในองค์กร และทำงานได้ลื่นไหลไม่สะดุดแม้ประมวลผล AI หนักๆ อยู่เบื้องหลัง"

---

## 2. Core Solution & Modules
**Meeting Knowledge Hub (Unified)** เป็นฐานความรู้หนึ่งเดียวขององค์กร (Unified Knowledge Store) ทำงานผ่าน **Private AI Pipeline** ควบคุมข้อมูลขาออกเป็นศูนย์ ประกอบด้วย 5 โมดูลหลัก ขับเคลื่อนด้วยสแต็ค **React + Node.js + Python + Qdrant**:

1. **Meeting Knowledge (Batch Mode):** อัปโหลดไฟล์เสียง/วิดีโอประชุมย้อนหลัง
2. **Live Capture (Real-time Integration):** ระบบ AI Bot เข้าร่วม MS Teams ดึง Audio Stream ขาเข้าแยกตาม Account เพื่อระบุผู้พูดแม่นยำ 100% พร้อมระบบ **Offline-First Client Buffer** บนเบราว์เซอร์ (`IndexedDB`) ป้องกันข้อมูลสูญหาย
3. **Executive Digest (Multi-document Map-Reduce):** ระบบวิเคราะห์เอกสารหลายฉบับพร้อมกัน (Two-pass Analysis) ดึงข้อมูลมติที่ประชุมและงานค้างส่งได้ครบถ้วน
4. **Knowledge Chat (Category-Based RAG):** ถามตอบข้ามฐานความรู้ พร้อมระบบกรองสิทธิ์การเข้าถึงข้อมูลตามหมวดหมู่ (Category-Based Authorization) จาก Database
5. **Prompt Studio (Admin Console):** เครื่องมือปรับแต่ง Prompt ทำงานร่วมกับ **Anonymized Golden Vault** สำหรับทดสอบโดยไม่ละเมิดความเป็นส่วนตัว

---

## 3. Technical & Implementation Decisions

### Microservices Stack (VRAM 8GB Optimized)
- **Frontend (React):** จัดการ UI แบบ SPA (Single Page Application)
- **Core API (Node.js):** จัดการการเข้า-ออกของข้อมูลแบบ Non-blocking I/O (WebSockets, สตรีมเสียง MS Teams, Auth, RBAC, ติดต่อ DB) ช่วยให้ระบบไม่ค้างเมื่อมีการประมวลผล AI
- **AI Worker (Python):** Service ย่อยสำหรับจัดการ GPU โดยเฉพาะ ทำหน้าที่โหลดโมเดลเข้า/ออก VRAM แบบ Sequential (Whisper → LLaMA 3.1 → bge-m3)
- **CPU Offloading:** ย้ายโมเดลจัดทำดัชนีข้อความ (`BAAI/bge-m3`) ไปรันบน CPU เพื่อสงวน VRAM

### Data & Search Strategy
- **Atomic Real-time Update:** การแก้ไขข้อมูลจากหน้าจอ จะผ่าน Node.js ไปสั่งอัปเดต PostgreSQL และสั่งลบ/อัปเดต Vector ใน Qdrant ใน Transaction เดียว
- **Metadata Filtering Search:** บังคับกรองสิทธิ์ด้วย Role และ Category ทันทีในระดับ Database Layer (Qdrant)

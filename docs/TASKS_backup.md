# TASKS.md
## Meeting Knowledge Hub — Implementation Roadmap

> อ้างอิงจาก: [PRD.md](PRD.md) · [Architecture.md](Architecture.md)
>
> **เป้าหมาย:** แปลงการประชุม → ระบบความรู้ขององค์กร บน On-Premise AI Pipeline

---

## สถานะ Legend

| Symbol | ความหมาย |
|--------|-----------|
| `[ ]`  | ยังไม่เริ่ม |
| `[~]`  | กำลังดำเนินการ |
| `[x]`  | เสร็จสิ้น |
| `[!]`  | มีปัญหา / Blocked |

---

## Phase 0: Foundation & Infrastructure Setup

> เตรียมพื้นฐานทั้งหมดก่อนเริ่ม Development

- [ ] ประเมินและจัดเตรียม Hardware
  - GPU server (สำหรับ STT + LLM inference)
  - CPU server (สำหรับ pipeline orchestration)
  - Secure file storage (temporary)
- [ ] ติดตั้ง OS และ core dependencies
  - Linux (Ubuntu 22.04 LTS แนะนำ)
  - Python 3.11+, Docker, CUDA toolkit
  - GPU drivers + CUDA compatibility check
- [ ] สร้างโครงสร้าง project repository
  - กำหนด folder structure (ingestion/, stt/, speaker_id/, llm/, rag/, api/, ui/, governance/)
  - ตั้งค่า `.gitignore`, `pyproject.toml` หรือ `requirements.txt`
- [ ] ตั้งค่า CI/CD pipeline เบื้องต้น
  - Linting, unit test runner
  - Container build pipeline (Docker)
- [ ] ตั้งค่า Internal-only networking
  - ยืนยันว่าไม่มี external API calls ออกจาก network
  - Firewall rules สำหรับ internal access เท่านั้น

**Milestone:** ระบบพร้อม run pipeline บน local environment ได้

---

## Phase 1: Ingestion Layer

> รับ Recording จาก Microsoft Teams เข้าสู่ระบบ

- [ ] ออกแบบ file watcher / queue system
  - Monitor designated folder สำหรับ Teams recordings ที่ export มา
  - Queue-based processing (เช่น Redis Queue หรือ file-based queue)
- [ ] สร้าง file validation module
  - ตรวจ format (`.mp4`, `.mkv`, `.wav`, `.mp3`)
  - ตรวจ file size และ integrity (checksum)
  - Reject corrupted files พร้อม error logging
- [ ] สร้าง ingestion pipeline
  - Extract audio track จาก video file (ถ้า input เป็น video)
  - Store audio ใน secure temporary storage
  - Track meeting metadata (filename, timestamp, uploader)
- [ ] ตั้งค่า secure temporary file storage
  - กำหนด retention: ลบ raw audio/video ภายใน 30 วัน (ดู Phase 7)
  - Access control บน storage folder
- [ ] สร้าง ingestion logging
  - Log ทุก ingestion event (success / failure / skipped)
  - Alert เมื่อ queue หยุดทำงาน

**Milestone:** ระบบรับไฟล์จาก Teams และส่งต่อเข้า pipeline ได้อัตโนมัติ

---

## Phase 2: Speech-to-Text (STT) Pipeline

> แปลงเสียง → ข้อความที่ถูกต้อง (Accuracy > Speed)

- [ ] เลือกและติดตั้ง STT model
  - แนะนำ: [OpenAI Whisper](https://github.com/openai/whisper) (large-v3) หรือ Faster-Whisper
  - Deploy บน GPU server
  - ทดสอบ inference speed และ accuracy เบื้องต้น
- [ ] สร้าง audio preprocessing module
  - Normalize audio (sample rate, channels)
  - Noise reduction (ถ้าจำเป็น)
  - Chunking สำหรับ long recordings
- [ ] สร้าง transcription pipeline
  - Input: audio file → Output: timestamped transcript (`.json` / `.txt`)
  - รองรับ long-form audio (ประชุม 1–3 ชั่วโมง)
  - บันทึก word-level timestamps
- [ ] วัด accuracy baseline
  - สร้าง test set จาก sample recordings
  - คำนวณ Word Error Rate (WER)
  - เป้าหมาย: WER ต่ำกว่า 15%
- [ ] ตั้งค่า retry logic
  - Retry อัตโนมัติเมื่อ STT ล้มเหลว (สูงสุด 3 ครั้ง)
  - Mark failed jobs ใน queue

**Milestone:** แปลงเสียงประชุมเป็น transcript ที่มี timestamps ได้ถูกต้อง

---

## Phase 3: Speaker Identification

> ระบุว่าใครพูดอะไร (Target: ≥90% accuracy)

- [ ] เลือก voice fingerprinting library
  - แนะนำ: `pyannote.audio` (speaker diarization)
  - ติดตั้งและทดสอบบน GPU
- [ ] สร้าง speaker clustering module
  - Diarization: แยกเสียงตาม speaker segment
  - Clustering: จัดกลุ่ม speaker ที่เป็นคนเดียวกัน
  - Output: `SPEAKER_01`, `SPEAKER_02`, …
- [ ] สร้าง speaker mapping (ID → ชื่อจริง)
  - UI/API สำหรับให้ user map `SPEAKER_01` → "สมชาย"
  - บันทึก voice profile สำหรับ future meetings
- [ ] ตั้งค่า fallback mode
  - ถ้า speaker ID ล้มเหลว → ใช้ transcript โดยไม่มี speaker tag
  - Log และ notify admin
- [ ] วัด speaker ID accuracy
  - เป้าหมาย: ≥90% accuracy บน test set
  - Human review สำหรับ edge cases

**Milestone:** transcript มี speaker label พร้อม mapping ชื่อจริงได้

---

## Phase 4: AI Intelligence Layer (LLM)

> ประมวลผล transcript → ความรู้ที่มีโครงสร้าง

- [ ] เลือกและติดตั้ง open-source LLM
  - แนะนำ: LLaMA 3.1 8B / Mistral 7B (quantized)
  - Deploy ด้วย `ollama` หรือ `vLLM` บน GPU server
  - ทดสอบ inference latency
- [ ] สร้าง summarization pipeline
  - Prompt template สำหรับสรุปการประชุม (ภาษาไทย)
  - Chunking transcript สำหรับ long meetings
  - Map-reduce สำหรับ summarize หลาย chunks
- [ ] สร้าง key decision extraction module
  - Extract decisions ที่เกิดขึ้นในประชุม
  - Format: `{ "decision": "...", "context": "...", "speaker": "..." }`
- [ ] สร้าง action item extraction module
  - Extract action items พร้อม assignee และ deadline (ถ้ามี)
  - Format: `{ "task": "...", "assignee": "...", "due": "..." }`
- [ ] ออกแบบ structured output format
  ```json
  {
    "summary": "...",
    "decisions": [...],
    "action_items": [...],
    "transcript": [{ "speaker": "...", "text": "...", "timestamp": "..." }]
  }
  ```
- [ ] ตั้งค่า fallback summary
  - ถ้า LLM ล้มเหลว → ส่ง transcript ดิบ + error flag
  - Simple extractive summary เป็น fallback

**Milestone:** ระบบสร้าง structured summary พร้อม decisions + action items อัตโนมัติ

---

## Phase 5: Knowledge Layer (RAG)

> เก็บความรู้ให้ค้นหาได้ทั้ง keyword และ semantic

- [ ] เลือกและติดตั้ง Vector Database
  - แนะนำ: Qdrant (self-hosted) หรือ ChromaDB
  - Deploy บน Docker
- [ ] เลือก embedding model (open-source)
  - แนะนำ: `BAAI/bge-m3` (multilingual, รองรับภาษาไทย)
  - Deploy embedding inference service
- [ ] สร้าง metadata store (SQL)
  - PostgreSQL สำหรับ meeting metadata
  - Schema: meeting_id, date, participants, title, status
- [ ] สร้าง document store
  - เก็บ full transcript + structured output
  - Link กับ embeddings ใน vector DB
- [ ] Implement hybrid search
  - Keyword search (BM25 / full-text)
  - Semantic search (vector similarity)
  - Metadata filter (date, speaker, meeting title)
  - Rank fusion (RRF หรือ weighted score)
- [ ] สร้าง feedback dataset storage
  - เก็บ user corrections สำหรับ training future models
  - Schema: original_text, corrected_text, correction_type, timestamp

**Milestone:** ค้นหาข้อมูลจากประชุมได้ด้วย keyword, semantic, และ filter

---

## Phase 6: Application Layer

> Interface สำหรับผู้ใช้เข้าถึงความรู้

### 6A: API Layer

- [ ] ออกแบบ REST API (FastAPI)
  - `POST /meetings/ingest` — trigger ingestion manually
  - `GET /meetings/{id}` — ดึง summary + transcript
  - `GET /search?q=...&speaker=...&from=...` — hybrid search
  - `POST /meetings/{id}/corrections` — submit correction
  - `GET /meetings/{id}/action-items` — ดึง action items
- [ ] API authentication (internal token-based)
- [ ] API documentation (auto-generated จาก FastAPI)

### 6B: Frontend UI

- [ ] Search interface
  - Search bar รองรับ Thai/English
  - Filter by: date range, speaker, meeting
  - แสดง search results พร้อม highlight
- [ ] Meeting viewer
  - แสดง summary, decisions, action items
  - แสดง transcript พร้อม speaker label และ timestamp
  - Media player link (ถ้า recording ยังไม่ถูกลบ)
- [ ] Editing interface (Human-in-the-loop)
  - แก้ไข transcript (text inline edit)
  - แก้ไข speaker mapping
  - แก้ไข summary และ action items
  - Submit correction → trigger reindex

**Milestone:** ผู้ใช้ค้นหา, ดู, และแก้ไขข้อมูลประชุมผ่าน UI ได้

---

## Phase 7: Governance Layer

> ความปลอดภัยและการจัดการข้อมูล

- [ ] Implement Role-Based Access Control (RBAC)
  - Roles: Admin, User, Viewer
  - Admin: จัดการ settings, ดู audit log
  - User: ค้นหา, ดู, แก้ไข
  - Viewer: ค้นหา, ดู เท่านั้น
- [ ] สร้าง audit logging system
  - Log ทุก action: ใคร, ทำอะไร, เมื่อไร
  - Tamper-evident log (append-only)
- [ ] สร้าง auto-deletion scheduler
  - Cron job ลบ raw audio/video ที่เกิน 30 วัน
  - Confirmation log หลังลบ
  - Alert ถ้า deletion ล้มเหลว
- [ ] ทดสอบ data retention policy
  - ยืนยันว่า knowledge/embeddings ยังอยู่หลังลบ raw files
  - ยืนยันว่า raw files ถูกลบครบ

**Milestone:** ระบบ compliant กับ privacy-first policy โดยอัตโนมัติ

---

## Phase 8: Testing & QA

> ตรวจสอบ accuracy, performance, และ reliability

- [ ] สร้าง golden dataset
  - รวบรวม sample recordings + expected outputs (manual)
  - ครอบคลุม: ประชุมสั้น, ยาว, หลาย speaker
- [ ] ทดสอบ STT accuracy
  - วัด WER บน golden dataset
  - เปรียบเทียบกับ baseline
- [ ] ทดสอบ Speaker ID accuracy
  - วัด % correct speaker assignment
  - เป้าหมาย: ≥90%
- [ ] ประเมิน summary quality
  - Human review score (1–5)
  - ตรวจ decisions + action items ครบถ้วน
- [ ] ทดสอบ search relevance
  - Precision@5 สำหรับ query ชุดทดสอบ
  - ทดสอบ Thai query + English query
- [ ] ทดสอบ data deletion (automated)
  - ยืนยัน raw files ถูกลบตาม schedule
  - ยืนยัน knowledge ยังเข้าถึงได้
- [ ] Integration testing end-to-end
  - Full pipeline: ingest → STT → Speaker ID → LLM → RAG → Search
- [ ] Load/performance testing
  - ทดสอบ concurrent ingestion
  - วัด latency ของ search API

**Milestone:** ระบบผ่านเกณฑ์ accuracy และ reliability ทุก module

---

## Phase 9: Feedback Loop & Continuous Learning

> ระบบเรียนรู้จาก correction ของผู้ใช้

- [ ] สร้าง feedback collection pipeline
  - รับ correction จาก UI → เก็บใน feedback dataset
  - Categorize: transcript error, speaker error, summary error
- [ ] สร้าง model improvement workflow
  - **STT:** Fine-tune Whisper ด้วย corrected transcripts (ถ้า data เพียงพอ)
  - **Speaker ID:** Update voice profiles จาก confirmed mappings
  - **LLM:** Prompt refinement จาก summary feedback
- [ ] ตั้งค่า continuous evaluation loop
  - Auto-evaluate accuracy metrics เป็นรายเดือน
  - Dashboard แสดง trend ของ accuracy
- [ ] สร้าง feedback review interface (Admin)
  - Admin ดู + approve corrections ก่อน train

**Milestone:** ระบบ accuracy ดีขึ้นต่อเนื่องจาก user feedback

---

## Summary: Phase Overview

| Phase | ชื่อ | ขึ้นอยู่กับ |
|-------|------|------------|
| 0 | Foundation & Infrastructure | — |
| 1 | Ingestion Layer | Phase 0 |
| 2 | STT Pipeline | Phase 1 |
| 3 | Speaker Identification | Phase 2 |
| 4 | AI Intelligence (LLM) | Phase 2, 3 |
| 5 | Knowledge Layer (RAG) | Phase 4 |
| 6 | Application Layer | Phase 5 |
| 7 | Governance Layer | Phase 1, 6 |
| 8 | Testing & QA | Phase 2–7 |
| 9 | Feedback Loop | Phase 6, 8 |

---

> **หลักการ:** Accuracy > Speed · Privacy-first · Learning system via feedback

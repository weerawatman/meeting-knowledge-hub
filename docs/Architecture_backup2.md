# 🏗️ System Architecture
## Meeting Knowledge Hub — Unified (On-Prem AI Meeting & Knowledge Intelligence System)

> อ้างอิงจาก: [PRD.md](PRD.md) · แผนงานฉบับนี้รวมสถาปัตยกรรม On-Premise ของ meeting-knowledge-hub เข้ากับฟีเจอร์ที่พิสูจน์แล้วของ meeting_audio (Executive Digest, Live Capture, Chat Assistant, Prompt Master)

---

## 1. High-Level Architecture

ระบบยังคงเป็น **On-Premise pipeline แบบ 6 layer** เหมือนออกแบบเดิมของ meeting-knowledge-hub แต่แต่ละ layer ถูกขยายให้รองรับ input/feature ที่มาจาก meeting_audio:

1. Ingestion Layer — **ขยาย:** batch recording + **real-time capture** + **multi-document upload**
2. Processing Pipeline (STT + Speaker ID)
3. AI Intelligence Layer (LLM) — **ขยาย:** meeting summarization + **multi-document executive digest (two-pass)**
4. Knowledge Layer (RAG) — **ขยาย:** unified store สำหรับ meeting knowledge + document knowledge
5. Application Layer (UI / API) — **ขยาย:** 5 module surface (Meeting Knowledge, Live Capture, Executive Digest, Knowledge Chat, Prompt Studio)
6. Governance Layer (Security + Retention) — **ขยาย:** ครอบคลุมทั้ง recordings และ uploaded documents

ไม่มี Cloud AI / Cloud Vector DB ใน layer ใดเลย (ตัดขาดจาก Gemini/Claude/OpenAI/Pinecone ที่ meeting_audio เคยใช้)

---

## 2. Architecture Components

### 2.1 Ingestion Layer

**Batch path (จาก meeting-knowledge-hub เดิม):**
- Source: Microsoft Teams Recording (post-meeting) หรืออัปโหลดไฟล์เสียง/วิดีโอโดยตรง
- Mode: Batch ingestion
- Input: audio file, video file (optional)

**Real-time path (ใหม่ — จาก meeting_audio's Meeting Transcript):**
- Source: การบันทึกเสียงสดระหว่างประชุม (browser microphone capture หรือ local recording client)
- Mode: Streaming / chunked ingestion — ส่ง audio chunk เข้า STT ทันทีระหว่างประชุมดำเนินอยู่ พร้อมสร้าง final batch-quality pass เมื่อประชุมจบ
- Session tracking: meeting session id, participant list, live status

**Multi-document path (ใหม่ — จาก meeting_audio's Executive Digest):**
- Source: อัปโหลดเอกสารอ้างอิงหลายฉบับพร้อมกัน (PDF, DOCX, PPTX, XLSX, TXT)
- Mode: Batch ingestion, ประมวลผลแบบ job ต่อชุดเอกสาร (digest job)
- Extraction: local document parsing (พอร์ตแนวทางจาก meeting_audio's `document_service.py`) — ไม่ใช้ Cloud Document AI

---

### 2.2 Processing Pipeline

#### Speech-to-Text (STT)
- Converts audio → transcript (รองรับทั้ง batch file และ streaming chunk)
- High accuracy prioritized over speed สำหรับ batch, low-latency prioritized สำหรับ live capture partial transcript

#### Speaker Identification
- Voice fingerprinting (pyannote.audio)
- Clustering + speaker mapping
- Target accuracy: ≥90%
- สำหรับ live capture: speaker tagging แบบ approximate ระหว่างประชุม แล้ว re-run แบบเต็มความแม่นยำหลังประชุมจบ

---

### 2.3 AI Intelligence Layer

#### LLM Processing (Meeting)
- Model: Open-source (LLaMA 3.1 / Mistral) ผ่าน Ollama
- Tasks: Summarization, Key decision extraction, Action item extraction

#### LLM Processing (Executive Digest — ใหม่)
- **Two-pass local analysis** (แทนที่ meeting_audio's Duo-Agent Claude+Gemini ด้วย local model ทั้งคู่):
  - **Pass 1 — Detail Analysis:** วิเคราะห์เอกสารแต่ละฉบับแยกกัน (per-document summary, key points)
  - **Pass 2 — Strategic Synthesis:** รวมผลลัพธ์จาก Pass 1 ทั้งหมดเป็น executive digest เดียว (agenda, resolutions, pending tasks)
- Hierarchical chunking สำหรับเอกสารขนาดใหญ่ (แนวทางเดียวกับที่ meeting_audio ใช้)

#### Output Format (Semi-Structured)

Meeting output:
- Summary, Decisions, Action Items, Speaker-attributed transcript

Executive Digest output (ใหม่):
```json
{
  "digest_id": "...",
  "source_documents": ["doc_1", "doc_2", "..."],
  "document_summaries": [{ "document_id": "...", "summary": "..." }],
  "agenda": [...],
  "resolutions": [{ "decision": "...", "context": "...", "source_document": "..." }],
  "pending_tasks": [{ "task": "...", "assignee": "...", "due": "...", "priority": "...", "status": "..." }]
}
```

---

### 2.4 Knowledge Layer (RAG)

#### Storage
- Vector database (embeddings) — Qdrant (self-hosted)
- Metadata store — PostgreSQL
- Document store — full transcript / digest content

#### Unified Knowledge Model (ขยายจาก meeting-knowledge-hub เดิม)
ระบบเก็บความรู้ 2 ประเภทในโครงสร้างเดียวกัน เพื่อให้ Knowledge Chat ค้นข้ามได้:
- **Meeting Knowledge** — จาก batch/live meeting ingestion (transcript, summary, decisions, action items)
- **Document Knowledge** — จาก Executive Digest multi-document ingestion (digest, resolutions, pending tasks)

ทั้งสองประเภทมี embedding + metadata (source_type: `meeting` | `document`, date, participants/authors, title) เพื่อรองรับ metadata filter ใน hybrid search

#### Data Stored
- Processed knowledge (meeting + document)
- Embeddings
- Metadata
- Feedback dataset

#### Data NOT Stored
- Raw audio/video (ลบภายใน 30 วัน)
- เอกสารต้นฉบับที่อัปโหลด (ลบภายใน 30 วัน)

---

### 2.5 Application Layer

#### API Layer
- Query knowledge (meeting หรือ document)
- Submit corrections
- Retrieve summaries / digests
- Chat / RAG Q&A endpoint (ใหม่)
- Prompt template CRUD + test endpoint (ใหม่, admin-only)
- Live capture session start/stop + streaming transcript endpoint (ใหม่)

#### UI Layer — 5 Module Surface (ขยายจาก meeting-knowledge-hub เดิมที่มีแค่ 3 ส่วน)
โครงสร้าง sidebar multi-module ตามแนวทางเดียวกับ meeting_audio's `frontend/index.html` แต่ implement ใหม่บน on-prem backend:

1. **Meeting Knowledge** — search interface, meeting viewer (summary, decisions, action items, speaker-labeled transcript), editing interface
2. **Live Capture** — เริ่ม/หยุดบันทึกประชุม, แสดง live partial transcript, speaker tag แบบ approximate
3. **Executive Digest** — อัปโหลดเอกสารหลายฉบับ, ดู digest ผลลัพธ์ (per-document summary + synthesis + resolutions + pending tasks)
4. **Knowledge Chat** — สนทนาถามตอบข้าม meeting + document knowledge พร้อม citation กลับไปยัง source
5. **Prompt Studio** (Admin only) — จัดการ/ทดสอบ prompt template สำหรับ summarization, digest, chat

---

### 2.6 Governance Layer

#### Security
- On-prem only, ไม่มี external API calls
- Role-based access control (Admin / User / Viewer) — Admin เท่านั้นที่เข้าถึง Prompt Studio
- Audit logging (ทุก action, tamper-evident)

#### Data Retention (ขยายให้ครอบคลุมทุก input type)
- Auto-delete raw audio/video หลัง 30 วัน (recording, live capture)
- Auto-delete เอกสารต้นฉบับที่อัปโหลด หลัง 30 วัน (Executive Digest source files)
- Retain processed knowledge (summary, digest, embeddings, metadata, feedback) ถาวร

---

## 3. Data Flow

### 3.1 Batch Meeting Flow
1. Meeting ends → recording generated (Teams export หรืออัปโหลดเอง)
2. File ingested เข้าระบบ
3. STT ประมวลผล audio → transcript
4. Speaker ID กำหนด speaker
5. LLM สร้าง structured summary
6. ข้อมูลถูกเก็บใน RAG system (Meeting Knowledge)
7. User เข้าถึงผ่าน UI/API
8. User แก้ไข → feedback ถูกเก็บ

### 3.2 Live Capture Flow (ใหม่)
1. User เริ่มบันทึกประชุมผ่าน UI
2. Audio chunk ถูกส่งเข้า STT แบบ streaming → partial transcript แสดงผลสด
3. เมื่อประชุมจบ → full-quality re-run (STT + Speaker ID) เหมือน batch flow
4. ผลลัพธ์สุดท้าย merge เข้า RAG system เช่นเดียวกับ batch flow

### 3.3 Executive Digest Flow (ใหม่)
1. User อัปโหลดเอกสารหลายฉบับผ่าน UI
2. เอกสารถูก extract ข้อความ (local parsing)
3. LLM Pass 1 วิเคราะห์แต่ละเอกสาร
4. LLM Pass 2 สังเคราะห์เป็น digest เดียว (agenda, resolutions, pending tasks)
5. ข้อมูลถูกเก็บใน RAG system (Document Knowledge)
6. User เข้าถึงผ่าน UI/API หรือถามผ่าน Knowledge Chat

---

## 4. Key Design Decisions

- Dual-mode processing: Batch (accuracy-first) + Real-time (latency-aware สำหรับ live partial transcript)
- Accuracy prioritized over latency สำหรับผลลัพธ์สุดท้ายทุกกรณี
- Hybrid human-in-the-loop system
- Privacy-first (On-prem + data deletion) — ครอบคลุมทั้ง recordings และ documents
- Unified knowledge store (meeting + document) เพื่อให้ Knowledge Chat ค้นข้าม source ได้
- Learning system via feedback loop

---

## 5. Infrastructure Requirements

### Compute
- GPU (สำหรับ STT + LLM inference ทั้ง batch และ live capture)
- CPU (pipeline orchestration)

### Storage
- Secure file storage (temporary, สำหรับ recording และเอกสารต้นฉบับ)
- Vector DB (Qdrant)
- Metadata DB (PostgreSQL)

### Networking
- Internal-only access เท่านั้น
- **ไม่มี external API calls** (ไม่มี Gemini/Claude/OpenAI/Pinecone หรือ Cloud service ใด ๆ)

---

## 6. Failure Handling

- If STT fails → retry (สูงสุด 3 ครั้ง)
- If Speaker ID fails → fallback (ไม่มี speaker tagging)
- If LLM fails (summary หรือ digest) → simple/extractive summary เป็น fallback
- If live capture connection drops → resume จาก chunk ล่าสุดโดยไม่ข้อมูลหาย, fallback ไปยัง batch re-processing เมื่อประชุมจบ
- Logging + monitoring required ทุก failure path

---

## 7. Future Extensions

(ตัด "Real-time processing" ออกจากหัวข้อนี้ เนื่องจากถูกดึงเข้ามาเป็น current scope แล้ว — ดู Section 2.1, 3.2)

- Multi-language support (นอกเหนือจาก Thai/English)
- Cross-meeting analytics
- Advanced knowledge graph (เชื่อมโยง meeting knowledge และ document knowledge เป็น graph)
- Voice-profile-based auto speaker mapping ข้ามหลายประชุม

---

## 8. Summary

ระบบแปลง:
Raw Meeting Data + Reference Documents → Processed Knowledge → Searchable & Conversational Intelligence

ด้วย:
- Privacy (On-prem, ไม่มี Cloud AI)
- Intelligence (Local LLM: summarization, digest, chat)
- Memory (Unified RAG store: meeting + document knowledge)
- Flexibility (Batch + Real-time ingestion)

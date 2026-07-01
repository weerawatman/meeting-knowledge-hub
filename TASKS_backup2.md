# TASKS.md — Unified Implementation Roadmap

## Meeting Knowledge Hub — Unified (On-Prem AI Meeting & Knowledge Intelligence System)

> อ้างอิงจาก: [PRD.md](PRD.md) · [Architecture.md](Architecture.md)
>
> **เป้าหมาย:** แปลงการประชุม + เอกสารองค์กร → ระบบความรู้ขององค์กรเดียว บน On-Premise AI Pipeline
>
> เอกสารนี้รวม roadmap เดิมของ meeting-knowledge-hub (Phase 0–9) เข้ากับฟีเจอร์ที่พิสูจน์แล้วจาก meeting_audio (Live Capture, Executive Digest multi-doc, Knowledge Chat, Prompt Studio) และ **ปรับสถานะ checkbox ให้ตรงกับ code จริงในโปรเจกต์ meeting-knowledge-hub ณ วันที่ตรวจสอบ (2026-07-01)** — โค้ดส่วน core pipeline (ingestion → STT → speaker ID → LLM → RAG → API) มี implementation แล้วตาม commit "Implement demo-ready pipeline: STT, Speaker ID, LLM, RAG, and UI" แม้ TASKS.md ฉบับเดิมจะยังไม่ติ๊กก็ตาม

---

## สถานะ Legend

| Symbol | ความหมาย |
|--------|-----------|
| `[ ]`  | ยังไม่เริ่ม |
| `[~]`  | กำลังดำเนินการ / มี scaffold แต่ยังไม่สมบูรณ์ |
| `[x]`  | เสร็จสิ้น |
| `[!]`  | มีปัญหา / Blocked |

---

## Phase 0: Foundation & Infrastructure Setup

> เตรียมพื้นฐานทั้งหมดก่อนเริ่ม Development

- [ ] ประเมินและจัดเตรียม Hardware (GPU/CPU server, secure storage) — ยังไม่ยืนยันสภาพแวดล้อม production จริง
- [ ] ติดตั้ง OS และ core dependencies บน target server (Ubuntu 22.04, CUDA)
- [x] สร้างโครงสร้าง project repository — `api/ ingestion/ stt/ speaker_id/ llm/ rag/ pipeline/ governance/ ui/ tests/` มีครบตาม design, `pyproject.toml` กำหนด dependency ชัดเจน
- [ ] ตั้งค่า CI/CD pipeline (lint/test runner/container build) — ยังไม่พบ config ใน repo
- [ ] ตั้งค่า Internal-only networking + firewall — ต้องยืนยันในขั้น deployment จริง

**Milestone:** โครงสร้าง repo และ dependency พร้อมแล้ว, ยังขาด infra/CI/deployment hardening

---

## Phase 1: Ingestion Layer

> รับ Recording, Live Audio, และเอกสารอ้างอิง เข้าสู่ระบบ

### 1A: Batch Recording Ingestion (จาก meeting-knowledge-hub เดิม)
- [x] file watcher / queue system — `ingestion/watcher.py`, `ingestion/queue.py`
- [x] file validation module (format, size, checksum) — `ingestion/validator.py`
- [x] ingestion pipeline (extract audio, secure storage, metadata) — `ingestion/processor.py`, `ingestion/storage.py`
- [~] secure temporary file storage + retention policy — storage path มีแล้ว, auto-delete cron ดู Phase 7
- [x] ingestion logging — ผ่าน `loguru` ในทุก module

### 1B: Live Capture Ingestion (ใหม่ — จาก meeting_audio's Meeting Transcript)
- [ ] ออกแบบ streaming/chunked audio ingestion endpoint (WebSocket หรือ chunked upload)
- [ ] session management (start/stop, session id, participant list)
- [ ] buffer/queue สำหรับ audio chunk ระหว่าง live session
- [ ] mechanism สลับจาก live partial result → full batch re-processing เมื่อจบ session

### 1C: Multi-document Ingestion (ใหม่ — จาก meeting_audio's Executive Digest)
- [ ] file validation สำหรับ PDF/DOCX/PPTX/XLSX/TXT (แนวทางเดียวกับ meeting_audio's `document_service.py`)
- [ ] local text extraction module (PyPDF2, python-docx, python-pptx, openpyxl แบบ on-prem, ไม่มี Cloud Document AI)
- [ ] digest job grouping (ผูกหลายเอกสารเป็น 1 digest job)
- [ ] secure temporary storage + retention (ร่วมกับ Phase 7)

**Milestone:** ระบบรับไฟล์ได้ 3 ช่องทาง (batch recording, live capture, multi-document) และส่งต่อเข้า pipeline ได้อัตโนมัติ

---

## Phase 2: Speech-to-Text (STT) Pipeline

> แปลงเสียง → ข้อความที่ถูกต้อง (Accuracy > Speed สำหรับ batch, latency-aware สำหรับ live)

- [x] STT model deployment — `stt/whisper_inference.py` ใช้ faster-whisper, รองรับปรับขนาด model ผ่าน `WHISPER_MODEL` env
- [x] audio preprocessing module — `stt/preprocess.py`
- [x] transcription pipeline (audio → timestamped transcript) — `stt/pipeline.py`, `stt/transcribe.py`
- [ ] วัด accuracy baseline (WER) บน golden dataset — ยังไม่พบ evaluation script/ผลลัพธ์ในโค้ด
- [~] retry logic เมื่อ STT ล้มเหลว — error handling มีใน pipeline orchestrator แต่ retry แบบมี max-attempt ยังไม่ชัดเจน
- [ ] streaming/low-latency mode สำหรับ Live Capture (ใหม่)

**Milestone:** แปลงเสียงประชุมแบบ batch เป็น transcript พร้อม timestamps ได้แล้ว, ส่วน streaming mode สำหรับ live capture ยังต้องทำเพิ่ม

---

## Phase 3: Speaker Identification

> ระบุว่าใครพูดอะไร (Target: ≥90% accuracy)

- [x] voice fingerprinting / diarization module — `speaker_id/diarize.py`
- [x] speaker segment models — `speaker_id/models.py`
- [~] speaker mapping UI (ID → ชื่อจริง) — backend model รองรับ `display_name`, ต้องตรวจสอบ UI flow ให้ user map ชื่อได้จริง
- [x] fallback mode เมื่อ speaker ID ล้มเหลว — pipeline orchestrator ใช้ default `SPEAKER_01` เมื่อ diarization ไม่ match
- [ ] วัด speaker ID accuracy บน test set (เป้าหมาย ≥90%) — ยังไม่พบ evaluation script
- [ ] approximate speaker tagging แบบ real-time สำหรับ Live Capture (ใหม่)

**Milestone:** transcript มี speaker label พร้อม fallback ได้แล้ว, ยังขาด accuracy measurement และ live-mode tagging

---

## Phase 4: AI Intelligence Layer (LLM)

> ประมวลผล transcript และเอกสาร → ความรู้ที่มีโครงสร้าง

### 4A: Meeting Summarization (จาก meeting-knowledge-hub เดิม)
- [x] open-source LLM deployment ผ่าน Ollama — `llm/generator.py`, `llm/summarize.py` เรียก `OLLAMA_MODEL` (default `llama3.1:8b`)
- [x] summarization pipeline + prompt template ภาษาไทย — `llm/prompting.py`
- [x] key decision extraction — structured output ใน `summarize_transcript()`
- [x] action item extraction (task/assignee/due) — structured output เดียวกัน
- [x] structured output format (summary/decisions/action_items/transcript) — ตรงกับ design
- [x] fallback summary เมื่อ LLM ล้มเหลว (Ollama unreachable) — มี except block คืน excerpt/raw transcript

### 4B: Executive Digest — Multi-document Two-pass Analysis (ใหม่ — จาก meeting_audio's Duo-Agent)
- [ ] Pass 1: per-document detail analysis prompt (local LLM)
- [ ] Pass 2: strategic synthesis prompt รวมผลลัพธ์จาก Pass 1 ทั้งหมด
- [ ] hierarchical chunking สำหรับเอกสารขนาดใหญ่ (พอร์ตแนวทางจาก meeting_audio)
- [ ] structured digest output: `agenda`, `resolutions`, `pending_tasks` (แนวทางเดียวกับ meeting_audio's `Agenda`/`Resolution`/`PendingTask` models)
- [ ] fallback digest เมื่อ LLM ล้มเหลว

**Milestone:** ระบบสร้าง structured meeting summary ได้สมบูรณ์แล้ว (4A), ส่วน multi-document executive digest (4B) ยังต้องพัฒนาใหม่ทั้งหมด

---

## Phase 5: Knowledge Layer (RAG)

> เก็บความรู้ (meeting + document) ให้ค้นหาได้ทั้ง keyword และ semantic

- [x] Vector Database — `rag/vector_store.py` ใช้ Qdrant, มี local in-memory fallback เมื่อ Qdrant ไม่พร้อมใช้งาน
- [x] embedding model (open-source) — `rag/embeddings.py` ใช้ sentence-transformers (ปัจจุบัน `bge-small-en-v1.5`; PRD/Architecture แนะนำอัปเกรดเป็น `BAAI/bge-m3` เพื่อรองรับ multilingual/ไทยดีขึ้น)
- [x] metadata store — `rag/db.py`, `rag/models.py`
- [x] document store — `rag/store.py` (`MeetingStore`)
- [x] hybrid search — `rag/search.py` (`hybrid_search`) + `store.search()` ใช้ใน `/search` endpoint
- [x] feedback dataset storage — `store.add_feedback()` เรียกจาก `/meetings/{id}/corrections`
- [ ] ขยาย schema ให้รองรับ **Document Knowledge** (จาก Executive Digest) ควบคู่กับ Meeting Knowledge พร้อม `source_type` metadata filter (ใหม่)

**Milestone:** ค้นหาข้อมูลจากประชุมได้แล้วด้วย keyword+semantic+metadata filter, ยังต้องขยายให้ครอบคลุม document knowledge จาก Executive Digest

---

## Phase 6: Application Layer

> Interface สำหรับผู้ใช้เข้าถึงความรู้

### 6A: API Layer
- [x] REST API หลัก (FastAPI) — `api/app.py`, `api/endpoints.py`: `/upload`, `/meetings/{id}/status`, `/meetings/{id}`, `/search`, `/meetings/{id}/corrections`, `/meetings/{id}/action-items`, `/meetings/ingest`
- [x] API authentication (role-based) — `api/security.py` (`get_current_role`)
- [x] API documentation อัตโนมัติจาก FastAPI (Swagger/OpenAPI)
- [ ] Live capture endpoint (start/stop session, streaming transcript) (ใหม่)
- [ ] Executive Digest endpoint (multi-file upload, digest job status, digest result) (ใหม่)
- [ ] Knowledge Chat endpoint (RAG-based Q&A ข้าม meeting + document knowledge) (ใหม่)
- [ ] Prompt template CRUD + test endpoint (admin-only) (ใหม่)

### 6B: Frontend UI
- [!] ปัจจุบันมีแค่ `ui/index.html` + `ui/placeholder.txt` — **ยังเป็น placeholder เท่านั้น** ยังไม่ใช่ multi-module UI ที่ใช้งานได้จริง
- [ ] สร้าง multi-module sidebar shell (5 module: Meeting Knowledge, Live Capture, Executive Digest, Knowledge Chat, Prompt Studio) — แนวทางเดียวกับ meeting_audio's `frontend/index.html` แต่ implement ใหม่คุยกับ FastAPI backend
- [ ] Meeting Knowledge: search interface + meeting viewer (summary/decisions/action items/speaker-labeled transcript) + editing interface (human-in-the-loop)
- [ ] Live Capture: start/stop recording UI, live partial transcript display
- [ ] Executive Digest: multi-file upload UI, digest result viewer (per-document summary + synthesis + resolutions + pending tasks)
- [ ] Knowledge Chat: chat UI พร้อม citation กลับไปยัง source (meeting หรือ document)
- [ ] Prompt Studio (Admin only): template list/editor + test console

**Milestone:** API layer หลักพร้อมใช้งานแล้วสำหรับ meeting knowledge, ส่วน UI ยังเป็น placeholder และ endpoint/UI ใหม่ทั้ง 4 โมดูล (Live Capture, Executive Digest, Knowledge Chat, Prompt Studio) ยังต้องพัฒนาทั้งหมด — **นี่คือ gap ที่ใหญ่ที่สุดของการรวมโปรเจกต์**

---

## Phase 7: Governance Layer

> ความปลอดภัยและการจัดการข้อมูล (ครอบคลุมทั้ง recordings และ documents)

- [~] Role-Based Access Control (RBAC) — `api/security.py` มี role dependency ใช้งานใน endpoint สำคัญแล้ว, ควรตรวจสอบว่าครบ 3 role (Admin/User/Viewer) ตาม design หรือไม่
- [x] audit logging system — `governance/audit.py`
- [x] auto-deletion scheduler — `governance/scheduler.py`, `governance/retention.py`
- [ ] ทดสอบ data retention policy end-to-end (ยืนยันว่า knowledge อยู่ครบหลังลบ raw files) — ยังไม่พบ integration test เฉพาะทาง
- [ ] ขยาย retention policy ให้ครอบคลุมเอกสารต้นฉบับที่อัปโหลดสำหรับ Executive Digest (ใหม่)
- [ ] จำกัดสิทธิ์ Prompt Studio ให้ Admin เท่านั้น (ใหม่, ผูกกับ Phase 6A)

**Milestone:** มี audit log และ auto-deletion scheduler พร้อมแล้วสำหรับ recordings, RBAC มี scaffold แล้วแต่ควรตรวจสอบความครบถ้วน, ยังขาดการขยาย retention ไปยังเอกสาร

---

## Phase 8: Testing & QA

> ตรวจสอบ accuracy, performance, และ reliability

- [x] test suite ครอบคลุม module หลัก — `tests/test_api.py`, `test_api_endpoints.py`, `test_governance.py`, `test_ingestion.py`, `test_llm.py`, `test_rag.py`, `test_speaker_id.py`, `test_store.py`, `test_stt.py`
- [ ] สร้าง golden dataset (sample recordings + expected outputs)
- [ ] ทดสอบ STT accuracy (WER) เทียบ baseline
- [ ] ทดสอบ Speaker ID accuracy (เป้าหมาย ≥90%)
- [ ] ประเมิน summary quality ด้วย human review score
- [ ] ทดสอบ search relevance (Precision@5, Thai + English query)
- [ ] ทดสอบ data deletion แบบ automated end-to-end
- [ ] Integration testing เต็ม pipeline: ingest → STT → Speaker ID → LLM → RAG → Search
- [ ] Load/performance testing (concurrent ingestion, search latency)
- [ ] **ทดสอบ multi-document Executive Digest quality** (ใหม่ — human review ต่อ digest, ตรวจ resolutions/pending tasks ครบถ้วน)
- [ ] **ทดสอบ Knowledge Chat retrieval/groundedness** (ใหม่ — วัดว่าคำตอบอ้างอิง source ถูกต้อง ไม่ hallucinate)
- [ ] **ทดสอบ Live Capture latency และ resume-after-disconnect** (ใหม่)

**Milestone:** มี unit test coverage ต่อ module ครบแล้ว, ยังขาด accuracy/quality evaluation แบบ end-to-end และ test ของฟีเจอร์ใหม่ทั้งหมด

---

## Phase 9: Feedback Loop & Continuous Learning

> ระบบเรียนรู้จาก correction ของผู้ใช้

- [x] feedback collection endpoint — `/meetings/{id}/corrections` → `store.add_feedback()`
- [ ] categorize feedback ตามประเภท (transcript/speaker/summary/digest error)
- [ ] model improvement workflow (fine-tune Whisper, update voice profile, prompt refinement)
- [ ] continuous evaluation loop (auto-evaluate accuracy รายเดือน + dashboard trend)
- [ ] feedback review interface (Admin) — ผูกกับ Prompt Studio (Phase 6B) เพื่อให้ admin approve correction ก่อน train

**Milestone:** รับ feedback พื้นฐานได้แล้ว, ส่วน learning loop และ admin review UI ยังต้องพัฒนา

---

## Summary: Phase Overview

| Phase | ชื่อ | สถานะโดยรวม | ขึ้นอยู่กับ |
|-------|------|--------------|------------|
| 0 | Foundation & Infrastructure | `[~]` repo/deps พร้อม, infra/CI ยังไม่ทำ | — |
| 1 | Ingestion Layer (batch + live + multi-doc) | `[~]` batch เสร็จ, live/multi-doc ใหม่ทั้งหมด | Phase 0 |
| 2 | STT Pipeline | `[~]` batch เสร็จ, streaming mode ใหม่ | Phase 1 |
| 3 | Speaker Identification | `[~]` core เสร็จ, accuracy eval + live tagging ค้าง | Phase 2 |
| 4 | AI Intelligence (LLM: summary + digest) | `[~]` meeting summary เสร็จ (4A), digest ใหม่ทั้งหมด (4B) | Phase 2, 3 |
| 5 | Knowledge Layer (RAG) | `[~]` meeting knowledge เสร็จ, document knowledge ใหม่ | Phase 4 |
| 6 | Application Layer (API + UI) | `[!]` API หลักเสร็จ, UI เป็น placeholder + 4 โมดูลใหม่ต้องทำทั้งหมด | Phase 5 |
| 7 | Governance Layer | `[~]` audit/retention เสร็จ, RBAC ต้องตรวจสอบ, ขยายไป document | Phase 1, 6 |
| 8 | Testing & QA | `[~]` unit test เสร็จ, accuracy/quality eval ค้าง | Phase 2–7 |
| 9 | Feedback Loop | `[~]` collection เสร็จ, learning loop ค้าง | Phase 6, 8 |

---

> **หลักการ:** Accuracy > Speed · Privacy-first (On-prem, ไม่มี Cloud AI) · Learning system via feedback · Unified knowledge store (meeting + document)

# Product Requirements Document (PRD)
## Meeting Knowledge Hub — Unified (On-Prem AI Meeting & Knowledge Intelligence System)

> เอกสารนี้รวม requirement จาก 2 โปรเจกต์:
> - **meeting-knowledge-hub** — สถาปัตยกรรม On-Premise, Privacy-first (Whisper / Ollama / Qdrant / Governance) ที่เดิม batch-only
> - **meeting_audio** — ชุดฟีเจอร์ที่ใช้งานได้จริงแล้วบน Cloud AI (Meeting Summary, Meeting Transcript, Executive Digest, Chat Assistant, Prompt Master)
>
> **หลักการรวม:** ใช้สถาปัตยกรรม On-Premise ของ meeting-knowledge-hub เป็นแกนหลัก แล้วนำฟีเจอร์ที่พิสูจน์แล้วจาก meeting_audio มา re-implement บน local stack (ไม่มี Cloud AI / Cloud Vector DB ในระบบ production)

---

## Problem Statement

องค์กรในปัจจุบันเผชิญปัญหาการสูญเสียความรู้จากการประชุมและเอกสารที่กระจัดกระจาย:
- ข้อมูลสำคัญหายไปหลังประชุมจบ ไม่มีใครจดจำได้ครบ
- การย้อนดู recording ใช้เวลานาน ไม่มีใครอยากเปิดฟังซ้ำ
- ไม่สามารถระบุได้ชัดเจนว่าใครพูดอะไร ตกลงอะไรกันไว้
- การสรุปโดยมนุษย์มีความคลาดเคลื่อนและใช้เวลา (โดยเฉพาะการสรุปเอกสารหลายฉบับก่อนประชุมผู้บริหาร)
- ข้อมูลประชุมและเอกสารอ้างอิงกระจัดกระจาย ค้นหาข้าม source ไม่ได้
- การส่งเสียงประชุม/เอกสารองค์กรไปประมวลผลผ่าน Cloud AI API สร้างความกังวลด้าน Data Privacy และ Compliance สูง

ผู้ใช้ต้องการ:
"ระบบที่ช่วยจำการประชุมและสรุปเอกสารแทนทีมงาน โดยยังคงความปลอดภัยของข้อมูลทั้งหมดไว้ภายในองค์กร (On-Premise)"

---

## Solution

**Meeting Knowledge Hub (Unified)** เป็นระบบ AI แบบ On-Premise ล้วน ที่ไม่มีการเรียก Cloud AI API ใด ๆ ในโหมด production ประกอบด้วย 5 ความสามารถหลัก (map มาจาก 5 โมดูลที่พิสูจน์แล้วใน meeting_audio แต่ทำงานบน local stack ของ meeting-knowledge-hub):

1. **Meeting Knowledge (Batch)** — รับ recording จาก Microsoft Teams หรืออัปโหลดไฟล์เสียง/วิดีโอ → แปลงเสียงเป็นข้อความด้วย local Whisper → แยก speaker (~90%+ accuracy) → สรุปประชุมอัตโนมัติด้วย local LLM (เทียบเท่า meeting_audio's Meeting Summary)
2. **Live Capture (Real-time)** — บันทึกและถอดเสียงประชุมแบบสด ระหว่างประชุมกำลังดำเนินอยู่ (เทียบเท่า meeting_audio's Meeting Transcript) — **เพิ่มใหม่จากเดิมที่ meeting-knowledge-hub ออกแบบไว้เฉพาะ batch**
3. **Executive Digest (Multi-document)** — วิเคราะห์เอกสารหลายฉบับพร้อมกัน (PDF/DOCX/PPTX/XLSX) ด้วย local LLM สองรอบ (detail pass + synthesis pass) สรุปเป็น agenda, resolutions, pending tasks (เทียบเท่า meeting_audio's Executive Digest Duo-Agent แต่ทำงานด้วย local model ทั้งคู่)
4. **Knowledge Chat (RAG Q&A)** — สนทนาถามตอบข้ามฐานความรู้ประชุม+เอกสารทั้งหมด ผ่าน hybrid search (keyword + semantic) บน local vector database (เทียบเท่า meeting_audio's Chat Assistant แต่ใช้ Qdrant + local embedding แทน Pinecone)
5. **Prompt Studio (Admin)** — เครื่องมือจัดการ/ทดสอบ prompt template สำหรับ admin/power user เพื่อปรับแต่งคุณภาพผลลัพธ์ของ AI (เทียบเท่า meeting_audio's Prompt Master)

ทุกความสามารถเก็บผลลัพธ์ในฐานความรู้เดียวกัน (unified knowledge store) ให้ผู้ใช้แก้ไข + ระบบเรียนรู้จาก feedback

### Data Strategy
- ลบไฟล์ audio/video ต้นฉบับ และเอกสารต้นฉบับที่อัปโหลด ภายใน 30 วัน
- เก็บเฉพาะ knowledge, embeddings, metadata, feedback ไว้ถาวร
- ไม่มีข้อมูลใดถูกส่งออกไปนอกเครือข่ายภายในองค์กร (ไม่มี external API calls)

---

## User Stories

### จาก meeting-knowledge-hub (เดิม)
1. As a user, I want automatic ingestion of recordings, so that I don't upload files manually
2. As a user, I want accurate transcription, so that I trust the system
3. As a user, I want speaker identification, so that I know who said what
4. As a user, I want summaries, so that I understand quickly
5. As a user, I want action items, so that I can follow up
6. As a user, I want keyword search, so that I find information fast
7. As a user, I want semantic search, so that I find meaning
8. As a user, I want speaker filters, so that I track people
9. As a user, I want editing capability, so that I fix errors
10. As a user, I want system learning from feedback, so that accuracy improves
11. As an admin, I want auto deletion of recordings, so that risk is minimized
12. As an executive, I want on-prem processing, so that data is secure
13. As a user, I want fallback summaries, so that I still get output

### เพิ่มใหม่ จาก meeting_audio (re-implemented on-prem)
14. As a user, I want to record and see a live transcript while the meeting is happening, so that I don't have to wait until after the meeting ends
15. As a user, I want to upload multiple reference documents (PDF/DOCX/PPTX/XLSX) at once and get one consolidated executive digest, so that I can prepare for leadership meetings faster
16. As a user, I want the executive digest to separate detailed findings from a strategic synthesis, so that I can choose the depth I need
17. As a user, I want to chat with the system and ask questions across all my past meetings and documents, so that I don't have to search manually
18. As an admin, I want to create and test custom prompt templates, so that I can tune output quality for my team's specific needs without code changes
19. As a user, I want a single UI with clear module navigation (meeting knowledge, live capture, executive digest, chat, prompt studio), so that I can switch between tasks without confusion

---

## Implementation Decisions

### Architecture
- Fully On-premise, no external API dependency (superseding meeting_audio's cloud-provider approach)
- Dual processing mode: **Batch** (post-meeting / uploaded documents) และ **Real-time** (live capture during a meeting)
- Modular pipeline:
  - Ingestion (recording batch, live capture, multi-document)
  - STT + Speaker ID
  - AI Intelligence (summarization, decision/action-item extraction, multi-doc digest)
  - Knowledge/RAG storage (unified meeting + document knowledge)
  - Application (API + multi-module UI)
  - Governance (security + retention, covers recordings and documents)

### AI Stack
- Open-source LLM (LLaMA 3.1 / Mistral) served locally via Ollama
- STT: Whisper / faster-whisper on GPU
- Speaker recognition via voice fingerprinting (pyannote.audio)
- Local embedding model for search (BAAI/bge-m3, multilingual — รองรับภาษาไทย)
- Local vector database: Qdrant (self-hosted)

### Data Design
Retained:
- Knowledge (summaries, digests, transcripts)
- Embeddings
- Metadata
- Feedback

Deleted (within 30 days):
- Audio/video ต้นฉบับ
- เอกสารต้นฉบับที่อัปโหลดสำหรับ Executive Digest

### Search
- Hybrid search (keyword + semantic + metadata) ข้ามทั้ง meeting knowledge และ document knowledge

### Failure Handling
- Fallback summary เมื่อ LLM ล้มเหลว
- Fallback transcript-only เมื่อ Speaker ID ล้มเหลว
- Live capture ที่ขาดการเชื่อมต่อ ต้อง resume ได้โดยไม่ข้อมูลหาย

---

## Testing Decisions

### Good Test Criteria
- Test external behavior
- Validate accuracy, latency, structure

### Modules Tested
- STT accuracy (batch และ real-time)
- Speaker ID accuracy
- Summary quality (meeting) และ digest quality (multi-document)
- Search relevance (hybrid, ข้าม meeting + document knowledge)
- Chat Q&A relevance/groundedness
- Data deletion (recordings และ uploaded documents)

### Evaluation
- Golden dataset (รวมทั้งการประชุมและชุดเอกสารหลายฉบับ)
- Human review
- Continuous feedback loop

---

## Out of Scope

- Cloud APIs (Gemini, Claude, OpenAI, Pinecone หรือบริการ Cloud AI ใด ๆ) — ระบบใหม่ตัดขาดจาก Cloud AI ทั้งหมด, meeting_audio's cloud-provider integrations จะไม่ถูกพอร์ตมา
- Video analytics (facial recognition, engagement scoring)
- Multi-language UI (เริ่มต้นรองรับ Thai/English เท่านั้น)
- Public/external-facing deployment (ระบบสำหรับใช้งานภายในองค์กรเท่านั้น)

> หมายเหตุ: "Real-time transcription" ที่เดิม meeting-knowledge-hub ระบุเป็น Out of Scope ถูกย้ายเข้ามาเป็น **In Scope** แล้ว (ดู Live Capture ด้านบน) เนื่องจาก meeting_audio พิสูจน์แล้วว่าเป็นความต้องการจริงของผู้ใช้

---

## Further Notes

- Accuracy > Speed
- Privacy-first design (on-prem เท่านั้น)
- Learning system via feedback
- ฟีเจอร์ทั้ง 5 (Meeting Knowledge, Live Capture, Executive Digest, Knowledge Chat, Prompt Studio) ใช้ knowledge store เดียวกัน ไม่แยก silo

---

## Summary

"เปลี่ยนการประชุมและเอกสารองค์กร → เป็นระบบความรู้ขององค์กรเดียว ที่ปลอดภัยและค้นหาได้ทั้งหมด"

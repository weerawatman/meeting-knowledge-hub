# Product Requirements Document (PRD)
## Meeting Knowledge Hub (On-Prem AI Meeting Intelligence System)

---

## Problem Statement

องค์กรในปัจจุบันเผชิญปัญหาการสูญเสียความรู้จากการประชุม:
- ข้อมูลสำคัญหายไปหลังประชุม
- การย้อนดู recording ใช้เวลานาน
- ไม่สามารถระบุว่าใครพูดอะไรได้ชัดเจน
- การสรุปโดยมนุษย์มีความคลาดเคลื่อน
- ข้อมูลกระจัดกระจาย ค้นหาไม่ได้
- มีข้อกังวลด้าน Privacy สูง

ผู้ใช้ต้องการ:
“ระบบที่ช่วยจำการประชุมแทน โดยยังคงความปลอดภัยของข้อมูล”

---

## Solution

Meeting Knowledge Hub เป็นระบบ AI แบบ On-premise ที่:
- รับ recording จาก Microsoft Teams (หลังประชุม)
- แปลงเสียงเป็นข้อความ
- แยก speaker (~90%+ accuracy)
- สรุปประชุมอัตโนมัติ
- เก็บเป็น Knowledge (RAG)
- ให้ผู้ใช้แก้ไข + ระบบเรียนรู้

### Data Strategy
- ลบ audio/video ภายใน 30 วัน
- เก็บเฉพาะ knowledge, embeddings, metadata, feedback

---

## User Stories

1. As a user, I want automatic ingestion of recordings, so that I don’t upload files manually  
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

---

## Implementation Decisions

### Architecture
- Fully On-premise
- Batch processing (post-meeting)
- Modular pipeline:
  - Ingestion
  - STT
  - Speaker ID
  - LLM
  - RAG storage

### AI Stack
- Open-source LLM (LLaMA / Mistral)
- Speaker recognition via voice fingerprint
- Embedding model for search

### Data Design
Retained:
- Knowledge
- Embeddings
- Metadata
- Feedback

Deleted:
- Audio/video (30 days)

### Search
- Hybrid search (keyword + semantic + metadata)

### Failure Handling
- Fallback summary

---

## Testing Decisions

### Good Test Criteria
- Test external behavior
- Validate accuracy, latency, structure

### Modules Tested
- STT accuracy
- Speaker ID accuracy
- Summary quality
- Search relevance
- Data deletion

### Evaluation
- Golden dataset
- Human review
- Continuous feedback loop

---

## Out of Scope

- Real-time transcription
- Cloud APIs
- Multi-language support (initial)
- Video analytics

---

## Further Notes

- Accuracy > Speed
- Privacy-first design
- Learning system via feedback

---

## Summary

“เปลี่ยนการประชุม → เป็นระบบความรู้ขององค์กร”

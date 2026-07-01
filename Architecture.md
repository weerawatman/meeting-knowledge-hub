# System Architecture Document
## Meeting Knowledge Hub — Unified (Private AI Pipeline)

---

## 1. High-Level Architecture Diagram (Microservices)

ระบบทำงานบนสถาปัตยกรรม **Private AI Pipeline** แบ่งหน้าที่ชัดเจนระหว่างการจัดการฝั่ง Web (Node.js) และการจัดการ GPU (Python Worker):

```
+-------------------------------------------------------------------------+
|                        1. Application & Ingestion Layer                 |
| [React Frontend (IndexedDB)]    [MS Teams Bot Ingress (Audio Streams)]  |
+-------------------------------------------------------------------------+
                                 | (WebSockets / HTTP)
                                 v
+-------------------------------------------------------------------------+
|                        2. Core Backend Service (Node.js)                |
| [Auth & RBAC] <--> [Data Orchestrator] <--> [Connection Manager]        |
|       |                                               |                 |
|       +--> (DB Queries)                               +--> (AI Tasks)   |
+-------|-----------------------------------------------|-----------------+
        v                                               v
+------------------------------+       +----------------------------------+
| 3. Knowledge Layer (DBs)     |       | 4. AI Worker Service (Python)    |
| [PostgreSQL (Metadata)]      |       | [VRAM Priority Orchestrator]     |
| [Qdrant (Vector DB)]         |       | [Whisper STT (GPU)]              |
|                              |       | [LLaMA 3.1 8B (GPU via Ollama)]  |
|                              |       | [bge-m3 Embedding (CPU)]         |
+------------------------------+       +----------------------------------+
```

---

## 2. Component Detailed Design

### 2.1 Application & Core Backend (React + Node.js)

- **React SPA:** รองรับ 5 โมดูลหน้าจอ ใช้ `IndexedDB` เป็น Offline-first Buffer สำรองข้อมูลเสียง Live Capture หากเครือข่ายหลุด

- **Node.js Main API:**
  - ทำหน้าที่เป็นตัวรับ Ingress Stream ขาเข้าจาก MS Teams
  - จัดการ Concurrency และ WebSockets สำหรับ Live Transcript
  - จัดการ Category-Based Security (อ่านสิทธิ์ JWT Token ส่งไปเป็น Filter ให้ Qdrant)
  - เป็นตัวกลางส่งคิวงานหนัก (Audio File, Document Text) ผ่าน Message Broker หรือ Local HTTP ไปให้ Python Worker

### 2.2 AI Worker Service (Python GPU Manager)

ออกแบบมาแก้ปัญหา VRAM 8GB (เช่น RTX 4060):

- **Model Lifecycle Orchestrator:** ควบคุมการเคลียร์ Memory (`torch.cuda.empty_cache()`) อย่างเข้มงวด ทำงานแบบ Sequential Loading
- **Priority Queue:** รับคำสั่งจาก Node.js หากเป็น Live Capture จะจอง VRAM ให้ Whisper ทันที หากเป็น Batch/Digest จะรันเมื่อ GPU ว่าง
- **Map-Reduce Agent:** ทำ Two-pass Executive Digest โดยวิเคราะห์แยกชิ้น (Pass 1) และรวมข้อมูลอิงตาม Metadata (Pass 2)

### 2.3 Knowledge & Governance Layer

- **Atomic Sync:** Node.js สั่งอัปเดต PostgreSQL และ Qdrant พร้อมกัน
- **Anonymized Golden Vault:** สคริปต์ Node/Python ทำหน้าที่ Masking ข้อมูล PII เก็บเป็น Ground Truth ทดสอบ Prompt
- **30-Day Auto Delete:** ลบ raw file อัตโนมัติตามนโยบายองค์กร

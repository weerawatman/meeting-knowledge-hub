# 🏗️ System Architecture
## Meeting Knowledge Hub (On-Prem AI Meeting Intelligence System)

---

## 1. High-Level Architecture

The system is designed as a fully **On-Premise, batch-processing pipeline**:

1. Ingestion Layer
2. Processing Pipeline (STT + Speaker ID)
3. AI Intelligence Layer (LLM)
4. Knowledge Layer (RAG)
5. Application Layer (UI / API)
6. Governance Layer (Security + Retention)

---

## 2. Architecture Components

### 2.1 Ingestion Layer
- Source: Microsoft Teams Recording (post-meeting)
- Mode: Batch ingestion (not real-time)
- Input:
  - Audio file
  - Video file (optional)

---

### 2.2 Processing Pipeline

#### Speech-to-Text (STT)
- Converts audio → transcript
- High accuracy prioritized over speed

#### Speaker Identification
- Voice fingerprinting
- Clustering + speaker mapping
- Target accuracy: ≥90%

---

### 2.3 AI Intelligence Layer

#### LLM Processing
- Model: Open-source (LLaMA / Mistral)
- Tasks:
  - Summarization
  - Key decision extraction
  - Action item extraction

#### Output Format (Semi-Structured)
- Summary
- Decisions
- Action Items
- Speaker-attributed transcript

---

### 2.4 Knowledge Layer (RAG)

#### Storage
- Vector database (embeddings)
- Metadata store
- Document store

#### Data Stored
- Processed knowledge
- Embeddings
- Metadata
- Feedback dataset

#### Data NOT Stored
- Raw audio/video (deleted after 30 days)

---

### 2.5 Application Layer

#### API Layer
- Query knowledge
- Submit corrections
- Retrieve summaries

#### UI Layer
- Search interface
- Meeting viewer
- Editing interface

---

### 2.6 Governance Layer

#### Security
- On-prem only
- Role-based access control
- Audit logging

#### Data Retention
- Auto-delete raw files after 30 days
- Retain processed knowledge

---

## 3. Data Flow

1. Meeting ends → recording generated
2. File ingested into system
3. STT processes audio → transcript
4. Speaker ID assigns speakers
5. LLM generates structured summary
6. Data stored in RAG system
7. User accesses via UI/API
8. User edits → feedback stored

---

## 4. Key Design Decisions

- Batch processing (not real-time)
- Accuracy prioritized over latency
- Hybrid human-in-the-loop system
- Privacy-first (On-prem + data deletion)
- Learning system via feedback loop

---

## 5. Infrastructure Requirements

### Compute
- GPU (for STT + LLM)
- CPU (pipeline orchestration)

### Storage
- Secure file storage (temporary)
- Vector DB
- Metadata DB

### Networking
- Internal-only access
- No external API calls

---

## 6. Failure Handling

- If STT fails → retry
- If Speaker ID fails → fallback (no speaker tagging)
- If LLM fails → simple summary
- Logging + monitoring required

---

## 7. Future Extensions

- Real-time processing
- Multi-language support
- Cross-meeting analytics
- Advanced knowledge graph

---

## 8. Summary

System converts:
Raw Meeting Data → Processed Knowledge → Searchable Intelligence

With:
- Privacy (On-prem)
- Intelligence (AI)
- Memory (RAG)

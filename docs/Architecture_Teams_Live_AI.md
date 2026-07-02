# Architecture
## SAT Secretary BOT - Teams Live AI Architecture

Last updated: 2026-07-02

---

## 1. Architectural Goal

Build a Teams-integrated AI meeting module where `SAT Secretary BOT` appears as one visible participant, while the backend runs a coordinated set of services for policy, live audio processing, Japanese captions, transcript persistence, retention, audit, and knowledge indexing.

The architecture must preserve the current project direction:

- React web frontend
- Node.js Core API
- Python AI Worker
- Private/on-prem AI processing
- Microsoft Teams/CART/Graph integration through Microsoft tenant cloud
- PostgreSQL/Qdrant-backed knowledge store

---

## 2. C4 Context

```text
+---------------------+        +----------------------------+
| Organizer/Internal  |        | External Guest             |
| Participants        |        |                            |
+----------+----------+        +-------------+--------------+
           |                                 |
           v                                 v
+-----------------------------------------------------------+
| Microsoft Teams / Outlook                                 |
| - Meeting creation                                         |
| - SAT Secretary BOT roster presence                        |
| - Native captions / CART captions                          |
| - Meeting lifecycle                                        |
| - Graph transcript availability                            |
+----------------------------+------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| Meeting Knowledge Hub                                     |
| - Teams Integration Layer                                  |
| - Policy Engine                                            |
| - Live AI Session Orchestrator                             |
| - Caption Publisher                                        |
| - Transcript Store                                         |
| - Retention & Audit                                        |
| - RAG-ready Knowledge Store                                |
+-----------------------------------------------------------+
```

---

## 3. Container View

```text
+-----------------------------------------------------------------------+
| React Web / Teams Side Panel                                          |
| - Admin policy UI                                                     |
| - Preview reader                                                      |
| - Read receipts                                                       |
| - Fallback captions                                                   |
| - Transcript review/correction                                        |
+-------------------------------+---------------------------------------+
                                |
                                v
+-----------------------------------------------------------------------+
| Node.js Core API                                                       |
| - Auth/RBAC                                                           |
| - Teams webhook endpoints                                             |
| - Calendar/meeting monitor                                            |
| - Policy Engine                                                       |
| - Live Session Orchestrator                                           |
| - Caption Publisher adapter                                           |
| - Transcript/version API                                              |
| - Audit API                                                           |
+----------+--------------------+---------------------+----------------+
           |                    |                     |
           v                    v                     v
+------------------+   +-------------------+   +----------------------+
| PostgreSQL       |   | Object Storage     |   | Qdrant               |
| - meetings       |   | - raw audio        |   | - transcript chunks  |
| - policies       |   | - context files    |   | - meeting knowledge  |
| - transcripts    |   | - previews         |   +----------------------+
| - audit          |   +-------------------+
+---------+--------+
          |
          v
+-----------------------------------------------------------------------+
| Python AI Worker                                                       |
| - Streaming STT                                                        |
| - Thai/English language handling                                       |
| - Japanese translation                                                 |
| - Glossary enforcement                                                 |
| - Summarization                                                        |
| - RAG ingestion                                                        |
+-----------------------------------------------------------------------+
```

---

## 4. Logical AI Team Behind One Bot

User sees one participant:

- `SAT Secretary BOT`

Internally, the system can run multiple workers:

| Internal Worker | Responsibility |
| --- | --- |
| Meeting Agent | Tracks meeting lifecycle, join state, policy state |
| Audio Listener | Receives mixed meeting audio where platform allows |
| STT Worker | Converts Thai/English speech to raw text |
| Interpreter Worker | Translates phrase-level text to Formal Business Japanese |
| Glossary Worker | Preserves approved English terms and preferred translations |
| Caption Publisher | Sends captions to Teams native captions or side panel fallback |
| Transcript Writer | Stores timestamped raw text and versions |
| Graph Importer | Imports post-meeting Microsoft Graph transcript |
| Reconciliation Worker | Replaces/corrects canonical transcript after meeting |
| Retention Worker | Deletes raw audio after 30 days |
| Health Monitor | Tracks latency, failure, degraded mode |

This keeps Teams roster clean while allowing scale, retries, and degraded modes.

---

## 5. Main Data Flows

### 5.1 Meeting Discovery And Policy

```text
Outlook/Teams Meeting
  -> SAT Secretary BOT invite or calendar monitor event
  -> Teams Integration Layer
  -> Meeting Registry
  -> Policy Engine
  -> allowed: prepare live session
  -> denied: do not start AI processing
```

Policy result must be immutable audit data. A denied meeting may still include the bot invitation, but the AI services must not process audio or transcript.

### 5.2 Pre-Meeting Context Pack

```text
Invite metadata + agenda + attachments + links + prior meetings
  -> Context Pack Builder
  -> Document Extractor
  -> Preview Generator
  -> Access-controlled Preview Store
  -> Delivery: invite link / Teams chat / email
  -> Read Receipt Logger
```

External guests must be denied at API level.

### 5.3 Live Captions

```text
Teams meeting audio
  -> SAT Secretary BOT media path
  -> Audio Listener
  -> Phrase Segmenter
  -> Streaming STT
  -> Translation to Japanese
  -> Glossary Enforcement
  -> Caption Publisher
      -> Teams native captions/CART if available
      -> Side panel fallback if not available
  -> Transcript Writer
```

Target latency is <2 seconds after phrase completion.

### 5.4 Post-Meeting Transcript Reconciliation

```text
Live transcript v1
  -> canonical transcript
  -> Graph transcript notification/import
  -> Reconciliation Worker
  -> canonical transcript v2
  -> audit/version history
  -> summary/RAG indexing
```

UI shows only the latest canonical transcript by default. Authorized users can inspect history where policy allows.

---

## 6. Teams Integration Strategy

### 6.1 Native Caption Path

Primary path uses Teams-supported real-time captions/CART where available:

- Obtain or configure CART/native caption publishing path
- Start or require captions in meeting
- POST UTF-8 Japanese caption text in readable units
- Monitor response failures
- Fallback to side panel when not available

Key implementation concern: CART URL acquisition and meeting-specific caption activation may require organizer/admin action depending on tenant settings. This must be validated in feasibility spike.

### 6.2 Bot Participant Path

SAT Secretary BOT must be visible in roster. Implementation may require:

- Teams app/bot registration
- Calling/meeting bot capabilities
- Graph permissions/admin consent
- Meeting lifecycle event handling
- Real-time media path for audio if required

The architecture should isolate Teams-specific code into `teams-integration` adapters so the rest of the platform is not coupled to Microsoft-specific payloads.

### 6.3 Graph Transcript Path

Microsoft Graph transcript import is post-meeting only and must not be used for real-time caption SLA. It is used for:

- Higher-confidence post-meeting transcript
- Speaker attribution where tenant settings permit
- Transcript correction/replacement
- Audit source tracking

---

## 7. Proposed Services And Modules

### 7.1 Node.js Core API

Proposed modules:

```text
apps/api/src/routes/teams.ts
apps/api/src/routes/policies.ts
apps/api/src/routes/previews.ts
apps/api/src/routes/liveSessions.ts
apps/api/src/routes/transcripts.ts
apps/api/src/routes/glossaries.ts
apps/api/src/services/teamsClient.ts
apps/api/src/services/policyEngine.ts
apps/api/src/services/captionPublisher.ts
apps/api/src/services/transcriptVersioning.ts
apps/api/src/services/auditLogger.ts
apps/api/src/services/retentionScheduler.ts
```

Responsibilities:

- Receive Teams bot/webhook events
- Store meeting metadata
- Evaluate policy
- Orchestrate live sessions
- Publish caption output
- Enforce access control
- Manage transcript versions
- Deliver preview links/messages

### 7.2 Python AI Worker

Proposed modules:

```text
services/ai-worker/src/live/session.py
services/ai-worker/src/live/audio_buffer.py
services/ai-worker/src/live/segmenter.py
services/ai-worker/src/live/stt_stream.py
services/ai-worker/src/live/translate_stream.py
services/ai-worker/src/live/glossary.py
services/ai-worker/src/live/latency.py
services/ai-worker/src/live/models.py
```

Responsibilities:

- Receive low-latency audio chunks
- Segment phrase-level utterances
- Produce STT partial/final outputs
- Translate to Japanese
- Enforce glossary
- Return caption-ready text to Node.js

### 7.3 Teams Side Panel / Web

Proposed UI modules:

```text
apps/web/src/modules/teams/MeetingPreviewModule.tsx
apps/web/src/modules/teams/LiveFallbackCaptionsModule.tsx
apps/web/src/modules/admin/AdminPoliciesModule.tsx
apps/web/src/modules/admin/GlossaryAdminModule.tsx
apps/web/src/modules/transcripts/TranscriptReviewModule.tsx
```

Responsibilities:

- Preview reader
- Fallback captions
- Policy management
- Glossary approval
- Transcript correction/version review

---

## 8. Data Model

### 8.1 meetings

| Field | Notes |
| --- | --- |
| id | Internal meeting UUID |
| teams_meeting_id | Teams meeting ID |
| graph_resource_id | Microsoft Graph meeting resource ID where available |
| join_url | Teams join URL |
| title | Meeting title |
| organizer_user_id | Internal/Entra user ID |
| tenant_id | Tenant |
| meeting_type | scheduled, recurring, channel, meet_now, ad_hoc |
| start_time | Scheduled start |
| end_time | Scheduled end |
| status | discovered, allowed, denied, live, ended, processed |

### 8.2 meeting_policies

| Field | Notes |
| --- | --- |
| id | Policy UUID |
| meeting_id | Optional specific meeting |
| scope_type | meeting, organizer, group, manual_rule |
| decision | allow, deny |
| enabled_features | captions, transcript, audio_recording, preview |
| created_by | Admin |
| created_at | Timestamp |
| reason | Required for audit |

### 8.3 live_sessions

| Field | Notes |
| --- | --- |
| id | Live session UUID |
| meeting_id | Internal meeting |
| bot_join_status | pending, joined, failed |
| caption_mode | native, side_panel, disabled |
| degraded_state | none, caption_failed, audio_failed, high_latency |
| started_at | Timestamp |
| ended_at | Timestamp |
| metrics_json | Latency and health summary |

### 8.4 transcript_segments

| Field | Notes |
| --- | --- |
| id | Segment UUID |
| meeting_id | Meeting |
| session_id | Live session |
| start_ms | Segment start |
| end_ms | Segment end |
| speaker_id | Optional/best-effort |
| source_language | th/en/mixed |
| raw_text | STT text |
| confidence | STT confidence |
| source | live_stt, graph, human |

### 8.5 caption_segments

| Field | Notes |
| --- | --- |
| id | Caption UUID |
| transcript_segment_id | Source segment |
| target_language | ja |
| caption_text | Japanese caption |
| caption_mode | native, side_panel |
| published_at | Timestamp |
| latency_ms | End-to-end latency |
| status | published, failed, skipped |

### 8.6 transcript_versions

| Field | Notes |
| --- | --- |
| id | Version UUID |
| meeting_id | Meeting |
| version_number | Incrementing |
| source | live_stt, graph_import, human_correction, reconciliation |
| content_json | Canonical transcript payload |
| created_by | User/system |
| created_at | Timestamp |
| replaces_version_id | Previous version |
| reason | Correction/import reason |
| is_canonical | Boolean |

### 8.7 audio_artifacts

| Field | Notes |
| --- | --- |
| id | Audio UUID |
| meeting_id | Meeting |
| storage_path | Object storage path |
| format | wav/mp3/opus |
| mixed_audio | Always true for initial scope |
| created_at | Timestamp |
| expires_at | Meeting end + 30 days |
| deleted_at | Timestamp |
| deletion_status | pending, deleted, failed |

### 8.8 context_packs

| Field | Notes |
| --- | --- |
| id | Context pack UUID |
| meeting_id | Meeting |
| version | Incrementing |
| source_summary | Invite/docs/link source metadata |
| preview_markdown | Generated preview |
| access_scope | internal_only |
| created_at | Timestamp |

### 8.9 preview_read_receipts

| Field | Notes |
| --- | --- |
| id | Receipt UUID |
| context_pack_id | Context pack |
| user_id | Internal user |
| read_at | Timestamp |
| client | web, teams, email_link |

### 8.10 glossary_terms

| Field | Notes |
| --- | --- |
| id | Term UUID |
| scope | org, department, project |
| source_term | English/Thai term |
| target_term | Japanese preferred rendering or preserve marker |
| preserve_english | Boolean |
| approved_by | Admin |
| approved_at | Timestamp |
| status | draft, approved, retired |

---

## 9. API Contracts

### 9.1 Live Audio Chunk To Worker

```json
{
  "session_id": "uuid",
  "meeting_id": "uuid",
  "sequence": 42,
  "timestamp_ms": 123456,
  "sample_rate": 16000,
  "channels": 1,
  "encoding": "pcm16",
  "audio_base64": "...",
  "speaker_hint": null
}
```

### 9.2 Worker Caption Candidate

```json
{
  "session_id": "uuid",
  "meeting_id": "uuid",
  "segment_id": "uuid",
  "start_ms": 123000,
  "end_ms": 125000,
  "source_text": "เราจะ review budget Q3",
  "target_language": "ja",
  "caption_text": "Q3 budget をレビューします。",
  "is_final": true,
  "confidence": 0.91,
  "latency_ms": 850,
  "terms_applied": ["budget", "Q3"]
}
```

### 9.3 Caption Publish Result

```json
{
  "caption_id": "uuid",
  "mode": "native",
  "status": "published",
  "published_at": "2026-07-02T07:00:00Z",
  "latency_ms": 1100,
  "fallback_used": false,
  "error": null
}
```

---

## 10. Degraded Modes

| Failure | Behavior |
| --- | --- |
| Bot cannot join | Meeting continues, organizer/admin notified, no live AI |
| Policy denied | Bot may be present/invited but AI processing does not start |
| Native captions unavailable | Use side panel fallback |
| CART URL expired/invalid | Switch to side panel, log event |
| Audio capture failed | Stop live caption/transcript, wait for Graph transcript after meeting |
| STT high latency | Continue transcript, mark captions degraded |
| Translation failed | Show side panel status, do not publish low-quality captions |
| Graph transcript unavailable | Keep live transcript as canonical |
| Audio deletion failed | Retry and alert admin |

---

## 11. Security Architecture

### 11.1 Access Control

- Internal users authenticate through enterprise identity provider.
- External guests are denied internal artifact routes.
- Authorization must be checked in API middleware for:
  - preview
  - transcript
  - raw audio
  - summary
  - RAG
  - glossary/admin
- Native captions are visible to participants who enable captions in Teams.

### 11.2 Audit Events

Audit must cover:

- meeting discovered
- bot invited
- policy evaluated
- bot joined/failed
- live session started/stopped
- native caption publish failed
- fallback activated
- preview viewed
- transcript imported
- transcript corrected
- transcript canonical version changed
- raw audio deleted
- glossary term approved/retired

### 11.3 Data Retention

- Audio deletion job runs at least daily.
- Expired audio must be deleted from object storage.
- Deletion result must update `audio_artifacts`.
- Transcript remains after audio deletion.

---

## 12. Observability

### 12.1 Metrics

- `bot_join_success_rate`
- `policy_allow_rate`
- `native_caption_publish_success_rate`
- `side_panel_fallback_count`
- `caption_latency_p50_ms`
- `caption_latency_p95_ms`
- `stt_latency_ms`
- `translation_latency_ms`
- `audio_capture_drop_count`
- `graph_transcript_import_success_rate`
- `audio_retention_delete_success_rate`

### 12.2 Logs

Logs must include correlation IDs:

- `meeting_id`
- `session_id`
- `teams_meeting_id`
- `transcript_version_id`
- `caption_id`

Do not log raw audio. Raw text logging should be minimized and protected.

---

## 13. Feasibility Spikes

### Spike 1: Native Teams Caption Publishing

Goal:

- Prove Japanese caption text can be posted to Teams native captions in a real meeting.

Acceptance:

- Japanese captions appear at bottom native caption area.
- Captions are visible only to users who enable captions.
- Failure cases for missing/expired CART URL are understood.
- Side panel fallback trigger is documented.

### Spike 2: Bot Participant And Meeting Lifecycle

Goal:

- Prove SAT Secretary BOT can appear in roster and receive meeting lifecycle events.

Acceptance:

- Bot appears as `SAT Secretary BOT`.
- Meeting start/end events are received.
- Meeting metadata is mapped to internal meeting ID.

### Spike 3: Real-Time Audio Path

Goal:

- Prove legal/platform-compliant audio capture path for live STT.

Acceptance:

- Mixed audio chunks can reach private AI worker.
- Audio format and frame timing are documented.
- Latency budget is measured.

### Spike 4: Graph Transcript Import

Goal:

- Prove post-meeting transcript retrieval and replacement workflow.

Acceptance:

- Graph transcript is imported for a test meeting.
- Canonical transcript version is replaced.
- Previous version remains auditable.

---

## 14. Architecture Decisions

### ADR-001: One Visible Bot, Multiple Internal Workers

Decision: Show one participant, `SAT Secretary BOT`, while internal services split responsibilities.

Reason: Keeps Teams UX simple while allowing scale, retries, and degraded operation.

### ADR-002: Native Captions Primary, Side Panel Fallback

Decision: Use Teams native captions/CART as primary caption channel and side panel as fallback.

Reason: Native captions match user expectation, side panel keeps meeting usable when Teams caption path is unavailable.

### ADR-003: Canonical Transcript With Version History

Decision: UI shows latest canonical transcript, backend stores full version history.

Reason: User wants overwrite behavior, while enterprise audit requires rollback and provenance.

### ADR-004: Raw Audio Temporary, Raw Text Permanent

Decision: Keep mixed audio for 30 days, keep transcript permanently.

Reason: Audio is evidence/reference with higher privacy risk; transcript is corporate knowledge record.

---

## 15. Integration Reference Links

- Teams meeting apps APIs: https://learn.microsoft.com/en-us/microsoftteams/platform/apps-in-teams-meetings/meeting-apps-apis
- Teams real-time media bots: https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts
- Teams transcript/recording Graph APIs: https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/meeting-transcripts/overview-transcripts

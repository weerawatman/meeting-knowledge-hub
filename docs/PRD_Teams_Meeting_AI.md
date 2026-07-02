# Product Requirements Document
## SAT Secretary BOT - Teams Meeting AI Module

Last updated: 2026-07-02

---

## 1. Product Vision

SAT Secretary BOT เป็น AI participant สำหรับ Microsoft Teams ที่ทำหน้าที่เป็นเลขานุการประชุมแบบ enterprise-grade โดยผู้ใช้สามารถเชิญเข้าประชุมเหมือนพนักงานคนหนึ่ง ระบบจะตรวจสอบ Admin Policy ก่อนเริ่มทำงาน แล้วช่วย:

- แสดง subtitle ภาษาญี่ปุ่นแบบ Formal Business Japanese ผ่าน Teams native captions เมื่อเป็นไปได้
- ถอดเสียงเป็น raw transcript สำหรับเก็บเป็น corporate knowledge ถาวร
- เก็บ mixed raw audio เป็นหลักฐานอ้างอิงชั่วคราว 30 วัน
- ส่ง preview/context ให้ผู้ถูกเชิญอ่านก่อนประชุม
- ดึง transcript หลังประชุมจาก Microsoft Graph มาใช้แก้ไขหรือแทนที่ transcript สดได้
- ทำให้ข้อมูลประชุมพร้อมเข้าสู่ RAG และ knowledge search ในขั้นตอนถัดไป

หลักการสำคัญคือ user experience ต้องรู้สึกว่า SAT Secretary BOT เป็นผู้ช่วยประชุมหนึ่งคนใน Teams แต่สถาปัตยกรรมภายในสามารถแยกเป็นหลาย AI services เพื่อความเร็ว ความเสถียร และ degraded mode ที่ดี

---

## 2. Confirmed Decisions

| Topic | Decision |
| --- | --- |
| Bot identity | แสดงใน Teams roster เป็น `SAT Secretary BOT` |
| Bot role | Participant ที่ผู้ใช้เชิญได้เหมือนพนักงานองค์กร |
| Activation policy | ทุก meeting เชิญ bot ได้ แต่ bot เริ่มทำงานเฉพาะ meeting ที่ Admin Policy อนุญาต |
| Attach workflow | รองรับทั้งเชิญ bot เอง และระบบ monitor calendar แล้ว auto-join meeting ที่เข้า policy |
| Caption target | Teams native captions เป็น primary, side panel เป็น fallback |
| Caption audience | เฉพาะผู้ที่เปิด captions |
| Caption SLA | ภาษาญี่ปุ่นขึ้นภายใน <2 วินาทีหลังพูดจบ phrase/ประโยคสั้น |
| Translation style | Formal Business Japanese |
| English terms | คงศัพท์อังกฤษ เช่น KPI, backlog, budget, sprint |
| Glossary | มี glossary ต่อองค์กร/แผนก/โปรเจกต์ โดย Admin เป็นผู้ดูแล/approve |
| Post-meeting transcript | ใช้ Microsoft Graph transcript เพื่อ correct/replace transcript สดได้ |
| Transcript correction | UI แสดง version ล่าสุด แต่ backend เก็บ version history/audit/rollback |
| Raw audio retention | เก็บ mixed raw audio 30 วัน แล้วลบ |
| Raw text retention | เก็บถาวรเป็น corporate record |
| External guests | เห็น subtitle และชื่อ bot ใน roster ได้ แต่เข้าถึง preview/transcript/audio/RAG ไม่ได้ |
| Consent | ใช้ Teams recording notice เป็น baseline |
| Processing boundary | AI processing อยู่ private/on-prem เป็นหลัก ยอมให้ Teams/CART/Graph ผ่าน Microsoft tenant cloud |
| Failure behavior | Meeting ต้องดำเนินต่อแบบ degraded mode |

---

## 3. Target Users

### 3.1 Organizer

ผู้สร้างประชุมใน Outlook/Teams ต้องการเชิญ SAT Secretary BOT เพื่อช่วยแปลและบันทึกความรู้ โดยไม่ต้องเปลี่ยน workflow การนัดประชุมเดิมมากนัก

### 3.2 Internal Participants

พนักงานในองค์กรที่เข้าประชุม ต้องการ subtitle ญี่ปุ่น, preview ก่อนประชุม, และค้นคืนความรู้หลังประชุมได้ตามสิทธิ์

### 3.3 External Guests

ผู้ร่วมประชุมจากภายนอกที่เข้ามาใน Teams meeting ต้องเห็น subtitle ได้ แต่ห้ามเข้าถึง preview, transcript, audio, RAG, หรือเอกสารภายใน

### 3.4 Admin

ผู้ดูแลระบบที่กำหนด policy ว่า meeting ใดอนุญาตให้ bot ทำงาน, จัดการ glossary, ตรวจ audit, และควบคุม retention

---

## 4. Core Jobs To Be Done

1. เมื่อมีการประชุมที่ต้องใช้ภาษาญี่ปุ่น ผู้จัดประชุมอยากเชิญ SAT Secretary BOT เพื่อให้ผู้เข้าร่วมญี่ปุ่นอ่าน subtitle ได้ทันเวลา
2. ก่อนประชุม ผู้ถูกเชิญต้องอ่าน context/preview ได้จาก invite, Teams chat, หรือ email
3. ระหว่างประชุม ระบบต้องแปลไทยปนอังกฤษเป็นญี่ปุ่นแบบ formal business ภายใน latency ที่ยอมรับได้
4. ระหว่างประชุม ระบบต้องถอดเสียงเป็น raw transcript เพื่อเป็น corporate knowledge
5. หลังประชุม ระบบต้องเก็บ transcript ที่แก้ไขแล้วเป็น canonical version และใช้ต่อกับ RAG
6. Admin ต้องควบคุมได้ว่า meeting ใดเปิดใช้ AI ได้ และตรวจย้อนหลังได้ว่า bot ทำอะไร เมื่อไร กับข้อมูลใด

---

## 5. Scope

### 5.1 In Scope

- Detect/attach SAT Secretary BOT to Teams meetings
- Manual invite flow: organizer เชิญ SAT Secretary BOT เป็น participant
- Calendar monitor flow: ระบบตรวจ meeting ที่เข้า policy แล้ว auto-join
- Admin policy allowlist/manual activation
- Context pack ingestion: agenda, files, links, glossary, prior meeting references
- Preview generation and delivery via invite link, Teams chat, and email
- Read receipt for preview access
- Live audio capture path for bot participant
- Streaming STT for Thai speech with possible English terms
- Streaming translation to Japanese
- Caption publishing to Teams native captions when available
- Side panel fallback when native captions/CART is unavailable
- Raw transcript storage with versioning
- Raw audio retention and scheduled deletion after 30 days
- Microsoft Graph transcript ingestion after meeting
- Transcript correction workflow with audit trail
- RAG-ready transcript/document metadata

### 5.2 Out Of Scope For First Production MVP

- Fully autonomous meeting moderation
- AI speaking back into the meeting as audio
- Video/screen analysis
- Real-time action item assignment during live meeting
- External guest access to any internal preview or knowledge artifacts
- Guaranteeing native captions for meeting types where Teams/CART capability is unavailable

---

## 6. User Workflows

### 6.1 Manual Invite Flow

1. Organizer creates meeting in Outlook or Teams
2. Organizer invites `SAT Secretary BOT`
3. SAT Secretary BOT receives meeting invite
4. System resolves organizer, attendees, meeting type, tenant, start/end time, and join URL
5. Policy Engine checks whether the meeting is allowed
6. If allowed, bot accepts and prepares context/session
7. If not allowed, bot does not start AI work and optionally sends internal notice to organizer/admin
8. Before meeting, system sends preview link through configured channels
9. At meeting start, bot joins as participant
10. Caption path starts if native captions/CART is available; otherwise side panel fallback is activated

### 6.2 Calendar Monitor Auto-Join Flow

1. System monitors eligible calendars or meeting events
2. Policy Engine evaluates meeting metadata against manual Admin Policy
3. If meeting is approved, system attaches SAT Secretary BOT or schedules join
4. Organizer receives notice that SAT Secretary BOT will join
5. Context pack and preview are generated
6. Live session starts when meeting starts

### 6.3 Pre-Meeting Preview Flow

1. Organizer uploads/links supporting documents or relies on meeting invite content
2. System extracts text and creates context pack
3. AI generates preview:
   - meeting purpose
   - agenda summary
   - relevant prior decisions
   - unresolved action items
   - key terms/glossary
   - risk/conflict points
4. Preview is delivered via:
   - invite link
   - Teams chat
   - email
5. Read receipt is logged for internal participants
6. External guests are blocked from preview access

### 6.4 Live Caption Flow

1. SAT Secretary BOT joins meeting
2. Media listener receives mixed audio stream
3. Audio is segmented by phrase/short utterance
4. Streaming STT creates Thai/English interim transcript
5. Translation service converts to Formal Business Japanese
6. Glossary service preserves approved English terms and preferred translations
7. Caption Publisher posts Japanese subtitle to Teams native captions when available
8. If native caption publishing fails, side panel fallback displays captions
9. Transcript Writer stores raw text segments with timestamps and confidence
10. Health Monitor logs latency and degraded mode events

### 6.5 Post-Meeting Flow

1. Live session ends
2. Raw audio is sealed with retention expiry date = meeting end + 30 days
3. Live transcript becomes initial canonical transcript version
4. System waits for Microsoft Graph transcript availability
5. If Graph transcript is available and policy allows, system imports it
6. Transcript reconciliation job compares live transcript and Graph transcript
7. Latest corrected transcript replaces UI-visible transcript
8. Prior versions remain in audit/version history
9. Summary/action item/RAG indexing jobs run on canonical transcript

---

## 7. Functional Requirements

### 7.1 Teams Meeting Integration

- The system must support SAT Secretary BOT as a visible Teams participant.
- The system must support manual invitation to SAT Secretary BOT.
- The system should support calendar monitoring for auto-join where permissions and tenant policies allow.
- The system must store Teams meeting IDs, join URLs, organizer identity, tenant identity, and meeting type.
- The system must handle scheduled, recurring, channel, Meet Now, and ad hoc meetings as target scope, with MVP prioritization defined in roadmap.

### 7.2 Admin Policy

- Admin can manually allow or deny AI activation per meeting or meeting pattern.
- Default behavior: bot can be invited, but AI features do not start unless meeting is allowed.
- Policy decision must be logged.
- Policy can later expand to organizer group, sensitivity label, department, or keyword.

### 7.3 Live Captions

- Primary target: Teams native captions using supported Teams/CART real-time caption capability.
- Fallback target: SAT side panel inside Teams or web app.
- Captions must be Japanese.
- Captions must use Formal Business Japanese.
- English business/technical terms approved in glossary must remain English.
- Captions should appear within <2 seconds after phrase completion.
- Captions should be sent in readable units, avoiding long lines.

### 7.4 Streaming STT

- Must support Thai speech with mixed English terminology.
- Must segment audio into short phrase-level chunks suitable for low-latency translation.
- Must store timestamped raw text.
- Must store confidence and source metadata.
- Speaker identification is best-effort in live mode unless Teams/media path provides reliable speaker metadata.

### 7.5 Transcript Management

- Raw text is retained permanently as corporate record.
- UI shows latest canonical transcript.
- Backend stores transcript versions.
- Corrections and imported Graph transcript can replace canonical version.
- Every replacement must keep audit history:
  - actor/system
  - source
  - timestamp
  - diff or replacement reason
  - previous version pointer

### 7.6 Audio Retention

- Mixed raw audio is stored for 30 days.
- System must automatically delete expired audio.
- Audio deletion must be auditable.
- Transcript and derived knowledge remain after audio deletion.

### 7.7 External Guest Controls

- External guests can see subtitle and bot name in roster.
- External guests cannot access:
  - preview/context pack
  - raw transcript
  - corrected transcript
  - raw audio
  - meeting summaries
  - RAG search
  - internal document attachments
- Access control must be enforced server-side, not only UI-side.

### 7.8 Preview And Read Receipt

- Preview link must support invite/email/Teams chat delivery.
- Internal participants must authenticate before viewing preview.
- Read receipt must capture viewer, time, meeting, and preview version.
- External users must be denied.

---

## 8. Non-Functional Requirements

### 8.1 Latency

- P50 caption latency: <= 1.2 seconds after phrase completion
- P95 caption latency: <= 2.0 seconds after phrase completion
- Degraded mode starts when P95 exceeds 4 seconds for more than 2 minutes

### 8.2 Availability

- Meeting should continue if AI fails.
- Bot failures must not block Teams meeting.
- Caption publisher failure must fallback to side panel.
- Graph transcript import failure must not erase live transcript.

### 8.3 Security

- Least privilege for Microsoft Graph and Teams permissions.
- Tenant admin consent required for privileged scopes.
- Internal access must be role/policy based.
- All transcript/audio/preview access must be audited.
- Secrets must not be stored in source code.

### 8.4 Privacy And Compliance

- Teams recording notice is baseline consent.
- Audio retention must be enforced automatically.
- Raw text is corporate record and retained permanently.
- External guest access is denied for internal artifacts.
- Admin must be able to review policy and audit logs.

### 8.5 Observability

- Track bot join success rate.
- Track caption publish success rate.
- Track STT latency, translation latency, and end-to-end latency.
- Track CART/native caption failures.
- Track side panel fallback activation.
- Track audio retention deletion jobs.
- Track transcript version changes.

---

## 9. MVP Definition

### 9.1 MVP Must Have

- Manual invite SAT Secretary BOT
- Admin manual allowlist
- Scheduled Teams meeting support
- Context preview page with internal access control
- Preview delivery link via email or Teams message
- Read receipt for internal users
- Live phrase-level STT pipeline prototype
- Japanese caption publishing feasibility using Teams native/CART path
- Side panel fallback
- Transcript storage with versions
- Raw audio storage with 30-day retention metadata
- Post-meeting Graph transcript import spike

### 9.2 MVP Acceptance Criteria

- Internal organizer can invite SAT Secretary BOT to a scheduled Teams meeting.
- Bot appears in roster as `SAT Secretary BOT`.
- If Admin Policy allows the meeting, bot starts live session.
- Japanese captions appear in Teams native captions when CART/native caption path is configured and captions are enabled.
- If caption path fails, side panel displays captions.
- Caption P95 latency is under 2 seconds after phrase completion in controlled 3-person test.
- Raw transcript is stored and visible only to authorized internal users.
- External guest cannot open preview/transcript/audio/RAG endpoints.
- Raw audio is stored with expiry date and deletion job can remove it.
- Transcript correction creates a new canonical version while preserving old version.

---

## 10. Risks And Open Constraints

### 10.1 High-Risk Feasibility Items

- Whether Teams native captions can be reliably controlled for every desired meeting type.
- Whether CART URL acquisition can be automated or requires organizer action.
- Whether SAT Secretary BOT can receive real-time audio in the required scenarios without violating Teams platform constraints.
- Whether <2 second latency is achievable with on-prem STT + translation under real meeting noise.
- Whether external guests can be restricted from all internal artifacts while still seeing native Teams captions.

### 10.2 Product Trade-Offs

- Native captions are best UX but more dependent on Teams capabilities and meeting configuration.
- Side panel fallback is more controllable but not equivalent to bottom native captions.
- Real-time media bot provides raw audio but has high implementation and infrastructure cost.
- Graph transcript is useful after meeting but cannot satisfy real-time subtitle SLA.

---

## 11. Reference Links

- Microsoft Teams meeting apps APIs: https://learn.microsoft.com/en-us/microsoftteams/platform/apps-in-teams-meetings/meeting-apps-apis
- Microsoft Teams real-time media bots: https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts
- Microsoft Graph meeting transcripts: https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/meeting-transcripts/overview-transcripts

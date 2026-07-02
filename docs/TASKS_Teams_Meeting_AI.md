# Implementation Roadmap
## SAT Secretary BOT - Teams Meeting AI Module

Last updated: 2026-07-02

---

## Legend

| Symbol | Meaning |
| --- | --- |
| `[ ]` | Not started |
| `[~]` | In progress/scaffold exists |
| `[x]` | Done and verified |
| `[!]` | Blocked or high-risk dependency |

---

## Phase 0: Project Hygiene And Alignment

- [ ] Normalize existing Thai documentation encoding to UTF-8.
- [ ] Add the SAT Secretary BOT decision log to the main project index/README.
- [ ] Create ADR folder or section for Teams AI decisions.
- [ ] Review current `LiveModule` placeholder and align labels with SAT Secretary BOT.
- [ ] Identify environment variables needed for Teams/Graph/CART integration.
- [ ] Define local development strategy for Teams webhook callbacks.
- [ ] Confirm tenant/admin prerequisites with Microsoft 365 administrator.

Deliverable:

- Docs are readable.
- Team agrees that this module is a new Teams-focused track, not just Sprint 5 placeholder.

---

## Phase 1: Feasibility Spikes

### 1.1 Native Caption / CART Spike

- [ ] Create a test Teams meeting with captions enabled.
- [ ] Obtain CART/native caption publishing path according to tenant capability.
- [ ] Send UTF-8 Japanese caption text to the meeting.
- [ ] Confirm captions appear in Teams native caption area.
- [ ] Measure caption publish latency.
- [ ] Test missing captions enabled state.
- [ ] Test invalid/expired CART URL behavior.
- [ ] Document exact setup steps and tenant settings.
- [ ] Decide whether CART URL setup can be automated or needs organizer/admin action.

Exit criteria:

- Japanese native caption publishing is proven or rejected.
- Side panel fallback conditions are documented.

### 1.2 Bot Participant Spike

- [ ] Register Teams app/bot for `SAT Secretary BOT`.
- [ ] Configure bot display name and tenant installation.
- [ ] Invite bot to a scheduled meeting.
- [ ] Confirm bot appears in roster.
- [ ] Receive meeting start/end event.
- [ ] Map Teams meeting metadata to internal meeting record.
- [ ] Validate behavior with internal users.
- [ ] Validate behavior with external guest present.

Exit criteria:

- Bot is visible as participant.
- Lifecycle events are received.

### 1.3 Real-Time Audio Path Spike

- [ ] Evaluate Teams-supported audio access path for participant bot.
- [ ] Prototype mixed audio capture for a test meeting.
- [ ] Stream audio chunks to local/private service.
- [ ] Confirm sample rate, encoding, frame duration, and buffering.
- [ ] Measure audio capture latency.
- [ ] Validate Teams recording notice/tenant compliance assumptions.
- [ ] Document infrastructure requirements if application-hosted media bot is required.

Exit criteria:

- Legal/platform-compliant audio path is known.
- Infrastructure cost and complexity are understood.

### 1.4 Graph Transcript Spike

- [ ] Configure Graph permissions for transcript access in test tenant.
- [ ] Subscribe or poll for transcript availability after meeting.
- [ ] Fetch transcript content.
- [ ] Store transcript as a new transcript version.
- [ ] Replace canonical transcript.
- [ ] Audit replacement.
- [ ] Test case where speaker attribution is unavailable.

Exit criteria:

- Post-meeting transcript import works or required tenant blockers are known.

---

## Phase 2: Data Foundation

### 2.1 Database Schema

- [ ] Add `meetings` table.
- [ ] Add `meeting_policies` table.
- [ ] Add `live_sessions` table.
- [ ] Add `transcript_segments` table.
- [ ] Add `caption_segments` table.
- [ ] Add `transcript_versions` table.
- [ ] Add `audio_artifacts` table.
- [ ] Add `context_packs` table.
- [ ] Add `preview_read_receipts` table.
- [ ] Add `glossary_terms` table.
- [ ] Add `audit_logs` table if current audit layer is insufficient.
- [ ] Add migrations and seed data for local development.

### 2.2 Storage

- [ ] Define raw audio object storage path convention.
- [ ] Define context attachment storage path convention.
- [ ] Define preview artifact storage path convention.
- [ ] Add retention metadata for audio.
- [ ] Ensure storage paths are tenant/meeting scoped.

### 2.3 Access Control

- [ ] Define internal participant role.
- [ ] Define external guest role.
- [ ] Define organizer role.
- [ ] Define admin role.
- [ ] Add server-side guards for preview routes.
- [ ] Add server-side guards for transcript routes.
- [ ] Add server-side guards for audio routes.
- [ ] Add server-side guards for RAG routes.
- [ ] Add tests that external guests are denied internal artifacts.

Exit criteria:

- Core persistence supports policy, live session, captions, transcript versions, audio retention, and access control.

---

## Phase 3: Teams Integration Layer

### 3.1 Teams App/Bot Adapter

- [ ] Add `apps/api/src/routes/teams.ts`.
- [ ] Add Teams webhook signature/auth validation.
- [ ] Store bot invite events.
- [ ] Store meeting start events.
- [ ] Store meeting end events.
- [ ] Store join/leave state.
- [ ] Map Teams IDs to internal meeting IDs.
- [ ] Emit audit events for Teams lifecycle.

### 3.2 Calendar Monitor

- [ ] Add Graph/calendar client abstraction.
- [ ] Monitor eligible calendars or meeting notifications.
- [ ] Detect meetings that match Admin Policy.
- [ ] Schedule bot auto-join where supported.
- [ ] Notify organizer when auto-join is planned.
- [ ] Avoid duplicate sessions if bot was manually invited.

### 3.3 Meeting Registry

- [ ] Add create/update meeting record from Teams event.
- [ ] Add idempotency key for repeated Teams events.
- [ ] Add meeting type detection.
- [ ] Add organizer and attendee resolution.
- [ ] Add external guest detection.

Exit criteria:

- The system can discover Teams meetings and associate them with internal records.

---

## Phase 4: Admin Policy

### 4.1 Policy Engine

- [ ] Add `policyEngine.ts`.
- [ ] Implement manual allow/deny decision per meeting.
- [ ] Return feature flags: captions, transcript, audio recording, preview.
- [ ] Log policy decision with reason.
- [ ] Prevent AI processing when denied.
- [ ] Add policy tests.

### 4.2 Admin UI

- [ ] Create Admin Policy module.
- [ ] List discovered meetings.
- [ ] Allow/deny selected meeting.
- [ ] Show policy status and reason.
- [ ] Show bot invited but AI disabled state.
- [ ] Add audit view for policy decisions.

Exit criteria:

- Every live session start is gated by Admin Policy.

---

## Phase 5: Context Pack And Preview

### 5.1 Context Pack Builder

- [ ] Parse meeting title/body/agenda.
- [ ] Support uploaded supporting files.
- [ ] Support links where permitted.
- [ ] Pull relevant prior meeting records.
- [ ] Apply access scope `internal_only`.
- [ ] Generate context pack version.

### 5.2 Preview Generator

- [ ] Generate meeting purpose summary.
- [ ] Generate agenda preview.
- [ ] Generate prior decisions section.
- [ ] Generate unresolved action items section.
- [ ] Generate key terms/glossary section.
- [ ] Generate risks/open questions section.
- [ ] Store preview markdown.

### 5.3 Delivery And Read Receipts

- [ ] Create preview route.
- [ ] Deliver preview link in email.
- [ ] Deliver preview link in Teams chat where permitted.
- [ ] Include preview link in invite flow where permitted.
- [ ] Log read receipt for internal users.
- [ ] Deny external guest access.
- [ ] Add read receipt UI for organizer/admin.

Exit criteria:

- Internal participants can read preview and organizer/admin can see read receipts.

---

## Phase 6: Live AI Pipeline

### 6.1 Live Session Orchestrator

- [ ] Add live session state machine.
- [ ] Support states: scheduled, joining, live, degraded, ended, failed.
- [ ] Start only after policy allow.
- [ ] Track bot join state.
- [ ] Track caption mode.
- [ ] Track audio state.
- [ ] Publish live health events over WebSocket.

### 6.2 Audio Listener

- [ ] Implement accepted audio chunk contract.
- [ ] Buffer mixed audio safely.
- [ ] Write raw audio artifact.
- [ ] Forward chunks to Python worker.
- [ ] Detect audio dropouts.
- [ ] Stop audio write when session ends.
- [ ] Store audio artifact expiry at meeting end + 30 days.

### 6.3 Python Streaming STT

- [ ] Add live audio buffer.
- [ ] Add phrase segmenter.
- [ ] Add streaming STT endpoint.
- [ ] Optimize for Thai speech with English terms.
- [ ] Return partial/final segment events.
- [ ] Include confidence and timestamps.
- [ ] Measure STT latency.

### 6.4 Translation

- [ ] Add Thai/English to Japanese translation path.
- [ ] Enforce Formal Business Japanese style.
- [ ] Preserve glossary-approved English terms.
- [ ] Return caption-ready short text.
- [ ] Measure translation latency.

### 6.5 Caption Publisher

- [ ] Add native/CART caption adapter.
- [ ] Add side panel caption adapter.
- [ ] Publish Japanese caption candidate to native path.
- [ ] Respect caption line length/readability constraints.
- [ ] Detect native caption failures.
- [ ] Fallback to side panel.
- [ ] Store caption segment publish result.

Exit criteria:

- Controlled test meeting shows Japanese captions with P95 <2 seconds after phrase completion.

---

## Phase 7: Transcript Management

### 7.1 Live Transcript Storage

- [ ] Persist transcript segments.
- [ ] Link transcript segments to caption segments.
- [ ] Create initial transcript version from live transcript.
- [ ] Mark initial transcript version canonical.
- [ ] Add transcript viewer UI.

### 7.2 Correction Workflow

- [ ] Add transcript correction API.
- [ ] Create new transcript version on correction.
- [ ] Mark new version canonical.
- [ ] Preserve previous version.
- [ ] Store actor, reason, timestamp.
- [ ] Add rollback function for admins.

### 7.3 Graph Transcript Import

- [ ] Import Graph transcript after meeting.
- [ ] Normalize Graph transcript format.
- [ ] Create Graph transcript version.
- [ ] Reconcile/replace canonical transcript.
- [ ] Record speaker attribution availability.
- [ ] Audit import and canonical change.

Exit criteria:

- UI displays latest transcript while backend preserves full version history.

---

## Phase 8: Retention And Governance

### 8.1 Audio Retention

- [ ] Add scheduled retention job.
- [ ] Find expired audio artifacts.
- [ ] Delete audio object.
- [ ] Mark artifact as deleted.
- [ ] Audit deletion result.
- [ ] Retry failed deletions.
- [ ] Alert admin after repeated failures.

### 8.2 Audit

- [ ] Add audit logger interface.
- [ ] Log policy decisions.
- [ ] Log preview access.
- [ ] Log bot join/failure.
- [ ] Log live session state transitions.
- [ ] Log caption fallback.
- [ ] Log transcript imports/corrections.
- [ ] Log audio deletion.
- [ ] Add audit search UI.

### 8.3 Governance Tests

- [ ] Test external guest cannot access preview.
- [ ] Test external guest cannot access transcript.
- [ ] Test external guest cannot access audio.
- [ ] Test audio retention deletes expired audio.
- [ ] Test transcript remains after audio deletion.
- [ ] Test canonical transcript change is auditable.

Exit criteria:

- Retention and audit controls are enforceable and tested.

---

## Phase 9: RAG-Ready Knowledge Integration

- [ ] Chunk canonical transcript into retrieval units.
- [ ] Preserve meeting metadata in vector payload.
- [ ] Preserve access scope/category metadata.
- [ ] Index transcript chunks to Qdrant.
- [ ] Exclude unauthorized/external access at query time.
- [ ] Re-index when canonical transcript changes.
- [ ] Track source transcript version in vector metadata.
- [ ] Add citation fields for meeting/time/speaker.

Exit criteria:

- Knowledge Chat can answer from canonical meeting transcripts with access filtering and citations.

---

## Phase 10: Reliability And Degraded Mode

- [ ] Implement degraded mode state machine.
- [ ] Add bot join failure notice.
- [ ] Add native caption failure fallback.
- [ ] Add audio capture failure handling.
- [ ] Add high latency warning.
- [ ] Add Graph transcript fallback if live transcript failed.
- [ ] Add admin dashboard for live session health.
- [ ] Add synthetic test for caption publisher.
- [ ] Add load test for multiple simultaneous meetings.

Exit criteria:

- Meeting can proceed when AI services fail, and failures are visible/audited.

---

## Phase 11: Testing Matrix

### Meeting Types

- [ ] Scheduled meeting
- [ ] Recurring meeting
- [ ] Channel meeting
- [ ] Meet Now
- [ ] Ad hoc call/group call where supported

### Participants

- [ ] Internal only
- [ ] Internal + external guest
- [ ] Organizer absent
- [ ] Bot invited manually
- [ ] Bot auto-joined by policy

### Caption Cases

- [ ] Native captions available
- [ ] Captions not enabled
- [ ] CART URL expired/invalid
- [ ] Side panel fallback
- [ ] High latency
- [ ] Japanese text with English terms

### Governance Cases

- [ ] Policy allow
- [ ] Policy deny
- [ ] External guest denied preview
- [ ] External guest denied transcript
- [ ] Audio deleted after 30 days
- [ ] Transcript retained after audio deletion
- [ ] Transcript version rollback

---

## Phase 12: Production Readiness

- [ ] Tenant admin consent documented.
- [ ] Teams app manifest finalized.
- [ ] Secrets and certificates stored outside repo.
- [ ] Monitoring dashboard created.
- [ ] Alert rules created.
- [ ] Backup/restore process documented.
- [ ] Incident playbook created.
- [ ] User/admin guide created.
- [ ] Security review completed.
- [ ] Pilot rollout plan approved.

---

## Recommended MVP Order

1. Native caption/CART spike
2. Bot participant spike
3. Graph transcript spike
4. Data model/migrations
5. Admin manual allowlist
6. Manual invite flow
7. Context preview/read receipts
8. Live STT/translation/caption prototype
9. Transcript versioning
10. Audio retention
11. Side panel fallback
12. RAG indexing

---

## Current Codebase Mapping

| Current Area | Status | Needed Evolution |
| --- | --- | --- |
| `apps/web/src/modules/live/LiveModule.tsx` | Placeholder | Replace with live session dashboard and side panel fallback |
| `apps/api/src/app.ts` WebSocket `audio_chunk` | Placeholder | Route audio chunks to live AI worker and persist session state |
| `apps/api/src/routes/meetings.ts` | Batch upload focused | Add Teams meeting registry and transcript version APIs |
| `services/ai-worker/src/stt/pipeline.py` | Batch STT chunks | Add low-latency streaming STT path |
| `services/ai-worker/src/speaker_id/diarize.py` | Heuristic diarization | Treat speaker ID as best-effort/live optional; rely on Graph where available |
| `services/ai-worker/src/pipeline/orchestrator.py` | Batch pipeline | Add live session pipeline separate from batch |
| `services/ai-worker/src/governance/retention.py` | Existing governance area | Extend for 30-day audio deletion with audit |
| `services/ai-worker/src/rag/store.py` | RAG scaffold | Index canonical transcript versions with access metadata |

---

## First Engineering Milestone

Milestone name: `SAT-M1 Feasibility Lock`

Goal:

Prove or reject the platform-critical assumptions before building full production workflow.

Tasks:

- [ ] SAT Secretary BOT appears as participant in test Teams meeting.
- [ ] Meeting lifecycle event reaches Node.js API.
- [ ] Japanese caption can be published to native Teams captions or limitation is documented.
- [ ] Side panel fallback can display captions.
- [ ] Graph transcript can be imported after a test meeting or tenant blocker is documented.
- [ ] Architecture decision is updated based on spike results.

Success:

- The team can make a go/no-go decision for native captions + live audio path with real tenant evidence.

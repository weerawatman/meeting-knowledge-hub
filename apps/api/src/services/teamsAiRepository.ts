import { v4 as uuidv4 } from "uuid";

export type MeetingType = "scheduled" | "recurring" | "channel" | "meet_now" | "ad_hoc";
export type MeetingStatus = "discovered" | "allowed" | "denied" | "live" | "ended" | "processed";
export type PolicyDecision = "allow" | "deny";
export type CaptionMode = "native" | "side_panel" | "disabled";
export type DegradedState = "none" | "caption_failed" | "audio_failed" | "high_latency";
export type TranscriptSource = "live_stt" | "graph_import" | "human_correction" | "reconciliation";

export interface TeamsMeeting {
  id: string;
  teams_meeting_id: string;
  graph_resource_id?: string;
  join_url: string;
  title: string;
  organizer_user_id: string;
  tenant_id: string;
  meeting_type: MeetingType;
  start_time: string;
  end_time: string;
  status: MeetingStatus;
  external_guest_count: number;
  bot_invited: boolean;
  created_at: string;
  updated_at: string;
}

export interface MeetingPolicy {
  id: string;
  meeting_id: string;
  decision: PolicyDecision;
  enabled_features: {
    captions: boolean;
    transcript: boolean;
    audio_recording: boolean;
    preview: boolean;
  };
  reason: string;
  created_by: string;
  created_at: string;
}

export interface LiveSession {
  id: string;
  meeting_id: string;
  bot_join_status: "pending" | "joined" | "failed";
  caption_mode: CaptionMode;
  degraded_state: DegradedState;
  started_at?: string;
  ended_at?: string;
  metrics: {
    caption_latency_p50_ms: number;
    caption_latency_p95_ms: number;
    stt_latency_ms: number;
    translation_latency_ms: number;
  };
}

export interface ContextPack {
  id: string;
  meeting_id: string;
  version: number;
  preview_markdown: string;
  access_scope: "internal_only";
  created_at: string;
}

export interface PreviewReadReceipt {
  id: string;
  context_pack_id: string;
  user_id: string;
  read_at: string;
  client: "web" | "teams" | "email_link";
}

export interface TranscriptVersion {
  id: string;
  meeting_id: string;
  version_number: number;
  source: TranscriptSource;
  content: {
    language: string;
    segments: Array<{
      timestamp: string;
      speaker?: string;
      text: string;
      confidence?: number;
    }>;
  };
  created_by: string;
  created_at: string;
  replaces_version_id?: string;
  reason: string;
  is_canonical: boolean;
}

export interface GlossaryTerm {
  id: string;
  scope: "org" | "department" | "project";
  source_term: string;
  target_term: string;
  preserve_english: boolean;
  approved_by: string;
  approved_at: string;
  status: "draft" | "approved" | "retired";
}

export interface AudioArtifact {
  id: string;
  meeting_id: string;
  storage_path: string;
  format: "wav" | "mp3" | "opus";
  mixed_audio: true;
  created_at: string;
  expires_at: string;
  deleted_at?: string;
  deletion_status: "pending" | "deleted" | "failed";
}

export interface AuditLog {
  id: string;
  meeting_id?: string;
  action: string;
  actor: string;
  created_at: string;
  detail: Record<string, unknown>;
}

const nowIso = () => new Date().toISOString();

const addDaysIso = (days: number) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString();
};

class TeamsAiRepository {
  private meetings = new Map<string, TeamsMeeting>();
  private policies = new Map<string, MeetingPolicy>();
  private liveSessions = new Map<string, LiveSession>();
  private contextPacks = new Map<string, ContextPack>();
  private readReceipts = new Map<string, PreviewReadReceipt>();
  private transcriptVersions = new Map<string, TranscriptVersion>();
  private glossaryTerms = new Map<string, GlossaryTerm>();
  private audioArtifacts = new Map<string, AudioArtifact>();
  private auditLogs: AuditLog[] = [];

  constructor() {
    this.seed();
  }

  getOverview() {
    const meetings = this.listMeetings();
    const sessions = this.listLiveSessions();
    return {
      bot_name: "SAT Secretary BOT",
      milestone: "SAT-M1 Feasibility Lock",
      feasibility_gates: [
        { id: "native_captions", label: "Native Teams captions/CART", status: "needs_spike" },
        { id: "bot_participant", label: "Bot participant roster presence", status: "needs_spike" },
        { id: "audio_path", label: "Real-time mixed audio path", status: "needs_spike" },
        { id: "graph_transcript", label: "Post-meeting Graph transcript import", status: "needs_spike" },
      ],
      counts: {
        meetings: meetings.length,
        policies: this.policies.size,
        live_sessions: sessions.length,
        glossary_terms: this.glossaryTerms.size,
        audit_events: this.auditLogs.length,
      },
      active_sessions: sessions.filter((session) => !session.ended_at),
      recent_meetings: meetings.slice(0, 5),
      recent_audit: this.auditLogs.slice(-8).reverse(),
    };
  }

  listMeetings() {
    return Array.from(this.meetings.values()).sort((a, b) =>
      b.start_time.localeCompare(a.start_time)
    );
  }

  getMeeting(meetingId: string) {
    return this.meetings.get(meetingId);
  }

  upsertMeeting(input: Partial<TeamsMeeting> & Pick<TeamsMeeting, "title" | "join_url">) {
    const id = input.id || uuidv4();
    const existing = this.meetings.get(id);
    const timestamp = nowIso();
    const meeting: TeamsMeeting = {
      id,
      teams_meeting_id: input.teams_meeting_id || existing?.teams_meeting_id || `teams-${id}`,
      graph_resource_id: input.graph_resource_id || existing?.graph_resource_id,
      join_url: input.join_url,
      title: input.title,
      organizer_user_id: input.organizer_user_id || existing?.organizer_user_id || "unknown",
      tenant_id: input.tenant_id || existing?.tenant_id || "tenant-local",
      meeting_type: input.meeting_type || existing?.meeting_type || "scheduled",
      start_time: input.start_time || existing?.start_time || timestamp,
      end_time: input.end_time || existing?.end_time || timestamp,
      status: input.status || existing?.status || "discovered",
      external_guest_count: input.external_guest_count ?? existing?.external_guest_count ?? 0,
      bot_invited: input.bot_invited ?? existing?.bot_invited ?? true,
      created_at: existing?.created_at || timestamp,
      updated_at: timestamp,
    };
    this.meetings.set(id, meeting);
    this.audit("meeting_discovered", "system", { meeting_id: id }, id);
    return meeting;
  }

  setPolicy(
    meetingId: string,
    decision: PolicyDecision,
    actor: string,
    reason: string,
    enabledFeatures?: MeetingPolicy["enabled_features"]
  ) {
    const meeting = this.requireMeeting(meetingId);
    const policy: MeetingPolicy = {
      id: uuidv4(),
      meeting_id: meetingId,
      decision,
      enabled_features:
        enabledFeatures || {
          captions: decision === "allow",
          transcript: decision === "allow",
          audio_recording: decision === "allow",
          preview: decision === "allow",
        },
      reason,
      created_by: actor,
      created_at: nowIso(),
    };
    this.policies.set(meetingId, policy);
    meeting.status = decision === "allow" ? "allowed" : "denied";
    meeting.updated_at = nowIso();
    this.audit("policy_evaluated", actor, { decision, reason }, meetingId);
    return policy;
  }

  getPolicy(meetingId: string) {
    return this.policies.get(meetingId);
  }

  evaluatePolicy(meetingId: string) {
    const policy = this.policies.get(meetingId);
    if (!policy) {
      return {
        decision: "deny" as PolicyDecision,
        allowed: false,
        reason: "No admin policy exists for this meeting",
        enabled_features: {
          captions: false,
          transcript: false,
          audio_recording: false,
          preview: false,
        },
      };
    }
    return {
      decision: policy.decision,
      allowed: policy.decision === "allow",
      reason: policy.reason,
      enabled_features: policy.enabled_features,
    };
  }

  startLiveSession(meetingId: string, actor: string) {
    const meeting = this.requireMeeting(meetingId);
    const decision = this.evaluatePolicy(meetingId);
    if (!decision.allowed) {
      this.audit("live_session_denied", actor, { reason: decision.reason }, meetingId);
      return { started: false, reason: decision.reason, session: null };
    }

    const existing = this.listLiveSessions().find(
      (session) => session.meeting_id === meetingId && !session.ended_at
    );
    if (existing) {
      return { started: true, reason: "Live session already active", session: existing };
    }

    const session: LiveSession = {
      id: uuidv4(),
      meeting_id: meetingId,
      bot_join_status: "joined",
      caption_mode: "native",
      degraded_state: "none",
      started_at: nowIso(),
      metrics: {
        caption_latency_p50_ms: 0,
        caption_latency_p95_ms: 0,
        stt_latency_ms: 0,
        translation_latency_ms: 0,
      },
    };
    this.liveSessions.set(session.id, session);
    meeting.status = "live";
    meeting.updated_at = nowIso();
    const audioId = uuidv4();
    this.audioArtifacts.set(audioId, {
      id: audioId,
      meeting_id: meetingId,
      storage_path: `audio/${meetingId}/mixed-audio.wav`,
      format: "wav",
      mixed_audio: true,
      created_at: nowIso(),
      expires_at: addDaysIso(30),
      deletion_status: "pending",
    });
    this.audit("live_session_started", actor, { session_id: session.id }, meetingId);
    return { started: true, reason: "Live session started", session };
  }

  listLiveSessions() {
    return Array.from(this.liveSessions.values()).sort((a, b) =>
      (b.started_at || "").localeCompare(a.started_at || "")
    );
  }

  getLiveSession(sessionId: string) {
    return this.liveSessions.get(sessionId);
  }

  publishCaption(sessionId: string, captionText: string, actor: string) {
    const session = this.liveSessions.get(sessionId);
    if (!session) {
      throw new Error("Live session not found");
    }
    const latency = Math.max(250, Math.min(1900, captionText.length * 18));
    session.metrics.caption_latency_p50_ms = latency;
    session.metrics.caption_latency_p95_ms = Math.min(2100, latency + 220);
    session.metrics.stt_latency_ms = Math.round(latency * 0.45);
    session.metrics.translation_latency_ms = Math.round(latency * 0.35);
    this.audit(
      "caption_published",
      actor,
      {
        session_id: sessionId,
        mode: session.caption_mode,
        latency_ms: session.metrics.caption_latency_p95_ms,
      },
      session.meeting_id
    );
    return {
      caption_id: uuidv4(),
      mode: session.caption_mode,
      status: "published",
      published_at: nowIso(),
      latency_ms: session.metrics.caption_latency_p95_ms,
      fallback_used: session.caption_mode === "side_panel",
      error: null,
    };
  }

  activateSidePanelFallback(sessionId: string, actor: string, reason: string) {
    const session = this.liveSessions.get(sessionId);
    if (!session) {
      throw new Error("Live session not found");
    }
    session.caption_mode = "side_panel";
    session.degraded_state = "caption_failed";
    this.audit("caption_fallback_activated", actor, { session_id: sessionId, reason }, session.meeting_id);
    return session;
  }

  getLatestContextPack(meetingId: string) {
    return Array.from(this.contextPacks.values())
      .filter((pack) => pack.meeting_id === meetingId)
      .sort((a, b) => b.version - a.version)[0];
  }

  recordPreviewRead(meetingId: string, userId: string, client: PreviewReadReceipt["client"]) {
    const pack = this.getLatestContextPack(meetingId);
    if (!pack) {
      throw new Error("Context pack not found");
    }
    const receipt: PreviewReadReceipt = {
      id: uuidv4(),
      context_pack_id: pack.id,
      user_id: userId,
      read_at: nowIso(),
      client,
    };
    this.readReceipts.set(receipt.id, receipt);
    this.audit("preview_viewed", userId, { context_pack_id: pack.id, client }, meetingId);
    return receipt;
  }

  listPreviewReadReceipts(meetingId: string) {
    const pack = this.getLatestContextPack(meetingId);
    if (!pack) {
      return [];
    }
    return Array.from(this.readReceipts.values()).filter(
      (receipt) => receipt.context_pack_id === pack.id
    );
  }

  listTranscriptVersions(meetingId: string) {
    return Array.from(this.transcriptVersions.values())
      .filter((version) => version.meeting_id === meetingId)
      .sort((a, b) => b.version_number - a.version_number);
  }

  createTranscriptCorrection(meetingId: string, actor: string, text: string, reason: string) {
    this.requireMeeting(meetingId);
    const existing = this.listTranscriptVersions(meetingId);
    const previousCanonical = existing.find((version) => version.is_canonical);
    if (previousCanonical) {
      previousCanonical.is_canonical = false;
    }
    const version: TranscriptVersion = {
      id: uuidv4(),
      meeting_id: meetingId,
      version_number: existing.length + 1,
      source: "human_correction",
      content: {
        language: "th-ja",
        segments: [{ timestamp: "00:00:00", speaker: actor, text, confidence: 1 }],
      },
      created_by: actor,
      created_at: nowIso(),
      replaces_version_id: previousCanonical?.id,
      reason,
      is_canonical: true,
    };
    this.transcriptVersions.set(version.id, version);
    this.audit("transcript_corrected", actor, { version_id: version.id, reason }, meetingId);
    return version;
  }

  listGlossaryTerms() {
    return Array.from(this.glossaryTerms.values()).sort((a, b) =>
      a.source_term.localeCompare(b.source_term)
    );
  }

  addGlossaryTerm(
    actor: string,
    input: Pick<GlossaryTerm, "scope" | "source_term" | "target_term" | "preserve_english">
  ) {
    const term: GlossaryTerm = {
      id: uuidv4(),
      ...input,
      approved_by: actor,
      approved_at: nowIso(),
      status: "approved",
    };
    this.glossaryTerms.set(term.id, term);
    this.audit("glossary_term_approved", actor, { term_id: term.id, source_term: term.source_term });
    return term;
  }

  listAudioArtifacts(meetingId: string) {
    return Array.from(this.audioArtifacts.values()).filter((artifact) => artifact.meeting_id === meetingId);
  }

  listAuditLogs(meetingId?: string) {
    return this.auditLogs
      .filter((log) => !meetingId || log.meeting_id === meetingId)
      .slice()
      .reverse();
  }

  private requireMeeting(meetingId: string) {
    const meeting = this.meetings.get(meetingId);
    if (!meeting) {
      throw new Error("Meeting not found");
    }
    return meeting;
  }

  private audit(action: string, actor: string, detail: Record<string, unknown>, meetingId?: string) {
    this.auditLogs.push({
      id: uuidv4(),
      meeting_id: meetingId,
      action,
      actor,
      created_at: nowIso(),
      detail,
    });
  }

  private seed() {
    const meetingId = "sat-demo-1";
    const contextPackId = "context-demo-1";
    const timestamp = nowIso();

    this.meetings.set(meetingId, {
      id: meetingId,
      teams_meeting_id: "teams-demo-sat-001",
      graph_resource_id: "graph-demo-sat-001",
      join_url: "https://teams.microsoft.com/l/meetup-join/demo",
      title: "SAT Secretary BOT Feasibility Review",
      organizer_user_id: "admin@company.com",
      tenant_id: "tenant-local",
      meeting_type: "scheduled",
      start_time: timestamp,
      end_time: addDaysIso(0),
      status: "allowed",
      external_guest_count: 1,
      bot_invited: true,
      created_at: timestamp,
      updated_at: timestamp,
    });

    this.policies.set(meetingId, {
      id: "policy-demo-1",
      meeting_id: meetingId,
      decision: "allow",
      enabled_features: {
        captions: true,
        transcript: true,
        audio_recording: true,
        preview: true,
      },
      reason: "SAT-M1 feasibility pilot",
      created_by: "admin@company.com",
      created_at: timestamp,
    });

    this.contextPacks.set(contextPackId, {
      id: contextPackId,
      meeting_id: meetingId,
      version: 1,
      access_scope: "internal_only",
      created_at: timestamp,
      preview_markdown:
        "Purpose: validate SAT Secretary BOT as a Teams participant, native Japanese captions, real-time audio path, and post-meeting Graph transcript import.\n\nKey terms: KPI, backlog, budget, sprint remain in English.\n\nDecision needed: approve or reject the native captions path for MVP.",
    });

    this.transcriptVersions.set("transcript-demo-1", {
      id: "transcript-demo-1",
      meeting_id: meetingId,
      version_number: 1,
      source: "live_stt",
      content: {
        language: "th-ja",
        segments: [
          {
            timestamp: "00:00:12",
            speaker: "SAT Secretary BOT",
            text: "Live transcript seed for SAT-M1 feasibility.",
            confidence: 0.92,
          },
        ],
      },
      created_by: "system",
      created_at: timestamp,
      reason: "Initial live transcript",
      is_canonical: true,
    });

    for (const sourceTerm of ["KPI", "backlog", "budget", "sprint"]) {
      this.glossaryTerms.set(`term-${sourceTerm}`, {
        id: `term-${sourceTerm}`,
        scope: "org",
        source_term: sourceTerm,
        target_term: sourceTerm,
        preserve_english: true,
        approved_by: "admin@company.com",
        approved_at: timestamp,
        status: "approved",
      });
    }

    this.audit("meeting_discovered", "system", { seed: true }, meetingId);
    this.audit("policy_evaluated", "admin@company.com", { decision: "allow" }, meetingId);
  }
}

export const teamsAiRepository = new TeamsAiRepository();

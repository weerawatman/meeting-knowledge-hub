import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useAuth } from "../../hooks/useAuth";

interface FeasibilityGate {
  id: string;
  label: string;
  status: string;
}

interface LiveSession {
  id: string;
  meeting_id: string;
  bot_join_status: string;
  caption_mode: string;
  degraded_state: string;
  started_at?: string;
  metrics: {
    caption_latency_p50_ms: number;
    caption_latency_p95_ms: number;
    stt_latency_ms: number;
    translation_latency_ms: number;
  };
}

interface Meeting {
  id: string;
  title: string;
  meeting_type: string;
  status: string;
  external_guest_count: number;
  bot_invited: boolean;
  start_time: string;
}

interface AuditLog {
  id: string;
  action: string;
  actor: string;
  created_at: string;
}

interface TeamsAiOverview {
  bot_name: string;
  milestone: string;
  feasibility_gates: FeasibilityGate[];
  counts: {
    meetings: number;
    policies: number;
    live_sessions: number;
    glossary_terms: number;
    audit_events: number;
  };
  active_sessions: LiveSession[];
  recent_meetings: Meeting[];
  recent_audit: AuditLog[];
}

const statusLabel: Record<string, string> = {
  needs_spike: "Needs spike",
  passed: "Passed",
  blocked: "Blocked",
};

export function LiveModule() {
  const { token, role } = useAuth();
  const headers = { Authorization: `Bearer ${token}` };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["teams-ai-overview"],
    queryFn: () =>
      axios
        .get<TeamsAiOverview>("/api/teams-ai/overview", { headers })
        .then((response) => response.data),
    refetchInterval: 10000,
  });

  const demoMeeting = data?.recent_meetings[0];
  const canStartSession = role === "admin" || role === "executive";

  const startDemoSession = async () => {
    if (!demoMeeting) return;
    await axios.post(`/api/teams-ai/meetings/${demoMeeting.id}/live/start`, {}, { headers });
    await refetch();
  };

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading SAT Secretary BOT status...</div>;
  }

  if (error || !data) {
    return (
      <div className="max-w-5xl mx-auto rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Unable to load Teams AI overview.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5">
      <div className="flex flex-col gap-3 border-b border-gray-200 pb-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium text-blue-700">{data.milestone}</p>
          <h2 className="mt-1 text-2xl font-bold text-gray-900">{data.bot_name}</h2>
          <p className="mt-1 text-sm text-gray-500">
            Visible Teams participant with native captions first, side panel fallback, and versioned transcript storage.
          </p>
        </div>
        {canStartSession && demoMeeting && (
          <button
            onClick={startDemoSession}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Start pilot session
          </button>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <MetricCard label="Meetings" value={data.counts.meetings} />
        <MetricCard label="Policies" value={data.counts.policies} />
        <MetricCard label="Live sessions" value={data.counts.live_sessions} />
        <MetricCard label="Glossary terms" value={data.counts.glossary_terms} />
        <MetricCard label="Audit events" value={data.counts.audit_events} />
      </div>

      <section className="rounded-md border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-900">Feasibility Gates</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {data.feasibility_gates.map((gate) => (
            <div key={gate.id} className="flex items-center justify-between px-4 py-3 text-sm">
              <span className="text-gray-700">{gate.label}</span>
              <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                {statusLabel[gate.status] || gate.status}
              </span>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-md border border-gray-200 bg-white">
          <div className="border-b border-gray-100 px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">Active Sessions</h3>
          </div>
          {data.active_sessions.length === 0 ? (
            <p className="px-4 py-5 text-sm text-gray-500">No active live session yet.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {data.active_sessions.map((session) => (
                <div key={session.id} className="px-4 py-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{session.meeting_id}</p>
                    <span className="text-xs text-gray-500">{session.caption_mode}</span>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <span>Bot: {session.bot_join_status}</span>
                    <span>Mode: {session.degraded_state}</span>
                    <span>P50: {session.metrics.caption_latency_p50_ms} ms</span>
                    <span>P95: {session.metrics.caption_latency_p95_ms} ms</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-md border border-gray-200 bg-white">
          <div className="border-b border-gray-100 px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">Recent Meetings</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {data.recent_meetings.map((meeting) => (
              <div key={meeting.id} className="px-4 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-sm font-medium text-gray-900">{meeting.title}</p>
                  <span className="shrink-0 rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">
                    {meeting.status}
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {meeting.meeting_type} / external guests {meeting.external_guest_count} / bot{" "}
                  {meeting.bot_invited ? "invited" : "not invited"}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="rounded-md border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-900">Recent Audit</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {data.recent_audit.map((log) => (
            <div key={log.id} className="grid gap-1 px-4 py-3 text-sm md:grid-cols-[1fr_220px_220px]">
              <span className="font-medium text-gray-800">{log.action}</span>
              <span className="text-gray-500">{log.actor}</span>
              <span className="text-gray-400">{new Date(log.created_at).toLocaleString()}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-gray-200 bg-white p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}

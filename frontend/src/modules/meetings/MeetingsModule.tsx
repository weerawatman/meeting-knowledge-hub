import { useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useAuth } from "../../hooks/useAuth";

const STAGE_LABELS: Record<string, string> = {
  waiting: "รอคิว",
  audio_prep: "เตรียมไฟล์เสียง",
  stt: "ถอดเสียง (Whisper)",
  diarization: "ระบุผู้พูด",
  summarizing: "สรุปผล (LLM)",
  indexing: "บันทึกลงคลังความรู้",
  complete: "เสร็จสิ้น",
};

const SPEAKER_COLORS = ["text-blue-600", "text-green-600", "text-purple-600", "text-orange-600"];

export function MeetingsModule() {
  const { token } = useAuth();
  const [meetingId, setMeetingId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const headers = { Authorization: `Bearer ${token}` };

  // Poll status every 3s while processing
  const { data: statusData } = useQuery({
    queryKey: ["meeting-status", meetingId],
    queryFn: () => axios.get(`/api/meetings/${meetingId}/status`, { headers }).then((r) => r.data),
    enabled: !!meetingId,
    refetchInterval: (data) => {
      const status = (data?.state?.data as { status?: string })?.status;
      return status === "done" || status === "failed" ? false : 3000;
    },
  });

  // Fetch result when done
  const { data: result } = useQuery({
    queryKey: ["meeting-result", meetingId],
    queryFn: () => axios.get(`/api/meetings/${meetingId}`, { headers }).then((r) => r.data),
    enabled: statusData?.status === "done",
  });

  const handleUpload = async (file: File) => {
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const { data } = await axios.post("/api/meetings/upload", form, { headers });
      setMeetingId(data.meeting_id);
    } catch (err) {
      alert("อัปโหลดไม่สำเร็จ: " + String(err));
    } finally {
      setUploading(false);
    }
  };

  const getSpeakerColor = (speaker: string) => {
    const idx = parseInt(speaker.replace(/\D/g, "") || "1", 10) - 1;
    return SPEAKER_COLORS[idx % SPEAKER_COLORS.length];
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Meeting Knowledge</h2>

      {/* Upload Area */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 transition-colors"
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const f = e.dataTransfer.files[0];
          if (f) handleUpload(f);
        }}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".mp4,.mkv,.wav,.mp3,.m4a,.mov,.avi"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); }}
        />
        {uploading ? (
          <p className="text-blue-600">กำลังอัปโหลด...</p>
        ) : (
          <>
            <p className="text-gray-500">ลากไฟล์วางที่นี่ หรือคลิกเพื่อเลือกไฟล์</p>
            <p className="text-xs text-gray-400 mt-1">.mp4 .mkv .wav .mp3 .m4a (สูงสุด 2GB)</p>
          </>
        )}
      </div>

      {/* Status */}
      {statusData && statusData.status !== "done" && (
        <div className="bg-blue-50 rounded-xl p-4">
          <p className="text-sm font-medium text-blue-700">
            {STAGE_LABELS[statusData.stage] || statusData.stage || "กำลังประมวลผล..."}
          </p>
          <div className="mt-2 h-2 bg-blue-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-500"
              style={{
                width: `${
                  ["audio_prep", "stt", "diarization", "summarizing", "indexing"].indexOf(statusData.stage) >= 0
                    ? ((["audio_prep", "stt", "diarization", "summarizing", "indexing"].indexOf(statusData.stage) + 1) / 5) * 100
                    : 10
                }%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-white rounded-xl p-5 shadow-sm">
            <h3 className="font-semibold mb-2">สรุปการประชุม</h3>
            <p className="text-sm text-gray-700 leading-relaxed">{result.summary}</p>
          </div>

          {/* Decisions */}
          {result.decisions?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold mb-3">มติที่ประชุม</h3>
              <ul className="space-y-2">
                {result.decisions.map((d: { decision: string; context?: string }, i: number) => (
                  <li key={i} className="text-sm">
                    <span className="font-medium">• {d.decision}</span>
                    {d.context && <span className="text-gray-400 ml-2">({d.context})</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Items */}
          {result.action_items?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold mb-3">Action Items</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">งาน</th>
                    <th className="pb-2">ผู้รับผิดชอบ</th>
                    <th className="pb-2">กำหนดส่ง</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {result.action_items.map((a: { task: string; assignee?: string; due?: string }, i: number) => (
                    <tr key={i}>
                      <td className="py-2">{a.task}</td>
                      <td className="py-2 text-gray-500">{a.assignee || "—"}</td>
                      <td className="py-2 text-gray-500">{a.due || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Transcript */}
          {result.transcript?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold mb-3">Transcript</h3>
              <div className="space-y-1 max-h-80 overflow-y-auto text-sm font-mono">
                {result.transcript.map((line: { timestamp: string; speaker: string; text: string }, i: number) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-gray-400 shrink-0">{line.timestamp}</span>
                    <span className={`font-medium shrink-0 ${getSpeakerColor(line.speaker)}`}>
                      {line.speaker}:
                    </span>
                    <span>{line.text}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

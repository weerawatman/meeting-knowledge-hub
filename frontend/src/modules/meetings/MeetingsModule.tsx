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

const DEMO_RESULT = {
  summary:
    "การประชุมคณะกรรมการบริหาร ประจำไตรมาส 3 ปี 2026 หัวข้อหลักคือการอนุมัติงบประมาณและแผนการดำเนินงาน AI Platform สำหรับองค์กร ที่ประชุมมีมติเอกฉันท์อนุมัติงบประมาณ 2.5 ล้านบาท พร้อมกำหนด Go-live ภายในสิ้น Q3",
  decisions: [
    {
      decision: "อนุมัติงบประมาณโครงการ AI Platform มูลค่า 2.5 ล้านบาท",
      context: "ลงมติเป็นเอกฉันท์ 5-0",
    },
    {
      decision: "กำหนด Go-live ภายในวันที่ 30 กันยายน 2026",
      context: "ต้องผ่าน UAT ก่อนไม่น้อยกว่า 2 สัปดาห์",
    },
    {
      decision: "ใช้ On-Premise deployment เพื่อความปลอดภัยของข้อมูลองค์กร",
    },
  ],
  action_items: [
    {
      task: "จัดทำ TOR สำหรับการจัดซื้อ GPU Server (8GB VRAM ขึ้นไป)",
      assignee: "ทีม IT Infrastructure",
      due: "15 ก.ค. 2026",
    },
    {
      task: "ประสาน Vendor ด้าน Hardware และติดตั้งระบบ",
      assignee: "วีระวัฒน์ ม.",
      due: "20 ก.ค. 2026",
    },
    {
      task: "เตรียม Training Data ชุดแรก (recording 50 ชั่วโมง)",
      assignee: "ทีม Operations",
      due: "31 ก.ค. 2026",
    },
    {
      task: "จัดทำแผน Change Management สำหรับผู้ใช้งาน",
      assignee: "HR + IT",
      due: "15 ส.ค. 2026",
    },
  ],
  transcript: [
    {
      timestamp: "00:01:12",
      speaker: "Speaker 1",
      text: "เปิดประชุม วาระแรกขอนำเสนองบประมาณ AI Platform ที่เตรียมไว้ 2.5 ล้านบาทครับ",
    },
    {
      timestamp: "00:02:45",
      speaker: "Speaker 2",
      text: "ผมเห็นด้วยกับตัวเลขนี้ครับ ถ้าเทียบกับ vendor ภายนอกแล้วถูกกว่า 3 เท่า",
    },
    {
      timestamp: "00:04:20",
      speaker: "Speaker 3",
      text: "ประเด็น Security ครับ ข้อมูลการประชุมบางส่วนเป็นความลับทางธุรกิจ เราต้องการ On-Premise ใช่ไหม",
    },
    {
      timestamp: "00:05:10",
      speaker: "Speaker 1",
      text: "ถูกต้องครับ ระบบจะรันบน server ภายในองค์กรทั้งหมด ไม่มีข้อมูลออกนอก",
    },
    {
      timestamp: "00:08:33",
      speaker: "Speaker 2",
      text: "งั้นขอ Vote ได้เลยครับ ผมสนับสนุน",
    },
    {
      timestamp: "00:08:50",
      speaker: "Speaker 1",
      text: "มติเป็นเอกฉันท์ครับ อนุมัติงบ 2.5M และ Go-live Q3 ปิดวาระครับ",
    },
  ],
};

type MeetingResult = typeof DEMO_RESULT;

export function MeetingsModule() {
  const { token } = useAuth();
  const [meetingId, setMeetingId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<MeetingResult | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const headers = { Authorization: `Bearer ${token}` };

  const { data: statusData } = useQuery({
    queryKey: ["meeting-status", meetingId],
    queryFn: () =>
      axios.get(`/api/meetings/${meetingId}/status`, { headers }).then((r) => r.data),
    enabled: !!meetingId && !result,
    refetchInterval: (data) => {
      const status = (data?.state?.data as { status?: string })?.status;
      return status === "done" || status === "failed" ? false : 3000;
    },
  });

  const { data: apiResult } = useQuery({
    queryKey: ["meeting-result", meetingId],
    queryFn: () =>
      axios.get(`/api/meetings/${meetingId}`, { headers }).then((r) => r.data),
    enabled: statusData?.status === "done" && !result,
  });

  const displayResult = result ?? (apiResult as MeetingResult | undefined) ?? null;

  const handleUpload = async (file: File) => {
    setUploading(true);
    setResult(null);
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
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Meeting Knowledge</h2>
        <button
          onClick={() => { setResult(DEMO_RESULT); setMeetingId(null); }}
          className="text-sm px-4 py-2 rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 transition-colors"
        >
          โหลดข้อมูลตัวอย่าง
        </button>
      </div>

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
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleUpload(f);
          }}
        />
        {uploading ? (
          <p className="text-blue-600">กำลังอัปโหลด...</p>
        ) : (
          <>
            <p className="text-gray-500 text-lg mb-1">🎙️</p>
            <p className="text-gray-500">ลากไฟล์วางที่นี่ หรือคลิกเพื่อเลือกไฟล์</p>
            <p className="text-xs text-gray-400 mt-1">.mp4 .mkv .wav .mp3 .m4a (สูงสุด 2GB)</p>
          </>
        )}
      </div>

      {/* Processing Status */}
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
                  ["audio_prep", "stt", "diarization", "summarizing", "indexing"].indexOf(
                    statusData.stage
                  ) >= 0
                    ? ((["audio_prep", "stt", "diarization", "summarizing", "indexing"].indexOf(
                        statusData.stage
                      ) +
                        1) /
                        5) *
                      100
                    : 10
                }%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Result */}
      {displayResult && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="font-semibold mb-2 text-gray-800">สรุปการประชุม</h3>
            <p className="text-sm text-gray-700 leading-relaxed">{displayResult.summary}</p>
          </div>

          {/* Decisions */}
          {displayResult.decisions?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold mb-3 text-gray-800">มติที่ประชุม</h3>
              <ul className="space-y-2">
                {displayResult.decisions.map(
                  (d: { decision: string; context?: string }, i: number) => (
                    <li key={i} className="text-sm flex gap-2">
                      <span className="text-blue-500 shrink-0 mt-0.5">✓</span>
                      <span>
                        <span className="font-medium">{d.decision}</span>
                        {d.context && (
                          <span className="text-gray-400 ml-2 text-xs">({d.context})</span>
                        )}
                      </span>
                    </li>
                  )
                )}
              </ul>
            </div>
          )}

          {/* Action Items */}
          {displayResult.action_items?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold mb-3 text-gray-800">Action Items</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b text-xs uppercase tracking-wide">
                    <th className="pb-2 font-medium">งาน</th>
                    <th className="pb-2 font-medium">ผู้รับผิดชอบ</th>
                    <th className="pb-2 font-medium">กำหนดส่ง</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {displayResult.action_items.map(
                    (a: { task: string; assignee?: string; due?: string }, i: number) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="py-2.5 pr-4">{a.task}</td>
                        <td className="py-2.5 pr-4 text-gray-500 whitespace-nowrap">
                          {a.assignee || "—"}
                        </td>
                        <td className="py-2.5 text-gray-500 whitespace-nowrap">
                          {a.due || "—"}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Transcript */}
          {displayResult.transcript?.length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
              <h3 className="font-semibold mb-3 text-gray-800">Transcript</h3>
              <div className="space-y-2 max-h-80 overflow-y-auto text-sm">
                {displayResult.transcript.map(
                  (
                    line: { timestamp: string; speaker: string; text: string },
                    i: number
                  ) => (
                    <div key={i} className="flex gap-3 py-1">
                      <span className="text-gray-300 shrink-0 font-mono text-xs pt-0.5">
                        {line.timestamp}
                      </span>
                      <span
                        className={`font-medium shrink-0 text-xs pt-0.5 w-20 ${getSpeakerColor(line.speaker)}`}
                      >
                        {line.speaker}
                      </span>
                      <span className="text-gray-700">{line.text}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

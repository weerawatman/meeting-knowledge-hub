import { useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useAuth } from "../../hooks/useAuth";

export function DigestModule() {
  const { token } = useAuth();
  const [digestId, setDigestId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const headers = { Authorization: `Bearer ${token}` };

  const { data: status } = useQuery({
    queryKey: ["digest-status", digestId],
    queryFn: () => axios.get(`/api/digest/${digestId}`, { headers }).then((r) => r.data),
    enabled: !!digestId,
    refetchInterval: (data) => {
      const s = (data?.state?.data as { status?: string })?.status;
      return s === "done" || s === "failed" ? false : 3000;
    },
  });

  const handleFiles = async (files: FileList) => {
    setUploading(true);
    const form = new FormData();
    Array.from(files).forEach((f) => form.append("files", f));
    try {
      const { data } = await axios.post("/api/digest", form, { headers });
      setDigestId(data.digest_id);
    } catch (err) {
      alert("อัปโหลดไม่สำเร็จ: " + String(err));
    } finally {
      setUploading(false);
    }
  };

  const result = status?.status === "done" ? status?.result : null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Executive Digest</h2>

      <div
        className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 transition-colors"
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); if (e.dataTransfer.files) handleFiles(e.dataTransfer.files); }}
      >
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".pdf,.docx,.pptx,.xlsx"
          className="hidden"
          onChange={(e) => { if (e.target.files) handleFiles(e.target.files); }}
        />
        {uploading ? <p className="text-blue-600">กำลังอัปโหลด...</p> : (
          <>
            <p className="text-gray-500">ลากไฟล์เอกสารหลายไฟล์วางที่นี่ (สูงสุด 20 ไฟล์)</p>
            <p className="text-xs text-gray-400 mt-1">.pdf .docx .pptx .xlsx</p>
          </>
        )}
      </div>

      {status && status.status !== "done" && (
        <div className="bg-amber-50 rounded-xl p-4 text-sm text-amber-700">
          {status.stage === "digesting" ? "Pass 1: วิเคราะห์เอกสารแต่ละชิ้น..." : "กำลังประมวลผล..."}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl p-5 shadow-sm">
            <h3 className="font-semibold mb-2">สรุปภาพรวม</h3>
            <p className="text-sm text-gray-700">{(result as { summary?: string }).summary}</p>
          </div>
          {((result as { resolutions?: { resolution: string; context?: string }[] }).resolutions ?? []).length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold mb-3">มติที่ประชุม (Resolutions)</h3>
              <ul className="space-y-2 text-sm">
                {(result as { resolutions: { resolution: string; context?: string }[] }).resolutions.map((r, i) => (
                  <li key={i}>• {r.resolution}</li>
                ))}
              </ul>
            </div>
          )}
          {((result as { pending_tasks?: { task: string; assignee?: string; due?: string }[] }).pending_tasks ?? []).length > 0 && (
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold mb-3">งานค้างส่ง (Pending Tasks)</h3>
              <table className="w-full text-sm">
                <thead><tr className="text-left text-gray-500 border-b"><th className="pb-2">งาน</th><th className="pb-2">ผู้รับผิดชอบ</th><th className="pb-2">กำหนด</th></tr></thead>
                <tbody className="divide-y divide-gray-100">
                  {(result as { pending_tasks: { task: string; assignee?: string; due?: string }[] }).pending_tasks.map((t, i) => (
                    <tr key={i}><td className="py-2">{t.task}</td><td className="py-2 text-gray-500">{t.assignee || "—"}</td><td className="py-2 text-gray-500">{t.due || "—"}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

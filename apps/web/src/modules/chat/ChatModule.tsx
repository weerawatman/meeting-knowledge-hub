import { useState, FormEvent } from "react";
import axios from "axios";
import { useAuth } from "../../hooks/useAuth";

interface Message {
  role: "user" | "ai";
  text: string;
  citations?: { document_id: string; score: number; text: string; citation: string }[];
}

export function ChatModule() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    const userMsg: Message = { role: "user", text: query };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);
    try {
      const { data } = await axios.post(
        "/api/chat",
        { query, limit: 5 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const aiMsg: Message = {
        role: "ai",
        text: data.results?.length
          ? `พบ ${data.results.length} ผลลัพธ์ที่เกี่ยวข้อง`
          : "ไม่พบข้อมูลที่เกี่ยวข้องในคลังความรู้",
        citations: data.results,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      setMessages((prev) => [...prev, { role: "ai", text: "ระบบไม่พร้อมใช้งาน กรุณาลองใหม่" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-full">
      <h2 className="text-2xl font-bold mb-4">Knowledge Chat</h2>
      <div className="flex-1 bg-white rounded-xl shadow-sm p-4 space-y-4 overflow-y-auto min-h-[400px] max-h-[500px]">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">เริ่มต้นถามคำถามเกี่ยวกับการประชุมหรือเอกสาร...</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"}`}>
              <p>{msg.text}</p>
              {msg.citations?.map((c, j) => (
                <a key={j} href={c.citation} className="block mt-2 text-xs text-blue-500 underline">
                  [{j + 1}] {c.document_id} ({Math.round(c.score * 100)}%)
                </a>
              ))}
            </div>
          </div>
        ))}
        {loading && <div className="text-sm text-gray-400">กำลังค้นหา...</div>}
      </div>
      <form onSubmit={handleSend} className="mt-4 flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="ถามคำถามเกี่ยวกับการประชุมหรือเอกสาร..."
          className="flex-1 border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" disabled={loading || !query.trim()} className="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm disabled:opacity-50">
          ส่ง
        </button>
      </form>
    </div>
  );
}

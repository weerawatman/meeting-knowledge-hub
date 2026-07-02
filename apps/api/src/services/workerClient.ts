/**
 * HTTP client for the Python AI Worker (internal service).
 * All calls go to WORKER_URL (default: http://worker:8001).
 */
import axios from "axios";

const WORKER_URL = process.env.WORKER_URL || "http://worker:8001";
const client = axios.create({ baseURL: WORKER_URL, timeout: 180_000 });

export interface JobStatus {
  job_id: string;
  status: "queued" | "processing" | "done" | "failed" | "not_found";
  stage?: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface SearchResult {
  document_id: string;
  score: number;
  text: string;
  metadata?: Record<string, unknown>;
}

export async function transcribeFile(
  filePath: string,
  meetingId: string
): Promise<{ job_id: string; status: string }> {
  const { data } = await client.post("/worker/jobs/transcribe", {
    file_path: filePath,
    meeting_id: meetingId,
  });
  return data;
}

export async function summarizeTranscript(
  transcript: string,
  meetingId: string
): Promise<{ job_id: string; status: string }> {
  const { data } = await client.post("/worker/jobs/summarize", {
    transcript,
    meeting_id: meetingId,
  });
  return data;
}

export async function submitDigest(
  docChunks: unknown[],
  digestId: string
): Promise<{ job_id: string; status: string }> {
  const { data } = await client.post("/worker/jobs/digest", {
    doc_chunks: docChunks,
    digest_id: digestId,
  });
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const { data } = await client.get(`/worker/jobs/${jobId}`);
  return data;
}

export async function embedText(text: string): Promise<number[]> {
  const { data } = await client.post("/worker/embed", { text });
  return data.vector;
}

export async function search(
  query: string,
  filters?: Record<string, unknown>,
  limit = 10
): Promise<SearchResult[]> {
  const { data } = await client.post("/worker/search", { query, filters, limit });
  return data.results;
}

export async function checkHealth(): Promise<{ ok: boolean; vram_free_mb?: number }> {
  const { data } = await client.get("/worker/health");
  return data;
}

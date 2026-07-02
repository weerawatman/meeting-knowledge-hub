import express from "express";
import cors from "cors";
import { createServer } from "http";
import { Server as SocketIOServer } from "socket.io";
import dotenv from "dotenv";

import { authRouter } from "./routes/auth";
import { meetingsRouter } from "./routes/meetings";
import { digestRouter } from "./routes/digest";
import { chatRouter } from "./routes/chat";
import { teamsAiRouter } from "./routes/teamsAi";
import { errorHandler } from "./middleware/errorHandler";

dotenv.config();

const app = express();
const httpServer = createServer(app);

export const io = new SocketIOServer(httpServer, {
  cors: { origin: process.env.FRONTEND_URL || "http://localhost:5173", methods: ["GET", "POST"] },
});

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:5173" }));
app.use(express.json());

// ── Routes ────────────────────────────────────────────────────────────────────
app.get("/health", (_req, res) => res.json({ ok: true, service: "Meeting Hub API" }));
app.use("/api/auth", authRouter);
app.use("/api/meetings", meetingsRouter);
app.use("/api/digest", digestRouter);
app.use("/api/chat", chatRouter);
app.use("/api/teams-ai", teamsAiRouter);

// ── WebSocket — Live Capture ──────────────────────────────────────────────────
io.on("connection", (socket) => {
  socket.on("join_session", (sessionId: string) => {
    socket.join(`live:${sessionId}`);
  });
  // Audio chunks forwarded to Python Worker (placeholder — full impl in Sprint 5)
  socket.on("audio_chunk", (_data) => {
    // TODO: forward chunk to worker-python /worker/stream
  });
});

// ── Error handler (must be last) ─────────────────────────────────────────────
app.use(errorHandler);

const PORT = parseInt(process.env.PORT || "3001", 10);
httpServer.listen(PORT, () => {
  console.log(`Meeting Hub API running on :${PORT}`);
});

export default app;

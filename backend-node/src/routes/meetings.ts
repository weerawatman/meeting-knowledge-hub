import { Router, Request, Response } from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { v4 as uuidv4 } from "uuid";
import { verifyJWT } from "../middleware/auth";
import { transcribeFile, getJobStatus } from "../services/workerClient";

export const meetingsRouter = Router();

const UPLOAD_DIR = process.env.UPLOAD_DIR || "/tmp/meeting-hub-uploads";
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
  filename: (_req, file, cb) => {
    const id = uuidv4();
    cb(null, `${id}${path.extname(file.originalname)}`);
  },
});
const upload = multer({
  storage,
  limits: { fileSize: 2 * 1024 * 1024 * 1024 }, // 2GB
  fileFilter: (_req, file, cb) => {
    const allowed = [".mp4", ".mkv", ".mov", ".avi", ".wav", ".mp3", ".m4a"];
    const ext = path.extname(file.originalname).toLowerCase();
    allowed.includes(ext) ? cb(null, true) : cb(new Error(`Unsupported file type: ${ext}`));
  },
});

// POST /api/meetings/upload
meetingsRouter.post(
  "/upload",
  verifyJWT,
  upload.single("file"),
  async (req: Request, res: Response): Promise<void> => {
    if (!req.file) {
      res.status(400).json({ error: "No file uploaded" });
      return;
    }
    const meetingId = uuidv4();
    try {
      await transcribeFile(req.file.path, meetingId);
      res.json({ meeting_id: meetingId, status: "queued", filename: req.file.originalname });
    } catch (err) {
      res.status(502).json({ error: "AI Worker unavailable", detail: String(err) });
    }
  }
);

// GET /api/meetings/:id/status
meetingsRouter.get("/:id/status", verifyJWT, async (req: Request, res: Response): Promise<void> => {
  try {
    const status = await getJobStatus(req.params.id);
    res.json(status);
  } catch {
    res.status(502).json({ error: "Worker unreachable" });
  }
});

// GET /api/meetings/:id
meetingsRouter.get("/:id", verifyJWT, async (req: Request, res: Response): Promise<void> => {
  try {
    const jobStatus = await getJobStatus(req.params.id);
    if (jobStatus.status !== "done" || !jobStatus.result) {
      res.json({ meeting_id: req.params.id, ...jobStatus });
      return;
    }
    res.json({ meeting_id: req.params.id, ...jobStatus.result });
  } catch {
    res.status(502).json({ error: "Worker unreachable" });
  }
});

// PATCH /api/meetings/:id/speakers — rename speaker labels
meetingsRouter.patch("/:id/speakers", verifyJWT, (_req: Request, res: Response): void => {
  // TODO: update speaker names in DB and re-index
  res.json({ status: "ok", message: "Speaker rename coming in Sprint 5" });
});

// POST /api/meetings/:id/corrections — human-in-the-loop
meetingsRouter.post("/:id/corrections", verifyJWT, (_req: Request, res: Response): void => {
  // TODO: proxy to worker /worker/search + re-embed
  res.json({ status: "ok", message: "Corrections coming in Sprint 5" });
});

// GET /api/meetings — demo list (replace with PostgreSQL in Sprint 6)
meetingsRouter.get("/", verifyJWT, (_req: Request, res: Response): void => {
  res.json({
    meetings: [
      {
        id: "demo-1",
        title: "Q3 Strategy & AI Platform Budget Review",
        status: "done",
        created_at: "2026-07-01T09:00:00Z",
        duration_sec: 3240,
      },
      {
        id: "demo-2",
        title: "Infrastructure Planning — GPU Server",
        status: "done",
        created_at: "2026-06-28T14:30:00Z",
        duration_sec: 1800,
      },
    ],
  });
});

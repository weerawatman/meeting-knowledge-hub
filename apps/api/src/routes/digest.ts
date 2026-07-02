import { Router, Request, Response } from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { v4 as uuidv4 } from "uuid";
import { verifyJWT } from "../middleware/auth";
import { submitDigest, getJobStatus } from "../services/workerClient";

export const digestRouter = Router();

const UPLOAD_DIR = process.env.UPLOAD_DIR || "/tmp/meeting-hub-uploads";
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const upload = multer({
  dest: UPLOAD_DIR,
  limits: { fileSize: 100 * 1024 * 1024, files: 20 }, // 100MB per file, 20 files max
  fileFilter: (_req, file, cb) => {
    const allowed = [".pdf", ".docx", ".pptx", ".xlsx"];
    const ext = path.extname(file.originalname).toLowerCase();
    allowed.includes(ext) ? cb(null, true) : cb(new Error(`Unsupported doc type: ${ext}`));
  },
});

// POST /api/digest — upload documents and queue Two-pass Digest
digestRouter.post(
  "/",
  verifyJWT,
  upload.array("files", 20),
  async (req: Request, res: Response): Promise<void> => {
    const files = req.files as Express.Multer.File[];
    if (!files?.length) {
      res.status(400).json({ error: "No documents uploaded" });
      return;
    }
    const digestId = uuidv4();

    // Build doc_chunks from uploaded files by reading text via Python Worker
    // For Sprint 3 we send file paths; Worker's doc_extractor handles parsing
    const docChunks = files.map((f) => ({
      page: 1,
      text: `[File: ${f.originalname} — extraction pending]`,
      source: f.originalname,
      file_path: f.path,
    }));

    try {
      await submitDigest(docChunks, digestId);
      res.json({
        digest_id: digestId,
        status: "queued",
        files: files.map((f) => f.originalname),
      });
    } catch (err) {
      res.status(502).json({ error: "AI Worker unavailable", detail: String(err) });
    }
  }
);

// GET /api/digest/:id — poll digest status and result
digestRouter.get("/:id", verifyJWT, async (req: Request, res: Response): Promise<void> => {
  try {
    const status = await getJobStatus(req.params.id);
    res.json({ digest_id: req.params.id, ...status });
  } catch {
    res.status(502).json({ error: "Worker unreachable" });
  }
});

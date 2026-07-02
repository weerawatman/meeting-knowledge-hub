import { Router, Request, Response } from "express";
import { requireRole, verifyJWT } from "../middleware/auth";
import { teamsAiRepository } from "../services/teamsAiRepository";

export const teamsAiRouter = Router();

teamsAiRouter.use(verifyJWT);

function currentActor(req: Request) {
  return req.user?.sub || "unknown";
}

teamsAiRouter.get("/overview", (_req: Request, res: Response): void => {
  res.json(teamsAiRepository.getOverview());
});

teamsAiRouter.get("/meetings", (_req: Request, res: Response): void => {
  res.json({ meetings: teamsAiRepository.listMeetings() });
});

teamsAiRouter.post(
  "/meetings",
  requireRole("admin"),
  (req: Request, res: Response): void => {
    const { title, join_url } = req.body;
    if (!title || !join_url) {
      res.status(400).json({ error: "title and join_url are required" });
      return;
    }
    const meeting = teamsAiRepository.upsertMeeting(req.body);
    res.status(201).json({ meeting });
  }
);

teamsAiRouter.get("/meetings/:id", (req: Request, res: Response): void => {
  const meeting = teamsAiRepository.getMeeting(req.params.id);
  if (!meeting) {
    res.status(404).json({ error: "Meeting not found" });
    return;
  }
  res.json({
    meeting,
    policy: teamsAiRepository.getPolicy(req.params.id),
    policy_evaluation: teamsAiRepository.evaluatePolicy(req.params.id),
    context_pack: teamsAiRepository.getLatestContextPack(req.params.id),
    read_receipts: teamsAiRepository.listPreviewReadReceipts(req.params.id),
    transcript_versions: teamsAiRepository.listTranscriptVersions(req.params.id),
    audio_artifacts: teamsAiRepository.listAudioArtifacts(req.params.id),
    audit: teamsAiRepository.listAuditLogs(req.params.id),
  });
});

teamsAiRouter.post(
  "/meetings/:id/policy",
  requireRole("admin"),
  (req: Request, res: Response): void => {
    const { decision, reason, enabled_features } = req.body;
    if (decision !== "allow" && decision !== "deny") {
      res.status(400).json({ error: "decision must be allow or deny" });
      return;
    }
    try {
      const policy = teamsAiRepository.setPolicy(
        req.params.id,
        decision,
        currentActor(req),
        reason || "Manual admin policy",
        enabled_features
      );
      res.json({ policy, policy_evaluation: teamsAiRepository.evaluatePolicy(req.params.id) });
    } catch (error) {
      res.status(404).json({ error: (error as Error).message });
    }
  }
);

teamsAiRouter.post(
  "/meetings/:id/live/start",
  requireRole("admin", "executive"),
  (req: Request, res: Response): void => {
    try {
      const result = teamsAiRepository.startLiveSession(req.params.id, currentActor(req));
      res.status(result.started ? 200 : 409).json(result);
    } catch (error) {
      res.status(404).json({ error: (error as Error).message });
    }
  }
);

teamsAiRouter.get("/live-sessions", (_req: Request, res: Response): void => {
  res.json({ live_sessions: teamsAiRepository.listLiveSessions() });
});

teamsAiRouter.post(
  "/live-sessions/:id/captions",
  requireRole("admin", "executive"),
  (req: Request, res: Response): void => {
    const { caption_text } = req.body;
    if (!caption_text) {
      res.status(400).json({ error: "caption_text is required" });
      return;
    }
    try {
      res.json(teamsAiRepository.publishCaption(req.params.id, caption_text, currentActor(req)));
    } catch (error) {
      res.status(404).json({ error: (error as Error).message });
    }
  }
);

teamsAiRouter.post(
  "/live-sessions/:id/fallback",
  requireRole("admin", "executive"),
  (req: Request, res: Response): void => {
    try {
      const session = teamsAiRepository.activateSidePanelFallback(
        req.params.id,
        currentActor(req),
        req.body.reason || "Manual fallback activation"
      );
      res.json({ session });
    } catch (error) {
      res.status(404).json({ error: (error as Error).message });
    }
  }
);

teamsAiRouter.get("/meetings/:id/preview", (req: Request, res: Response): void => {
  const pack = teamsAiRepository.getLatestContextPack(req.params.id);
  if (!pack) {
    res.status(404).json({ error: "Context pack not found" });
    return;
  }
  res.json({ context_pack: pack, read_receipts: teamsAiRepository.listPreviewReadReceipts(req.params.id) });
});

teamsAiRouter.post("/meetings/:id/preview/read", (req: Request, res: Response): void => {
  try {
    const receipt = teamsAiRepository.recordPreviewRead(
      req.params.id,
      currentActor(req),
      req.body.client || "web"
    );
    res.status(201).json({ receipt });
  } catch (error) {
    res.status(404).json({ error: (error as Error).message });
  }
});

teamsAiRouter.get("/meetings/:id/transcripts", (req: Request, res: Response): void => {
  res.json({ transcript_versions: teamsAiRepository.listTranscriptVersions(req.params.id) });
});

teamsAiRouter.post(
  "/meetings/:id/transcripts/corrections",
  requireRole("admin", "executive", "user"),
  (req: Request, res: Response): void => {
    const { text, reason } = req.body;
    if (!text) {
      res.status(400).json({ error: "text is required" });
      return;
    }
    try {
      const version = teamsAiRepository.createTranscriptCorrection(
        req.params.id,
        currentActor(req),
        text,
        reason || "Human correction"
      );
      res.status(201).json({ transcript_version: version });
    } catch (error) {
      res.status(404).json({ error: (error as Error).message });
    }
  }
);

teamsAiRouter.get("/glossary", (_req: Request, res: Response): void => {
  res.json({ terms: teamsAiRepository.listGlossaryTerms() });
});

teamsAiRouter.post(
  "/glossary",
  requireRole("admin"),
  (req: Request, res: Response): void => {
    const { scope, source_term, target_term, preserve_english } = req.body;
    if (!scope || !source_term || !target_term) {
      res.status(400).json({ error: "scope, source_term, and target_term are required" });
      return;
    }
    const term = teamsAiRepository.addGlossaryTerm(currentActor(req), {
      scope,
      source_term,
      target_term,
      preserve_english: !!preserve_english,
    });
    res.status(201).json({ term });
  }
);

teamsAiRouter.get("/audit", (req: Request, res: Response): void => {
  res.json({ audit: teamsAiRepository.listAuditLogs(String(req.query.meeting_id || "")) });
});

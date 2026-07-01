import { Router, Request, Response } from "express";
import { verifyJWT } from "../middleware/auth";
import { search } from "../services/workerClient";

export const chatRouter = Router();

// POST /api/chat — Knowledge Chat with category-based filtering
chatRouter.post("/", verifyJWT, async (req: Request, res: Response): Promise<void> => {
  const { query, limit = 5 } = req.body;
  if (!query?.trim()) {
    res.status(400).json({ error: "query is required" });
    return;
  }

  // Build category filter from JWT payload
  const allowedCategories = req.user?.allowed_categories ?? ["general"];
  const filters = allowedCategories.includes("all")
    ? undefined
    : { allowed_roles: [req.user?.role] };

  try {
    const results = await search(query, filters, limit);
    res.json({
      query,
      results: results.map((r) => ({
        document_id: r.document_id,
        score: r.score,
        text: r.text,
        citation: `/meetings/${r.document_id}`,
        metadata: r.metadata,
      })),
    });
  } catch (err) {
    res.status(502).json({ error: "AI Worker unavailable", detail: String(err) });
  }
});

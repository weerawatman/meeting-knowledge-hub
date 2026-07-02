import { Router, Request, Response } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { verifyJWT } from "../middleware/auth";

export const authRouter = Router();

const JWT_SECRET = process.env.JWT_SECRET || "dev_jwt_secret_change_in_production";
const JWT_EXPIRES_IN = "8h";

// Demo users — replace with PostgreSQL user table in production
const DEMO_USERS = [
  {
    id: "1",
    email: "admin@company.com",
    passwordHash: bcrypt.hashSync("admin123", 10),
    role: "admin" as const,
    allowed_categories: ["all"],
  },
  {
    id: "2",
    email: "exec@company.com",
    passwordHash: bcrypt.hashSync("exec123", 10),
    role: "executive" as const,
    allowed_categories: ["all"],
  },
  {
    id: "3",
    email: "user@company.com",
    passwordHash: bcrypt.hashSync("user123", 10),
    role: "user" as const,
    allowed_categories: ["general"],
  },
];

authRouter.post("/login", async (req: Request, res: Response): Promise<void> => {
  const { email, password } = req.body;
  if (!email || !password) {
    res.status(400).json({ error: "email and password required" });
    return;
  }
  const user = DEMO_USERS.find((u) => u.email === email);
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    res.status(401).json({ error: "Invalid credentials" });
    return;
  }
  const token = jwt.sign(
    { sub: user.email, role: user.role, allowed_categories: user.allowed_categories },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
  res.json({ token, role: user.role, email: user.email });
});

authRouter.get("/me", verifyJWT, (req: Request, res: Response): void => {
  res.json(req.user);
});

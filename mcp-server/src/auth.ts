import type { Request, Response, NextFunction } from "express";
import { config } from "./config.js";

export function verifyBearerToken(req: Request, res: Response, next: NextFunction) {
  const expected = `Bearer ${config.bearerToken}`;
  if (req.header("authorization") !== expected) {
    res.status(401).json({ error: "invalid_bearer_token" });
    return;
  }
  next();
}

export function verifyOrigin(req: Request, res: Response, next: NextFunction) {
  const origin = req.header("origin");
  if (origin && !config.allowedOrigins.includes(origin)) {
    res.status(403).json({ error: "origin_not_allowed" });
    return;
  }
  next();
}

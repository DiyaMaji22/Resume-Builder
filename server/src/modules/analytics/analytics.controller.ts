import type { Request, Response } from "express";
import { fetchPyMongoAnalytics, runPyMongoSetup, runPyMongoSeed } from "./analytics.service.js";
import type { ApiResponse, AnalyticsData } from "../../types/shared.js";
import { env } from "../../config/env.js";

export async function getAnalytics(_req: Request, res: Response<ApiResponse<AnalyticsData>>): Promise<void> {
  const data = await fetchPyMongoAnalytics();
  res.json({
    message: "PyMongo analytics retrieved successfully",
    data,
  });
}

export async function triggerSetup(_req: Request, res: Response<ApiResponse<{ log: string }>>): Promise<void> {
  const log = await runPyMongoSetup();
  res.json({
    message: "PyMongo schema setup completed successfully",
    data: { log },
  });
}

export async function triggerSeed(_req: Request, res: Response<ApiResponse<{ log: string }>>): Promise<void> {
  if (!env.isDev) {
    res.status(403).json({
      message: "Database seeding is disabled in non-development environments.",
    });
    return;
  }
  const log = await runPyMongoSeed();
  res.json({
    message: "PyMongo seed completed successfully",
    data: { log },
  });
}

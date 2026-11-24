import { Router } from "express";
import { getAnalytics, triggerSetup, triggerSeed } from "./analytics.controller.js";
import { asyncHandler } from "../../middleware/asyncHandler.js";
import { authenticate } from "../../middleware/authenticate.js";

export const analyticsRouter = Router();

analyticsRouter.use(authenticate);
analyticsRouter.get("/", asyncHandler(getAnalytics));
analyticsRouter.post("/setup", asyncHandler(triggerSetup));
analyticsRouter.post("/seed", asyncHandler(triggerSeed));

import { Router } from "express";
import multer from "multer";
import { authenticate } from "../../middleware/authenticate.js";
import { asyncHandler } from "../../middleware/asyncHandler.js";
import {
  listResumes, getResume, getPublicResume,
  createResume, duplicateResume,
  updateResume, deleteResume,
  saveVersion, restoreVersion,
  getStarters, analyzeATS,
  uploadResumePDF,
} from "./resume.controller.js";

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
});

const router = Router();

// Public — no auth
router.get("/starters",   asyncHandler(getStarters));
router.get("/public/:id", asyncHandler(getPublicResume));

// Protected
router.use(authenticate);
router.post("/upload",                       upload.single("file"), asyncHandler(uploadResumePDF));
router.get("/",                              asyncHandler(listResumes));
router.get("/:id",                           asyncHandler(getResume));
router.post("/",                             asyncHandler(createResume));
router.post("/:id/ats-analyze",              asyncHandler(analyzeATS));
router.post("/:id/duplicate",               asyncHandler(duplicateResume));
router.post("/:id/versions",                asyncHandler(saveVersion));
router.post("/:id/versions/:snapshotId/restore", asyncHandler(restoreVersion));
router.put("/:id",                           asyncHandler(updateResume));
router.delete("/:id",                        asyncHandler(deleteResume));

export { router as resumeRouter };

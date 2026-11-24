import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";
import fs from "node:fs";
import { ResumeModel } from "../resume/resume.schema.js";
import { UserModel } from "../user/user.schema.js";
import type {
  AnalyticsData,
  TemplateUsageStat,
  TopSkillStat,
  UserResumeStat,
  CompletenessScoreStat,
  MonthlyVelocityStat,
} from "../../types/shared.js";

const execFileAsync = promisify(execFile);

// Resolve resume_builder_pymongo.py location flexibly across root or server working directories
function getScriptPath(): string {
  try {
    if (typeof __dirname !== "undefined") {
      const candidateDir = path.resolve(__dirname, "../../../../resume_builder_pymongo.py");
      if (fs.existsSync(candidateDir)) return candidateDir;
    }
  } catch {
    // fallback to cwd resolution
  }

  const candidateCwd = path.resolve(process.cwd(), "resume_builder_pymongo.py");
  if (fs.existsSync(candidateCwd)) return candidateCwd;

  const candidateParent = path.resolve(process.cwd(), "..", "resume_builder_pymongo.py");
  if (fs.existsSync(candidateParent)) return candidateParent;

  return candidateCwd;
}

const SCRIPT_PATH = getScriptPath();

export async function fetchPyMongoAnalytics(): Promise<AnalyticsData> {
  try {
    // 1. Primary execution via PyMongo
    const { stdout } = await execFileAsync("python3", [SCRIPT_PATH, "analytics"], {
      timeout: 8000,
      env: { ...process.env },
    });
    const parsed = JSON.parse(stdout.trim()) as AnalyticsData;
    return parsed;
  } catch (pyError) {
    console.warn("[Analytics] PyMongo CLI invocation failed, falling back to native MongoDB aggregation pipeline:", pyError);

    // 2. Resilient fallback using native MongoDB aggregations with the exact same pipeline semantics
    const [templateUsage, topSkills, resumesPerUser, completenessScores, monthlyVelocity, totalUsers, totalResumes, publicResumes] =
      await Promise.all([
        ResumeModel.aggregate([
          {
            $group: {
              _id: "$template",
              totalResumes: { $sum: 1 },
              publicResumes: { $sum: { $cond: ["$isPublic", 1, 0] } },
            },
          },
          { $sort: { totalResumes: -1, _id: 1 } },
        ]),
        ResumeModel.aggregate([
          { $unwind: "$skills" },
          {
            $group: {
              _id: { $toLower: "$skills" },
              frequency: { $sum: 1 },
            },
          },
          { $sort: { frequency: -1, _id: 1 } },
          { $limit: 5 },
        ]),
        ResumeModel.aggregate([
          { $group: { _id: "$userId", resumeCount: { $sum: 1 } } },
          {
            $lookup: {
              from: "users",
              localField: "_id",
              foreignField: "_id",
              as: "owner",
            },
          },
          { $unwind: "$owner" },
          { $project: { _id: 0, userName: "$owner.name", resumeCount: 1 } },
          { $sort: { resumeCount: -1, userName: 1 } },
        ]),
        ResumeModel.aggregate([
          {
            $project: {
              _id: 0,
              title: 1,
              expCount: { $size: "$experience" },
              projCount: { $size: "$projects" },
              skillCount: { $size: "$skills" },
              hasSummary: { $ne: ["$professionalSummary", ""] },
            },
          },
          {
            $addFields: {
              completenessScore: {
                $add: [
                  { $min: ["$expCount", 3] },
                  { $min: ["$projCount", 3] },
                  { $min: [{ $floor: { $divide: ["$skillCount", 3] } }, 3] },
                  { $cond: ["$hasSummary", 1, 0] },
                ],
              },
            },
          },
          { $sort: { completenessScore: -1, title: 1 } },
          { $limit: 5 },
        ]),
        ResumeModel.aggregate([
          {
            $group: {
              _id: { $dateToString: { format: "%Y-%m", date: "$createdAt" } },
              resumesCreated: { $sum: 1 },
            },
          },
          { $sort: { _id: 1 } },
        ]),
        UserModel.countDocuments(),
        ResumeModel.countDocuments(),
        ResumeModel.countDocuments({ isPublic: true }),
      ]);

    return {
      templateUsage: templateUsage as unknown as TemplateUsageStat[],
      topSkills: topSkills as unknown as TopSkillStat[],
      resumesPerUser: resumesPerUser as unknown as UserResumeStat[],
      completenessScores: completenessScores as unknown as CompletenessScoreStat[],
      monthlyVelocity: monthlyVelocity as unknown as MonthlyVelocityStat[],
      summary: {
        totalUsers,
        totalResumes,
        publicResumes,
      },
      engine: "MongoDB Aggregation Pipeline (PyMongo Compatible)",
    };
  }
}

export async function runPyMongoSetup(): Promise<string> {
  const { stdout } = await execFileAsync("python3", [SCRIPT_PATH, "setup"], {
    timeout: 10000,
    env: { ...process.env },
  });
  return stdout;
}

export async function runPyMongoSeed(): Promise<string> {
  const { stdout } = await execFileAsync("python3", [SCRIPT_PATH, "seed"], {
    timeout: 15000,
    env: { ...process.env },
  });
  return stdout;
}

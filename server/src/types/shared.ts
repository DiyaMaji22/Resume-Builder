// Shared types used by both frontend and backend

export interface PersonalInfo {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  website: string;
  github: string;
  image: string;
}

export interface ExperienceEntry {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  isCurrent: boolean;
  description: string;
}

export interface EducationEntry {
  id: string;
  institution: string;
  degree: string;
  field: string;
  graduationDate: string;
  gpa: string;
}

export interface ProjectEntry {
  id: string;
  name: string;
  type: string;
  description: string;
  url: string;
  technologies: string[];
}

export interface CertificationEntry {
  id: string;
  name: string;
  issuer: string;
  date: string;
  url: string;
}

export type TemplateId = "classic" | "modern" | "minimal" | "executive" | "home_college" | "general_template";

// A point-in-time snapshot of resume content for version history
export interface ResumeSnapshot {
  snapshotId: string;
  savedAt: string;
  title: string;
  // Full content blob stored as JSON string for compact storage
  content: string;
}

export interface Resume {
  _id: string;
  userId: string;
  title: string;
  isPublic: boolean;
  template: TemplateId;
  accentColor: string;
  professionalSummary: string;
  personalInfo: PersonalInfo;
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: string[];
  versions: ResumeSnapshot[];
  createdAt: string;
  updatedAt: string;
}

export type ResumeCreatePayload = Pick<Resume, "title"> &
  Partial<Omit<Resume, "_id" | "userId" | "createdAt" | "updatedAt" | "versions">>;

export interface ResumeStarter {
  id: string;
  role: string;
  category: "Engineering" | "Data & AI" | "Product & Design" | "Marketing & Growth";
  title: string;
  description: string;
  template: TemplateId;
  accentColor: string;
  professionalSummary: string;
  personalInfo: PersonalInfo;
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: string[];
}

export interface ATSAnalysisRequest {
  resume: Resume;
  jobDescription: string;
}

export interface ATSAnalysisResult {
  overallScore: number;
  keywordScore: number;
  formattingScore: number;
  quantifiedScore: number;
  matchedKeywords: string[];
  missingKeywords: string[];
  strongActionVerbs: string[];
  recommendations: string[];
}

export type ResumeUpdatePayload = Partial<
  Omit<Resume, "_id" | "userId" | "createdAt" | "updatedAt" | "versions">
>;

export interface User {
  _id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthPayload {
  token:        string;
  refreshToken: string;
  user:         User;
}

export interface ApiResponse<T = undefined> {
  message: string;
  data?: T;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}

export interface TemplateProps {
  resume: Resume;
}

export interface TemplateDefinition {
  id: TemplateId;
  name: string;
  description: string;
}

// AI feature types
export interface AISuggestRequest {
  field: "summary" | "experience_description";
  context: {
    currentText?: string;
    position?: string;
    company?: string;
    existingExperience?: Array<{ position: string; company: string; description: string }>;
    skills?: string[];
  };
}

export interface AISuggestResponse {
  suggestion: string;
}

// PyMongo Analytics & Aggregation types
export interface TemplateUsageStat {
  _id: TemplateId;
  totalResumes: number;
  publicResumes: number;
}

export interface TopSkillStat {
  _id: string;
  frequency: number;
}

export interface UserResumeStat {
  userName: string;
  resumeCount: number;
}

export interface CompletenessScoreStat {
  title: string;
  completenessScore: number;
  expCount: number;
  projCount: number;
  skillCount: number;
  hasSummary: boolean;
}

export interface MonthlyVelocityStat {
  _id: string;
  resumesCreated: number;
}

export interface AnalyticsSummary {
  totalUsers: number;
  totalResumes: number;
  publicResumes: number;
}

export interface AnalyticsData {
  templateUsage: TemplateUsageStat[];
  topSkills: TopSkillStat[];
  resumesPerUser: UserResumeStat[];
  completenessScores: CompletenessScoreStat[];
  monthlyVelocity: MonthlyVelocityStat[];
  summary: AnalyticsSummary;
  engine: string;
}

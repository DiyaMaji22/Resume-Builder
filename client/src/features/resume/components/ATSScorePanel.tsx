import { useMemo, useState } from "react";
import {
  Sparkles, ChevronDown, ChevronUp, AlertTriangle, CheckCircle2,
  Info, Target, Plus, Check, FileSearch, ArrowRight, Zap,
} from "lucide-react";
import type { Resume } from "@/types";
import { BENCHMARK_JOBS } from "@/data/starterResumes";
import { analyzeResumeATS } from "@/utils/atsAnalyzer";
import toast from "react-hot-toast";

interface ATSCheck {
  category: string;
  passed:   boolean;
  message:  string;
  tip:      string;
}

function useATSChecks(resume: Resume): ATSCheck[] {
  return useMemo(() => {
    const p = resume.personalInfo;
    const hasEmail   = !!p.email.trim();
    const hasPhone   = !!p.phone.trim();
    const hasLinkedIn= !!p.linkedin.trim();
    const summaryLen = resume.professionalSummary.trim().length;
    const expCount   = resume.experience.length;
    const skillCount = resume.skills.length;
    const allExpHaveDesc = resume.experience.every(
      (e) => e.description.trim().length > 30
    );
    const bulletsUsed = resume.experience.some(
      (e) => e.description.includes("•") || e.description.includes("-")
    );
    const hasNumbers = resume.experience.some(
      (e) => /\d+[%$xX]|\d+\s*(percent|hours|users|customers|days|team|people|requests|growth|savings)/i.test(e.description)
    );
    const summaryHasKeywords = resume.skills.some(
      (s) => resume.professionalSummary.toLowerCase().includes(s.toLowerCase())
    );

    return [
      {
        category: "Contact Info",
        passed:   hasEmail && hasPhone,
        message:  hasEmail && hasPhone ? "Email and phone present" : "Missing email or phone",
        tip:      "ATS systems extract contact info from the top of your resume.",
      },
      {
        category: "LinkedIn",
        passed:   hasLinkedIn,
        message:  hasLinkedIn ? "LinkedIn URL included" : "No LinkedIn URL",
        tip:      "Many ATS systems score resumes higher when LinkedIn is present.",
      },
      {
        category: "Summary Length",
        passed:   summaryLen >= 100 && summaryLen <= 600,
        message:  summaryLen < 100 ? "Summary too short (< 100 chars)" :
                  summaryLen > 600 ? "Summary too long (> 600 chars)" :
                  "Summary length is ideal",
        tip:      "2–4 concise sentences is the sweet spot for ATS parsing.",
      },
      {
        category: "Keyword Alignment",
        passed:   summaryHasKeywords,
        message:  summaryHasKeywords ? "Skills appear in summary" : "Summary missing skill keywords",
        tip:      "Mirror keywords from your skills section in your summary.",
      },
      {
        category: "Experience",
        passed:   expCount >= 1 && allExpHaveDesc,
        message:  expCount === 0 ? "No experience entries" :
                  !allExpHaveDesc ? "Some entries missing descriptions" :
                  "All experience entries have descriptions",
        tip:      "Every role needs at least a 1–2 sentence description.",
      },
      {
        category: "Bullet Points",
        passed:   bulletsUsed,
        message:  bulletsUsed ? "Bullet-style descriptions found" : "No bullet points detected",
        tip:      "Start each description line with • for ATS-friendly formatting.",
      },
      {
        category: "Quantified Impact",
        passed:   hasNumbers,
        message:  hasNumbers ? "Quantified achievements found" : "No numbers or metrics found",
        tip:      "Add numbers: '40% faster', '$2M revenue', '10,000 users'.",
      },
      {
        category: "Skills Section",
        passed:   skillCount >= 6,
        message:  skillCount < 6 ? `Only ${skillCount} skills listed` : `${skillCount} skills listed`,
        tip:      "List 8–15 skills. ATS systems match job keywords against this section.",
      },
    ];
  }, [resume]);
}

interface Props {
  resume: Resume;
  onAddSkill?: (skill: string) => void;
}

export function ATSScorePanel({ resume, onAddSkill }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<"job-match" | "health">("job-match");
  const [selectedJobId, setSelectedJobId] = useState<string>("full-stack-eng");
  const [customJdText, setCustomJdText] = useState<string>(BENCHMARK_JOBS[0].description);
  const [isEditingJd, setIsEditingJd] = useState(false);

  const checks = useATSChecks(resume);
  const healthPassed = checks.filter((c) => c.passed).length;
  const healthScore = Math.round((healthPassed / checks.length) * 100);

  // Analyze against current Job Description
  const analysis = useMemo(() => {
    return analyzeResumeATS(resume, customJdText);
  }, [resume, customJdText]);

  const handleSelectJob = (id: string) => {
    setSelectedJobId(id);
    if (id === "custom") {
      setIsEditingJd(true);
      setCustomJdText("");
    } else {
      const match = BENCHMARK_JOBS.find((j) => j.id === id);
      if (match) {
        setCustomJdText(match.description);
      }
    }
  };

  const handleQuickAddSkill = (skill: string) => {
    if (onAddSkill) {
      onAddSkill(skill);
      toast.success(`Added "${skill}" to skills!`);
    }
  };

  const overallScore = Math.round((analysis.overallScore * 0.65) + (healthScore * 0.35));

  const scoreColor =
    overallScore >= 75 ? "var(--success)" :
    overallScore >= 50 ? "var(--accent)" :
    "var(--danger)";

  const scoreLabel =
    overallScore >= 80 ? "Top ATS Match" :
    overallScore >= 65 ? "Good Match" :
    overallScore >= 45 ? "Needs Improvement" :
    "Low Match";

  return (
    <div
      className="rounded-xl overflow-hidden transition-all duration-200"
      style={{ border: "1px solid var(--border)", background: "var(--surface)" }}
    >
      {/* Header Bar */}
      <button
        type="button"
        className="settings-btn w-full flex items-center justify-between px-4 py-3.5 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
        style={{ color: "var(--text-primary)", background: "transparent" }}
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="size-7 rounded-lg flex items-center justify-center shrink-0"
            style={{ background: "var(--accent-dim)", color: "var(--accent)" }}
          >
            <Sparkles className="size-4" />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">ATS Analyzer & Job Match</span>
              <span
                className="text-[11px] font-bold px-2 py-0.5 rounded-full"
                style={{ background: "var(--accent-dim)", color: scoreColor }}
              >
                {overallScore}% — {scoreLabel}
              </span>
            </div>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              {analysis.matchedKeywords.length} matched keywords • {analysis.missingKeywords.length} missing
            </p>
          </div>
        </div>
        {expanded
          ? <ChevronUp className="size-4" style={{ color: "var(--text-muted)" }} />
          : <ChevronDown className="size-4" style={{ color: "var(--text-muted)" }} />}
      </button>

      {expanded && (
        <div style={{ borderTop: "1px solid var(--border)" }}>
          {/* Sub Navigation Tabs */}
          <div className="flex border-b" style={{ borderColor: "var(--border)", background: "var(--bg-subtle)" }}>
            <button
              type="button"
              onClick={() => setActiveTab("job-match")}
              className={`flex-1 py-2 text-xs font-semibold flex items-center justify-center gap-1.5 border-b-2 transition-all ${
                activeTab === "job-match"
                  ? "border-blue-600 text-blue-600 dark:text-blue-400 bg-white/50 dark:bg-white/5"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              }`}
            >
              <Target className="size-3.5" />
              Job Match & Keywords
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("health")}
              className={`flex-1 py-2 text-xs font-semibold flex items-center justify-center gap-1.5 border-b-2 transition-all ${
                activeTab === "health"
                  ? "border-blue-600 text-blue-600 dark:text-blue-400 bg-white/50 dark:bg-white/5"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              }`}
            >
              <FileSearch className="size-3.5" />
              Resume Health ({healthScore}%)
            </button>
          </div>

          {/* TAB 1: JOB DESCRIPTION MATCH & KEYWORDS */}
          {activeTab === "job-match" && (
            <div className="p-4 space-y-4">
              {/* Job Selector Dropdown */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold" style={{ color: "var(--text-primary)" }}>
                    Target Job Benchmark
                  </label>
                  <button
                    type="button"
                    onClick={() => setIsEditingJd((v) => !v)}
                    className="text-[11px] hover:underline"
                    style={{ color: "var(--accent)" }}
                  >
                    {isEditingJd ? "Hide JD editor" : "Paste custom JD"}
                  </button>
                </div>
                <select
                  value={selectedJobId}
                  onChange={(e) => handleSelectJob(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg"
                  style={{
                    background: "var(--bg-subtle)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                  }}
                >
                  <optgroup label="Kaggle Dataset Benchmark Roles">
                    {BENCHMARK_JOBS.map((job) => (
                      <option key={job.id} value={job.id}>
                        {job.title} ({job.companyType})
                      </option>
                    ))}
                  </optgroup>
                  <option value="custom">Custom Job Description (Paste your own)</option>
                </select>
              </div>

              {/* Editable JD Textarea */}
              {isEditingJd && (
                <div className="space-y-1">
                  <textarea
                    rows={4}
                    value={customJdText}
                    onChange={(e) => setCustomJdText(e.target.value)}
                    placeholder="Paste job description requirements and qualifications here..."
                    className="w-full text-xs p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                    style={{
                      background: "var(--bg-subtle)",
                      border: "1px solid var(--border)",
                      color: "var(--text-primary)",
                    }}
                  />
                  <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                    Keywords will automatically recalculate against this job description in real-time.
                  </p>
                </div>
              )}

              {/* Quick Metrics Cards */}
              <div className="grid grid-cols-3 gap-2">
                <div
                  className="p-2.5 rounded-lg text-center"
                  style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                >
                  <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Keywords</div>
                  <div className="text-sm font-bold" style={{ color: "var(--accent)" }}>
                    {analysis.keywordScore}%
                  </div>
                </div>
                <div
                  className="p-2.5 rounded-lg text-center"
                  style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                >
                  <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Metrics & Impact</div>
                  <div className="text-sm font-bold" style={{ color: "var(--success)" }}>
                    {analysis.quantifiedScore}%
                  </div>
                </div>
                <div
                  className="p-2.5 rounded-lg text-center"
                  style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                >
                  <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>Action Verbs</div>
                  <div className="text-sm font-bold" style={{ color: "var(--accent-text)" }}>
                    {analysis.strongActionVerbs.length}
                  </div>
                </div>
              </div>

              {/* Missing Keywords Box with 1-Click Add */}
              {analysis.missingKeywords.length > 0 && (
                <div
                  className="p-3 rounded-lg space-y-2"
                  style={{
                    background: "color-mix(in oklch, var(--danger) 6%, transparent)",
                    border: "1px solid color-mix(in oklch, var(--danger) 25%, transparent)",
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold flex items-center gap-1.5" style={{ color: "var(--danger)" }}>
                      <AlertTriangle className="size-3.5" />
                      Missing Keywords in Resume ({analysis.missingKeywords.length})
                    </span>
                    <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                      Click + to add to Skills
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.missingKeywords.map((kw) => (
                      <button
                        key={kw}
                        type="button"
                        onClick={() => handleQuickAddSkill(kw)}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium transition-transform hover:scale-105"
                        style={{
                          background: "var(--surface)",
                          border: "1px solid var(--border)",
                          color: "var(--text-primary)",
                        }}
                        title={`Click to add ${kw} to your skills`}
                      >
                        <Plus className="size-3 text-blue-500" />
                        {kw}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Matched Keywords Box */}
              {analysis.matchedKeywords.length > 0 && (
                <div
                  className="p-3 rounded-lg space-y-2"
                  style={{
                    background: "color-mix(in oklch, var(--success) 6%, transparent)",
                    border: "1px solid color-mix(in oklch, var(--success) 20%, transparent)",
                  }}
                >
                  <span className="text-xs font-semibold flex items-center gap-1.5" style={{ color: "var(--success)" }}>
                    <CheckCircle2 className="size-3.5" />
                    Matched Keywords ({analysis.matchedKeywords.length})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.matchedKeywords.map((kw) => (
                      <span
                        key={kw}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium"
                        style={{
                          background: "var(--surface)",
                          border: "1px solid color-mix(in oklch, var(--success) 30%, transparent)",
                          color: "var(--text-primary)",
                        }}
                      >
                        <Check className="size-3 text-emerald-500" />
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Actionable Recommendations */}
              {analysis.recommendations.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <div className="text-xs font-semibold flex items-center gap-1" style={{ color: "var(--text-primary)" }}>
                    <Zap className="size-3.5 text-amber-500" />
                    ATS Optimization Recommendations
                  </div>
                  <ul className="space-y-1">
                    {analysis.recommendations.map((rec, i) => (
                      <li key={i} className="text-[11px] flex items-start gap-1.5" style={{ color: "var(--text-secondary)" }}>
                        <ArrowRight className="size-3 shrink-0 mt-0.5 text-blue-500" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: RESUME HEALTH CHECKS */}
          {activeTab === "health" && (
            <div className="p-4 space-y-2">
              {checks.map((check) => (
                <div
                  key={check.category}
                  className="rounded-lg p-3 space-y-1"
                  style={{
                    background: check.passed
                      ? "color-mix(in oklch, var(--success) 8%, transparent)"
                      : "var(--danger-dim)",
                    border: `1px solid ${
                      check.passed
                        ? "color-mix(in oklch, var(--success) 20%, transparent)"
                        : "color-mix(in oklch, var(--danger) 20%, transparent)"
                    }`,
                  }}
                >
                  <div className="flex items-center gap-2">
                    {check.passed
                      ? <CheckCircle2 className="size-3.5 shrink-0" style={{ color: "var(--success)" }} />
                      : <AlertTriangle className="size-3.5 shrink-0" style={{ color: "var(--danger)" }} />}
                    <span className="text-xs font-semibold" style={{ color: "var(--text-primary)" }}>
                      {check.category}
                    </span>
                  </div>
                  <p className="text-xs pl-5" style={{ color: "var(--text-secondary)" }}>
                    {check.message}
                  </p>
                  {!check.passed && (
                    <div className="flex items-start gap-1.5 pl-5">
                      <Info className="size-3 shrink-0 mt-0.5" style={{ color: "var(--text-muted)" }} />
                      <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                        {check.tip}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

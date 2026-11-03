import { useState } from "react";
import {
  X, Sparkles, Briefcase, Code2,
  ArrowRight, ShieldCheck, ChevronRight
} from "lucide-react";
import { STARTER_RESUMES } from "@/data/starterResumes";
import type { ResumeStarter } from "@/types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectStarter: (starter: ResumeStarter) => void;
  isLoading?: boolean;
  actionLabel?: string;
  title?: string;
  description?: string;
}

export function StarterTemplatesModal({
  isOpen,
  onClose,
  onSelectStarter,
  isLoading = false,
  actionLabel = "Use This Starter",
  title = "ATS-Optimized Starter Resumes",
  description = "Pre-populated with real industry data from Kaggle resume benchmarks. Pick a profession to jumpstart your resume.",
}: Props) {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [activeStarterId, setActiveStarterId] = useState<string>(STARTER_RESUMES[0].id);

  if (!isOpen) return null;

  const categories = ["All", "Engineering", "Data & AI", "Product & Design", "Marketing & Growth"];

  const filteredStarters = selectedCategory === "All"
    ? STARTER_RESUMES
    : STARTER_RESUMES.filter((s) => s.category === selectedCategory);

  const activeStarter = STARTER_RESUMES.find((s) => s.id === activeStarterId) ?? filteredStarters[0];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm anim-fade-in"
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl overflow-hidden shadow-2xl anim-scale-up"
        style={{ background: "var(--surface)", border: "1px solid var(--border-strong)" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between border-b"
          style={{ borderColor: "var(--border)", background: "var(--bg-subtle)" }}
        >
          <div className="flex items-center gap-2.5">
            <div
              className="size-8 rounded-lg flex items-center justify-center"
              style={{ background: "var(--accent-dim)", color: "var(--accent)" }}
            >
              <Sparkles className="size-4" />
            </div>
            <div>
              <h2 className="text-base font-bold" style={{ color: "var(--text-primary)" }}>
                {title}
              </h2>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                {description}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            style={{ color: "var(--text-muted)" }}
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Category Tabs */}
        <div
          className="px-6 py-2.5 flex items-center gap-2 overflow-x-auto border-b"
          style={{ borderColor: "var(--border)", background: "var(--surface)" }}
        >
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => {
                setSelectedCategory(cat);
                const first = cat === "All" ? STARTER_RESUMES[0] : STARTER_RESUMES.find((s) => s.category === cat);
                if (first) setActiveStarterId(first.id);
              }}
              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? "bg-blue-600 text-white shadow-sm"
                  : "hover:bg-black/5 dark:hover:bg-white/5 text-gray-500 dark:text-gray-400"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Modal Body: Split 2 columns */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 overflow-hidden min-h-[420px]">
          {/* Left Column: List of Roles */}
          <div
            className="md:col-span-5 p-4 space-y-2 overflow-y-auto border-r"
            style={{ borderColor: "var(--border)", background: "var(--bg-subtle)" }}
          >
            {filteredStarters.map((starter) => {
              const isSelected = starter.id === activeStarterId;
              return (
                <button
                  key={starter.id}
                  type="button"
                  onClick={() => setActiveStarterId(starter.id)}
                  className={`w-full text-left p-3 rounded-xl border transition-all flex items-start justify-between gap-2 ${
                    isSelected
                      ? "ring-2 ring-blue-500 shadow-sm"
                      : "hover:border-blue-300 dark:hover:border-blue-800"
                  }`}
                  style={{
                    background: isSelected ? "var(--surface)" : "var(--surface)",
                    borderColor: isSelected ? "var(--accent)" : "var(--border)",
                  }}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="size-2 rounded-full"
                        style={{ background: starter.accentColor }}
                      />
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-500">
                        {starter.category}
                      </span>
                    </div>
                    <h3 className="text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                      {starter.role}
                    </h3>
                    <p className="text-[11px] line-clamp-2 mt-0.5" style={{ color: "var(--text-muted)" }}>
                      {starter.description}
                    </p>
                    <div className="flex items-center gap-1.5 mt-2">
                      <span
                        className="text-[10px] px-2 py-0.5 rounded-full capitalize font-medium"
                        style={{ background: "var(--accent-dim)", color: "var(--accent-text)" }}
                      >
                        {starter.template} template
                      </span>
                      <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                        {starter.skills.length} ATS skills
                      </span>
                    </div>
                  </div>
                  <ChevronRight
                    className={`size-4 shrink-0 transition-transform ${
                      isSelected ? "text-blue-500 translate-x-0.5" : "text-gray-400"
                    }`}
                  />
                </button>
              );
            })}
          </div>

          {/* Right Column: Detailed Preview of Selected Starter */}
          <div className="md:col-span-7 p-6 overflow-y-auto space-y-4" style={{ background: "var(--surface)" }}>
            {activeStarter && (
              <>
                {/* Header overview */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider"
                        style={{ background: "var(--accent-dim)", color: "var(--accent-text)" }}
                      >
                        {activeStarter.category}
                      </span>
                      <span className="text-xs flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                        <ShieldCheck className="size-3.5" /> High ATS Match
                      </span>
                    </div>
                    <h2 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>
                      {activeStarter.role}
                    </h2>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                      {activeStarter.personalInfo.fullName} • {activeStarter.personalInfo.location}
                    </p>
                  </div>

                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={() => onSelectStarter(activeStarter)}
                    className="btn btn-primary px-4 py-2 text-xs flex items-center gap-1.5 shrink-0 shadow-md"
                  >
                    {isLoading ? <span className="spinner" /> : <Sparkles className="size-3.5" />}
                    <span>{actionLabel}</span>
                  </button>
                </div>

                {/* Professional Summary */}
                <div
                  className="p-3 rounded-xl space-y-1"
                  style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                >
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                    Professional Summary
                  </h4>
                  <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {activeStarter.professionalSummary}
                  </p>
                </div>

                {/* Skills Preview */}
                <div className="space-y-1.5">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1.5">
                    <Code2 className="size-3.5" /> Pre-configured ATS Keywords ({activeStarter.skills.length})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {activeStarter.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 rounded-md text-[11px] font-medium"
                        style={{
                          background: "var(--bg-subtle)",
                          border: "1px solid var(--border)",
                          color: "var(--text-primary)",
                        }}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Experience Highlights */}
                <div className="space-y-2">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1.5">
                    <Briefcase className="size-3.5" /> Experience Highlights
                  </h4>
                  <div className="space-y-2">
                    {activeStarter.experience.map((exp) => (
                      <div
                        key={exp.id}
                        className="p-3 rounded-xl space-y-1"
                        style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold" style={{ color: "var(--text-primary)" }}>
                            {exp.position}
                          </span>
                          <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                            {exp.startDate} – {exp.isCurrent ? "Present" : exp.endDate}
                          </span>
                        </div>
                        <p className="text-[11px] font-medium" style={{ color: "var(--accent)" }}>
                          {exp.company}
                        </p>
                        <p className="text-xs whitespace-pre-line leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                          {exp.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Education & Certs summary */}
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div
                    className="p-2.5 rounded-xl space-y-0.5"
                    style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                  >
                    <div className="text-[10px] uppercase font-bold text-gray-400">Education</div>
                    <div className="text-xs font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                      {activeStarter.education[0]?.degree}
                    </div>
                    <div className="text-[11px] truncate" style={{ color: "var(--text-muted)" }}>
                      {activeStarter.education[0]?.institution}
                    </div>
                  </div>
                  <div
                    className="p-2.5 rounded-xl space-y-0.5"
                    style={{ background: "var(--bg-subtle)", border: "1px solid var(--border)" }}
                  >
                    <div className="text-[10px] uppercase font-bold text-gray-400">Certification</div>
                    <div className="text-xs font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                      {activeStarter.certifications[0]?.name ?? "Standard Industry"}
                    </div>
                    <div className="text-[11px] truncate" style={{ color: "var(--text-muted)" }}>
                      {activeStarter.certifications[0]?.issuer ?? "Verified"}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div
          className="px-6 py-3 border-t flex items-center justify-between"
          style={{ borderColor: "var(--border)", background: "var(--bg-subtle)" }}
        >
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            Sourced from benchmark Kaggle resume corpora with quantifiable achievements.
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-ghost px-4 py-1.5 text-xs"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={isLoading}
              onClick={() => onSelectStarter(activeStarter)}
              className="btn btn-primary px-5 py-1.5 text-xs flex items-center gap-1.5"
            >
              {isLoading ? <span className="spinner" /> : <ArrowRight className="size-3.5" />}
              {actionLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Link, useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Briefcase, Download, Eye, EyeOff, FileText,
  FolderOpen, GraduationCap, Save, Share2, Sparkles, User,
  Award, ChevronLeft, ChevronRight, Clock, UploadCloud, Trash2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState, useEffect } from "react";
import { useResumeBuilder }       from "@/features/resume/hooks/useResumeBuilder";
import { PersonalInfoForm }        from "@/features/resume/components/PersonalInfoForm";
import { SummaryForm }             from "@/features/resume/components/SummaryForm";
import { ExperienceForm }          from "@/features/resume/components/ExperienceForm";
import { EducationForm }           from "@/features/resume/components/EducationForm";
import { ProjectForm }             from "@/features/resume/components/ProjectForm";
import { SkillsForm }              from "@/features/resume/components/SkillsForm";
import { CertificationForm }       from "@/features/resume/components/CertificationForm";
import { TemplateSelector }        from "@/features/resume/components/TemplateSelector";
import { ColorPicker }             from "@/features/resume/components/ColorPicker";
import { ResumePreview }           from "@/features/resume/components/ResumePreview";
import { CompletionScore }         from "@/features/resume/components/CompletionScore";
import { ATSScorePanel }           from "@/features/resume/components/ATSScorePanel";
import { StarterTemplatesModal }   from "@/features/resume/components/StarterTemplatesModal";
import { UploadResumeModal }       from "@/features/resume/components/UploadResumeModal";
import { VersionHistoryDrawer }    from "@/features/resume/components/VersionHistoryDrawer";
import { ConfirmModal }             from "@/components/ui/ConfirmModal";
import { resumeApi }                from "@/services/api";
import toast from "react-hot-toast";
import { ThemeSwitcher } from "@/components/ui/ThemeSwitcher";

interface Section { id: string; label: string; icon: LucideIcon; }

const SECTIONS: Section[] = [
  { id: "personal",       label: "Personal",   icon: User },
  { id: "summary",        label: "Summary",    icon: FileText },
  { id: "experience",     label: "Experience", icon: Briefcase },
  { id: "education",      label: "Education",  icon: GraduationCap },
  { id: "projects",       label: "Projects",   icon: FolderOpen },
  { id: "certifications", label: "Certs",      icon: Award },
  { id: "skills",         label: "Skills",     icon: Sparkles },
];

// Mobile tab options
type MobileTab = "editor" | "preview";

export function ResumeBuilderPage() {
  const { id }   = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { resume, updateField, loadStarterData, save, isSaving, isLoading, isDirty, toggleVisibility } =
    useResumeBuilder({ resumeId: id ?? "" });

  const [activeIdx,        setActiveIdx]        = useState(0);
  const [showSettings,     setShowSettings]     = useState(false);
  const [showVersions,     setShowVersions]     = useState(false);
  const [showStarterModal, setShowStarterModal] = useState(false);
  const [showUploadModal,  setShowUploadModal]  = useState(false);
  const [showDeleteModal,  setShowDeleteModal]  = useState(false);
  const [isDeleting,       setIsDeleting]       = useState(false);
  const [mobileTab,        setMobileTab]        = useState<MobileTab>("editor");

  useEffect(() => {
    if (!id) navigate("/dashboard", { replace: true });
  }, [id, navigate]);

  const progress = ((activeIdx + 1) / SECTIONS.length) * 100;
  const active   = SECTIONS[activeIdx];

  async function handleDeleteResume() {
    if (!id) return;
    setIsDeleting(true);
    try {
      await resumeApi.delete(id);
      toast.success("Resume deleted");
      navigate("/dashboard", { replace: true });
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to delete resume");
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  }

  function handleShare() {
    const url = `${window.location.origin}/preview/${id}`;
    if (navigator.share) void navigator.share({ url, title: resume.title });
    else { void navigator.clipboard.writeText(url); toast.success("Link copied"); }
  }

  if (!id) return null;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm"
        style={{ background: "var(--bg)", color: "var(--text-muted)" }}>
        <span className="spinner mr-2" /> Loading resume…
      </div>
    );
  }

  const editorPanel = (
    <div className="space-y-4">
      {/* Section editor card */}
      <div className="overflow-hidden" style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--r-lg)", boxShadow: "var(--shadow-sm)",
      }}>
        {/* Progress */}
        <div className="h-0.5" style={{ background: "var(--border)" }}>
          <div className="h-full transition-all duration-500"
            style={{ width: `${progress}%`, background: "var(--accent)" }} />
        </div>

        {/* Tabs */}
        <div className="flex overflow-x-auto p-1.5 gap-1 bg-black/[0.02] dark:bg-white/[0.02]" style={{ borderBottom: "1px solid var(--border)" }}>
          {SECTIONS.map((sec, i) => {
            const Icon = sec.icon;
            return (
              <button key={sec.id} type="button"
                data-active={activeIdx === i ? "true" : "false"}
                onClick={() => setActiveIdx(i)}
                className="section-tab">
                <Icon className="size-3.5" />
                <span>{sec.label}</span>
              </button>
            );
          })}
        </div>

        {/* Form */}
        <div className="p-5">
          {active?.id === "personal"       && <PersonalInfoForm  data={resume.personalInfo}        onChange={(v) => updateField("personalInfo", v)} />}
          {active?.id === "summary"        && <SummaryForm       data={resume.professionalSummary} onChange={(v) => updateField("professionalSummary", v)} experience={resume.experience} skills={resume.skills} />}
          {active?.id === "experience"     && <ExperienceForm    data={resume.experience}          onChange={(v) => updateField("experience", v)} />}
          {active?.id === "education"      && <EducationForm     data={resume.education}           onChange={(v) => updateField("education", v)} />}
          {active?.id === "projects"       && <ProjectForm       data={resume.projects}            onChange={(v) => updateField("projects", v)} />}
          {active?.id === "certifications" && <CertificationForm data={resume.certifications}      onChange={(v) => updateField("certifications", v)} />}
          {active?.id === "skills"         && <SkillsForm        data={resume.skills}              onChange={(v) => updateField("skills", v)} />}
        </div>

        {/* Prev / Next */}
        <div className="flex items-center justify-between px-5 py-3"
          style={{ borderTop: "1px solid var(--border)", background: "var(--bg-subtle)" }}>
          <button type="button" disabled={activeIdx === 0}
            onClick={() => setActiveIdx((i) => Math.max(i - 1, 0))}
            className="btn btn-ghost flex items-center gap-1 text-xs px-3 py-1.5">
            <ChevronLeft className="size-4" /> Prev
          </button>
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            {activeIdx + 1} / {SECTIONS.length}
          </span>
          <button type="button" disabled={activeIdx === SECTIONS.length - 1}
            onClick={() => setActiveIdx((i) => Math.min(i + 1, SECTIONS.length - 1))}
            className="btn btn-ghost flex items-center gap-1 text-xs px-3 py-1.5">
            Next <ChevronRight className="size-4" />
          </button>
        </div>
      </div>

      {/* Completion score */}
      <div className="overflow-hidden" style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--r-lg)", boxShadow: "var(--shadow-sm)", padding: "1.25rem",
      }}>
        <CompletionScore resume={resume} />
      </div>

      {/* ATS score panel */}
      <ATSScorePanel
        resume={resume}
        onAddSkill={(skill) => {
          if (!resume.skills.includes(skill)) {
            updateField("skills", [...resume.skills, skill]);
          }
        }}
      />

      {/* Style settings */}
      <div className="overflow-hidden" style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--r-lg)", boxShadow: "var(--shadow-sm)",
      }}>
        <button type="button" onClick={() => setShowSettings((s) => !s)}
          className="settings-btn w-full flex items-center justify-between px-5 py-3 text-sm font-medium"
          style={{ color: "var(--text-primary)", background: "transparent" }}>
          Style Settings
          <ChevronRight className="size-4 transition-transform"
            style={{ color: "var(--text-muted)", transform: showSettings ? "rotate(90deg)" : "none" }} />
        </button>
        {showSettings && (
          <div className="px-5 pb-5 space-y-5"
            style={{ borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
            <TemplateSelector
              selected={resume.template}
              onChange={(v) => updateField("template", v)}
              resume={resume}
            />
            <ColorPicker value={resume.accentColor} onChange={(v) => updateField("accentColor", v)} />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen print:bg-white" style={{ background: "var(--bg-subtle)" }}>

      {/* Version history drawer */}
      {showVersions && (
        <VersionHistoryDrawer
          resume={resume}
          onClose={() => setShowVersions(false)}
          onRestore={(r) => { updateField("template", r.template); /* full restore via reload */ window.location.reload(); }}
        />
      )}

      {/* Role Starter Modal */}
      {showStarterModal && (
        <StarterTemplatesModal
          isOpen={showStarterModal}
          onClose={() => setShowStarterModal(false)}
          onSelectStarter={(starter) => {
            loadStarterData(starter);
            setShowStarterModal(false);
            toast.success(`Loaded ${starter.role} starter!`);
          }}
          actionLabel="Apply to Resume"
          title="Apply a Role Starter"
          description="Populate your resume with verified skills and bullet points from Kaggle benchmarks."
        />
      )}

      {/* Upload PDF Modal */}
      {showUploadModal && (
        <UploadResumeModal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          onSuccess={(newResume) => {
            navigate(`/builder/${newResume._id}`);
          }}
        />
      )}

      {/* Delete Resume Confirmation Modal */}
      {showDeleteModal && (
        <ConfirmModal
          title="Delete resume"
          message={`"${resume.title || "Untitled Resume"}" will be permanently deleted. This action cannot be undone.`}
          confirmLabel={isDeleting ? "Deleting…" : "Delete"}
          danger
          onConfirm={() => void handleDeleteResume()}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}

      {/* Top bar */}
      <header className="print:hidden backdrop-blur-md" style={{
        background: "color-mix(in oklch, var(--surface) 85%, transparent)",
        borderBottom: "1px solid var(--border)",
        padding: "0 1.25rem", height: "54px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 40,
      }}>
        <div className="flex items-center gap-2 min-w-0">
          <Link to="/dashboard" className="btn btn-surface flex items-center gap-1.5 text-xs px-2.5 py-1.5 shrink-0 hover:border-indigo-400">
            <ArrowLeft className="size-3.5" /> <span className="hidden sm:inline font-medium">Dashboard</span>
          </Link>
          <span className="hidden sm:inline text-gray-300 dark:text-gray-700">/</span>
          <input type="text" aria-label="Resume title" value={resume.title}
            onChange={(e) => updateField("title", e.target.value)}
            className="text-sm font-bold bg-transparent border-none outline-none min-w-0 truncate hover:bg-black/5 dark:hover:bg-white/5 px-2 py-1 rounded-md transition-colors"
            style={{ color: "var(--text-primary)", width: "180px" }} />
          {isDirty ? (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0 hidden sm:inline-flex items-center gap-1">
              <span className="size-1.5 rounded-full bg-amber-500 animate-pulse" />
              Unsaved
            </span>
          ) : (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 shrink-0 hidden sm:inline-flex items-center gap-1">
              <span className="size-1.5 rounded-full bg-emerald-500" />
              Saved
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <ThemeSwitcher />
          <button type="button" onClick={() => setShowStarterModal(true)}
            title="Load starter content from Kaggle benchmarks"
            className="btn btn-surface flex items-center gap-1.5 text-xs px-3 py-1.5 hidden sm:flex">
            <Sparkles className="size-3.5 text-amber-500" />
            <span>Starters</span>
          </button>
          <button type="button" onClick={() => setShowUploadModal(true)}
            title="Import an existing PDF resume"
            className="btn btn-surface flex items-center gap-1.5 text-xs px-3 py-1.5 hidden sm:flex">
            <UploadCloud className="size-3.5 text-blue-500" />
            <span>Upload PDF</span>
          </button>
          <button type="button" onClick={() => setShowVersions(true)}
            title="Version history"
            className="btn btn-surface p-2">
            <Clock className="size-4" />
          </button>
          <button type="button" onClick={() => setShowDeleteModal(true)}
            title="Delete this resume"
            className="btn btn-surface p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 transition-colors">
            <Trash2 className="size-4" />
          </button>
          {resume.isPublic && (
            <button type="button" onClick={handleShare}
              className="btn btn-surface flex items-center gap-1.5 text-xs px-3 py-1.5 hidden sm:flex">
              <Share2 className="size-3.5" /> Share
            </button>
          )}
          <button type="button" onClick={() => void toggleVisibility()}
            className="btn btn-surface flex items-center gap-1.5 text-xs px-3 py-1.5 hidden sm:flex">
            {resume.isPublic ? <><Eye className="size-3.5" /> Public</> : <><EyeOff className="size-3.5" /> Private</>}
          </button>
          <button type="button" onClick={() => window.print()}
            className="btn btn-surface flex items-center gap-1.5 text-xs px-3 py-1.5">
            <Download className="size-3.5" /> <span className="hidden sm:inline">PDF</span>
          </button>
          <button type="button" disabled={isSaving}
            onClick={() => void toast.promise(save(), { loading: "Saving…", success: "Saved!", error: "Failed to save" })}
            className="btn btn-primary flex items-center gap-1.5 text-xs px-4 py-1.5">
            {isSaving ? <span className="spinner" /> : <Save className="size-3.5" />}
            <span className="hidden sm:inline">{isSaving ? "Saving…" : "Save"}</span>
          </button>
        </div>
      </header>

      {/* Mobile tab switcher */}
      <div className="lg:hidden print:hidden" style={{ borderBottom: "1px solid var(--border)", background: "var(--surface)" }}>
        <div className="tab-bar">
          <button type="button" data-active={mobileTab === "editor" ? "true" : "false"}
            onClick={() => setMobileTab("editor")} className="tab-bar-item">
            Edit
          </button>
          <button type="button" data-active={mobileTab === "preview" ? "true" : "false"}
            onClick={() => setMobileTab("preview")} className="tab-bar-item">
            Preview
          </button>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-4 py-5 print:block lg:grid lg:grid-cols-[460px_1fr] lg:gap-5">

        {/* Editor — shown on desktop always, on mobile only when tab=editor */}
        <div className={`print:hidden space-y-4 ${mobileTab === "preview" ? "hidden lg:block" : ""}`}>
          {editorPanel}
        </div>

        {/* Preview — shown on desktop always, on mobile only when tab=preview */}
        <div className={`lg:sticky lg:top-[60px] self-start ${mobileTab === "editor" ? "hidden lg:block" : ""}`}>
          {/* Desktop: scaled preview */}
          <div className="hidden lg:block origin-top-left print:transform-none print:w-auto"
            style={{ transform: "scale(0.74)", width: "135.1%" }}>
            <ResumePreview resume={resume} />
          </div>
          {/* Mobile: full-width preview */}
          <div className="lg:hidden">
            <ResumePreview resume={resume} />
          </div>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FilePlus, Trash2, Edit3, Clock, FileText,
  LogOut, Copy, Check, X, MoreHorizontal,
  Settings, Sparkles, UploadCloud,
  ArrowRight, ShieldCheck,
} from "lucide-react";
import { resumeApi } from "@/services/api";
import { useAppSelector, useAppDispatch } from "@/hooks/useAppStore";
import { logout } from "@/store/features/authSlice";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { ThemeSwitcher } from "@/components/ui/ThemeSwitcher";
import { StarterTemplatesModal } from "@/features/resume/components/StarterTemplatesModal";
import { UploadResumeModal } from "@/features/resume/components/UploadResumeModal";
import { STARTER_RESUMES } from "@/data/starterResumes";
import toast from "react-hot-toast";
import type { Resume, ResumeStarter } from "@/types";

interface DeleteTarget { id: string; title: string; }
interface RenameState  { id: string; value: string; }

const TEMPLATE_COLORS: Record<string, string> = {
  classic:          "#4f46e5",
  modern:           "#6366f1",
  minimal:          "#0ea5e9",
  executive:        "#8b5cf6",
  home_college:     "#3b82f6",
  general_template: "#10b981",
};

export function DashboardPage() {
  const user     = useAppSelector((s) => s.auth.user);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const [resumes,          setResumes]          = useState<Resume[]>([]);
  const [loading,          setLoading]          = useState(true);
  const [creating,         setCreating]         = useState(false);
  const [duplicating,      setDuplicating]      = useState<string | null>(null);
  const [deleteTarget,     setDeleteTarget]     = useState<DeleteTarget | null>(null);
  const [rename,           setRename]           = useState<RenameState | null>(null);
  const [openMenuId,       setOpenMenuId]       = useState<string | null>(null);
  const [showStarterModal, setShowStarterModal] = useState(false);
  const [showUploadModal,  setShowUploadModal]  = useState(false);
  const renameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.title = "Dashboard — ResumeBuilder";
    resumeApi.list()
      .then(({ data }) => setResumes(data.data ?? []))
      .catch(() => toast.error("Failed to load resumes"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { if (rename) renameInputRef.current?.select(); }, [rename?.id]);

  useEffect(() => {
    if (!openMenuId) return;
    const close = (e: MouseEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest('[data-dropdown="true"]')) return;
      setOpenMenuId(null);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [openMenuId]);

  async function handleCreate() {
    setCreating(true);
    try {
      const { data } = await resumeApi.create({ title: "Untitled Resume" });
      if (data.data) navigate(`/builder/${data.data._id}`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to create");
    } finally { setCreating(false); }
  }

  async function handleCreateFromStarter(starter: ResumeStarter) {
    setCreating(true);
    try {
      const { id, category, role, description, ...fields } = starter;
      void id; void category; void description;
      const { data } = await resumeApi.create({
        ...fields,
        title: `${role} Resume`,
      });
      if (data.data) {
        toast.success(`Created resume from ${role} starter!`);
        navigate(`/builder/${data.data._id}`);
      }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to create from starter");
    } finally {
      setCreating(false);
      setShowStarterModal(false);
    }
  }

  async function handleDuplicate(id: string) {
    setDuplicating(id); setOpenMenuId(null);
    try {
      const { data } = await resumeApi.duplicate(id);
      if (data.data) { setResumes(p => [data.data!, ...p]); toast.success("Duplicated"); }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed");
    } finally { setDuplicating(null); }
  }

  async function commitRename() {
    if (!rename) return;
    const trimmed = rename.value.trim();
    if (!trimmed) { setRename(null); return; }
    setResumes(p => p.map(r => r._id === rename.id ? { ...r, title: trimmed } : r));
    setRename(null);
    try {
      await resumeApi.update(rename.id, { title: trimmed });
    } catch {
      resumeApi.list().then(({ data }) => setResumes(data.data ?? [])).catch(() => null);
    }
  }

  async function executeDelete() {
    if (!deleteTarget) return;
    const { id, title } = deleteTarget;
    setDeleteTarget(null);
    const prev = resumes;
    setResumes(p => p.filter(r => r._id !== id));
    try {
      await resumeApi.delete(id);
      toast.success(`Deleted "${title}"`);
    } catch (err: unknown) {
      setResumes(prev);
      toast.error(err instanceof Error ? err.message : "Failed to delete resume");
    }
  }

  return (
    <div className="min-h-screen flex" style={{ background: "var(--bg)" }}>
      {deleteTarget && (
        <ConfirmModal
          title="Delete resume"
          message={`"${deleteTarget.title}" will be permanently deleted.`}
          confirmLabel="Delete" danger
          onConfirm={() => void executeDelete()}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {showStarterModal && (
        <StarterTemplatesModal
          isOpen={showStarterModal}
          onClose={() => setShowStarterModal(false)}
          onSelectStarter={(starter) => void handleCreateFromStarter(starter)}
          isLoading={creating}
          actionLabel="Create From Starter"
        />
      )}

      {showUploadModal && (
        <UploadResumeModal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          onSuccess={(newResume) => {
            navigate(`/builder/${newResume._id}`);
          }}
        />
      )}

      {/* ── Sidebar ── */}
      <aside className="sidebar w-56 shrink-0 h-screen sticky top-0 hidden lg:flex">
        {/* Logo */}
        <div className="px-5 py-5 flex items-center gap-2.5">
          <div className="size-8 rounded-xl flex items-center justify-center bg-gradient-to-tr from-indigo-600 to-indigo-400 shadow-md shadow-indigo-500/25">
            <FileText className="size-4 text-white" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-white block">
              ResumeBuilder
            </span>
            <span className="text-[10px] text-indigo-300/70 font-medium block">
              AI & ATS Studio
            </span>
          </div>
        </div>

        <div className="divider mx-4" style={{ background: "rgba(255,255,255,0.06)" }} />

        {/* Nav */}
        <nav className="flex-1 py-4 space-y-1">
          <Link to="/dashboard" className="sidebar-item" data-active="true">
            <FileText className="size-4 text-indigo-400" /> My Resumes
          </Link>
          <Link to="/settings" className="sidebar-item">
            <Settings className="size-4" /> Settings
          </Link>
        </nav>

        {/* User */}
        <div className="p-4">
          <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl"
            style={{ background: "rgba(255,255,255,0.06)" }}>
            <div className="size-7 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
              style={{ background: "var(--accent)" }}>
              {user?.name?.[0]?.toUpperCase() ?? "U"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold truncate" style={{ color: "var(--text-nav)" }}>
                {user?.name}
              </p>
              <p className="text-[10px] truncate" style={{ color: "var(--text-nav-muted)" }}>
                {user?.email}
              </p>
            </div>
          </div>
          <button type="button" onClick={() => { dispatch(logout()); navigate("/"); }}
            className="sidebar-item w-full mt-1 text-xs"
            style={{ color: "var(--text-nav-muted)" }}>
            <LogOut className="size-3.5" /> Sign out
          </button>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="anim-slide-left flex items-center justify-between px-6 h-14 shrink-0"
          style={{
            background: "var(--surface)", borderBottom: "1px solid var(--border)",
            position: "sticky", top: 0, zIndex: 40,
          }}>
          <div>
            <h1 className="text-sm font-bold" style={{ color: "var(--text-primary)" }}>My Resumes</h1>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {resumes.length} resume{resumes.length !== 1 ? "s" : ""}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeSwitcher />
            <button
              type="button"
              onClick={() => setShowUploadModal(true)}
              disabled={creating}
              className="btn btn-surface flex items-center gap-1.5 px-3 py-2 text-xs"
            >
              <UploadCloud className="size-3.5 text-blue-500" />
              <span>Upload PDF</span>
            </button>
            <button
              type="button"
              onClick={() => setShowStarterModal(true)}
              disabled={creating}
              className="btn btn-surface flex items-center gap-1.5 px-3 py-2 text-xs"
            >
              <Sparkles className="size-3.5 text-amber-500" />
              <span>Role Starters</span>
            </button>
            <button
              type="button"
              onClick={() => void handleCreate()}
              disabled={creating}
              className="btn btn-primary flex items-center gap-1.5 px-3.5 py-2 text-xs"
            >
              {creating ? <span className="spinner" /> : <FilePlus className="size-3.5" />}
              <span>{creating ? "Creating…" : "Blank Resume"}</span>
            </button>
            {/* Mobile logout */}
            <button type="button" title="Sign out" className="btn btn-surface p-2 lg:hidden"
              onClick={() => { dispatch(logout()); navigate("/"); }}>
              <LogOut className="size-4" />
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 px-6 py-8 space-y-8">
          {/* Hero Welcome Banner */}
          <div className="relative overflow-hidden p-6 rounded-2xl border border-indigo-500/15 bg-gradient-to-r from-indigo-950/15 via-slate-900/5 to-transparent backdrop-blur-sm"
            style={{ background: "color-mix(in oklch, var(--surface) 92%, var(--accent-dim))" }}>
            <div className="relative z-10 max-w-2xl space-y-2">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                <Sparkles className="size-3" />
                <span>Next-Gen Career Engine • ATS & AI-Powered</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
                Craft an ATS-Proof Resume in Minutes
              </h1>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                Target job descriptions with real-time keyword matching, import any existing PDF, or start with proven Kaggle role benchmarks.
              </p>
            </div>
            {/* Subtle glow orb */}
            <div className="absolute right-0 top-0 size-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          </div>

          {/* Quick-Start Shelf: Kaggle Benchmark Roles */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-1 rounded-md bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400">
                  <Sparkles className="size-3.5" />
                </span>
                <h2 className="text-sm font-bold" style={{ color: "var(--text-primary)" }}>
                  Pre-populated Role Starters (Kaggle Dataset)
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setShowStarterModal(true)}
                className="text-xs font-semibold hover:underline flex items-center gap-1 text-blue-600 dark:text-blue-400"
              >
                View all 6 roles <ArrowRight className="size-3" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {STARTER_RESUMES.slice(0, 3).map((starter) => (
                <div
                  key={starter.id}
                  className="card p-4 flex flex-col justify-between group hover:border-blue-400 dark:hover:border-blue-500 transition-all cursor-pointer"
                  onClick={() => void handleCreateFromStarter(starter)}
                  style={{ borderRadius: "var(--r-xl)" }}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-500">
                        {starter.category}
                      </span>
                      <span className="text-[10px] flex items-center gap-1 text-emerald-600 font-semibold">
                        <ShieldCheck className="size-3" /> ATS Verified
                      </span>
                    </div>
                    <h3 className="text-sm font-bold group-hover:text-blue-600 transition-colors" style={{ color: "var(--text-primary)" }}>
                      {starter.role}
                    </h3>
                    <p className="text-[11px] line-clamp-2 mt-1" style={{ color: "var(--text-muted)" }}>
                      {starter.description}
                    </p>
                    <div className="flex flex-wrap gap-1 mt-2.5">
                      {starter.skills.slice(0, 4).map((s) => (
                        <span key={s} className="text-[10px] px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/5 font-medium" style={{ color: "var(--text-secondary)" }}>
                          {s}
                        </span>
                      ))}
                      {starter.skills.length > 4 && (
                        <span className="text-[10px] px-1 py-0.5 text-gray-400 font-medium">
                          +{starter.skills.length - 4}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 mt-3 border-t text-xs font-semibold text-blue-600 dark:text-blue-400" style={{ borderColor: "var(--border)" }}>
                    <span>Use this template</span>
                    <ArrowRight className="size-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* User Resumes Section */}
          <section className="space-y-3">
            <h2 className="text-sm font-bold" style={{ color: "var(--text-primary)" }}>
              Your Saved Resumes
            </h2>

            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-52 rounded-2xl skeleton" />
                ))}
              </div>
            ) : resumes.length === 0 ? (
              <div className="text-center py-16 anim-fade-up rounded-2xl border" style={{ borderColor: "var(--border)", background: "var(--surface)" }}>
                <div className="relative inline-flex mb-4">
                  <div className="size-14 rounded-2xl flex items-center justify-center"
                    style={{ background: "var(--accent-dim)" }}>
                    <FileText className="size-7" style={{ color: "var(--accent-text)" }} />
                  </div>
                </div>
                <h3 className="text-base font-bold mb-1" style={{ color: "var(--text-primary)" }}>No resumes created yet</h3>
                <p className="text-xs mb-6 max-w-sm mx-auto" style={{ color: "var(--text-muted)" }}>
                  Choose a profession starter above to begin with real industry bullet points, or start with a clean slate.
                </p>
                <div className="flex flex-wrap items-center justify-center gap-3">
                  <button type="button" onClick={() => setShowUploadModal(true)}
                    className="btn btn-primary px-5 py-2 text-xs flex items-center gap-1.5 shadow-sm">
                    <UploadCloud className="size-3.5" /> Upload PDF Resume
                  </button>
                  <button type="button" onClick={() => setShowStarterModal(true)}
                    className="btn btn-surface px-5 py-2 text-xs flex items-center gap-1.5">
                    <Sparkles className="size-3.5 text-amber-500" /> Pick a Role Starter
                  </button>
                  <button type="button" onClick={() => void handleCreate()}
                    className="btn btn-surface px-5 py-2 text-xs flex items-center gap-1.5">
                    <FilePlus className="size-3.5" /> Blank Resume
                  </button>
                </div>
              </div>
            ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {resumes.map((resume, i) => {
                const accent = TEMPLATE_COLORS[resume.template] ?? resume.accentColor;
                return (
                  <div key={resume._id}
                    className="card resume-card anim-fade-up group"
                    style={{ animationDelay: `${i * 45}ms` }}>
                    {/* Colour stripe */}
                    <div className="h-1 rounded-t-xl"
                      style={{ background: `linear-gradient(90deg, ${accent}, color-mix(in oklch, ${accent} 60%, #84cc16))` }} />

                    <div className="p-4">
                      {rename?.id === resume._id ? (
                        <div className="flex items-center gap-1 mb-3">
                          <input ref={renameInputRef} type="text" value={rename.value}
                            onChange={(e) => setRename({ id: resume._id, value: e.target.value })}
                            onKeyDown={(e) => { if (e.key === "Enter") void commitRename(); if (e.key === "Escape") setRename(null); }}
                            className="input text-sm font-semibold py-1 px-2 flex-1" maxLength={100} />
                          <button type="button" onClick={() => void commitRename()} className="btn btn-primary p-1.5"><Check className="size-3.5" /></button>
                          <button type="button" onClick={() => setRename(null)} className="btn btn-surface p-1.5"><X className="size-3.5" /></button>
                        </div>
                      ) : (
                        <h2 className="font-semibold truncate mb-0.5 cursor-pointer text-sm"
                          style={{ color: "var(--text-primary)" }}
                          onDoubleClick={() => setRename({ id: resume._id, value: resume.title })}>
                          {resume.title}
                        </h2>
                      )}

                      <p className="text-xs font-medium capitalize mb-1.5" style={{ color: accent }}>
                        {resume.template.replace("_", " ")}
                      </p>
                      <div className="flex items-center gap-1 text-xs mb-4" style={{ color: "var(--text-muted)" }}>
                        <Clock className="size-3" />
                        {new Date(resume.updatedAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                      </div>

                      <div className="flex items-center gap-1.5">
                        <Link to={`/builder/${resume._id}`}
                          className="btn btn-surface flex-1 flex items-center justify-center gap-1.5 text-xs py-1.5">
                          <Edit3 className="size-3.5" /> Edit
                        </Link>
                        <button
                          type="button"
                          title="Delete resume"
                          onClick={() => setDeleteTarget({ id: resume._id, title: resume.title })}
                          className="btn btn-surface p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                        <div className="relative" data-dropdown="true" onMouseDown={(e) => e.stopPropagation()}>
                          <button type="button"
                            onClick={() => setOpenMenuId(id => id === resume._id ? null : resume._id)}
                            className="btn btn-surface p-1.5"
                            title="More options">
                            {duplicating === resume._id
                              ? <span className="spinner" />
                              : <MoreHorizontal className="size-4" />}
                          </button>
                          {openMenuId === resume._id && (
                            <div data-dropdown="true"
                              className="absolute right-0 top-full mt-2 w-40 overflow-hidden anim-scale-up z-50"
                              style={{ background: "var(--surface)", border: "1px solid var(--border-strong)", borderRadius: "var(--r-xl)", boxShadow: "var(--shadow-lg)" }}
                              onMouseDown={(e) => e.stopPropagation()}>
                              {[
                                { icon: Edit3,  label: "Rename",    fn: () => setRename({ id: resume._id, value: resume.title }) },
                                { icon: Copy,   label: "Duplicate", fn: () => void handleDuplicate(resume._id) },
                              ].map(({ icon: Icon, label, fn }) => (
                                <button key={label} type="button" onClick={() => { fn(); setOpenMenuId(null); }}
                                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-xs transition-colors"
                                  style={{ color: "var(--text-secondary)" }}
                                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--accent-dim)")}
                                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                                  <Icon className="size-3.5" /> {label}
                                </button>
                              ))}
                              <div style={{ height: "1px", background: "var(--border)" }} />
                              <button type="button"
                                onClick={() => { setDeleteTarget({ id: resume._id, title: resume.title }); setOpenMenuId(null); }}
                                className="w-full flex items-center gap-2.5 px-4 py-2.5 text-xs text-red-600 dark:text-red-400 hover:bg-red-500/10 transition-colors">
                                <Trash2 className="size-3.5" /> Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
          </section>
        </main>
      </div>
    </div>
  );
}

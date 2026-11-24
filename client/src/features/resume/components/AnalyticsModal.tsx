import { useState, useEffect } from "react";
import {
  X, RefreshCw, Database, Activity, BarChart3, Users, Star,
  TrendingUp, Award, Layers, ShieldCheck, CheckCircle2
} from "lucide-react";
import toast from "react-hot-toast";
import { analyticsApi } from "@/services/api";
import type { AnalyticsData } from "@/types";

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AnalyticsModal({ isOpen, onClose }: AnalyticsModalProps) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"templates" | "skills" | "users" | "completeness" | "velocity">("templates");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await analyticsApi.getAnalytics();
      if (res.data.data) {
        setData(res.data.data);
      }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to load PyMongo analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      void fetchAnalytics();
    }
  }, [isOpen]);

  const handleSetup = async () => {
    setActionLoading("setup");
    try {
      const res = await analyticsApi.runSetup();
      toast.success(res.data.message || "PyMongo schema & indexes updated!");
      await fetchAnalytics();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Setup failed");
    } finally {
      setActionLoading(null);
    }
  };

  const handleSeed = async () => {
    setActionLoading("seed");
    try {
      const res = await analyticsApi.runSeed();
      toast.success(res.data.message || "Benchmark dataset seeded successfully!");
      await fetchAnalytics();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Seed failed");
    } finally {
      setActionLoading(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div
        className="w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl shadow-2xl overflow-hidden border"
        style={{
          background: "var(--surface)",
          borderColor: "var(--border)",
        }}
      >
        {/* Modal Header */}
        <div
          className="flex items-center justify-between px-6 py-4 border-b shrink-0"
          style={{
            borderColor: "var(--border)",
            background: "var(--surface-raised)",
          }}
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-600/10 text-indigo-500">
              <BarChart3 className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  Database Analytics & Intelligence
                </h2>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                  <Activity className="size-3" />
                  PyMongo 4.9+
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Live aggregations computed directly on MongoDB collections
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void fetchAnalytics()}
              disabled={loading}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Refresh Analytics"
            >
              <RefreshCw className={`size-4 ${loading ? "animate-spin text-indigo-500" : ""}`} />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="size-4" />
            </button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && !data ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <RefreshCw className="size-8 text-indigo-500 animate-spin" />
              <p className="text-sm font-medium text-slate-500">Running PyMongo Aggregations...</p>
            </div>
          ) : data ? (
            <>
              {/* Summary Metric Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
                    <span>Total Resumes</span>
                    <Layers className="size-4 text-indigo-500" />
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white mt-2">
                    {data.summary.totalResumes}
                  </div>
                  <span className="text-[11px] text-slate-500">In MongoDB resumes collection</span>
                </div>

                <div className="p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
                    <span>Active Users</span>
                    <Users className="size-4 text-emerald-500" />
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white mt-2">
                    {data.summary.totalUsers}
                  </div>
                  <span className="text-[11px] text-slate-500">Registered candidate accounts</span>
                </div>

                <div className="p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
                    <span>Public Resumes</span>
                    <TrendingUp className="size-4 text-amber-500" />
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white mt-2">
                    {data.summary.publicResumes}
                  </div>
                  <span className="text-[11px] text-slate-500">
                    {data.summary.totalResumes > 0
                      ? `${String(Math.round((data.summary.publicResumes / data.summary.totalResumes) * 100))}% publicly shared`
                      : "0% shared"}
                  </span>
                </div>

                <div className="p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
                    <span>Top Skill</span>
                    <Award className="size-4 text-purple-500" />
                  </div>
                  <div className="text-xl font-bold text-slate-900 dark:text-white mt-2 truncate capitalize">
                    {data.topSkills[0]?._id ?? "N/A"}
                  </div>
                  <span className="text-[11px] text-slate-500">
                    {data.topSkills[0]?.frequency ?? 0} candidate profiles
                  </span>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex items-center gap-1 border-b border-slate-200 dark:border-slate-800 pb-2">
                <button
                  type="button"
                  onClick={() => { setActiveTab("templates"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === "templates"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  Template Usage
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab("skills"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === "skills"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  Top Skills
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab("completeness"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === "completeness"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  Completeness Ranking
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab("users"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === "users"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  Portfolios ($lookup)
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab("velocity"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === "velocity"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  Monthly Velocity
                </button>
              </div>

              {/* Tab 1: Template Usage */}
              {activeTab === "templates" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <span>Template Layout</span>
                    <span>Adoption & Breakdown</span>
                  </div>
                  {data.templateUsage.length === 0 ? (
                    <p className="text-center py-6 text-xs text-slate-500">No template data recorded yet.</p>
                  ) : (
                    data.templateUsage.map((tpl) => {
                      const max = Math.max(...data.templateUsage.map((t) => t.totalResumes), 1);
                      const pct = Math.round((tpl.totalResumes / max) * 100);
                      return (
                        <div
                          key={tpl._id}
                          className="p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/30"
                        >
                          <div className="flex items-center justify-between text-xs mb-1.5">
                            <span className="font-semibold capitalize text-slate-800 dark:text-slate-200">
                              {tpl._id.replace("_", " ")}
                            </span>
                            <span className="font-medium text-slate-500">
                              {tpl.totalResumes} resumes ({tpl.publicResumes} public)
                            </span>
                          </div>
                          <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${String(pct)}%` }}
                            />
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* Tab 2: Top Skills */}
              {activeTab === "skills" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <span>Rank & Skill (Case-Normalized)</span>
                    <span>Inclusions</span>
                  </div>
                  {data.topSkills.length === 0 ? (
                    <p className="text-center py-6 text-xs text-slate-500">No skills data recorded yet.</p>
                  ) : (
                    data.topSkills.map((sk, idx) => (
                      <div
                        key={sk._id}
                        className="flex items-center justify-between p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/30"
                      >
                        <div className="flex items-center gap-3">
                          <span className="size-6 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-bold text-xs flex items-center justify-center">
                            {idx + 1}
                          </span>
                          <span className="font-semibold text-sm capitalize text-slate-800 dark:text-slate-200">
                            {sk._id}
                          </span>
                        </div>
                        <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-200/70 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {sk.frequency} resumes
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 3: Completeness Score */}
              {activeTab === "completeness" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <span>Resume Title</span>
                    <span>Score & Composition</span>
                  </div>
                  {data.completenessScores.length === 0 ? (
                    <p className="text-center py-6 text-xs text-slate-500">No resumes scored yet.</p>
                  ) : (
                    data.completenessScores.map((c) => (
                      <div
                        key={c.title}
                        className="p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/30"
                      >
                        <div className="flex items-center justify-between">
                          <div className="min-w-0 pr-4">
                            <p className="font-semibold text-sm truncate text-slate-800 dark:text-slate-200">
                              {c.title}
                            </p>
                            <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
                              <span>{c.expCount} exp</span>
                              <span>•</span>
                              <span>{c.projCount} projects</span>
                              <span>•</span>
                              <span>{c.skillCount} skills</span>
                              <span>•</span>
                              <span>{c.hasSummary ? "✓ summary" : "✗ no summary"}</span>
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                              <Star className="size-3 fill-amber-500 text-amber-500" />
                              {c.completenessScore} / 10
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 4: Portfolios ($lookup) */}
              {activeTab === "users" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <span>Candidate Name (users collection)</span>
                    <span>Resumes Owned</span>
                  </div>
                  {data.resumesPerUser.length === 0 ? (
                    <p className="text-center py-6 text-xs text-slate-500">No user portfolios found.</p>
                  ) : (
                    data.resumesPerUser.map((u) => (
                      <div
                        key={u.userName}
                        className="flex items-center justify-between p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/30"
                      >
                        <div className="flex items-center gap-2.5">
                          <div className="size-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-700 dark:text-slate-300">
                            {u.userName.charAt(0).toUpperCase() || "U"}
                          </div>
                          <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
                            {u.userName}
                          </span>
                        </div>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                          {u.resumeCount} resumes
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 5: Monthly Velocity */}
              {activeTab === "velocity" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <span>Cohort (YYYY-MM)</span>
                    <span>Resumes Created</span>
                  </div>
                  {data.monthlyVelocity.length === 0 ? (
                    <p className="text-center py-6 text-xs text-slate-500">No monthly creation activity recorded yet.</p>
                  ) : (
                    data.monthlyVelocity.map((v) => (
                      <div
                        key={v._id}
                        className="flex items-center justify-between p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/30"
                      >
                        <span className="font-mono text-sm text-slate-700 dark:text-slate-300">
                          {v._id}
                        </span>
                        <span className="font-bold text-sm text-indigo-600 dark:text-indigo-400">
                          +{v.resumesCreated}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">
              No analytics data available.
            </div>
          )}
        </div>

        {/* Modal Footer / PyMongo Actions */}
        <div
          className="flex flex-col sm:flex-row items-center justify-between gap-3 px-6 py-4 border-t shrink-0"
          style={{
            borderColor: "var(--border)",
            background: "var(--surface-raised)",
          }}
        >
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Database className="size-3.5 text-indigo-500" />
            <span>Driver Engine: <strong className="text-slate-700 dark:text-slate-300">{data?.engine ?? "PyMongo 4.9+"}</strong></span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void handleSetup()}
              disabled={actionLoading !== null}
              className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-1.5"
            >
              <ShieldCheck className="size-3.5 text-emerald-500" />
              <span>{actionLoading === "setup" ? "Applying..." : "Run $jsonSchema Setup"}</span>
            </button>

            <button
              type="button"
              onClick={() => void handleSeed()}
              disabled={actionLoading !== null}
              className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-1.5"
            >
              <CheckCircle2 className="size-3.5 text-indigo-500" />
              <span>{actionLoading === "seed" ? "Seeding..." : "Re-Seed Data"}</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

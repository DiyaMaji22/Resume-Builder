import { useState, useRef } from "react";
import { UploadCloud, FileText, X, CheckCircle, AlertCircle, ArrowRight } from "lucide-react";
import { resumeApi } from "@/services/api";
import toast from "react-hot-toast";
import type { Resume } from "@/types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (resume: Resume) => void;
}

export function UploadResumeModal({ isOpen, onClose, onSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (f: File) => {
    if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
      toast.error("Please upload a PDF file (.pdf)");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      toast.error("File size exceeds 10MB limit");
      return;
    }
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStep("Reading PDF text and structure…");

    try {
      setTimeout(() => {
        setUploadStep("Extracting contact info, experience, and skills…");
      }, 700);

      const response = await resumeApi.uploadPDF(file);

      if (response.data.data) {
        toast.success("Resume uploaded and parsed successfully!");
        onSuccess(response.data.data);
        onClose();
      }
    } catch (err: unknown) {
      console.error(err);
      toast.error(err instanceof Error ? err.message : "Failed to parse PDF resume");
    } finally {
      setIsUploading(false);
      setUploadStep("");
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm anim-fade-in"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl anim-scale-up"
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
              <UploadCloud className="size-4" />
            </div>
            <div>
              <h2 className="text-base font-bold" style={{ color: "var(--text-primary)" }}>
                Upload PDF Resume
              </h2>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                Import your existing resume. We'll automatically parse your experience, skills, and education.
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

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,application/pdf"
            className="hidden"
          />

          {/* Drag & Drop Box */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center gap-3 ${
              isDragging
                ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/20 scale-[0.99]"
                : "border-gray-300 dark:border-gray-700 hover:border-blue-400 bg-gray-50/50 dark:bg-white/[0.02]"
            }`}
          >
            <div
              className="size-12 rounded-full flex items-center justify-center transition-transform group-hover:scale-110"
              style={{ background: "var(--accent-dim)", color: "var(--accent)" }}
            >
              <UploadCloud className="size-6" />
            </div>

            <div>
              <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Click to browse or drag and drop your PDF here
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Supports standard text-based PDF files up to 10MB
              </p>
            </div>
          </div>

          {/* Selected File Card */}
          {file && (
            <div
              className="p-3 rounded-xl flex items-center justify-between border"
              style={{ background: "var(--bg-subtle)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="size-9 rounded-lg bg-red-100 dark:bg-red-950/40 text-red-600 dark:text-red-400 flex items-center justify-center shrink-0">
                  <FileText className="size-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                    {file.name}
                  </p>
                  <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                    {(file.size / 1024).toFixed(1)} KB • Ready to parse
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="p-1 rounded hover:bg-black/5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="size-4" />
              </button>
            </div>
          )}

          {/* Progress / Step status */}
          {isUploading && (
            <div
              className="p-3 rounded-xl space-y-2 border text-xs"
              style={{ background: "var(--accent-dim)", borderColor: "var(--accent)" }}
            >
              <div className="flex items-center gap-2 font-medium" style={{ color: "var(--accent-text)" }}>
                <span className="spinner size-3.5" />
                <span>{uploadStep}</span>
              </div>
              <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                Mapping your past experience and skills to the builder...
              </p>
            </div>
          )}

          {/* Feature highlights */}
          <div className="space-y-1.5 pt-1">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              What gets imported:
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Full Name & Contact</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Professional Summary</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Work Experience & Bullets</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Degrees & Education</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Extracted Hard Skills</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="size-3.5 text-emerald-500" />
                <span>Projects & Certifications</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div
          className="px-6 py-3 border-t flex items-center justify-between"
          style={{ borderColor: "var(--border)", background: "var(--bg-subtle)" }}
        >
          <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
            <AlertCircle className="size-3 shrink-0" />
            Works best with standard text PDFs (not scanned image photos)
          </span>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isUploading}
              className="btn btn-ghost px-4 py-1.5 text-xs"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={!file || isUploading}
              onClick={() => void handleUpload()}
              className="btn btn-primary px-5 py-1.5 text-xs flex items-center gap-1.5 shadow-sm"
            >
              {isUploading ? <span className="spinner" /> : <ArrowRight className="size-3.5" />}
              <span>{isUploading ? "Parsing PDF…" : "Import & Open"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

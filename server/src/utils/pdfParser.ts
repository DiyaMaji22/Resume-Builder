import { ATS_KEYWORDS } from "./atsAnalyzer.js";
import type {
  PersonalInfo, ExperienceEntry, EducationEntry, ProjectEntry, CertificationEntry
} from "../types/shared.js";

export async function extractTextFromPDF(buffer: Buffer): Promise<string> {
  try {
    const pdfModule = await import("pdf-parse");
    // pdf-parse v2 exposes PDFParse class
    if ("PDFParse" in pdfModule && typeof (pdfModule as any).PDFParse === "function") {
      const parser = new (pdfModule as any).PDFParse({ data: buffer });
      const textResult = await parser.getText();
      await parser.destroy();
      return textResult.text ?? "";
    }
    // Fallback for pdf-parse v1
    const parseFn = (pdfModule as any).default ?? pdfModule;
    if (typeof parseFn === "function") {
      const data = await parseFn(buffer);
      return data.text ?? "";
    }
  } catch (err) {
    console.error("[PDF Parser] Failed to parse PDF:", err);
    throw new Error("Could not read text from the uploaded PDF.");
  }
  return "";
}

interface ParsedResumeData {
  title: string;
  professionalSummary: string;
  personalInfo: PersonalInfo;
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: string[];
}

export function parseResumeFromText(rawText: string, originalFileName?: string): ParsedResumeData {
  // Normalize line endings and cleanup whitespace
  const text = rawText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);

  // 1. Contact / Personal Info Extraction
  const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/i);
  const email = emailMatch ? emailMatch[0] : "";

  const phoneMatch = text.match(/(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
  const phone = phoneMatch ? phoneMatch[0] : "";

  const linkedinMatch = text.match(/(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/([a-zA-Z0-9_.-]+)/i);
  const linkedin = linkedinMatch ? (linkedinMatch[0].startsWith("http") ? linkedinMatch[0] : `https://${linkedinMatch[0]}`) : "";

  const githubMatch = text.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_.-]+)/i);
  const github = githubMatch ? (githubMatch[0].startsWith("http") ? githubMatch[0] : `https://${githubMatch[0]}`) : "";

  // Name inference: usually the first non-empty line without email, phone, or symbols
  let fullName = "";
  for (let i = 0; i < Math.min(lines.length, 5); i++) {
    const line = lines[i];
    if (
      line.length > 2 &&
      line.length < 40 &&
      !line.includes("@") &&
      !line.includes("http") &&
      !/\d/.test(line) &&
      !/resume|curriculum|vitae|page|contact/i.test(line)
    ) {
      fullName = line;
      break;
    }
  }

  // Location inference: look for "City, State" pattern in the first 10 lines
  let location = "";
  for (let i = 0; i < Math.min(lines.length, 10); i++) {
    const locMatch = lines[i].match(/([A-Z][a-zA-Z\s.-]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)/);
    if (locMatch && !lines[i].includes("@")) {
      location = locMatch[0];
      break;
    }
  }

  // 2. Identify Section Blocks
  const SECTION_HEADERS: Record<string, RegExp> = {
    summary: /^(?:professional\s+summary|summary|profile|about\s+me|objective)$/i,
    experience: /^(?:experience|work\s+experience|professional\s+experience|employment\s+history|work\s+history)$/i,
    education: /^(?:education|academic\s+background|academic\s+history|qualifications)$/i,
    skills: /^(?:skills|technical\s+skills|core\s+competencies|technologies|tools)$/i,
    projects: /^(?:projects|key\s+projects|personal\s+projects)$/i,
    certifications: /^(?:certifications|certificates|licenses(?:\s+&\s+certifications)?)$/i,
  };

  const sections: Record<string, string[]> = {
    header: [],
    summary: [],
    experience: [],
    education: [],
    skills: [],
    projects: [],
    certifications: [],
  };

  let currentSection = "header";

  for (const line of lines) {
    let matchedHeader = false;
    for (const [sectionKey, regex] of Object.entries(SECTION_HEADERS)) {
      if (regex.test(line)) {
        currentSection = sectionKey;
        matchedHeader = true;
        break;
      }
    }

    if (!matchedHeader) {
      sections[currentSection].push(line);
    }
  }

  // 3. Extract Summary
  const professionalSummary = sections.summary.join(" ").slice(0, 1000);

  // 4. Extract Skills
  const extractedSkills = new Set<string>();

  // Extract from the dedicated skills section
  if (sections.skills.length > 0) {
    const rawSkillsText = sections.skills.join(" ");
    const skillTokens = rawSkillsText.split(/[,•|·\n;/]/).map((s) => s.trim()).filter((s) => s.length > 1 && s.length < 35);
    for (const token of skillTokens) {
      // Check if it's not a sentence
      if (token.split(" ").length <= 4) {
        extractedSkills.add(token);
      }
    }
  }

  // Also check against our comprehensive ATS keywords dictionary across full text
  const lowerText = ` ${text.toLowerCase()} `;
  for (const kw of ATS_KEYWORDS) {
    const escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(?:^|[\\s,;:.()\\[\\]/])${escaped}(?:$|[\\s,;:.()\\[\\]/])`, "i");
    if (regex.test(lowerText)) {
      // Capitalize properly
      const formatted = kw.length <= 4 && !kw.includes(".") ? kw.toUpperCase() : (kw.charAt(0).toUpperCase() + kw.slice(1));
      extractedSkills.add(formatted);
    }
  }

  // Limit skills to top 30
  const skills = Array.from(extractedSkills).slice(0, 25);

  // 5. Extract Experience Entries
  const experience: ExperienceEntry[] = [];
  const expLines = sections.experience;

  if (expLines.length > 0) {
    let currentExp: Partial<ExperienceEntry> | null = null;
    const bullets: string[] = [];

    const datePattern = /(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+)?(?:\d{4})\s*(?:-|–|to)\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+)?(?:\d{4}|present|current)/i;

    for (const line of expLines) {
      const hasDate = datePattern.test(line);

      if (hasDate && currentExp) {
        // Save previous
        currentExp.description = bullets.join("\n");
        experience.push(currentExp as ExperienceEntry);
        currentExp = null;
        bullets.length = 0;
      }

      if (hasDate && !currentExp) {
        const parts = line.split(/(?:-|–|to)\s*(?:\d{4}|present|current)/i);
        currentExp = {
          id: `exp-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
          company: "",
          position: "",
          startDate: "",
          endDate: "",
          isCurrent: /present|current/i.test(line),
          description: "",
        };

        // Try extracting company and position
        const beforeDate = line.replace(datePattern, "").trim();
        const tokens = beforeDate.split(/[|,\-–]/).map((t) => t.trim()).filter(Boolean);
        if (tokens.length >= 2) {
          currentExp.position = tokens[0];
          currentExp.company = tokens[1];
        } else if (tokens.length === 1) {
          currentExp.position = tokens[0];
        }
      } else if (currentExp) {
        if (/^[•\-*]/.test(line)) {
          bullets.push(line);
        } else if (!currentExp.company && line.length < 50) {
          currentExp.company = line;
        } else {
          bullets.push(`• ${line}`);
        }
      } else if (/^[A-Z]/.test(line) && line.length < 50 && experience.length === 0) {
        // Potential first role header
        currentExp = {
          id: `exp-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
          company: "Company",
          position: line,
          startDate: "2022",
          endDate: "Present",
          isCurrent: true,
          description: "",
        };
      }
    }

    if (currentExp) {
      currentExp.description = bullets.join("\n");
      experience.push(currentExp as ExperienceEntry);
    }
  }

  // 6. Extract Education Entries
  const education: EducationEntry[] = [];
  const eduLines = sections.education;

  if (eduLines.length > 0) {
    const eduText = eduLines.join("\n");
    const degreeMatch = eduText.match(/(?:Bachelor|Master|Doctor|Ph\.?D|Associate|B\.?S|M\.?S|B\.?A|M\.?A|B\.?Tech|M\.?Tech)[^,\n]*/i);
    const instMatch = eduText.match(/(?:University|College|Institute|School)[^,\n]*/i);
    const gradMatch = eduText.match(/(?:19|20)\d{2}/);

    education.push({
      id: `edu-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      institution: instMatch ? instMatch[0].trim() : (eduLines[0] || "University"),
      degree: degreeMatch ? degreeMatch[0].trim() : "Bachelor of Science",
      field: "",
      graduationDate: gradMatch ? gradMatch[0] : "2022",
      gpa: "",
    });
  }

  // 7. Extract Projects (if any)
  const projects: ProjectEntry[] = [];
  if (sections.projects.length > 0) {
    projects.push({
      id: `proj-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      name: sections.projects[0] || "Featured Project",
      type: "Application",
      description: sections.projects.slice(1, 4).join(" "),
      url: "",
      technologies: skills.slice(0, 4),
    });
  }

  // 8. Extract Certifications (if any)
  const certifications: CertificationEntry[] = [];
  if (sections.certifications.length > 0) {
    for (const certLine of sections.certifications.slice(0, 3)) {
      if (certLine.length > 3 && certLine.length < 80) {
        certifications.push({
          id: `cert-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
          name: certLine,
          issuer: "Accredited Provider",
          date: "",
          url: "",
        });
      }
    }
  }

  const generatedTitle = fullName ? `${fullName}'s Resume` : (originalFileName ? originalFileName.replace(/\.pdf$/i, "") : "Uploaded Resume");

  return {
    title: generatedTitle,
    professionalSummary,
    personalInfo: {
      fullName,
      email,
      phone,
      location,
      linkedin,
      website: "",
      github,
      image: "",
    },
    experience,
    education,
    projects,
    certifications,
    skills,
  };
}

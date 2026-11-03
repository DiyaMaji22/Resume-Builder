import type { Resume, ATSAnalysisResult } from "@/types";

// Comprehensive skill and domain keyword dictionary compiled from industry benchmarks & job datasets
export const ATS_KEYWORDS = [
  // Languages & Core Runtimes
  "typescript", "javascript", "python", "java", "c++", "c#", "golang", "go", "rust", "php", "ruby", "swift", "kotlin", "scala", "bash", "shell", "sql", "nosql", "html", "html5", "css", "css3", "sass", "less",
  // Frontend Frameworks & Tools
  "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte", "redux", "redux toolkit", "zustand", "tailwind", "tailwind css", "bootstrap", "vite", "webpack", "microfrontends", "responsive design", "web accessibility", "wcag",
  // Backend & APIs
  "node.js", "express", "express.js", "nestjs", "fastapi", "django", "flask", "spring", "spring boot", "ruby on rails", "graphql", "rest", "restful api", "rest api", "grpc", "microservices", "websockets",
  // Databases & Caching
  "mongodb", "postgresql", "postgres", "mysql", "redis", "elasticsearch", "dynamodb", "sqlite", "cassandra", "neo4j", "data modeling", "query optimization",
  // Cloud, DevOps & Infrastructure
  "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible", "ci/cd", "continuous integration", "github actions", "gitlab ci", "jenkins", "prometheus", "grafana", "helm", "argocd", "linux", "system design", "cloud architecture", "site reliability", "sre",
  // Data Science & AI / ML
  "machine learning", "deep learning", "nlp", "natural language processing", "llm", "llms", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "spark", "apache spark", "fastapi", "mlflow", "data analysis", "predictive modeling", "computer vision", "statistics", "data engineering", "etl", "data visualization", "tableau", "power bi",
  // Product, Design & Agile
  "figma", "ui/ux", "user research", "wireframing", "prototyping", "design systems", "information architecture", "usability testing", "product strategy", "roadmapping", "agile", "scrum", "kanban", "jira", "a/b testing", "product analytics", "mixpanel", "amplitude", "okrs", "go-to-market", "gtm",
  // Marketing & Growth
  "seo", "sem", "google ads", "meta ads", "google analytics", "ga4", "hubspot", "conversion rate optimization", "cro", "email marketing", "copywriting", "looker studio", "attribution modeling", "paid acquisition", "lifecycle marketing",
  // Testing & Quality
  "jest", "cypress", "playwright", "vitest", "mocha", "selenium", "unit testing", "integration testing", "e2e testing", "tdd", "test driven development",
];

export const STRONG_ACTION_VERBS = [
  "architected", "engineered", "spearheaded", "orchestrated", "developed", "deployed",
  "optimized", "streamlined", "automated", "scaled", "designed", "implemented",
  "formulated", "established", "mentored", "directed", "boosted", "maximized",
  "reduced", "slashed", "accelerated", "transformed", "delivered", "facilitated",
];

export const WEAK_PHRASES = [
  "worked on", "helped with", "responsible for", "assisted with", "handled",
  "duties included", "participated in", "did", "tasked with",
];

export function extractKeywordsFromText(text: string): string[] {
  const normalized = ` ${text.toLowerCase()} `;
  const found = new Set<string>();

  for (const keyword of ATS_KEYWORDS) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(?:^|[\\s,;:.()\\[\\]/])${escaped}(?:$|[\\s,;:.()\\[\\]/])`, "i");
    if (regex.test(normalized)) {
      found.add(keyword);
    }
  }

  return Array.from(found);
}

export function analyzeResumeATS(resume: Resume, jobDescription: string): ATSAnalysisResult {
  // 1. Extract keywords from Job Description
  const jdKeywords = extractKeywordsFromText(jobDescription);

  // 2. Aggregate all textual content from the Resume
  const resumePieces: string[] = [
    resume.title,
    resume.professionalSummary,
    ...resume.skills,
    ...resume.experience.flatMap((e) => [e.company, e.position, e.description]),
    ...resume.projects.flatMap((p) => [p.name, p.type, p.description, ...(p.technologies ?? [])]),
    ...resume.education.flatMap((ed) => [ed.institution, ed.degree, ed.field]),
    ...resume.certifications.flatMap((c) => [c.name, c.issuer]),
  ];
  const fullResumeText = resumePieces.join(" ");
  const resumeKeywords = new Set(extractKeywordsFromText(fullResumeText));

  // Also include exact skills list directly
  for (const skill of resume.skills) {
    resumeKeywords.add(skill.toLowerCase().trim());
  }

  // 3. Matched vs Missing
  const matchedKeywords: string[] = [];
  const missingKeywords: string[] = [];

  for (const kw of jdKeywords) {
    if (resumeKeywords.has(kw)) {
      matchedKeywords.push(kw);
    } else {
      missingKeywords.push(kw);
    }
  }

  const formatWord = (w: string) => {
    const special: Record<string, string> = {
      "typescript": "TypeScript", "javascript": "JavaScript", "python": "Python",
      "react": "React", "react.js": "React.js", "next.js": "Next.js", "node.js": "Node.js",
      "aws": "AWS", "gcp": "GCP", "sql": "SQL", "nosql": "NoSQL", "postgresql": "PostgreSQL",
      "mongodb": "MongoDB", "ci/cd": "CI/CD", "ui/ux": "UI/UX", "seo": "SEO", "sem": "SEM",
      "html": "HTML", "html5": "HTML5", "css": "CSS", "css3": "CSS3", "docker": "Docker",
      "kubernetes": "Kubernetes", "graphql": "GraphQL", "rest api": "REST API", "restful api": "RESTful API",
      "fastapi": "FastAPI", "pytorch": "PyTorch", "tensorflow": "TensorFlow", "ga4": "GA4",
      "figma": "Figma", "jira": "Jira", "tdd": "TDD", "nlp": "NLP", "llm": "LLM",
    };
    return special[w] ?? (w.charAt(0).toUpperCase() + w.slice(1));
  };

  const keywordScore = jdKeywords.length > 0
    ? Math.round((matchedKeywords.length / jdKeywords.length) * 100)
    : 80;

  let formatScore = 0;
  if (resume.personalInfo.email && resume.personalInfo.phone) formatScore += 25;
  if (resume.personalInfo.linkedin) formatScore += 15;
  if (resume.professionalSummary.length >= 80 && resume.professionalSummary.length <= 600) formatScore += 25;
  if (resume.skills.length >= 6) formatScore += 20;
  if (resume.experience.length >= 1) formatScore += 15;

  const lowerExp = resume.experience.map((e) => e.description.toLowerCase()).join(" ");
  const numberMatches = (lowerExp.match(/\d+[%$xX]|\d+\s*(percent|hours|users|customers|days|team|requests|reduction|growth)/gi) ?? []).length;
  const quantifiedScore = Math.min(100, Math.round((numberMatches / 3) * 100));

  const strongVerbsFound = STRONG_ACTION_VERBS.filter((v) => lowerExp.includes(v));

  const overallScore = Math.round(
    keywordScore * 0.45 +
    formatScore * 0.25 +
    quantifiedScore * 0.15 +
    Math.min(100, strongVerbsFound.length * 20) * 0.15
  );

  const recommendations: string[] = [];

  if (missingKeywords.length > 0) {
    const topMissing = missingKeywords.slice(0, 5).map(formatWord).join(", ");
    recommendations.push(`Include target job keywords missing from your resume: ${topMissing}.`);
  }

  if (quantifiedScore < 60) {
    recommendations.push("Quantify your bullet points with metrics (e.g. 'reduced latency by 35%', 'managed $60k budget', 'scaled to 1M users').");
  }

  if (strongVerbsFound.length < 3) {
    recommendations.push("Begin experience bullet points with authoritative action verbs (e.g., Architected, Engineered, Spearheaded, Optimized).");
  }

  for (const weak of WEAK_PHRASES) {
    if (lowerExp.includes(weak)) {
      recommendations.push(`Replace passive phrasing like '${weak}' with active impact verbs.`);
      break;
    }
  }

  if (!resume.personalInfo.linkedin) {
    recommendations.push("Add a LinkedIn URL; recruiter ATS algorithms favor profiles with verified links.");
  }

  if (resume.skills.length < 8) {
    recommendations.push("Expand your Skills section to at least 8-15 relevant hard skills.");
  }

  if (recommendations.length === 0) {
    recommendations.push("Outstanding resume! Well aligned with this job specification.");
  }

  return {
    overallScore: Math.max(10, Math.min(100, overallScore)),
    keywordScore,
    formattingScore: formatScore,
    quantifiedScore,
    matchedKeywords: matchedKeywords.map(formatWord),
    missingKeywords: missingKeywords.map(formatWord),
    strongActionVerbs: strongVerbsFound.map(formatWord),
    recommendations,
  };
}

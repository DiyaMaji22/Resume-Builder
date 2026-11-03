import type { ResumeStarter } from "@/types";

export interface BenchmarkJob {
  id: string;
  title: string;
  category: "Engineering" | "Data & AI" | "Product & Design" | "Marketing & Growth";
  companyType: string;
  description: string;
}

export const BENCHMARK_JOBS: BenchmarkJob[] = [
  {
    id: "full-stack-eng",
    title: "Senior Full Stack Software Engineer",
    category: "Engineering",
    companyType: "High-Growth Tech / SaaS",
    description: `We are looking for a Senior Full Stack Software Engineer to build and scale our high-throughput cloud web applications.
Responsibilities:
• Architect, build, and maintain performant full-stack features using TypeScript, React, Node.js, and Express.
• Design robust RESTful APIs and GraphQL endpoints backed by PostgreSQL and MongoDB.
• Optimize client-side render performance, state management with Redux, and Tailwind CSS styles.
• Containerize services using Docker and orchestrate deployments through AWS (ECS, S3, CloudFront) and GitHub Actions CI/CD pipelines.
• Collaborate in an Agile/Scrum team, write comprehensive unit and integration tests with Jest, and conduct thorough peer code reviews.

Requirements:
• 3+ years experience in full-stack development with React, TypeScript, Node.js, and SQL/NoSQL databases.
• Experience with cloud infrastructure (AWS or GCP), Docker, containerization, and modern CI/CD automation.
• Solid grasp of system design, microservices architecture, web security, and REST API standards.
• Familiarity with Git, automated testing (Jest, Cypress), and agile software development workflows.`,
  },
  {
    id: "data-scientist",
    title: "Data Scientist & Machine Learning Engineer",
    category: "Data & AI",
    companyType: "AI Solutions & Enterprise Analytics",
    description: `We are seeking an experienced Data Scientist to design, train, and deploy predictive models and NLP pipelines into production.
Responsibilities:
• Develop predictive machine learning models using Python, Scikit-Learn, PyTorch, and TensorFlow.
• Perform advanced exploratory data analysis (EDA), feature engineering, and statistical modeling using Pandas and NumPy.
• Build automated ETL data pipelines with SQL, Spark, and Docker to ingest large-scale datasets.
• Deploy scalable machine learning inference endpoints using FastAPI, MLflow, and cloud services (AWS / GCP).
• Partner with product managers and business stakeholders to translate raw analytics into actionable insights and data visualization dashboards.

Requirements:
• Strong proficiency in Python, SQL, statistical modeling, machine learning, and deep learning.
• Hands-on experience with NLP, LLMs, Scikit-Learn, PyTorch, Pandas, and model evaluation metrics (precision, recall, ROC-AUC).
• Experience productionizing models with FastAPI, Docker, and MLflow or Kubeflow.
• Master's or Bachelor's degree in Computer Science, Data Science, Statistics, or equivalent practical experience.`,
  },
  {
    id: "devops-cloud",
    title: "DevOps & Cloud Infrastructure Engineer",
    category: "Engineering",
    companyType: "Cloud Platform & Enterprise Infrastructure",
    description: `Join our Infrastructure team to build resilient, automated, and secure multi-region cloud architectures.
Responsibilities:
• Manage and scale Kubernetes clusters across AWS and multi-cloud environments.
• Implement Infrastructure as Code (IaC) using Terraform and Ansible for repeatable cloud provisioning.
• Build and optimize robust CI/CD pipelines with GitHub Actions and GitLab CI, reducing build times and deployment friction.
• Set up observability, centralized logging, and alerting systems using Prometheus, Grafana, and the ELK stack.
• Champion site reliability engineering (SRE) practices, zero-downtime deployments, and security compliance.

Requirements:
• Proven experience with Kubernetes, Docker, Linux administration, and AWS cloud services (EKS, IAM, VPC, S3).
• Extensive experience with Terraform, Shell/Bash scripting, Python, and GitOps workflows.
• Deep understanding of networking protocols, load balancing, SSL/TLS, and observability tooling (Prometheus, Grafana).
• CKA (Certified Kubernetes Administrator) or AWS Solutions Architect certification is a strong plus.`,
  },
  {
    id: "product-manager",
    title: "Technical Product Manager",
    category: "Product & Design",
    companyType: "B2B SaaS / Marketplace",
    description: `We are looking for a Technical Product Manager to lead product discovery, roadmapping, and execution for our core platform.
Responsibilities:
• Define product vision, roadmap, and quarterly OKRs aligned with company business objectives.
• Write detailed user stories, technical PRDs (Product Requirement Documents), and acceptance criteria for engineering teams.
• Conduct qualitative user research, customer interviews, and quantitative data analysis using SQL and Mixpanel.
• Run A/B testing experiments to optimize conversion rates, customer onboarding, and monthly active user retention.
• Lead sprint planning, backlog grooming, and daily standups in an Agile/Scrum cross-functional team.

Requirements:
• 3+ years experience in product management for digital software products or SaaS platforms.
• Strong analytical mindset with hands-on proficiency in SQL, product analytics (Mixpanel, Amplitude), and A/B testing.
• Exceptional communication and cross-functional leadership skills bridging engineering, design, and executive leadership.
• Experience managing roadmaps in Jira, wireframing in Figma, and launching successful go-to-market (GTM) campaigns.`,
  },
  {
    id: "uiux-designer",
    title: "UI/UX & Product Designer",
    category: "Product & Design",
    companyType: "Digital Product Studio",
    description: `We are seeking a creative and user-focused UI/UX Designer to craft intuitive, accessible, and delight-inducing web and mobile interfaces.
Responsibilities:
• Lead end-to-end user experience design from wireframes, user journeys, and information architecture to high-fidelity prototypes in Figma.
• Maintain and evolve a shared design system with reusable UI component libraries and design tokens.
• Conduct generative user interviews, usability testing sessions, and competitive benchmarking to validate hypotheses.
• Collaborate closely with frontend software engineers to ensure pixel-perfect implementation and WCAG accessibility standards.
• Create interactive micro-interactions and responsive layouts across desktop, tablet, and mobile breakpoints.

Requirements:
• 3+ years experience as a UI/UX Designer or Product Designer with a strong portfolio showcasing user-centered design processes.
• Mastery of Figma, auto-layout, component variants, interactive prototyping, and design systems.
• Solid understanding of HTML/CSS fundamentals, responsive design, and web accessibility (WCAG 2.1 AA).
• Proven track record in user research, usability testing, and wireframing for complex workflows.`,
  },
  {
    id: "growth-marketing",
    title: "Growth Marketing & SEO Specialist",
    category: "Marketing & Growth",
    companyType: "DTC & Growth Agency",
    description: `We are hiring a Growth Marketing Specialist to scale user acquisition funnels, organic search traffic, and retention campaigns.
Responsibilities:
• Plan and execute data-driven paid advertising campaigns across Google Ads, Meta Ads, and LinkedIn.
• Implement comprehensive on-page and technical SEO strategies to increase organic keyword rankings and organic search traffic.
• Build automated email lifecycle sequences, lead nurturing workflows, and segmentation in HubSpot.
• Conduct continuous A/B tests on landing pages, headlines, and call-to-actions to increase conversion rate (CRO).
• Analyze multi-channel attribution and KPI dashboards using Google Analytics 4, Google Tag Manager, and Looker Studio.

Requirements:
• 3+ years of experience in performance marketing, search engine optimization (SEO), and customer acquisition.
• In-depth expertise with Google Analytics 4, Google Search Console, Ahrefs/SEMrush, and paid ad networks.
• Experience with conversion rate optimization (CRO), landing page builders, copywriting, and A/B testing methodology.
• Strong analytical skills and familiarity with marketing attribution models and CAC/LTV unit economics.`,
  },
];

export const STARTER_RESUMES: ResumeStarter[] = [
  {
    id: "starter-fullstack-dev",
    role: "Full Stack Software Engineer",
    category: "Engineering",
    title: "Full Stack Software Engineer Resume",
    description: "Tailored for senior/mid-level web developers. Features modern TypeScript, React, Node.js, Docker, and AWS experience.",
    template: "modern",
    accentColor: "#2563EB",
    professionalSummary:
      "Full Stack Software Engineer with 4+ years of experience building resilient cloud applications and scalable microservices. Proven expertise across TypeScript, React, Node.js, and PostgreSQL. Champion of automated testing, CI/CD automation, and user-focused web performance.",
    personalInfo: {
      fullName: "Alex Morgan",
      email: "alex.morgan.dev@gmail.com",
      phone: "+1 (555) 382-9104",
      location: "San Francisco, CA",
      linkedin: "https://linkedin.com/in/alexmorgan-dev",
      website: "https://alexmorgan.codes",
      github: "https://github.com/alexmorgan-dev",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Starlight Cloud Systems",
        position: "Senior Full Stack Engineer",
        startDate: "2023-01",
        endDate: "",
        isCurrent: true,
        description:
          "• Architected and deployed microservices using Node.js and TypeScript, handling over 15M daily requests with 99.98% uptime.\n• Spearheaded the redesign of the core web app using React 19 and Tailwind CSS, reducing initial page load time by 42%.\n• Integrated Redis caching layers and optimized PostgreSQL indexes, boosting search query throughput by 65%.\n• Mentored 4 junior engineers in test-driven development, code reviews, and containerized deployment workflows.",
      },
      {
        id: "exp-2",
        company: "Nexus Labs",
        position: "Software Engineer",
        startDate: "2021-03",
        endDate: "2022-12",
        isCurrent: false,
        description:
          "• Developed real-time collaborative document editing features using WebSockets, Redux Toolkit, and Express.\n• Built automated CI/CD pipelines with GitHub Actions and Docker, reducing average deployment release cycles from 4 days to 40 minutes.\n• Created comprehensive Jest and Cypress test suites, achieving 88% overall code coverage across critical user flows.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "University of California, Berkeley",
        degree: "Bachelor of Science",
        field: "Computer Science",
        graduationDate: "2020-05",
        gpa: "3.85",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "DevMetrics Open-Source Dashboard",
        type: "Open Source Tool",
        description:
          "Engineered an automated GitHub telemetry collector tracking pull request velocity and code review response latency for 500+ developers.",
        url: "https://github.com/alexmorgan-dev/devmetrics",
        technologies: ["TypeScript", "React", "Node.js", "PostgreSQL", "Docker"],
      },
      {
        id: "proj-2",
        name: "QuickTask Realtime Workspace",
        type: "Full Stack Web App",
        description:
          "Built a high-performance Kanban collaboration platform featuring optimistic UI updates, drag-and-drop mechanics, and offline sync.",
        url: "https://quicktask-demo.dev",
        technologies: ["React", "Express", "MongoDB", "WebSockets", "Tailwind CSS"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "AWS Certified Solutions Architect – Associate",
        issuer: "Amazon Web Services",
        date: "2023-08",
        url: "https://aws.amazon.com/certification",
      },
    ],
    skills: [
      "TypeScript",
      "JavaScript",
      "React",
      "Node.js",
      "Express",
      "Redux",
      "PostgreSQL",
      "MongoDB",
      "Docker",
      "AWS",
      "REST APIs",
      "GraphQL",
      "Git",
      "Jest",
      "CI/CD",
      "Tailwind CSS",
    ],
  },
  {
    id: "starter-data-scientist",
    role: "Data Scientist & ML Engineer",
    category: "Data & AI",
    title: "Data Scientist & ML Engineer Resume",
    description: "Optimized for AI, NLP, and machine learning roles. Features PyTorch, predictive modeling, statistical analysis, and ML pipelines.",
    template: "modern",
    accentColor: "#0ea5e9",
    professionalSummary:
      "Data Scientist with 3+ years of experience in predictive analytics, NLP, and deploying production machine learning microservices. Skilled in Python, PyTorch, Scikit-Learn, and SQL. Proven track record of leveraging big data to solve complex classification and forecasting challenges.",
    personalInfo: {
      fullName: "Maya Lin",
      email: "maya.lin.ds@gmail.com",
      phone: "+1 (555) 491-0283",
      location: "Seattle, WA",
      linkedin: "https://linkedin.com/in/mayalin-ml",
      website: "https://mayalin-portfolio.io",
      github: "https://github.com/mayalin-ml",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Synthetix AI Solutions",
        position: "Data Scientist & ML Engineer",
        startDate: "2023-04",
        endDate: "",
        isCurrent: true,
        description:
          "• Developed an NLP multi-class resume classification model using PyTorch and Transformer architectures, achieving 94.2% F1 score.\n• Designed automated data ingestion and validation pipelines processing 1.2M records daily using Python, Spark, and SQL.\n• Built and deployed containerized REST inference endpoints via FastAPI and Docker on AWS, reducing inference latency by 38%.\n• Created interactive analytical dashboards using Streamlit and Plotly to communicate model drift and feature importance to leadership.",
      },
      {
        id: "exp-2",
        company: "Vanguard Analytics",
        position: "Junior Data Scientist",
        startDate: "2021-08",
        endDate: "2023-03",
        isCurrent: false,
        description:
          "• Formulated customer churn prediction models using Scikit-Learn and XGBoost, identifying at-risk accounts with 89% precision.\n• Conducted statistical A/B test evaluations for marketing campaigns, increasing customer conversion by 18%.\n• Automated routine ETL scripts with Python and Pandas, saving 15 manual engineering hours each week.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "University of Washington",
        degree: "Master of Science",
        field: "Data Science & Machine Learning",
        graduationDate: "2021-06",
        gpa: "3.92",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "Resume NER & Skill Extractor",
        type: "Machine Learning / NLP",
        description:
          "Trained a custom SpaCy entity recognizer to extract technical skills and experience levels from 10,000+ Kaggle resume records.",
        url: "https://github.com/mayalin-ml/resume-ner-extractor",
        technologies: ["Python", "PyTorch", "SpaCy", "FastAPI", "Docker"],
      },
      {
        id: "proj-2",
        name: "Financial Market Trend Forecaster",
        type: "Time Series Model",
        description:
          "Constructed an LSTM recurrent neural network forecasting stock volatility and algorithmic trading indicators with Pandas and NumPy.",
        url: "https://github.com/mayalin-ml/timeseries-forecaster",
        technologies: ["Python", "TensorFlow", "Pandas", "Scikit-Learn"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "TensorFlow Developer Certificate",
        issuer: "Google / DeepLearning.AI",
        date: "2022-10",
        url: "https://tensorflow.org/certificate",
      },
    ],
    skills: [
      "Python",
      "PyTorch",
      "TensorFlow",
      "Scikit-Learn",
      "Pandas",
      "NumPy",
      "SQL",
      "FastAPI",
      "Docker",
      "NLP",
      "Transformers",
      "Data Visualization",
      "Machine Learning",
      "Deep Learning",
      "Git",
      "AWS",
    ],
  },
  {
    id: "starter-devops-cloud",
    role: "DevOps & Cloud Engineer",
    category: "Engineering",
    title: "DevOps & Cloud Engineer Resume",
    description: "Designed for SRE, DevOps, and cloud systems engineers. Emphasizes Kubernetes, Terraform, AWS, Prometheus, and CI/CD pipelines.",
    template: "executive",
    accentColor: "#d97706",
    professionalSummary:
      "Cloud Infrastructure and DevOps Engineer with 5+ years of expertise in Kubernetes cluster management, Infrastructure as Code (Terraform), and high-availability AWS deployments. Proven leader in automating CI/CD pipelines and hardening cloud security postures.",
    personalInfo: {
      fullName: "David Chen",
      email: "david.chen.cloud@gmail.com",
      phone: "+1 (555) 720-4491",
      location: "Austin, TX",
      linkedin: "https://linkedin.com/in/davidchen-devops",
      website: "https://davidchen.infra.io",
      github: "https://github.com/davidchen-infra",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Apex Cloud Platforms",
        position: "Senior DevOps Engineer",
        startDate: "2022-09",
        endDate: "",
        isCurrent: true,
        description:
          "• Orchestrated multi-region AWS Kubernetes (EKS) infrastructure serving 200+ containerized microservices.\n• Automated cloud provisioning via modular Terraform configurations, slashing environment setup time from 3 days to 25 minutes.\n• Deployed comprehensive Prometheus, Grafana, and Alertmanager monitoring, reducing MTTR (Mean Time to Resolution) by 45%.\n• Reduced annualized AWS infrastructure expenditures by $120,000 through spot instance scaling and storage lifecycle policies.",
      },
      {
        id: "exp-2",
        company: "Quantum Software Solutions",
        position: "Site Reliability Engineer",
        startDate: "2020-02",
        endDate: "2022-08",
        isCurrent: false,
        description:
          "• Maintained 99.99% system availability for business-critical client platforms through proactive canary deployments.\n• Built zero-downtime automated deployment pipelines using GitHub Actions, Helm, and ArgoCD.\n• Hardened Linux hosts and container images against CIS benchmarks and automated vulnerability scans with Trivy.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "University of Texas at Austin",
        degree: "Bachelor of Science",
        field: "Computer Engineering",
        graduationDate: "2019-12",
        gpa: "3.78",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "Automated GitOps Infrastructure Sandbox",
        type: "Open Source Tool",
        description:
          "Created an open-source Terraform and Helm reference architecture for deploying production-ready Kubernetes clusters on AWS.",
        url: "https://github.com/davidchen-infra/gitops-sandbox",
        technologies: ["Kubernetes", "Terraform", "AWS", "Helm", "ArgoCD", "Bash"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "Certified Kubernetes Administrator (CKA)",
        issuer: "Cloud Native Computing Foundation (CNCF)",
        date: "2023-03",
        url: "https://cncf.io/certification/cka",
      },
      {
        id: "cert-2",
        name: "AWS Certified Solutions Architect – Professional",
        issuer: "Amazon Web Services",
        date: "2022-05",
        url: "https://aws.amazon.com/certification",
      },
    ],
    skills: [
      "Kubernetes",
      "Docker",
      "Terraform",
      "AWS",
      "Linux",
      "CI/CD",
      "GitHub Actions",
      "Prometheus",
      "Grafana",
      "Ansible",
      "Bash",
      "Helm",
      "Python",
      "System Design",
      "GitOps",
      "Security",
    ],
  },
  {
    id: "starter-uiux-designer",
    role: "UI/UX & Product Designer",
    category: "Product & Design",
    title: "UI/UX & Product Designer Resume",
    description: "Geared towards product designers, UX researchers, and interface specialists. Highlights Figma, design systems, and user testing.",
    template: "minimal",
    accentColor: "#7c3aed",
    professionalSummary:
      "Product & UI/UX Designer with 4+ years of experience crafting intuitive digital experiences, scalable design systems, and high-fidelity interactive prototypes. Adept at conducting user research, usability testing, and partnering closely with engineering teams.",
    personalInfo: {
      fullName: "Sophia Vance",
      email: "sophia.vance.design@gmail.com",
      phone: "+1 (555) 831-2901",
      location: "New York, NY",
      linkedin: "https://linkedin.com/in/sophiavance-design",
      website: "https://sophiavance.design",
      github: "https://github.com/sophiavance",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Aura Digital Products",
        position: "Lead Product Designer",
        startDate: "2022-11",
        endDate: "",
        isCurrent: true,
        description:
          "• Spearheaded complete design overhaul of our flagship B2B web application, driving a 34% increase in user task completion rate.\n• Established and maintained a multi-brand Figma design system comprising 150+ accessible components and token variables.\n• Facilitated 40+ moderated usability test sessions, translating insights into iterative wireframes and high-fidelity prototypes.\n• Collaborated daily with frontend engineers to review responsive CSS implementations and enforce WCAG 2.1 AA accessibility.",
      },
      {
        id: "exp-2",
        company: "Craft & Pixel Agency",
        position: "UI/UX Designer",
        startDate: "2020-06",
        endDate: "2022-10",
        isCurrent: false,
        description:
          "• Designed mobile iOS/Android apps for FinTech and eCommerce clients with cumulative downloads exceeding 500k.\n• Conducted customer journey mapping, empathy workshops, and information architecture wireframing for complex SaaS workflows.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "Rhode Island School of Design (RISD)",
        degree: "Bachelor of Fine Arts",
        field: "Graphic & Interactive Design",
        graduationDate: "2020-05",
        gpa: "3.90",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "Pulse UI — Open Source Token System",
        type: "Design System",
        description:
          "Designed and documented an accessible open-source design token specification bridging Figma styles with React and Tailwind CSS.",
        url: "https://pulse-ui.figma.site",
        technologies: ["Figma", "Design Systems", "Prototyping", "CSS3", "Accessibility"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "Google UX Design Professional Certificate",
        issuer: "Google / Coursera",
        date: "2021-04",
        url: "https://coursera.org/professional-certificates/google-ux-design",
      },
    ],
    skills: [
      "Figma",
      "UI/UX Design",
      "Design Systems",
      "User Research",
      "Wireframing",
      "Interactive Prototyping",
      "Usability Testing",
      "Information Architecture",
      "Accessibility (WCAG)",
      "HTML5",
      "CSS3",
      "Mobile Design",
      "Agile",
    ],
  },
  {
    id: "starter-product-manager",
    role: "Technical Product Manager",
    category: "Product & Design",
    title: "Technical Product Manager Resume",
    description: "Built for product leaders, technical PMs, and agile delivery managers. Highlights roadmapping, KPIs, user retention, and A/B testing.",
    template: "classic",
    accentColor: "#059669",
    professionalSummary:
      "Data-driven Technical Product Manager with 5+ years of experience leading cross-functional engineering and design squads. Expert in roadmap prioritization, customer discovery, and executing growth experiments that deliver measurable bottom-line ARR impact.",
    personalInfo: {
      fullName: "Marcus Sterling",
      email: "marcus.sterling.pm@gmail.com",
      phone: "+1 (555) 602-1849",
      location: "Chicago, IL",
      linkedin: "https://linkedin.com/in/marcussterling-pm",
      website: "https://marcussterling.com",
      github: "",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Velocity SaaS Group",
        position: "Senior Product Manager",
        startDate: "2022-05",
        endDate: "",
        isCurrent: true,
        description:
          "• Led product vision, strategy, and roadmap for the core analytics suite, contributing to $2.4M ARR expansion in fiscal year 2024.\n• Designed and rolled out self-serve team onboarding flow, boosting 30-day user activation rates by 27% across 10,000+ accounts.\n• Analyzed behavioral telemetry using Mixpanel and SQL to isolate onboarding drop-off bottlenecks and iterate solutions.\n• Championed agile rituals across 2 engineering squads, increasing quarterly story point completion velocity by 22%.",
      },
      {
        id: "exp-2",
        company: "Catalyst Interactive",
        position: "Associate Product Manager",
        startDate: "2019-09",
        endDate: "2022-04",
        isCurrent: false,
        description:
          "• Authored 60+ detailed product requirement specifications (PRDs), user stories, and acceptance criteria in Jira.\n• Directed 25 user interview cycles that shaped the 2021 platform mobile feature roadmap.\n• Coordinated go-to-market release enablement across customer success, product marketing, and sales teams.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "Northwestern University",
        degree: "Bachelor of Arts",
        field: "Economics & Cognitive Science",
        graduationDate: "2019-06",
        gpa: "3.82",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "Enterprise Integrations Marketplace",
        type: "Product Launch",
        description:
          "Spearheaded discovery, partner API scoping, and commercial launch for third-party integrations with Slack, HubSpot, and Salesforce.",
        url: "https://velocity.com/integrations",
        technologies: ["Product Strategy", "API Design", "SQL", "Mixpanel", "Jira"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "Certified Scrum Product Owner (CSPO)",
        issuer: "Scrum Alliance",
        date: "2021-08",
        url: "https://scrumalliance.org",
      },
    ],
    skills: [
      "Product Strategy",
      "Roadmapping",
      "Agile / Scrum",
      "User Research",
      "A/B Testing",
      "SQL",
      "Product Analytics",
      "Mixpanel",
      "Jira",
      "Wireframing",
      "Go-to-Market (GTM)",
      "Cross-functional Leadership",
      "KPI Tracking",
    ],
  },
  {
    id: "starter-growth-marketing",
    role: "Growth Marketing Specialist",
    category: "Marketing & Growth",
    title: "Growth Marketing Specialist Resume",
    description: "Crafted for growth marketers, performance marketing leads, and SEO specialists. Highlights paid acquisition, analytics, and CRO.",
    template: "modern",
    accentColor: "#e11d48",
    professionalSummary:
      "Growth Marketing Specialist with 4+ years of experience scaling customer acquisition funnels, organic search traffic, and lifecycle retention workflows. Proven track record managing $500k+ annual paid ad budgets with sustained ROAS gains.",
    personalInfo: {
      fullName: "Chloe Ramirez",
      email: "chloe.ramirez.mkt@gmail.com",
      phone: "+1 (555) 914-7720",
      location: "Boston, MA",
      linkedin: "https://linkedin.com/in/chloeramirez-growth",
      website: "https://chloeramirez.com",
      github: "",
      image: "",
    },
    experience: [
      {
        id: "exp-1",
        company: "Elevate Media & Commerce",
        position: "Senior Growth Marketing Manager",
        startDate: "2023-02",
        endDate: "",
        isCurrent: true,
        description:
          "• Directed paid acquisition across Google Ads and Meta Ads with a $60,000 monthly budget, generating a 3.4x average ROAS.\n• Executed technical and content SEO roadmap that grew organic search clicks by 185% year-over-year (120k to 342k monthly sessions).\n• Engineered high-converting landing page A/B experiments that lifted overall visitor-to-lead conversion rate from 2.8% to 4.6%.\n• Designed multi-step automated email onboarding nurture journeys in HubSpot, decreasing 60-day customer churn by 19%.",
      },
      {
        id: "exp-2",
        company: "BrightWave Marketing",
        position: "Digital Marketing Specialist",
        startDate: "2021-01",
        endDate: "2023-01",
        isCurrent: false,
        description:
          "• Managed search engine marketing (SEM) campaigns and keyword bid adjustments, lowering cost-per-click (CPC) by 24%.\n• Built multi-channel attribution and KPI dashboards using Google Analytics 4, Tag Manager, and Looker Studio.\n• Wrote copy for 50+ conversion-focused ad creatives and long-form authority blog posts.",
      },
    ],
    education: [
      {
        id: "edu-1",
        institution: "Boston University",
        degree: "Bachelor of Science",
        field: "Marketing & Communications",
        graduationDate: "2020-05",
        gpa: "3.75",
      },
    ],
    projects: [
      {
        id: "proj-1",
        name: "Viral Product Launch Campaign",
        type: "Growth Campaign",
        description:
          "Created a waitlist referral growth loop that acquired 28,000 verified email signups in 30 days prior to platform launch.",
        url: "https://chloeramirez.com/case-studies/growth",
        technologies: ["Google Analytics 4", "SEO", "HubSpot", "A/B Testing", "Copywriting"],
      },
    ],
    certifications: [
      {
        id: "cert-1",
        name: "Google Analytics 4 (GA4) Certification",
        issuer: "Google Skillshop",
        date: "2023-05",
        url: "https://skillshop.exceedlms.com",
      },
      {
        id: "cert-2",
        name: "Inbound Marketing Certified",
        issuer: "HubSpot Academy",
        date: "2022-09",
        url: "https://academy.hubspot.com",
      },
    ],
    skills: [
      "SEO",
      "Google Ads",
      "Meta Ads",
      "Google Analytics 4",
      "HubSpot",
      "Conversion Rate Optimization (CRO)",
      "A/B Testing",
      "Email Marketing",
      "Content Strategy",
      "Copywriting",
      "Looker Studio",
      "Attribution Modeling",
    ],
  },
];

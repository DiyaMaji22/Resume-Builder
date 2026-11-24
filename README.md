# Resume Builder

An ATS-aware resume builder. A React client with live preview and PDF-style templates, backed by a
Django API on MongoDB.

## Stack

| Layer | Technology |
|---|---|
| Client | React 19, TypeScript 5, Vite 7, Tailwind CSS v4, Redux Toolkit |
| Backend | Django 5.2 LTS, Django REST Framework, Python 3.12 |
| Database | MongoDB 6+ (via `django-mongodb-backend`) |
| Auth | JWT access and refresh tokens |

## Layout

```
resume-builder/
├── client/        React app (Vite). Talks to the API through src/services/api.ts
├── backend/       Django API. See backend/README.md for setup, API reference and cutover notes
├── package.json   Root scripts that run both halves
└── README.md
```

## Getting started

Prerequisites: Node.js 20+, Python 3.12+, MongoDB 6+ (local or Atlas).

```bash
npm run install:all            # client npm packages + backend Python packages
cp backend/.env.example backend/.env
npm run backend:setup          # migrations (fake-initial) and MongoDB validators and indexes
npm run backend:seed           # optional demo data; sign in as diyamaji22@gmail.com / password123
npm run dev                    # client on :5173, API on :8000
```

Client environment: `client/.env.example` sets `VITE_API_URL`. It is empty by default, which
uses the Vite dev proxy.

## Upgrading from the Express server

The Django backend reads the existing MongoDB data without rewriting it. Run
`npm run backend:setup` against the existing database, then follow the cutover checklist in
`backend/README.md`. Existing accounts keep their passwords. Users sign in again once, because
sessions are re-issued.

## Common tasks

| Task | Command |
|---|---|
| Run the API tests | `npm run backend:test` |
| Lint the backend | `npm run backend:lint` |
| Lint and type-check the client | `npm run lint` and `npm run type-check` |
| Production build of the client | `npm run build` |

## Adding a template

1. Add the template ID to `TemplateId` in `backend/resumes/constants.py`.
2. Add the same ID to the client's `TemplateId` union in `client/src/types/index.ts`.
3. Create the component in `client/src/features/templates/components/` and register it in
   `client/src/features/templates/registry/index.ts`.

The template selector, preview and PDF export pick it up automatically.

## ATS notes

Every template follows these conventions, which keep them parseable by applicant tracking systems:
semantic HTML (`<article>`, `<section>`, `<h1>`–`<h3>`, `<time>`), no tables, floats or absolute
positioning, and skills as plain text.

## License

Private project.

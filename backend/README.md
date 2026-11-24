# Resume Builder — Backend

The API for the Resume Builder, written in Django 5.2 LTS on MongoDB. It replaces the earlier
Express/TypeScript service and keeps its HTTP contract, so the React client works unchanged.

## Stack

| Concern | Choice |
|---|---|
| Framework | Django 5.2 LTS, Django REST Framework |
| Database | MongoDB 6+ through the official `django-mongodb-backend` |
| Auth | JWT (PyJWT), Argon2 password hashing, bcrypt read-compatibility for migrated accounts |
| Validation | DRF serializers (single boundary for every write) |
| Outbound HTTP | httpx, with explicit timeouts |
| PDF import | pypdf |
| Lint and format | ruff |
| Tests | Django's test runner against a real MongoDB (93+ tests, including golden parity tests) |

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env              # defaults work for a local MongoDB on 127.0.0.1:27017

python manage.py migrate --fake-initial   # see "Adopting an existing database" below
python manage.py setup_mongodb            # $jsonSchema validators and indexes (idempotent)
python manage.py seed_demo_data --flush   # optional: demo users (password: password123)
python manage.py runserver                # http://127.0.0.1:8000
```

Run the tests (they create and drop a `test_*` database on the same server):

```bash
python manage.py test --settings=config.settings.test
ruff check . && ruff format --check .
```

## Adopting an existing database

The original service wrote MongoDB documents with Mongoose. The new code reads them unchanged:
collection names, field names (`userId`, `isPublic`, `personalInfo`, …) and the stored
bcrypt password hashes are all preserved through `db_column` and the legacy password check.

Run the same two commands on a new or an existing database:

```bash
python manage.py migrate --fake-initial
python manage.py setup_mongodb
```

`--fake-initial` marks the initial schema as applied when its collections already exist. Without
it, Django tries to create collections that are already there. Two data migrations then backfill
fields that the Node service did not write (`is_active`, `is_staff`, resume list fields), because
without them every migrated account would appear inactive.

Cutover checklist:

1. Stop the Node service so no writes happen during the migration.
2. Take a backup (`mongodump`).
3. Run the two commands above against the production database.
4. Start the Django service and sign in with an existing account. The password is upgraded to
   the current hasher on that first login.
5. Existing sessions are invalidated (refresh tokens are now stored by ID, not as bcrypt hashes),
   so users sign in once.

I verified this procedure against a database written in the original Mongoose shape: legacy
bcrypt login, reads, partial updates, version save and restore, ATS scoring, the public page and
analytics all worked.

## Configuration

All configuration comes from environment variables. See `.env.example` for the full list.

| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | no | `config.settings.development` (default), `.production`, or `.test` |
| `DJANGO_SECRET_KEY` | production | 50+ characters. Production refuses to start without it |
| `JWT_KEY` | production | 32+ characters. Signs access and refresh tokens |
| `DJANGO_ALLOWED_HOSTS` | production | Comma-separated public hostnames |
| `DJANGO_NUM_PROXIES` | behind a proxy | Trusted proxies in front of the app; controls which `X-Forwarded-For` is trusted |
| `MONGODB_URI`, `MONGODB_DB` | yes | Connection string and database name |
| `CLIENT_URL` | yes | Origin allowed by CORS |
| `REDIS_URL` | recommended with >1 worker | Shared cache for rate limits and login failure counters |
| `OPENAI_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_TIMEOUT_SECONDS` | optional | Any OpenAI-compatible endpoint. Without a key, AI routes return 503 |

## Running in production

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Put it behind a TLS-terminating proxy that sets `X-Forwarded-Proto`. Set `DJANGO_NUM_PROXIES` to
the number of proxies in front of the app. Use Redis as the cache when running more than one
worker, because the default in-process cache does not share rate-limit counters.

## API

Every response uses one envelope: `{"message": string, "data"?: T}`. Errors add `errors` for
validation failures, keyed by field:

```json
{ "message": "Validation failed", "errors": { "template": ["\"fancy\" is not a valid choice."] } }
```

Auth header: `Authorization: Bearer <access token>`. Access tokens last 15 minutes. Refresh tokens
last 24 hours, or 7 days with `rememberMe`.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | — | Create account, returns session |
| POST | `/api/auth/login` | — | Sign in, returns session |
| POST | `/api/auth/refresh` | — | Exchange refresh token for an access token |
| POST | `/api/auth/logout` | Bearer | Revoke one refresh token |
| GET | `/api/auth/me` | Bearer | Current user |
| PUT | `/api/users/me` | Bearer | Update name or email |
| PUT | `/api/users/me/password` | Bearer | Change password (ends all sessions) |
| DELETE | `/api/users/me` | Bearer | Delete account and resumes (needs password) |
| GET | `/api/resumes` | Bearer | List own resumes, newest first |
| POST | `/api/resumes` | Bearer | Create resume |
| GET / PUT / DELETE | `/api/resumes/{id}` | Bearer | Read, partially update, delete |
| POST | `/api/resumes/{id}/duplicate` | Bearer | Copy |
| POST | `/api/resumes/{id}/versions` | Bearer | Save a version (keeps the 10 most recent) |
| POST | `/api/resumes/{id}/versions/{snapshotId}/restore` | Bearer | Restore a version |
| POST | `/api/resumes/{id}/ats-analyze` | Bearer | Score against a job description |
| POST | `/api/resumes/upload` | Bearer | Import a text PDF (multipart `file`, max 10 MB) |
| GET | `/api/resumes/public/{id}` | — | Published resume, without version history |
| GET | `/api/resumes/starters` | — | Starter templates and benchmark jobs |
| POST | `/api/ai/suggest` | Bearer | Summary or bullet suggestions (20/min per user) |
| GET | `/api/analytics` | Staff | Aggregated dashboard |
| POST | `/api/analytics/setup`, `/seed` | Staff | Operator actions, only when `ENABLE_DB_ADMIN_ENDPOINTS` is true (development) |
| GET | `/health` | — | Liveness, plus a database check (503 when unreachable) |

Rate limits: 200 requests per 15 minutes per IP overall; registration 5 per hour per IP; login
10 failed attempts per 15 minutes per IP; token refresh 30 per 15 minutes per IP.

## Architecture

```
config/          settings (base + per-environment), root URLs, WSGI/ASGI
core/            envelope, error handling, throttling, Mongo validators, demo data, health
accounts/        User model, tokens, JWT authentication, services, views
resumes/         embedded document models, serializers (validation boundary),
                 services (use cases), ats.py + ats_data.py, pdf_import.py, starters
ai/              prompt building, OpenAI-compatible client, service, view
analytics/       aggregation pipelines run in-process, service, staff-only views
```

Views translate HTTP into service calls; services hold the rules and know nothing about requests.
Every resume query is scoped to the requesting user, and a resume that belongs to someone else
returns 404, not 403, so resume IDs are not confirmed to other users.

Resumes are single MongoDB documents with embedded sections, because the sections are always
read and written together. `db_column` keeps the stored camelCase names.

## Fidelity to the original

The ATS analyser and PDF text parser are ported from the TypeScript code and checked against
golden outputs recorded from that code: 36 starter-by-job ATS results, the edge cases, keyword
extraction, and three PDF samples. The tests fail on any difference. Two details make the port
exact: JavaScript's `Math.round` rounds halves upward (Python's `round` does not), and the same
keyword lexicon and word-boundary rules are used.

## Behaviour changes from the Express service

Each of these is intentional. Most fix a bug in the original.

- **Analytics is staff-only.** The old API let any signed-in user read figures that included other
  users' names.
- **Analytics no longer runs a Python subprocess per request.** The aggregations run in-process.
- **Setup and seed are operator commands,** not public routes. HTTP access exists only when
  `ENABLE_DB_ADMIN_ENDPOINTS` is set (development).
- **Wrong current password returns 400, not 401.** A 401 made the client treat the request as an
  expired session and log the user out.
- **Public resumes no longer include version history.** The old response leaked snapshots that
  could contain older personal details.
- **Version restore is validated.** Stored content goes through the same serializer as an edit.
  Previously it was written straight into the document.
- **Partial updates merge personal info** instead of replacing the whole object.
- **Password change ends all sessions,** including those on other devices.
- **Unknown-account logins take the same time as wrong-password logins.** This prevents
  account enumeration by timing.
- **Templates `home_college` and `general_template` are accepted everywhere.** The old schema
  rejected them after validation had passed.
- **Refresh tokens are stored as IDs,** not bcrypt hashes of long JWTs (bcrypt truncates at 72
  bytes, so distinct tokens could collide).
- **Email is normalised on profile update** as on registration.
- **Seeding protects data.** It requires `--flush` over existing data and refuses to run outside
  development unless `--force` is passed.
- **Unknown resume IDs return 404,** not 400.
- **Passwords use Argon2** (Django's recommended hasher), with the Django password validators.

## Known limitations and follow-ups

- **Keyword matching is inherited.** `rest` and `go` match ordinary English words, which inflates
  ATS scores. Fixing it would change scores, so it is left for a deliberate change.
- **Version saves are not atomic.** Two saves at the same moment can drop one snapshot. The
  original had the same race. A `$push` with `$slice` would fix it.
- **Public resume IDs are guessable-ish** (MongoDB ObjectIds embed a timestamp). A random share
  token would be better, and it would allow revoking a link.
- **Account lockout is per IP only,** so one IP can still try many accounts slowly. Per-account
  limits would need care, because they let an attacker lock out a real user.
- **PDF parsing runs in the request.** A pathological file could be slow. Moving it to a worker
  queue with a timeout is the next step if large uploads become common.
- **The local cache is per process.** Use Redis for rate limits with more than one worker.
- Embedded document models create empty `resumes_*` collections in MongoDB during migrations.
  This is harmless and comes from how the backend generates migrations.

## Developer notes

- **Adding a template:** add the value to `TemplateId` in `resumes/constants.py`, then update the
  client's `TemplateId` union and registry. The `$jsonSchema` validator reads the same list.
- **Adding a resume section:** add an embedded model (`managed = False`) and a migration, then add
  a serializer and extend `_SECTION_MODELS` in `resumes/services.py`.
- **Changing the ATS lexicon:** edit `resumes/ats_data.py`. The parity tests will flag any change
  to scoring, so update the golden fixture only when a scoring change is intended.

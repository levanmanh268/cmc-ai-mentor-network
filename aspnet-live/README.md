# ASP.NET Core 10 Live Portal for CMC AI Mentor Network

**Status:** Separate, non-destructive backend prototype. The existing Streamlit production app on Render is not replaced. This feature is experimental until a dedicated PostgreSQL instance is attached and the public URL passes a live two-browser UAT.

## 1. Architecture

```text
Browser A -- GET/POST JSON --> ASP.NET Core 10 Minimal API -- Npgsql --> PostgreSQL
Browser B <-- SSE event ----- ASP.NET Core 10 LiveBus <---- committed POST
Browser B -- GET /api/requests --> same PostgreSQL persisted rows
                             [one Render service instance; no Redis or distributed bus]
```

- Public page served at `/` with HTML/CSS/JavaScript from `Group6Live/wwwroot`.
- `GET /health/live`: confirms web process, **not database**.
- `GET /health/ready`: confirms PostgreSQL connection and schema bootstrap. HTTP 503 if unavailable.
- `GET /api/status`: database and persisted record count.
- `GET /api/mentors`: seeded synthetic mentor directory loaded **from PostgreSQL**.
- `GET /api/requests`: up to 40 most recent publicly submitted study requests.
- `POST /api/requests`: validates fields, inserts with parameterized query, responds 201, then broadcasts event.
- `GET /api/events`: native Server-Sent Events. Clients use EventSource and GET fresh state upon receipt; 12-second polling provides fallback.

Never claim the page is backed by PostgreSQL unless `/health/ready` returns HTTP 200 and the persistence-after-restart test passes against the **actual deployment's database**.

## 2. Technology

.NET **10 LTS** (ASP.NET Core), Npgsql 10.0.3, PostgreSQL 16+; Docker multi-stage build; GitHub Actions Postgres test service. This is a **new** ASP.NET portal, not a silent conversion of the original Python/Streamlit implementation.

## 3. Run locally

Install the .NET 10 SDK and a standalone PostgreSQL database. Set `DATABASE_URL` to a secret connection string. Do not commit, print, copy into GitHub Issues, or send to others.

```bash
export DATABASE_URL='Host=localhost;Port=5432;Database=group6_dev;Username=dev_user;Password=<REDACTED>;SSL Mode=Prefer'
dotnet run --project aspnet-live/Group6Live/Group6Live.csproj
```

Use the URL shown by dotnet. The code automatically creates tables under `group6_live` schema, inserts *synthetic* mentor examples and reads/writes actual requests. Disabling DATABASE_URL intentionally produces a **503 not_ready** response; there is no fake in-memory persistence mode.

## 4. Test on GitHub

```bash
dotnet test aspnet-live/Group6Live.Tests/Group6Live.Tests.csproj
```

`.github/workflows/aspnet-live.yml` runs dotnet restore/build/test, a real PostgreSQL 16 service with `aspnet-live/e2e_integration.py`, and Docker image build. Acceptance checks:
1. PostgreSQL health and actual schema.
2. Synthetic mentors read from DB.
3. POST returns 201 with assigned DB record ID.
4. GET retrieves committed row.
5. Invalid input returns 400.
6. An SSE client receives `event: changed` on a commit.
7. After ASP.NET process restart, both test records remain in PostgreSQL.
8. Docker can build the production image.

CI database is **ephemeral and distinct** from any user production/staging DB. A green CI verifies the test environment, not a live public Postgres deployment.

## 5. Deploy a new Render Web Service

Create a **separate** web service without modifying the Streamlit deployment:

| Setting | Value |
| --- | --- |
| Runtime | Docker |
| Branch | `feat/aspnet10-live-postgres-20261110` until reviewed |
| Docker context | `aspnet-live/Group6Live` |
| Dockerfile | `aspnet-live/Group6Live/Dockerfile` |
| Plan | Free (classroom demo only) |
| Region | Singapore |
| Environment | `DATABASE_URL`: **dedicated, isolated PostgreSQL** |
| Port | 10000 |

The current Render workspace already has one **free** Postgres instance dedicated to another project, Delta Travel. **Do not reuse or edit it**. Render permits one Free PostgreSQL per workspace, and free DBs expire after 30 days, with no managed backups. For durable classroom records, provision an isolated PostgreSQL service on a separate authorized provider or move to a supported paid DB after explicit cost approval. In all cases, keep connection strings in Render Environment, not repository files. For any cloud database, enable TLS and review network controls.

## 6. Security and limitations

- Anonymous read and append-only submissions. Not a multi-user authenticated system; no private conversations, role access, shared mentor editing, or user data deletion workflow.
- Public submissions are visible to everyone. No email, phone, account credentials, API keys or other sensitive PII should be entered.
- Each request contains only nickname, topic and message; server enforces field lengths and a 16 KB request size cap.
- Fixed-window 4-posts-per-minute limit partitions by effective connection IP; this is **not** enterprise-grade abuse protection, moderation or multi-instance rate limiting.
- Query parameters are bound via Npgsql parameters. UI renders dynamic user text via `textContent`, never `innerHTML`; CSP prohibits inline JavaScript.
- SSE bus works inside **one ASP.NET process**. On multiple service replicas, use Postgres NOTIFY, Redis Pub/Sub or a managed SignalR backplane; current demo does not claim distributed realtime.
- On Free Render, sleeping causes cold starts. The page reconnects SSE and polls for updates, but **no uptime SLA** is claimed.
- Database credentials are kept on server. Never expose DB connection strings in browser code or CI artifacts. Production backups, moderation, privacy notice and independent security review remain pending.

## 7. Definition of Done before teacher demonstration

- [ ] .NET + xUnit + real PostgreSQL + SSE + restart tests PASS on exact code SHA.
- [ ] Docker build PASS and service reaches `live` on Render.
- [ ] A separate PostgreSQL database is provisioned and `DATABASE_URL` configured without exposing a secret.
- [ ] Public `/health/ready` returns HTTP 200, not 503.
- [ ] From Browser A submit a *synthetic* request; Browser B displays it without manual refresh.
- [ ] Reload both browsers and restart backend; record is still displayed.
- [ ] Note actual deployed SHA, URL, date/time, test reporter, and attach screenshot/redacted outputs in a Markdown report.
- [ ] PR reviewed by another team member before merge to `main`.

# SpecBridge

**AI-powered installation procurement platform · BEP Grand Rapids pilot · T&M division rollout**

SpecBridge is a production procurement tool for installation subcontracting at Burke Porter Group. It captures structured scope data, runs competitive quote tracking, generates AI-powered RFQs and Statements of Work, and surfaces ECN risk analytics — all from a single HTML file backed by Supabase and the Claude API.

> **Status: Live in production.** SpecBridge is actively being used on the Scout Motors EOL Systems project ($1.375M installation scope). It is not a prototype.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Single HTML file (`specbridge.html`) — vanilla JavaScript, no build step, no framework |
| Database | Supabase (PostgreSQL) at `https://vvukjjuxjhlpuczcxirp.supabase.co` |
| AI | Claude Sonnet via Supabase Edge Function (`claude-proxy`) |
| Hosting | Vercel — GitHub `main` branch auto-deploys in ~30 seconds |
| Auth | Supabase Auth (email/password) — **Entra ID SSO migration planned as P1 hardening item** |
| Source control | `github.com/ryan-pearman-ascentialtech/specbridge` |

---

## Quick Start

### 1. Clone and open

```bash
git clone https://github.com/ryan-pearman-ascentialtech/specbridge.git
cd specbridge
# Open specbridge.html in your browser — it connects live to Supabase
```

### 2. Add your Anthropic API key to Supabase

Go to: `supabase.com` → specbridge project → Edge Functions → Secrets

```
ANTHROPIC_API_KEY = sk-ant-...your key...
```

The Edge Function (`claude-proxy`) injects BEP GR 2025 labor rates into every prompt before forwarding to the Anthropic API:

| Role | Rate |
|---|---|
| Mechanical Engineer (ME) | $89.73/hr |
| Electrical Engineer (EE) | $99.93/hr |
| Systems Engineer (SE) | $102.51/hr |
| Project Manager (PM) | $79.69/hr |
| Service (SVC) | $80.28/hr |

### 3. Connect Vercel

Import this repo at `vercel.com`. No build command — it is a static HTML file. Deploy → live URL in ~30 seconds.

> **Important:** Never create an `index.html` file in this repo. Vercel serves it as the root and breaks the deployment. `specbridge.html` must remain the only HTML file.

### 4. Create your first user

Go to Supabase → Authentication → Users → Add user

Then set their role in the `profiles` table:

```sql
UPDATE profiles SET role = 'admin'    WHERE email = 'mark@bepgr.com';
UPDATE profiles SET role = 'engineer' WHERE email = 'paul@bepgr.com';
```

---

## File Editing (Windows / PowerShell)

All edits to `specbridge.html` on Windows must use PowerShell with explicit UTF-8 no-BOM encoding. **Never use `Set-Content` or `Get-Content`** — they misread UTF-8 emoji and special characters as Windows-1252 and will corrupt the file.

```powershell
# Read
$content = [System.IO.File]::ReadAllText('specbridge.html', [System.Text.Encoding]::UTF8)

# Write
[System.IO.File]::WriteAllText('specbridge.html', $content, (New-Object System.Text.UTF8Encoding $false))
```

## Git Workflow

```bash
cd C:\Users\rpearman\Documents\specbridge

git add specbridge.html          # Always explicit — never git add .
git commit -m "your message"
git push origin main             # Vercel auto-deploys within ~30 seconds
```

---

## Supabase Project

| Item | Value |
|---|---|
| Project URL | `https://vvukjjuxjhlpuczcxirp.supabase.co` |
| Project name | specbridge |
| Region | us-east-1 |
| Edge Function | `claude-proxy` (all AI calls proxy through here) |

> **Security note:** Row-level security (RLS) is **not yet enabled** on production tables. This is a documented P1 hardening item. The anon key is currently embedded in the HTML file. Both issues are tracked in the deployment backlog and must be resolved before broad team rollout.

---

## Database Schema

> **Critical:** The primary projects table is `rfq_projects` — not `projects`. Any direct SQL queries must use this table name.

| Table | Purpose |
|---|---|
| `rfq_projects` | Core project records — primary table for all project data |
| `profiles` | Users extending `auth.users`. Roles: `admin` / `engineer` / `viewer` |
| `entities` | T&M division entities — BEP GR seeded as pilot entity |
| `scopes` | Installation scope packages per project (Steel, Crane, Mechanical, Electrical, etc.) |
| `quotes` | Supplier quotes per scope — tracks all quote submissions and awarded values |
| `negotiation_log` | Timestamped entries per scope — calls, email clarifications, scope changes |
| `suppliers` | Preferred supplier roster with contact info and category tags |
| `spec_entries` | Typed spec fields across 7 categories per project |
| `analyses` | AI results: classification, gap check, should-cost |
| `reports` | Generated RFQ and SOW documents |
| `documents` | Uploaded spec files (storage: `spec-documents` bucket) |
| `audit_log` | Full change history on projects (user, timestamp, old/new values) |

### Key field notes

- Buyer field: `buyer_name` (not `buyer`)
- Project status: `status` field using the workflow values below
- Entity isolation: `entity_id` foreign key on `rfq_projects` — used for multi-entity rollout

---

## Project Status Workflow

Mirrors the BEP GR AE weekly RFQ meeting structure (confirmed by Paul Kitchen, Director of Procurement):

```
in_process_rfq → nopo_authorization → anticipated_order → new_po_received
                                    ↘ on_hold
                                    ↘ lost
```

---

## Spec Capture Tabs (7 categories)

```
project_overview · technical_reqs · materials · dimensions · surface_finish · delivery · certifications
```

---

## Core Functions (`specbridge.html`)

```javascript
showPage(pageId)                    // Route between all screens
callClaude(action, payload)         // All AI calls via claude-proxy edge function
dbQuery(table, op, options)         // All Supabase DB operations — use this, not raw client calls
showToast(message, type)            // Feedback: 'success' | 'warning' | 'error'
saveField(projectId, table, field, value)  // Auto-save on input blur — triggers refreshScore()
refreshScore(projectId)             // Recalculate spec completeness % from all 7 spec tables
```

> **Pattern:** All DB calls go through `dbQuery()`. All AI calls go through `callClaude()`. Never make raw Supabase client calls or direct fetch calls to the Anthropic API in page code — this was the root cause of several bugs in earlier builds.

---

## AI Actions (`claude-proxy` Edge Function)

| Action | Input | Output |
|---|---|---|
| `classify` | Project description | `type`, `complexity`, `tags`, `confidence` |
| `check_gaps` | Project type + spec entries | Completeness score, gap flags with severity |
| `should_cost` | Spec entries + historical projects | Cost estimate, breakdown, risk flags |
| `generate_rfq` | Project + spec entries + BEP labor rates | Formatted RFQ document (markdown) |
| `generate_sow` | Project + awarded scope + supplier | Structured Statement of Work (markdown) |

---

## What SpecBridge Does Today (Production Features)

| Capability | Status |
|---|---|
| Structured scope intake with AI gap detection | ✅ Live |
| Slate gate logic — flags $1M+ installation scope misses | ✅ Live |
| AI-generated RFQs and SOWs with BEP GR 2025 labor rates | ✅ Live |
| Competitive quote tracking per scope per supplier | ✅ Live |
| Over-budget and single-source risk alerts | ✅ Live |
| Negotiation log with timestamped entries per scope | ✅ Live |
| Savings dashboard — competitive savings, ECN rate, AE/customer risk | ✅ Live |
| ECN analytics — 26.7% rate from BEP GR PO log, AE and customer breakdown | ✅ Live |
| Admin page — entity rollout management, preferred supplier roster | ✅ Live |
| Multi-entity scaffold — BEP Brugge, EPIC, Kleinknecht, Galileo, LISMAR ready to activate | ✅ Scaffolded |
| PDF export (branded RFQ/SOW) | 🔧 P1 hardening item |
| Microsoft Entra ID SSO | 🔧 P1 hardening item |
| Row-level security (RLS) | 🔧 P1 hardening item |
| Baan data sync (nightly) | 🔧 P2 item |
| Email notifications | 🔧 P2 item |
| Quote PDF extraction (AI-assisted) | 🔧 P2 item |
| Deal Desk integration (governance screening + form pre-population) | 📋 Future / Phase 2 |
| Supplier portal | 📋 Future / Phase 2 |

---

## Live Project Data (as of April 2026)

**Scout Motors EOL Systems** — First live project

| Item | Value |
|---|---|
| SOW number | #001 |
| BEP internal budget | $1,375,452 |
| Awarded contractor | Griffin Contracting |
| Awarded value | $896,804 |
| Culver Development baseline | $1,650,521 |
| Competitive savings | $753,717 |
| PO number | #317327RDI |

**Harbinger LCF** — Second active project (brought in by Matthew Staal)

| Item | Value |
|---|---|
| Scope | Calibration cell, Garden Grove CA (Class 4–6 LCF trucks) |
| Customer contacts | Raymond Leung (Purchasing), Phil To (AME), Matt Morgan (PM) |

**ECN analytics (BEP GR PO log, YTD Jan–Apr 2026)**

| Metric | Value |
|---|---|
| Total POs | 90 |
| ECN count | 24 (26.7%) |
| ECN PO value YTD | $1,965,803 |
| Annualized ECN exposure | ~$8.4M/year |
| Highest AE ECN rate | 62.5% — Jennifer Willbrandt (16 POs) |
| Highest customer ECN rate | 70.0% — GM Orion (10 POs) |

---

## Entity Rollout Plan

| Phase | Entity | Location | Annual Spend | Status |
|---|---|---|---|---|
| Pilot | BEP Grand Rapids | Grand Rapids, MI | $27.1M | **Active** |
| Scale 1 | BEP Brugge | Brugge, Belgium | $25.3M | Scaffolded — pending activation |
| Scale 2 | EPIC | TBC | $20.1M | Scaffolded |
| Scale 3 | Kleinknecht | Germany | $7.3M | Scaffolded |
| Scale 4 | Galileo | Turin, Italy | $7.2M | Scaffolded |
| Scale 5 | LISMAR EMEA | Netherlands | $5.4M | Scaffolded |
| **Total** | | | **$92.4M** | |

---

## Key Contacts

| Role | Person | Relevance |
|---|---|---|
| VP Procurement / Business sponsor | Mark Mensonides | Primary stakeholder, project approvals |
| Director Indirect Procurement | Dave Drelles | Co-builder, domain knowledge |
| Procurement Manager / Builder | Ryan Pearman | Owns the codebase |
| CFO | Mike Pisch | Budget approver for production deployment |
| CLO / Deal Desk governance | Georgette Dulworth | Confirmed Deal Desk integration scope |
| Legal / Deal Desk submissions | Teri Norton | teri.norton@ascentialtech.com |
| Finance / Deal Desk formulas | Matt Boschoven | Owns Excel formula logic in Deal Desk form |
| Director of Procurement | Paul Kitchen | Confirmed ECN data, project volume |
| Applications Engineer (first user) | Matthew Staal | BEP GR — live on Harbinger LCF project |
| BEP Brugge Senior AE | Pieter Vancraeynest | Scout Motors PM, Brugge rollout contact |
| Brugge buyer (best-practice model) | Rik Dierckens | Modeled best-in-class procurement behavior incorporated into SpecBridge |

---

## P1 Hardening Backlog (Pre-Production Requirements)

These items must be completed before SpecBridge is opened to the full BEP GR team. A separate deployment readiness document covers the full specification.

| Item | Description | Effort |
|---|---|---|
| Entra ID SSO | Replace email/password auth with Microsoft Entra ID (Azure AD) corporate SSO | 3–5 days |
| Row-level security | Enable Supabase RLS policies on all tables — entity and role isolation at the DB layer | 2–3 days |
| API key hardening | Remove Supabase anon key from client HTML; Edge Function validates Entra ID JWT before executing | 2–3 days |
| Infrastructure ownership | Transfer GitHub repo and Vercel project to Ascential corporate accounts; branch protection rules | 1 day |
| RFQ / SOW print & PDF export | Print-optimized CSS with BEP branding, auto-generated document numbers, page headers/footers, signature blocks | 3–4 days |
| Data backup | Supabase Pro tier — daily automated backups, point-in-time recovery, documented recovery procedure | 0.5 day |
| Audit logging | Audit trail implementation (currently schema exists, trigger functions not yet complete) | 1–2 days |
| User management UI | Admin screen for provisioning users without direct Supabase dashboard access | 2–3 days |

---

## Demo Narrative (Two-Act Structure)

The strongest demo format:

**Act 1 — Build a project from blank** (shows ease of use and AI gap detection)
- Create new project → AI classifies scope → spec fields populate → gap flags fire → RFQ generated

**Act 2 — Cut to Scout Motors completed project** (shows real outcomes)
- Live data: Griffin at $896,804 vs. Culver baseline $1,650,521 → $753,717 competitive savings
- Savings dashboard: 26.7% ECN rate, $8.4M annualized exposure, AE and customer risk tables
- Admin page: click + Add Entity → type "Galileo · Turin, Italy" → appears instantly

---

## Financial Impact Summary

| Metric | Value | Basis |
|---|---|---|
| Competitive sourcing savings — BEP GR | $877K–$1.37M/year | 15–20 projects × 3–4 scopes × $19.5K avg savings/scope |
| ECN reduction savings — BEP GR | $1.26M–$1.68M/year | 15–20% prevention rate on $8.4M annualized ECN exposure |
| **Combined annual value — BEP GR pilot** | **$2.1M–$2.3M/year** | Independent mechanisms, additive |
| Division-wide (6 entities, $92.4M spend) | $9.2M+/year | Equivalent savings rate at full rollout |
| Phase 1 development cost (hardening) | $35,000–$45,000 | One-time — P1 + P2 items |
| Annual infrastructure cost | ~$1,400–$2,900 | Supabase Pro + Vercel/Azure + Anthropic API |

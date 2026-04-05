# SpecBridge
**AI-powered spec capture and RFQ intelligence · BEP GR pilot · T&M division rollout**

Single-file web app. Push to `main` → live on Vercel in 30 seconds.

---

## Stack
- **Frontend**: Single HTML file (`specbridge.html`) — no build step, no framework
- **Database**: Supabase (PostgreSQL + RLS)
- **AI**: Claude via Supabase Edge Function (`claude-proxy`)
- **Hosting**: Vercel (static)
- **Auth**: Supabase Auth (email/password)

---

## Quick Start

### 1. Clone and open
```bash
git clone https://github.com/YOUR_ORG/specbridge.git
cd specbridge
# Open specbridge.html in your browser — it connects live to Supabase
```

### 2. Add your Anthropic API key to Supabase
Go to: [supabase.com](https://supabase.com) → `specbridge` project → **Edge Functions** → **Secrets**

Add:
```
ANTHROPIC_API_KEY = sk-ant-...your key...
```

### 3. Connect Vercel
- Import this repo in [vercel.com](https://vercel.com)
- No build command needed — it's a static HTML file
- Deploy → you get a live URL instantly

### 4. Create your first user
Go to Supabase → **Authentication** → **Users** → **Add user**

Set role in the `profiles` table:
```sql
UPDATE profiles SET role = 'admin' WHERE email = 'mark@bepgr.com';
UPDATE profiles SET role = 'engineer' WHERE email = 'paul@bepgr.com';
```

---

## Supabase Project
- **URL**: `https://vvukjjuxjhlpuczcxirp.supabase.co`
- **Project**: `specbridge`
- **Region**: `us-east-1`
- **Edge Function**: `claude-proxy` (handles all AI calls)

---

## Database Schema

| Table | Purpose |
|---|---|
| `profiles` | Users extending auth.users (roles: admin / engineer / viewer) |
| `entities` | T&M division entities — BEP GR seeded as pilot |
| `projects` | RFQ projects with 4-bucket status workflow |
| `spec_entries` | Typed spec fields across 7 categories per project |
| `analyses` | AI results (classification, gap check, should-cost) |
| `reports` | Generated RFQ documents |
| `documents` | Uploaded spec files (storage: spec-documents bucket) |
| `audit_log` | Full change history on projects |

### Project Status Workflow
Mirrors Paul Kitchen's weekly AE RFQ meeting structure:
```
in_process_rfq → nopo_authorization → anticipated_order → new_po_received
                                   ↘ on_hold
                                   ↘ lost
```

### Spec Capture Tabs (7)
`project_overview` · `technical_reqs` · `materials` · `dimensions` · `surface_finish` · `delivery` · `certifications`

---

## Core Functions (in specbridge.html)

```js
showPage(pageId)              // Route between all 7 screens
callClaude(action, payload)   // All AI calls via edge function
dbQuery(table, op, options)   // All Supabase DB operations
showToast(message, type)      // success | warning | error
saveField(projectId, ...)     // Auto-save on input blur
refreshScore(projectId)       // Recalculate completeness %
```

---

## AI Actions (claude-proxy edge function)

| Action | Input | Output |
|---|---|---|
| `classify` | Project description | type, complexity, tags, confidence |
| `check_gaps` | Project type + spec entries | completeness score, gap flags, severity |
| `should_cost` | Spec entries + historical projects | cost estimate, breakdown, risk flags |
| `generate_rfq` | Project + spec entries | formatted RFQ document (markdown) |

---

## Demo Scope (What We Build)

**7 screens:** Login → Dashboard → New Project → Spec Capture → Review & Route → RFQ Output → Savings Dashboard

**Deliberately skipped for demo:** multi-entity UI, Teams notifications, user admin, file upload/PDF parsing, Power BI embed, RLS enforcement, mobile views.

---

## Team
Mark Mensonides · Dave Drelles · Ryan Pearman
**Demo Day: April 2026**

---

## Entity Rollout Plan
| Phase | Entity | Spend | Timeline |
|---|---|---|---|
| Pilot | BEP GR | $27.1M | Demo Day + 90 days |
| Scale 1 | BEP Brugge | $25.3M | Month 3 |
| Scale 2 | EPIC | $20.1M | Month 5 |
| Scale 3 | Kleinknecht | $7.3M | Month 7 |
| Scale 4 | Galileo | $7.2M | Month 9 |
| Scale 5 | LISMAR EMEA | $5.4M | Month 11 |

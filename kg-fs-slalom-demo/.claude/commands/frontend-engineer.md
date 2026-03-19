# Frontend Engineer — Slalom KG + RAG Platform

You are operating as the **Frontend Engineer** on the Slalom Field Services Intelligence Platform.

## Your Responsibilities

You own the consultant-facing application:
- **Chat UI**: The primary query interface — input, streaming response, citations, follow-ups
- **Discovery Question Tree**: Interactive, branching question tree for utility FSM meeting prep
- **Meeting Prep Brief**: Structured output view for pre-meeting consultant briefs
- **Graph Explorer**: Visual exploration of the knowledge graph (client → system → engagement)
- **Feedback UI**: Thumbs up/down + comment capture on responses
- **Admin Console** (Phase 2): Ingestion dashboard, entity review queue, ontology management UI

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode — no `any`, no `@ts-ignore` without comment)
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **State**: React hooks only (no Redux, no Zustand for Phase 1)
- **API calls**: Always through `lib/api.ts` — never raw `fetch` in components
- **Types**: Always defined in `lib/types.ts` — kept in sync with backend response shapes

## Design Principles

- **Desktop-first** (this is a productivity tool used at a desk, not mobile)
- **Clean, minimal** — no visual clutter; let the content breathe
- **Slate/gray palette** with a single brand accent (Slalom teal: `#00A3AD`)
- **Card-based layout** with subtle shadows (`shadow-sm`, `rounded-lg`)
- **Always show loading states** — every async operation has a skeleton or spinner
- **Toast notifications** for errors and success (use a lightweight toast, not a modal)
- **Citations are non-negotiable** — every AI response shows its sources; never hide them
- **Confidence indicators** — show retrieval confidence as a subtle badge on citations

## TypeScript Types (keep in sync with backend)

```typescript
// lib/types.ts

export interface QueryRequest {
  query: string;
  tenant_id: string;
  filters?: {
    use_case_tags?: string[];
    industry_tags?: string[];
    utility_sub_domain?: string;
  };
}

export interface Citation {
  doc_id: string;
  engagement_id?: string;
  doc_type: 'narrative' | 'qa_bank' | 'transcript' | 'rfd' | 'industry_ref';
  title: string;
  excerpt: string;
  relevance_score: number;
  url?: string;
}

export interface ConsultantReferral {
  initials: string;
  seniority: string;
  utility_experience_years: number;
  relevant_engagements: string[];
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  suggested_follow_ups: string[];
  consultant_referrals: ConsultantReferral[];
  retrieval_latency_ms: number;
  generation_latency_ms: number;
}

export interface DiscoveryQuestion {
  id: string;
  text: string;
  category: 'pain' | 'technical' | 'org' | 'data' | 'regulatory';
  likely_answers: Array<{
    answer_text: string;
    implication: string;
    leads_to?: string; // next question ID
  }>;
}

export interface MeetingBrief {
  client_name: string;
  use_case: string;
  key_questions: DiscoveryQuestion[];
  relevant_past_work: Citation[];
  system_landscape: string[];
  regulatory_context: string[];
  suggested_consultants: ConsultantReferral[];
  generated_at: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'Client' | 'TechSystem' | 'UseCase' | 'Engagement' | 'Consultant';
  properties: Record<string, string | number | boolean>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  properties?: Record<string, string | number>;
}
```

## Page Structure

```
app/
  layout.tsx              — Root layout: nav, global styles, Slalom brand header
  page.tsx                — Dashboard: quick-access cards (Chat, Meeting Prep, Graph, History)

  chat/
    page.tsx              — Main consultant chat interface

  meeting-prep/
    page.tsx              — Meeting prep brief generator (client + use case selector → brief)

  discovery/
    page.tsx              — Interactive discovery question tree

  graph/
    page.tsx              — Knowledge graph explorer

  admin/
    ingest/page.tsx       — Ingestion status (Phase 1e): job queue, doc counts, last-run timestamps (read-only)
    page.tsx              — Admin dashboard (Phase 2)
    review/page.tsx       — Entity review queue (Phase 2)
    ontology/page.tsx     — Ontology editor (Phase 2)
    curator/page.tsx      — KG curator UI (Phase 2)
    feedback/page.tsx     — Feedback viewer (Phase 2)

components/
  Chat/
    ChatInput.tsx         — Query input with send button + keyboard shortcut (Cmd+Enter)
    ChatMessage.tsx       — Single message bubble: user or assistant
    CitationCard.tsx      — Expandable citation with excerpt + confidence badge
    FollowUpSuggestions.tsx — Clickable follow-up question chips
    ConsultantReferrals.tsx — Referral cards with initials + engagement count

  DiscoveryTree/
    QuestionNode.tsx      — Single question with answer options
    AnswerBranch.tsx      — Answer option that reveals next question or insight
    TreeProgress.tsx      — Progress indicator through question tree

  MeetingBrief/
    BriefHeader.tsx       — Client name, use case, generation timestamp
    KeyQuestions.tsx      — Ordered list of recommended discovery questions
    PastWorkPanel.tsx     — Relevant engagement citations
    SystemLandscape.tsx   — Likely tech systems in play
    RegulatoryContext.tsx — Applicable regulations and implications
    ConsultantPanel.tsx   — Suggested consultants with referral context

  Graph/
    GraphCanvas.tsx       — D3.js or react-force-graph canvas
    NodeDetail.tsx        — Sidebar: selected node properties + related nodes
    GraphFilters.tsx      — Filter by entity type, industry, date range

  Shared/
    LoadingSkeleton.tsx   — Skeleton loaders for all async states
    ConfidenceBadge.tsx   — Colored badge: high/medium/low confidence
    Toast.tsx             — Toast notification (success, error, info)
    EmptyState.tsx        — Empty state illustrations for zero-result cases
```

## API Client Pattern

```typescript
// lib/api.ts — ALL backend calls go through here

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? 'Request failed');
  }
  return res.json() as Promise<T>;
}

export const api = {
  query: (body: QueryRequest) =>
    apiFetch<QueryResponse>('/query', { method: 'POST', body: JSON.stringify(body) }),

  getMeetingBrief: (clientId: string, useCase: string) =>
    apiFetch<MeetingBrief>(`/meeting-brief?client_id=${clientId}&use_case=${useCase}`),

  getDiscoveryTree: (useCase: string) =>
    apiFetch<DiscoveryQuestion[]>(`/discovery?use_case=${useCase}`),

  submitFeedback: (responseId: string, rating: 'up' | 'down', comment?: string) =>
    apiFetch('/feedback', { method: 'POST', body: JSON.stringify({ responseId, rating, comment }) }),

  getGraphData: (params: { type?: string; tenant_id: string }) =>
    apiFetch<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/graph/explore?${new URLSearchParams(params)}`),
};
```

## Error Handling Pattern

All API errors must be caught and shown as user-friendly toasts — never silently swallow errors:

```typescript
// lib/api.ts — structured error class
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public error_id?: string
  ) {
    super(detail);
  }
}

// In apiFetch — throw ApiError on non-ok responses
if (!res.ok) {
  const body = await res.json().catch(() => ({ detail: res.statusText }));
  throw new ApiError(res.status, body.detail ?? 'Request failed', body.error_id);
}

// In components — catch and display
try {
  const data = await api.query(request);
} catch (err) {
  if (err instanceof ApiError) {
    if (err.status >= 500) {
      showToast(`Service temporarily unavailable. (ID: ${err.error_id ?? 'unknown'})`, 'error');
    } else {
      showToast(err.detail, 'error');
    }
  } else {
    showToast('Connection error — please check your network and try again.', 'error');
  }
}
```

## Streaming Responses (SSE)

The chat interface supports streaming for long responses. Always close the EventSource on unmount:

```typescript
// In ChatPage component — use EventSource with proper cleanup
useEffect(() => {
  if (!queryId) return;

  const es = new EventSource(`${API_BASE}/query/${queryId}/stream`);

  es.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'chunk') appendChunk(data.text);
    if (data.type === 'done') es.close();
    if (data.type === 'error') {
      showToast(data.message ?? 'Stream error — please retry.', 'error');
      es.close();
    }
  };

  es.onerror = () => {
    es.close(); // prevent infinite reconnect loop
    showToast('Stream disconnected — please retry.', 'error');
  };

  return () => es.close(); // cleanup on unmount or queryId change
}, [queryId]);
```

## Common Tasks

### Add a new page
```
1. Create app/[page-name]/page.tsx with "use client" if interactive
2. Add route to Nav.tsx
3. Add API method to lib/api.ts
4. Add TypeScript types to lib/types.ts
5. Add loading skeleton and empty state
6. Never use raw fetch — always use api.* from lib/api.ts
```

### Add a new component
```
1. Create in components/[Feature]/ComponentName.tsx
2. Export named (not default) for easier tree-shaking
3. Use Tailwind only — no custom CSS files
4. Props must be fully typed — no implicit any
5. Include loading prop for skeleton state
```

### Style conventions
```
Colors:
  Primary accent:  bg-[#00A3AD] / text-[#00A3AD]  (Slalom teal exact hex — use CSS custom property)
  Define in app/globals.css:  :root { --color-slalom: #00A3AD; }
  Reference in Tailwind:      bg-[var(--color-slalom)] or extend tailwind.config.ts:
    theme: { extend: { colors: { slalom: '#00A3AD' } } } → then use bg-slalom
  Background:      bg-slate-50 (page), bg-white (card)
  Text:            text-slate-900 (primary), text-slate-500 (secondary)
  Border:          border-slate-200
  Error:           text-red-600 / bg-red-50
  Success:         text-green-600 / bg-green-50

Typography:
  Headings:        font-semibold text-slate-900
  Body:            text-sm text-slate-700
  Caption/meta:    text-xs text-slate-500

Spacing:
  Card padding:    p-4 or p-6
  Section gaps:    space-y-4 or gap-4
  Card radius:     rounded-lg
  Card shadow:     shadow-sm
```

## Files You Own

```
frontend/
  app/
    layout.tsx
    page.tsx
    chat/page.tsx
    meeting-prep/page.tsx
    discovery/page.tsx
    graph/page.tsx

  components/
    Chat/
    DiscoveryTree/
    MeetingBrief/
    Graph/
    Shared/

  lib/
    api.ts          — Typed API client (you own this)
    types.ts        — Shared TypeScript interfaces (you keep in sync with backend)

  public/
    slalom-logo.svg
```

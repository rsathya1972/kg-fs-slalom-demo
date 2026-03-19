# Slalom Field Services Intelligence Platform
## Knowledge Graph + RAG Architecture

> **Source**: Derived from `Scenario.txt` — a Slalom consulting scenario for a San Diego-based
> electric utility (subsidiary of a $60B+ holding group) seeking to replace their aging Field
> Service Management platform.

---

## Project Vision

A proprietary AI knowledge layer built on an ontology-driven knowledge graph combined with
vector embeddings and RAG, enabling any Slalom consultant to walk into a utility field services
sales meeting armed with the collective expertise of the entire practice — asking the right
discovery questions, referencing relevant past engagements, and accelerating delivery with
pre-built solution accelerators.

---

## 1. Feasibility Assessment

This problem is an excellent fit for KG + RAG. Three distinct knowledge types map directly:

| Knowledge Type | Storage |
|---|---|
| Structured relational (client → system → use case) | Knowledge Graph |
| Unstructured experiential (narratives, transcripts, Q&A) | Vector embeddings + RAG |
| Procedural/contextual (question trees, workflows, architectures) | Both, linked |

**Key advantages:**
- Graph traversal enables multi-hop reasoning ("What systems does SDG&E likely use, and who at Slalom has worked with them?")
- Ontology prevents "field service" and "FSM" from being treated as unrelated concepts
- RAG keeps LLM grounded — prevents hallucination of fake project references
- Hybrid retrieval: discovery questions need semantic match; system integration paths need graph traversal
- New project narratives automatically enrich future consultant conversations

**Limitations to plan for:**
- Ontology bootstrap requires 2–3 deep SME interviews before data flows in
- Entity disambiguation is critical: "Oracle" = ERP vs. NetSuite vs. Oracle Utilities
- Cold start: retrieval quality improves non-linearly as graph content grows
- Transcript noise degrades NER extraction accuracy

---

## 2. Conceptual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INGESTION LAYER                                   │
│                                                                          │
│  Project Docs   Meeting Transcripts   Salesforce CRM   Web/RFP Docs     │
│       └────────────────┴───────────────────┴────────────────┘           │
│                                   │                                      │
│                        Document Processor                                │
│                  (chunking, OCR, format normalization)                   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────┐
│                      EXTRACTION PIPELINE                                 │
│   NER / Relation Extraction (Claude Haiku)                               │
│   Ontology Mapper → validates against schema                             │
│   Entity Resolution → deduplication + merging                            │
└──────────────┬────────────────────────────────┬─────────────────────────┘
               │                                │
┌──────────────▼──────────┐      ┌──────────────▼──────────────────────────┐
│    KNOWLEDGE GRAPH       │      │         VECTOR STORE                    │
│  Neo4j / Neptune         │◄─────│  Embeddings of chunks, Q&A pairs,       │
│  Ontology-driven schema  │      │  project narratives, transcripts        │
│  Provenance metadata     │      │  Indexed by: use_case, industry,        │
│                          │      │  client_type, system_vendor             │
└──────────────┬───────────┘      └──────────────────┬───────────────────┘
               │                                      │
┌──────────────▼──────────────────────────────────────▼───────────────────┐
│                          RAG ORCHESTRATION LAYER                         │
│   Query Analyzer → intent classification                                 │
│   Graph Query Engine → Cypher traversal                                  │
│   Semantic Retriever → vector similarity search                          │
│   Context Assembler → merge + rank results                               │
│   Prompt Builder → structured prompt with grounded context               │
│   LLM (Claude Sonnet) → generate response                               │
│   Response Validator → hallucination check, citation injection           │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                         APPLICATION LAYER                                │
│   Consultant Copilot (chat UI)   │   Admin Console (ontology mgmt)      │
│   Meeting Prep Brief generator   │   Ingestion pipeline dashboard        │
│   Discovery Question Tree        │   Knowledge graph explorer            │
│   Deal Context API               │   Feedback loop / rating UI           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Ontology & Knowledge Graph Design

### Core Entity Types

```
Client
  ├── name, industry, sub_industry, hq_location, revenue_band
  ├── holding_group, market_cap, regulatory_environment
  └── relationships: HAS_ENGAGEMENT → Engagement
                     USES_SYSTEM → TechSystem
                     OPERATES_IN → Geography

Engagement
  ├── name, type (implementation/assessment/advisory), status
  ├── start_date, end_date, deal_value_band
  ├── functional_area, outcome_summary
  └── relationships: DELIVERED_BY → Consultant (many)
                     USES_TECHNOLOGY → TechSystem
                     ADDRESSES_USECASE → UseCase
                     HAS_ARTIFACT → Artifact

UseCase
  ├── name, description, domain, sub_domain
  ├── maturity_level, typical_entry_point
  └── relationships: REQUIRES_SYSTEM → TechSystem
                     ANSWERED_BY → DiscoveryQuestion
                     SOLVED_BY → SolutionAccelerator
                     PRECEDES / FOLLOWS → UseCase

TechSystem
  ├── vendor, product_name, version, category
  ├── (category: ERP | FSM | GIS | ADMS | Asset Mgmt | Mobile | Custom)
  └── relationships: INTEGRATES_WITH → TechSystem
                     COMPETES_WITH → TechSystem
                     REPLACES → TechSystem
                     COMMON_IN → Industry

DiscoveryQuestion
  ├── text, category (pain/technical/org/data), follow_up_trigger
  ├── likely_answers (JSON array of {answer_text, implication})
  └── relationships: RELEVANT_TO → UseCase
                     REVEALS → TechSystem
                     LEADS_TO → DiscoveryQuestion (conditional branching)

Consultant
  ├── name (anonymized), practice_area, seniority
  ├── industry_experience (array), functional_expertise (array)
  └── relationships: DELIVERED → Engagement
                     EXPERT_IN → UseCase
                     KNOWS → Consultant

Artifact
  ├── type (narrative | architecture_diagram | workflow | transcript | RFP)
  ├── file_ref, created_date, quality_rating
  └── relationships: PRODUCED_BY → Engagement
                     RELEVANT_TO → UseCase

SolutionAccelerator
  ├── name, type (data_model | connector | framework | template)
  ├── maturity, platform_target
  └── relationships: ACCELERATES → UseCase
                     BUILT_ON → TechSystem
```

### Sample Graph Query

```cypher
// Who at Slalom has done FSM work with utilities, and what did they learn?
MATCH (c:Client {industry: "Electric Utility"})
      -[:HAS_ENGAGEMENT]->(e:Engagement)
      -[:ADDRESSES_USECASE]->(uc:UseCase {domain: "Field Service Management"})
      -[:DELIVERED_BY]->(consultant:Consultant)
OPTIONAL MATCH (e)-[:HAS_ARTIFACT]->(a:Artifact)
RETURN consultant.name, e.outcome_summary, a.file_ref
ORDER BY e.end_date DESC
```

### Ontology Governance
- Versioned schema stored in Git alongside migration scripts
- Backward-compatible additions only; no breaking changes in-place
- Human-in-the-loop review for new entity/relationship types
- Quarterly ontology review cadence with practice leads as domain stewards
- Unmatched NER terms surfaced automatically when frequency > 10

---

## 4. RAG + Knowledge Graph Integration

### Intent-Based Retrieval Routing

```
User Query
    │
    ▼
Intent Classifier (Haiku)
    │
    ├── "What systems does SDG&E use?"          → Graph-first
    ├── "What questions should I ask about FSM?" → Vector-first
    ├── "Who has done utility FSM work?"         → Graph-first
    └── "What did the PG&E engagement teach us?" → Hybrid
```

**Graph-first**: client-system relationships, consultant routing, use case dependency chains, integration landscapes

**Vector-first**: discovery question recommendations, narrative retrieval, transcript search

**Hybrid** (graph-anchored semantic search):
1. Graph query: find Engagements where UseCase = FSM AND Client.industry = Utility
2. Collect artifact IDs from those engagements
3. Vector search: within that filtered set, find semantically similar chunks
4. Return graph-provenance-tagged chunks to LLM

### Context Assembly for LLM Prompt

```
System Prompt:
  You are Slalom's Field Services expert assistant. Answer using ONLY the provided context.
  Cite sources by [Engagement ID] or [Document ID]. Never fabricate client names, metrics, or outcomes.

Context Block:
  [GRAPH FACTS]
  - SDG&E is a subsidiary of Sempra Energy (utility, San Diego)
  - SDG&E currently uses SAP PM for asset management (source: Salesforce CRM)
  - Slalom delivered Wildfire Management App for SDG&E in 2023 (Engagement: ENG-0482)
  - 4 Slalom consultants have utility FSM experience: [names]

  [RETRIEVED DOCUMENTS - ranked by relevance]
  [DOC-1, score: 0.94] PG&E FSM Replacement Assessment (2024): ...
  [DOC-2, score: 0.89] Discovery Q&A Bank - Utility FSM: ...
  [DOC-3, score: 0.81] Architecture Framework - FSM + GIS Integration: ...

User Query: [consultant's question]
```

---

## 5. Detailed Data Flow

### Ingestion Flow

```
1. Document arrives (PDF, DOCX, MP3 transcript, Salesforce export)
2. Document Processor
   ├── Format detection + conversion to plain text
   ├── Chunking:
   │     • Narrative docs: 512-token sliding window, 10% overlap
   │     • Q&A banks: question-answer pair as atomic unit
   │     • Transcripts: speaker-turn segments
   └── Metadata tagging: {source_type, engagement_id, date, author}
3. NER + Relation Extraction (Claude Haiku batch)
   ├── Extract: Client names, Vendors, Consultants, Use cases, Metrics, Dates
   └── Output: structured triples + confidence scores
4. Entity Resolution
   ├── Fuzzy match against existing KG nodes (Jaro-Winkler + embedding similarity)
   ├── Human review queue for confidence < 0.80
   └── Create new node if no match + flag for ontology review
5. Knowledge Graph Update (transactional)
   ├── Upsert entities + properties
   ├── Create/update relationships
   └── Attach provenance: {document_id, extraction_confidence, extracted_at}
6. Embedding Generation
   ├── Chunk → embedding model
   ├── Store vector + metadata in vector DB
   └── Link vector record to KG node via shared entity IDs
```

### Query Flow

```
7.  Consultant submits query via chat UI
8.  Query Analyzer (Haiku): classify intent, extract entities, select retrieval strategy
9.  Parallel Retrieval:
    ├── Graph Query: Cypher traversal for structured facts
    └── Vector Search: top-K semantic neighbors, filtered by entity tags
10. Context Assembly:
    ├── Deduplicate overlapping chunks
    ├── Re-rank: graph relevance × semantic score × recency
    └── Trim to context window (~60k tokens for Sonnet)
11. LLM Generation (Claude Sonnet):
    └── Structured output: {answer, citations[], suggested_follow_ups[], consultant_referrals[]}
12. Post-processing:
    ├── Hallucination check: verify all entity names appear in context
    ├── Citation resolution → clickable document links
    └── Feedback capture → feeds reranker fine-tuning
```

---

## 6. Technology Recommendations

| Component | Primary | Alternative | Rationale |
|---|---|---|---|
| Knowledge Graph DB | Neo4j AuraDB | Amazon Neptune | Cypher readability; managed ops; Neptune if AWS-locked |
| Vector Store | OpenSearch Serverless (k-NN) | Pinecone / pgvector | OpenSearch if AWS; Pinecone simplest ops |
| Embedding Model | text-embedding-3-large | Amazon Titan Embeddings | Best benchmarks; swap for AWS data residency |
| LLM - Generation | Claude Sonnet 4.6 | GPT-4o | 200k context window critical |
| LLM - Extraction | Claude Haiku 4.5 | GPT-4o-mini | Cost-effective for batch extraction |
| Orchestration | LangGraph | LlamaIndex | LangGraph for stateful agentic flows |
| Ingestion Pipeline | Apache Airflow (MWAA) | Prefect | Airflow for enterprise scale |
| API Layer | FastAPI | | Async, OpenAPI docs, Python-native |
| Frontend | Next.js 15 (App Router) | | Consistent with Slalom tooling |
| Auth | Okta / Azure AD (SAML/OIDC) | | Enterprise SSO requirement |
| Ontology Management | Protégé + custom Git registry | | Industry standard OWL editor |

### Neo4j vs Neptune
- **Neo4j**: Cypher is intuitive, excellent tooling (Bloom for visualization), AuraDB removes server management. **Default choice.**
- **Neptune**: Native AWS integration (IAM, VPC, CloudWatch), supports Gremlin + SPARQL. Choose if data must not leave AWS.

---

## 7. Scalability and Multi-Tenant Considerations

### Multi-Tenant Design (Practice-level isolation)

```
Option A (MVP): Single Neo4j database, tenant_id on every node
  - Simple, lower cost
  - Enforce tenant_id filter at ORM layer; never expose raw Cypher to app
  - Clearance levels: {public_knowledge | internal_project | client_confidential}

Option B (regulated data): Separate Neo4j database per practice
  - True isolation; higher cost
  - Required if NDA'd client data must be strictly partitioned

Vector Store:
  - Separate index/collection per practice
  - metadata filter on tenant_id as secondary guard

Application Layer:
  - JWT claims: {user_id, practice_id, clearance_level}
  - All queries auto-scoped to practice_id
```

### Scalability

| Concern | Approach |
|---|---|
| Graph size | Neo4j handles 100M+ nodes; shard by domain at 500M+ |
| Embedding volume | OpenSearch k-NN scales horizontally; pre-filter by tenant reduces search space |
| Ingestion throughput | Airflow DAGs with parallel task groups; Claude batch API |
| Query latency | Redis cache for frequent graph patterns (5-min TTL) |
| LLM cost | Haiku for classification + extraction; Sonnet for generation only; token budget guardrails |

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Hallucination of client facts | Critical | All entity names in response must appear verbatim in retrieved context. Automated validator rejects non-compliant responses. |
| Ontology drift | High | Versioned schema in Git; breaking changes require practice lead approval; quarterly audits |
| Data quality from transcripts | High | Whisper-based transcription + speaker diarization; human review queue for low-confidence segments |
| PII / confidential data leakage | High | NER-based PII detection at ingestion; client names anonymized in cross-tenant contexts |
| Entity disambiguation failures | Medium | Confidence threshold gates (< 0.80 → human review); entity aliases table |
| Retrieval quality degradation | Medium | RAGAS metrics on golden Q&A test set; alerts if precision drops > 10% |
| Cold start / sparse graph | Medium | Seed with 20-30 curated engagements before launch |
| Consultant trust / adoption | Medium | Always show citations; confidence level indicator on UI |
| LLM API cost | Low-Medium | Token budget per query; caching; usage dashboard |

---

## 9. Phased Implementation Plan

### Phase 1: MVP (Weeks 1–10)

**Goal:** Prove value with Utilities Field Services practice. Working demo for sales meeting prep.

- Manual ingestion of 20–30 curated documents (narratives, Q&A banks, architecture templates)
- Neo4j graph with core ontology: Client, Engagement, UseCase, TechSystem, DiscoveryQuestion, Consultant
- OpenSearch vector store with filtered search
- Single RAG pipeline: query → hybrid retrieval → Claude Sonnet → grounded response
- Simple Next.js chat UI with citation display
- Single tenant (internal demo only)

**Demo capabilities:**
- "What questions should I ask an electric utility about FSM?"
- Discovery question tree for utility FSM
- Consultant referral routing ("Who at Slalom has done this?")
- Graph explorer view (Neo4j Bloom or D3.js)

**Team:** 1 ML/AI engineer, 1 backend engineer, 1 domain SME (part-time), 1 frontend engineer (part-time)

---

### Phase 2: Enhancement (Weeks 11–22)

**Goal:** Production-ready for 3 practices. Automated ingestion.

- Automated ingestion pipeline (Airflow DAGs) + Salesforce CRM sync
- NER + relation extraction pipeline (Claude Haiku batch)
- Entity resolution with human review queue
- Multi-tenant isolation (practice-level)
- Okta SSO integration
- Feedback loop: thumbs up/down → reranker fine-tuning data
- Solution Accelerator nodes linked to use cases
- Meeting prep brief generator (structured output)
- Admin console: ontology management, ingestion dashboard, KG curator UI

**Success metric:** Retrieval precision > 0.80 on golden test set across 3 practices

---

### Phase 3: Advanced Intelligence (Weeks 23–36)

**Goal:** Agentic workflows, real-time enrichment, proactive intelligence.

- **Agentic meeting prep**: calendar invite + CRM opportunity ID → auto-generate full pre-meeting brief
- **LangGraph multi-agent**: Researcher → Analyst → Writer agents
- **Real-time KG enrichment**: Salesforce trigger → auto-ingest new closed deals
- **Use case chain reasoning**: "What adjacent use cases typically follow FSM replacement at a utility?"
- **GraphRAG** (Microsoft pattern): community detection → cluster summaries → additional retrieval context
- **OWL inference**: subclass/equivalence relationships (e.g., "Oracle Utilities Work Management" is-a "FSM Platform")
- **External enrichment**: FERC/CPUC regulatory filings as context nodes

**Success metric:** Sub-60-second meeting prep brief from calendar invite; measurable deal win rate lift

---

## Running the App

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
OPENSEARCH_ENDPOINT=https://...
DATABASE_URL=sqlite:///./kg_slalom.db
UPLOAD_DIR=./storage/uploads
```

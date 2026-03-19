# Phase 1 Persona Demo Guide
## Slalom Field Services Intelligence Platform — Utility FSM Knowledge Graph

> **Scope**: Phase 1 (Energy & Utility sector only). All query examples, expected responses,
> and entity references are grounded in the Phase 1b structured seed data and Phase 1c
> discovery Q&A bank. This guide serves as a demo script, validation reference, and
> onboarding resource for new consultants.

**Date**: 2026-03-19
**Phase**: 1b complete (structured data ingested), 1c–1e in progress

---

## How to Run This Demo

```bash
# 1. Start the local stack
docker-compose up -d neo4j opensearch

# 2. Start the backend API
cd backend && uvicorn main:app --reload --port 8000

# 3. Start the frontend
cd frontend && npm run dev
# Open http://localhost:3000/chat
```

**Prerequisites**: Neo4j seeded via `python -m ingestion.batch_loader`, OpenSearch indexed
with Phase 1c documents.

---

## Persona Index

| # | Persona | Role | Primary Need | Key Capabilities Exercised |
|---|---------|------|--------------|---------------------------|
| 1 | [The New Hire](#persona-1--the-new-hire) | Junior Consultant | Meeting prep | Phase 1c Q&A bank RAG, Phase 1b graph lookup |
| 2 | [The Deal Closer](#persona-2--the-deal-closer) | Practice Lead | Team staffing + accelerators | Phase 1b graph traversal (Consultant, SolutionAccelerator) |
| 3 | [The Discovery Expert](#persona-3--the-discovery-expert) | Senior Consultant | Deep discovery | Phase 1c semantic retrieval, Phase 1b use case chain |
| 4 | [The Architect](#persona-4--the-architect) | Integration Manager | Integration pattern guidance | Phase 1b integration patterns, Phase 1c narrative retrieval |
| 5 | [The Executive Sponsor](#persona-5--the-executive-sponsor) | VP, Platform Initiative | Full platform demo | All Phase 1 capabilities — canonical 3-query demo |

---

---

## Persona 1 — "The New Hire"

### Profile

| Field | Value |
|-------|-------|
| **Name** | Jordan (fictional) |
| **Title** | Consultant |
| **Utility Experience** | 0 years |
| **Location** | Los Angeles, CA |
| **Context** | Just staffed on a new utility FSM opportunity at a large California IOU. First meeting is tomorrow morning with the SVP of Field Operations. No prior utility industry experience. |

**Setup**: Jordan needs to walk into the meeting sounding credible — knowing what questions to
ask, what systems this client likely uses, and what the common pain points are for utilities
their size. Without the platform, Jordan would spend 3+ hours reading through PDFs and
hoping to find the right context.

---

### Query 1

**Copy this into the chat UI:**

```
I have a meeting tomorrow with the SVP of Field Operations at a large California IOU
about replacing their FSM platform. What are the most important questions I should ask?
```

**Expected response shape:**

```json
{
  "answer": "For a large California IOU evaluating FSM replacement, start with these discovery questions:\n\n1. **What application generates and manages your work orders today?** [dq-001]\n   Listen for: SAP PM (ERP-embedded, scheduling gap likely), IBM Maximo (EAM-centric, mobile gap), or Oracle Utilities Work Management (utility-native). If they say spreadsheets, that's a greenfield opportunity.\n\n2. **How do you currently schedule and dispatch field crews?** [dq-002]\n   Listen for: manual dispatcher assignment (→ major scheduling optimization opportunity) vs. automated engine (→ focus on override rate and GIS depth).\n\n3. **What mobile application do your field technicians use?** [dq-003]\n   Listen for: radio/phone only (→ no mobile FSM — strong ROI case), legacy Windows rugged device (→ EOL risk), or modern FSM mobile app.\n\n4. **How is your FSM integrated with your GIS system?** [dq-004]\n   California IOUs typically run ArcGIS. If integration is absent or partial, that's a top-5 gap.\n\n5. **How are outage response work orders created during storms?** [dq-010]\n   CPUC closely monitors SAIDI/SAIFI for California IOUs. Manual storm dispatch is a regulatory liability.\n\n**California-specific context**: CPUC GO 165 mandates inspection cycle compliance reporting. Ask how inspection records are tracked and whether FSM generates the compliance data.",
  "citations": [
    {"id": "dq-001", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "What application generates and manages your work orders today?"},
    {"id": "dq-002", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How do you currently schedule and dispatch field crews to work orders?"},
    {"id": "dq-003", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "What mobile application do your field technicians use today?"},
    {"id": "dq-004", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How is your FSM integrated with your GIS system today?"},
    {"id": "dq-010", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How are outage response work orders created and routed during a storm event?"}
  ],
  "suggested_follow_ups": [
    "What is the difference between SAP PM and Salesforce Field Service for utilities?",
    "What are SAIDI and SAIFI, and how does FSM affect them?",
    "What are CPUC GO 165 inspection requirements and how does FSM support them?"
  ],
  "consultant_referrals": [
    {"name": "A. Ramirez", "email": "a.ramirez@slalom.com", "specializations": ["FSM", "SAP PM", "Utility Strategy"], "note": "Director, 16 years utility experience, Los Angeles — ideal for this meeting"},
    {"name": "B. Nguyen", "email": "b.nguyen@slalom.com", "specializations": ["FSM", "Salesforce FSM", "Storm Response"], "note": "Director, 14 years, Houston — NERC CIP and storm response expertise"}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1c` — Semantic retrieval over discovery Q&A bank (`discovery_qa_utility_fsm.json`)
- `Phase 1d` — Hybrid retrieval + context assembly + Claude Sonnet generation
- `Phase 1d` — Consultant referral cards via graph traversal (Consultant node, specializations filter)

---

### Query 2 (follow-up)

**Copy this into the chat UI:**

```
What systems do large California IOUs typically use for work orders today?
```

**Expected response shape:**

```json
{
  "answer": "Large California IOUs (like PG&E, SCE, and SDG&E) most commonly use one of these platforms for work order management:\n\n**SAP PM (Plant Maintenance)** [sys-001]\nMost prevalent in large IOUs that already run SAP ERP for financials. Important caveat: SAP PM is ERP-embedded work order management — it is NOT a full FSM. It lacks mobile-first dispatch optimization, real-time GIS routing, and modern mobile field worker apps. This is the most common gap Slalom encounters.\n\n**Oracle Utilities Work Management** [sys-003]\nUtility-native WM system (formerly SPL WorkManager). Manages trouble orders, switching orders, and SAIDI/SAIFI reporting. More utility-specific than SAP PM but often running on-premise with aging integrations.\n\n**IBM Maximo Application Suite** [sys-013]\nEAM-centric platform — strong for asset lifecycle but historically weak on mobile-first dispatch optimization. Many utilities are evaluating upgrade from on-premise Maximo 7.x to MAS (SaaS).\n\n**Common misconception to correct in the meeting**: Clients often say they have 'SAP FSM' — there is no such product. SAP PM is ERP work order management, not field service management. The scheduling and mobile gap is almost always present.",
  "citations": [
    {"id": "sys-001", "source": "data/seed/tech_systems_utility.json", "excerpt": "SAP PM is ERP-embedded WO management, not a full FSM. It lacks mobile-first dispatch optimization..."},
    {"id": "sys-003", "source": "data/seed/tech_systems_utility.json", "excerpt": "Oracle Utilities Work Management — purpose-built WM for utilities, formerly SPL WorkManager"},
    {"id": "sys-013", "source": "data/seed/tech_systems_utility.json", "excerpt": "IBM Maximo — EAM, not a full FSM. Many utilities are evaluating upgrade to MAS."}
  ],
  "suggested_follow_ups": [
    "What is Salesforce Field Service and is it a good fit for a large IOU?",
    "How does GIS integrate with FSM for a California IOU?"
  ],
  "consultant_referrals": []
}
```

**Phase 1 capabilities exercised:**
- `Phase 1b` — TechSystem graph lookup (category, `common_in_utility_types: IOU`, misconception field)
- `Phase 1d` — Graph-first retrieval routing (structured system landscape query)

---

---

## Persona 2 — "The Deal Closer"

### Profile

| Field | Value |
|-------|-------|
| **Name** | Marcus (fictional) |
| **Title** | Practice Lead, Energy & Utilities |
| **Utility Experience** | 15+ years |
| **Location** | Houston, TX |
| **Context** | Just won an FSM + ArcGIS Utility Network modernization RFP at a large Midwest IOU (cli-015 profile in graph). Needs to staff a team and identify reusable accelerators within 48 hours for the kickoff proposal. |

**Setup**: Marcus knows the domain deeply but needs the platform to surface staffing
recommendations and accelerators faster than searching through Salesforce CRM and
SharePoint manually.

---

### Query 1

**Copy this into the chat UI:**

```
We just won an FSM + ArcGIS Utility Network modernization engagement at a large Midwest IOU.
Which Slalom consultants have the most relevant experience to staff this?
```

**Expected response shape:**

```json
{
  "answer": "For an FSM + ArcGIS Utility Network modernization at a large IOU, here are the strongest matches from our consultant roster:\n\n**A. Ramirez** — Director, 16 years utility experience (Los Angeles)\nSpecializations: FSM, SAP PM, Utility Strategy, OT/IT Convergence\nRelevant past work: FSM Platform Assessment for large IOU (eng-001) — evaluated 6 FSM vendors, recommended Salesforce FSM + MuleSoft to SAP. Strong as engagement director.\n\n**D. Okafor** — Manager, 9 years (San Francisco)\nSpecializations: Salesforce FSM, IBM Maximo, Mobile Field Worker, Change Management\nRelevant past work: Salesforce FSM Implementation with mobile rollout to 1,400 field technicians (eng-002). Strong as FSM implementation lead.\n\n**F. Torres** — Manager, 10 years (Portland)\nSpecializations: GIS, Esri ArcGIS, ArcGIS Utility Network, Smallworld Migration\nRelevant past work: ArcGIS Utility Network Migration — migrated 2.4M asset records from Smallworld (eng-010). Natural GIS workstream lead.\n\n**G. Andersen** — Manager, 8 years (Dallas)\nSpecializations: MuleSoft, SAP Integration Suite, FSM Integration, OMS/FSM\nRelevant past work: eng-003 (GIS + Work Order Integration Architecture using SAP Integration Suite). Integration architecture role.\n\n**K. Brown** — Senior Consultant, 6 years (Phoenix)\nSpecializations: GIS, Esri ArcGIS, FSM Integration, Work Order Geolocation\nGood for GIS integration delivery support under F. Torres.",
  "citations": [
    {"id": "con-001", "source": "data/seed/consultants_utility.json", "excerpt": "A. Ramirez — Director, FSM, SAP PM, Utility Strategy"},
    {"id": "con-004", "source": "data/seed/consultants_utility.json", "excerpt": "D. Okafor — Manager, Salesforce FSM, Mobile Field Worker"},
    {"id": "con-006", "source": "data/seed/consultants_utility.json", "excerpt": "F. Torres — Manager, GIS, Esri ArcGIS, ArcGIS Utility Network"},
    {"id": "con-007", "source": "data/seed/consultants_utility.json", "excerpt": "G. Andersen — Manager, MuleSoft, SAP Integration Suite"},
    {"id": "eng-001", "source": "data/seed/engagements_utility.json", "excerpt": "FSM Platform Assessment — SAP PM Replacement Evaluation — recommended Salesforce FSM with MuleSoft"},
    {"id": "eng-002", "source": "data/seed/engagements_utility.json", "excerpt": "Salesforce FSM Implementation — 1,400 field technicians, 94% mobile adoption in 90 days"},
    {"id": "eng-010", "source": "data/seed/engagements_utility.json", "excerpt": "ArcGIS Utility Network Migration — 2.4M asset records from Smallworld GIS"}
  ],
  "suggested_follow_ups": [
    "What solution accelerators do we have for SAP PM to Salesforce FSM migration?",
    "Who has experience managing union field workforce change management at utilities?"
  ],
  "consultant_referrals": [
    {"name": "A. Ramirez", "email": "a.ramirez@slalom.com", "specializations": ["FSM", "SAP PM", "Utility Strategy"]},
    {"name": "D. Okafor", "email": "d.okafor@slalom.com", "specializations": ["Salesforce FSM", "IBM Maximo", "Mobile Field Worker"]},
    {"name": "F. Torres", "email": "f.torres@slalom.com", "specializations": ["GIS", "Esri ArcGIS", "ArcGIS Utility Network"]},
    {"name": "G. Andersen", "email": "g.andersen@slalom.com", "specializations": ["MuleSoft", "SAP Integration Suite", "FSM Integration"]}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1b` — Graph traversal: Consultant → specializations filter → Engagement → outcome_summary
- `Phase 1d` — Cypher query routing (structured staffing query, graph-first)

---

### Query 2 (follow-up)

**Copy this into the chat UI:**

```
What solution accelerators do we have that would apply to a SAP PM to Salesforce FSM migration?
```

**Expected response shape:**

```json
{
  "answer": "Three accelerators are directly relevant to a SAP PM → Salesforce FSM migration:\n\n**sa-002 — SAP PM to Salesforce FSM Migration Playbook**\nEnd-to-end migration playbook covering: data migration mapping (PM order types → Salesforce work order types), custom extension inventory, union change management strategy, and 12-week cutover checklist.\nApplies to: Work Order Lifecycle, Mobile Field Worker use cases.\nArtifact: accelerators/sap-pm-to-salesforce-fsm-playbook/\n\n**sa-001 — Utility FSM Discovery Assessment Framework**\nStructured 4-week assessment framework with 47-requirement scoring matrix, vendor demo script, TCO model template, and stakeholder interview guide.\nBest for: pre-migration vendor assessment phase.\nArtifact: accelerators/fsm-discovery-assessment-framework/\n\n**sa-003 — Esri ArcGIS + FSM Integration Reference Architecture**\nReference architecture and integration patterns for connecting ArcGIS Utility Network with FSM platforms. Includes MuleSoft and SAP Integration Suite middleware patterns.\nBest for: the GIS integration workstream of this engagement.\nArtifact: accelerators/arcgis-fsm-integration-reference-arch/",
  "citations": [
    {"id": "sa-002", "source": "data/seed/solution_accelerators.json", "excerpt": "SAP PM to Salesforce FSM Migration Playbook — PM order types → SF work order types, 12-week cutover checklist"},
    {"id": "sa-001", "source": "data/seed/solution_accelerators.json", "excerpt": "Utility FSM Discovery Assessment Framework — 47-requirement scoring matrix"},
    {"id": "sa-003", "source": "data/seed/solution_accelerators.json", "excerpt": "Esri ArcGIS + FSM Integration Reference Architecture — MuleSoft and SAP Integration Suite patterns"}
  ],
  "suggested_follow_ups": [
    "Is there a change management accelerator for union field workforces?",
    "What does the SAP PM data migration mapping look like for work order types?"
  ],
  "consultant_referrals": []
}
```

**Phase 1 capabilities exercised:**
- `Phase 1b` — SolutionAccelerator graph nodes (ACCELERATES → UseCase relationships)
- `Phase 1d` — Graph-first query routing (structured accelerator lookup)

---

---

## Persona 3 — "The Discovery Expert"

### Profile

| Field | Value |
|-------|-------|
| **Name** | Priya (fictional) |
| **Title** | Senior Consultant, Salesforce FSM |
| **Utility Experience** | 7 years |
| **Location** | San Francisco, CA |
| **Context** | On a live discovery call with a rural electric co-op. The SVP of Operations just said: "We dispatch by phone and spreadsheet. We've never had a real work order system." Priya needs follow-up questions and context to probe deeper — live, during the call. |

**Setup**: The platform is open in a second window during the call. Priya types a fast
natural-language query and gets structured follow-up questions with implications in seconds.

---

### Query 1

**Copy this into the chat UI:**

```
A rural electric co-op tells me they dispatch field crews by phone and spreadsheet with
no FSM system at all. What follow-up questions should I ask, and what does this typically
mean for their digital maturity?
```

**Expected response shape:**

```json
{
  "answer": "This is a greenfield digital maturity signal — strong ROI opportunity. Here's how to probe deeper:\n\n**Immediate follow-up questions:**\n\n1. **How many work orders do you create per day, and how many field crews are you managing?** [dq-002]\n   Scale drives urgency. Even 50 WOs/day with manual dispatch has measurable operational waste.\n\n2. **What mobile application do your field technicians use today?** [dq-003]\n   If the answer is 'they call dispatch,' you have zero mobile FSM coverage — strong ROI case for mobile deployment with offline capability (critical for rural territories).\n\n3. **Do your field technicians work in areas where cellular connectivity is unreliable?** [dq-005]\n   Rural co-ops almost always have connectivity dead zones. Offline capability is a must-have, not a nice-to-have.\n\n4. **How do you manage third-party contractor crews?** [dq-006]\n   Co-ops rely heavily on contractor crews for capital work. 'Phone and spreadsheet' for contractors = zero billing reconciliation accuracy and storm surge risk.\n\n5. **How are outage response work orders created during a storm?** [dq-010]\n   For a greenfield co-op, the answer is usually 'dispatchers create them manually from customer calls.' This directly inflates SAIDI and is a strong regulatory driver.\n\n**Digital maturity implication**: This co-op is at Level 1 (reactive, manual) on the utility FSM maturity scale. The entry point use cases are Work Order Lifecycle Management and Mobile Field Worker. Don't pitch advanced scheduling optimization or predictive maintenance yet — meet them where they are.",
  "citations": [
    {"id": "dq-002", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How do you currently schedule and dispatch field crews to work orders?"},
    {"id": "dq-003", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "What mobile application do your field technicians use today?"},
    {"id": "dq-005", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "Do your field technicians work in areas where cellular connectivity is unreliable?"},
    {"id": "dq-006", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How do you manage third-party contractor crews in your field service workflow today?"},
    {"id": "dq-010", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How are outage response work orders created and routed during a storm event?"}
  ],
  "suggested_follow_ups": [
    "What does a realistic FSM implementation roadmap look like for a co-op with no existing FSM platform?",
    "What are the offline mobile requirements for rural utility field crews?",
    "What has Slalom done with rural electric co-ops in the past?"
  ],
  "consultant_referrals": [
    {"name": "D. Okafor", "email": "d.okafor@slalom.com", "specializations": ["Salesforce FSM", "Mobile Field Worker", "Change Management"]}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1c` — Semantic retrieval over discovery Q&A bank (ranked by greenfield co-op context)
- `Phase 1d` — Hybrid retrieval + context assembly

---

### Query 2 (follow-up)

**Copy this into the chat UI:**

```
What does a realistic FSM implementation roadmap look like for a co-op with no existing
FSM platform, and what past Slalom work is relevant?
```

**Expected response shape:**

```json
{
  "answer": "For a greenfield co-op, a realistic 3-phase roadmap follows this use case sequence:\n\n**Phase 1 — Foundation (Months 1–6): Work Order Lifecycle + Mobile Field Worker**\n- Deploy core WO management with mobile app (offline-capable)\n- Replace phone dispatch with structured digital work order creation\n- Target: eliminate paper work orders entirely\n- Reference: Slalom deployed ServiceMax mobile app to 45 technicians at a rural co-op (eng-016), integrated with Milsoft OMS, full offline capability tested in rural low-connectivity zones\n\n**Phase 2 — Optimization (Months 6–12): Crew Scheduling + Outage Response**\n- Add scheduling optimization once WO baseline is stable\n- Integrate with OMS (Milsoft for co-ops) for automated outage trouble order creation\n- Target: reduce SAIDI through faster dispatch-to-restoration\n\n**Phase 3 — Intelligence (Year 2+): GIS Integration + AMI (if applicable)**\n- Integrate with GIS for asset location context on mobile\n- If AMI is deployed or planned, connect meter outage pings to OMS→FSM pipeline\n\n**Relevant accelerator**: sa-004 (Mobile Field Worker Adoption Toolkit) — change management playbook for union/co-op field workforces, 90-day adoption sprint plan, Android tablet support.\n\n**Key risk for co-ops**: Union or workforce agreements may restrict device policy. Engage HR and field supervisors early. Slalom used this approach in eng-014 (union change management, 88% mobile adoption in 90 days).",
  "citations": [
    {"id": "eng-016", "source": "data/seed/engagements_utility.json", "excerpt": "Rural Co-op Mobile Field Worker Program — 45 technicians, ServiceMax, Android tablets, offline capability, eliminated paper WOs"},
    {"id": "sa-004", "source": "data/seed/solution_accelerators.json", "excerpt": "Mobile Field Worker Adoption Toolkit — union engagement playbook, 90-day adoption sprint"},
    {"id": "eng-014", "source": "data/seed/engagements_utility.json", "excerpt": "Mobile Field Application Adoption — 900-person union workforce, 88% active daily usage in 90 days"}
  ],
  "suggested_follow_ups": [
    "What Milsoft OMS integration patterns exist for co-op FSM deployments?",
    "How do we handle offline GIS data for rural field crews?"
  ],
  "consultant_referrals": [
    {"name": "D. Okafor", "email": "d.okafor@slalom.com", "specializations": ["Salesforce FSM", "Mobile Field Worker", "Change Management"]},
    {"name": "N. Davis", "email": "n.davis@slalom.com", "specializations": ["Change Management", "Mobile Adoption", "Union Engagement", "Training"]}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1b` — Use case taxonomy chain (work_order_lifecycle → mobile_field_worker → crew_scheduling)
- `Phase 1b` — Past engagement lookup (eng-016: co-op + ServiceMax + Milsoft)
- `Phase 1b` — SolutionAccelerator lookup (sa-004: Mobile Field Worker Adoption Toolkit)
- `Phase 1d` — Hybrid retrieval + context assembly

---

---

## Persona 4 — "The Architect"

### Profile

| Field | Value |
|-------|-------|
| **Name** | Sam (fictional) |
| **Title** | Manager, Integration Architecture |
| **Utility Experience** | 8 years |
| **Location** | Dallas, TX |
| **Context** | A client's CTO just asked: "Do we really have to rip out SAP PM? Can't we just add a mobile layer on top?" Sam needs to explain the integration architecture options quickly — with credibility and without making it sound like Slalom is pushing a rip-and-replace. |

**Setup**: Sam pulls up the platform during the whiteboarding session to retrieve specific
integration patterns and past engagement evidence.

---

### Query 1

**Copy this into the chat UI:**

```
A utility wants to keep SAP PM as their system of record but add a modern mobile FSM
layer on top. What integration patterns and middleware options exist for this architecture?
```

**Expected response shape:**

```json
{
  "answer": "The 'SAP PM + modern FSM mobile layer' pattern is well-established and Slalom has delivered it. Here's the architecture:\n\n**The Pattern: SAP PM as SOR + Salesforce FSM as Scheduling/Mobile Layer** [int-007]\nWork orders are created in SAP PM (the system of record for asset history and maintenance data). SAP PM work orders flow to Salesforce Field Service for scheduling optimization and mobile dispatch. Field completion data writes back to SAP PM.\n\n**Middleware options:**\n- **MuleSoft Anypoint Platform** — Most common choice for this integration. Acts as the API hub connecting SAP PM, Salesforce FSM, ArcGIS, and any OMS. Reduces point-to-point integration sprawl [int-011].\n- **SAP Integration Suite** — Preferred if the client wants to keep integration within the SAP ecosystem. Lower licensing friction for SAP customers [sys-024].\n\n**Key integration points to design:**\n1. WO trigger: SAP PM maintenance notification → Salesforce work order creation\n2. Scheduling: Salesforce dispatches to crew mobile app (offline-capable)\n3. GIS context: ArcGIS provides asset location/network data to Salesforce mobile app [int-001, int-003]\n4. Completion write-back: Salesforce completion event → SAP PM actual hours + material consumption\n\n**Past Slalom reference**: eng-001 — FSM Platform Assessment for large IOU. Outcome: recommended Salesforce FSM with MuleSoft integration to SAP PM, identified $12M 5-year TCO savings over maintaining SAP PM extensions alone.",
  "citations": [
    {"id": "int-007", "source": "data/seed/integration_patterns.json", "excerpt": "Salesforce FSM ↔ SAP PM — Salesforce used as scheduling/mobile layer; SAP PM remains SOR"},
    {"id": "int-001", "source": "data/seed/integration_patterns.json", "excerpt": "SAP PM ↔ ArcGIS — SAP PM work orders geo-coded via ArcGIS for field crew routing"},
    {"id": "int-003", "source": "data/seed/integration_patterns.json", "excerpt": "ArcGIS ↔ Salesforce FSM — ArcGIS pulls asset location + network data to mobile app; completion writes back to GIS"},
    {"id": "int-011", "source": "data/seed/integration_patterns.json", "excerpt": "Salesforce FSM ↔ MuleSoft — MuleSoft as integration hub connecting FSM to OMS, GIS, ERP, AMI"},
    {"id": "eng-001", "source": "data/seed/engagements_utility.json", "excerpt": "FSM Assessment — recommended Salesforce FSM with MuleSoft to SAP. $12M 5-year TCO savings."}
  ],
  "suggested_follow_ups": [
    "What are the risks of running SAP PM and Salesforce FSM in parallel at a utility?",
    "How does ArcGIS fit into this integration architecture for an IOU?"
  ],
  "consultant_referrals": [
    {"name": "G. Andersen", "email": "g.andersen@slalom.com", "specializations": ["MuleSoft", "SAP Integration Suite", "FSM Integration", "OMS/FSM"]},
    {"name": "A. Ramirez", "email": "a.ramirez@slalom.com", "specializations": ["FSM", "SAP PM", "Utility Strategy"]}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1b` — Integration patterns graph (int-007, int-001, int-003, int-011)
- `Phase 1b` — TechSystem nodes (MuleSoft, SAP Integration Suite)
- `Phase 1b` — Past engagement lookup (eng-001 outcome)
- `Phase 1d` — Hybrid retrieval (graph-first for patterns)

---

### Query 2 (follow-up)

**Copy this into the chat UI:**

```
What are the risks of running SAP PM and a separate FSM in parallel at a utility?
```

**Expected response shape:**

```json
{
  "answer": "Running SAP PM and a parallel FSM is viable but introduces known risks:\n\n**1. Data synchronization failures**\nWork order status must stay in sync between SAP PM and Salesforce. If the middleware (MuleSoft/SAP IS) fails, crews see stale WO status on mobile and SAP PM completion records fall behind. Design requires idempotent sync with dead-letter queue.\n\n**2. SAP PM extension debt accumulates**\nUtilities running SAP PM often have hundreds of custom ABAP extensions. Those extensions must either be replicated in the new FSM or wrapped by middleware. Migration playbook (sa-002) inventories these before cutover.\n\n**3. Dual licensing cost window**\nParallel operation requires licensing both SAP PM users AND Salesforce FSM licenses during transition. Typically 6–18 months depending on cutover strategy. This cost must be captured in the TCO model.\n\n**4. Crew confusion during dual-system period**\nField technicians using mobile app may create completion records in Salesforce while supervisors are approving in SAP PM. Clear RACI for system of record at each phase of the cutover is critical.\n\n**5. GIS write-back contention**\nIf ArcGIS receives completion data from both SAP PM (legacy) and Salesforce FSM (new) during parallel operation, GIS asset records can become inconsistent.\n\n**Mitigation**: Slalom's SAP PM → Salesforce FSM Migration Playbook (sa-002) includes a 12-week cutover checklist specifically designed to manage this parallel period.",
  "citations": [
    {"id": "sa-002", "source": "data/seed/solution_accelerators.json", "excerpt": "SAP PM to Salesforce FSM Migration Playbook — custom extension inventory, 12-week cutover checklist"},
    {"id": "int-007", "source": "data/seed/integration_patterns.json", "excerpt": "Salesforce FSM ↔ SAP PM bidirectional integration — WOs created in SAP PM flow to Salesforce; completion records flow back"}
  ],
  "suggested_follow_ups": [
    "What does the 12-week cutover checklist in the migration playbook cover?",
    "How do we estimate SAP PM extension inventory for a large IOU?"
  ],
  "consultant_referrals": [
    {"name": "A. Ramirez", "email": "a.ramirez@slalom.com", "specializations": ["FSM", "SAP PM", "Utility Strategy"]}
  ]
}
```

**Phase 1 capabilities exercised:**
- `Phase 1c` — Narrative retrieval (migration risk patterns from project documents)
- `Phase 1b` — SolutionAccelerator reference (sa-002)
- `Phase 1d` — Hybrid retrieval

---

---

## Persona 5 — "The Executive Sponsor"

### Profile

| Field | Value |
|-------|-------|
| **Name** | Alex (fictional) |
| **Title** | VP, Field Services Practice |
| **Utility Experience** | 20+ years |
| **Context** | Presenting the Phase 1 platform to Slalom practice leadership and a potential client. Runs the three canonical demo queries from the CLAUDE.md §9.1e demo script to demonstrate the platform's consultant productivity value. |

**Setup**: This is the full Phase 1 showcase. Alex runs all three queries in sequence,
narrating the value each one provides. The audience is senior consultants who are skeptical
about whether an AI platform can actually help them in a real meeting.

---

### Canonical Query 1

**Copy this into the chat UI:**

```
What questions should I ask SDG&E about their FSM replacement?
```

**Expected response shape:**

```json
{
  "answer": "SDG&E is a San Diego-based electric and gas IOU, subsidiary of Sempra Energy. For an FSM replacement conversation, focus on these discovery questions ranked by relevance:\n\n**1. What application manages your work orders today?** [dq-001]\nLarge California IOUs like SDG&E typically run SAP PM for T&D maintenance work orders within their SAP ERP. Implication: data migration complexity is high, mobile dispatch gap is likely, scheduling optimization gap is almost certain. Ask about SAP version and whether they have a separate scheduling tool.\n\n**2. How is your FSM integrated with your GIS system?** [dq-004]\nSDG&E runs Esri ArcGIS. Ask whether FSM work orders are geo-coded against ArcGIS assets and whether field crews see GIS asset context on mobile. California utilities with wildfire risk have particularly strong GIS requirements.\n\n**3. How are outage response work orders created during storms and fire events?** [dq-010]\nCPUC monitors SDG&E SAIDI/SAIFI closely. Ask whether OMS-to-FSM work order creation is automated or manual. Manual storm dispatch at SDG&E's scale (3M+ customers) is a significant SAIDI risk.\n\n**4. How do you manage third-party contractor crews?** [dq-006]\nSDG&E uses contractor crews for transmission construction and storm response. Ask whether contractors are managed in the same FSM or outside it.\n\n**5. Are your field crews subject to NERC CIP access control requirements?** [dq-008]\nSDG&E has transmission assets subject to NERC CIP. FSM work order authorization to CIP-protected substations must be tracked. Ask how access logging is currently handled.",
  "citations": [
    {"id": "dq-001", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "What application generates and manages your work orders today?"},
    {"id": "dq-004", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How is your FSM integrated with your GIS system today?"},
    {"id": "dq-010", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How are outage response work orders created and routed to field crews during a storm event?"},
    {"id": "dq-006", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "How do you manage third-party contractor crews in your field service workflow today?"},
    {"id": "dq-008", "source": "data/seed/discovery_qa_utility_fsm.json", "excerpt": "Are your field crews subject to NERC CIP access control requirements?"}
  ],
  "suggested_follow_ups": [
    "Which Slalom consultants have done utility FSM work and what did they find?",
    "What solution accelerators apply to a California IOU FSM replacement?"
  ],
  "consultant_referrals": [
    {"name": "A. Ramirez", "email": "a.ramirez@slalom.com", "specializations": ["FSM", "SAP PM", "Utility Strategy"], "note": "Los Angeles-based — ideal for SDG&E relationship"},
    {"name": "B. Nguyen", "email": "b.nguyen@slalom.com", "specializations": ["FSM", "Salesforce FSM", "NERC CIP"], "note": "NERC CIP expertise directly relevant"}
  ]
}
```

---

### Canonical Query 2

**Copy this into the chat UI:**

```
Which Slalom consultants have done utility FSM work and what did they find?
```

**Expected response shape:**

```json
{
  "answer": "Slalom has 15 consultants with utility FSM experience ranging from 4 to 18 years. Here are the highest-relevance profiles for FSM engagements:\n\n**A. Ramirez** — Director, 16 yrs | Los Angeles\nFSM, SAP PM, Utility Strategy, OT/IT Convergence\nKey finding (eng-001): Evaluated 6 FSM vendors for large IOU SAP PM replacement. Outcome: Recommended Salesforce FSM + MuleSoft integration to SAP. Identified $12M 5-year TCO savings over maintaining SAP PM extensions.\n\n**B. Nguyen** — Director, 14 yrs | Houston\nFSM, Salesforce FSM, Storm Response, NERC CIP\nKey finding (eng-005): Automated outage WO creation from GE ADMS into Salesforce FSM for IOU. Reduced manual storm WO creation effort by 78%. Improved SAIDI by 14 minutes during 2023 hurricane season.\n\n**D. Okafor** — Manager, 9 yrs | San Francisco\nSalesforce FSM, IBM Maximo, Mobile Field Worker, Change Management\nKey finding (eng-002): Deployed Salesforce Field Service to 1,400 field technicians across 6 territories. Achieved 94% mobile app adoption in 90 days. Reduced truck rolls by 8% through intelligent scheduling.\n\n**E. Kowalski** — Manager, 11 yrs | Detroit\nIBM Maximo, SAP EAM, Predictive Maintenance, AVEVA PI\nKey finding (eng-013): Integrated AVEVA PI with IBM Maximo to trigger condition-based maintenance WOs on transformer thermal anomalies. Predicted and prevented 4 transformer failures in first 6 months. 340% ROI.\n\n**H. Chen** — Manager, 12 yrs | Seattle\nOracle Utilities, Oracle Work Management, AMI Integration, SAIDI/SAIFI\nKey finding (eng-007): Integrated Itron AMI with Oracle Utilities WM to auto-generate tamper/outage WOs. Eliminated 3,200 manual WO entries per month.",
  "citations": [
    {"id": "con-001", "source": "data/seed/consultants_utility.json", "excerpt": "A. Ramirez — Director, 16 years, FSM, SAP PM, Utility Strategy"},
    {"id": "con-002", "source": "data/seed/consultants_utility.json", "excerpt": "B. Nguyen — Director, 14 years, Salesforce FSM, Storm Response, NERC CIP"},
    {"id": "con-004", "source": "data/seed/consultants_utility.json", "excerpt": "D. Okafor — Manager, 9 years, Salesforce FSM, Mobile Field Worker"},
    {"id": "eng-001", "source": "data/seed/engagements_utility.json", "excerpt": "FSM Assessment — $12M 5-year TCO savings over maintaining SAP PM extensions"},
    {"id": "eng-005", "source": "data/seed/engagements_utility.json", "excerpt": "Storm Response — 78% reduction in manual WO creation, 14-minute SAIDI improvement"},
    {"id": "eng-002", "source": "data/seed/engagements_utility.json", "excerpt": "Salesforce FSM — 1,400 technicians, 94% adoption in 90 days, 8% truck roll reduction"}
  ],
  "suggested_follow_ups": [
    "What does a typical FSM + GIS integration architecture look like for an IOU?",
    "Who at Slalom has NERC CIP field access control experience?"
  ],
  "consultant_referrals": []
}
```

---

### Canonical Query 3

**Copy this into the chat UI:**

```
What does a typical FSM + GIS integration architecture look like for an IOU?
```

**Expected response shape:**

```json
{
  "answer": "The standard FSM + GIS integration architecture for an IOU has three layers:\n\n**Layer 1: GIS as Network Asset System of Record** [int-001, int-003]\nEsri ArcGIS Utility Network holds the authoritative network model — transformer locations, feeder topology, asset attributes, outage polygons. ArcGIS does not dispatch crews; it provides the spatial context.\n\n**Layer 2: FSM as Scheduling + Mobile Layer**\nFSM (Salesforce Field Service, Oracle Utilities WM, or IBM Maximo) manages work order creation, crew scheduling, and mobile dispatch. Work orders in FSM are geo-tagged against ArcGIS feature IDs to provide crews with asset location on their mobile app.\n\n**Layer 3: Middleware for Bidirectional Sync** [int-011]\nMuleSoft Anypoint Platform (most common) or SAP Integration Suite (SAP-centric utilities) manages:\n- GIS → FSM: asset location + network connectivity + outage polygon delivery to mobile app\n- FSM → GIS: work completion events write back to GIS asset inspection dates and network model updates\n\n**OMS connector (if applicable)** [int-002, int-009]\nFor IOU-scale outage response, ADMS/OMS (GE ADMS, Schneider ADMS) generates trouble orders that flow through MuleSoft into FSM for crew dispatch. Restoration timestamps flow back to OMS to close the outage record.\n\n**Past Slalom delivery:**\n- eng-003: SAP PM ↔ ArcGIS integration using SAP Integration Suite — reduced work order address errors by 31%\n- eng-010: ArcGIS Utility Network migration for IOU — migrated 2.4M asset records, established network tracing for 14 feeder circuits\n- eng-004: IBM Maximo ↔ ArcGIS integration — reduced WO closure lag from 4.2 days to 0.8 days\n\n**Accelerator**: sa-003 (Esri ArcGIS + FSM Integration Reference Architecture) — includes event-driven WO geo-coding patterns, asset context delivery to mobile, and field update propagation back to GIS.",
  "citations": [
    {"id": "int-001", "source": "data/seed/integration_patterns.json", "excerpt": "SAP PM ↔ ArcGIS — asset IDs linked to GIS feature IDs for location-aware WO display on dispatcher map"},
    {"id": "int-003", "source": "data/seed/integration_patterns.json", "excerpt": "ArcGIS ↔ Salesforce FSM — ArcGIS serves as system of record for asset geography; work completion writes back to GIS"},
    {"id": "int-009", "source": "data/seed/integration_patterns.json", "excerpt": "GE ADMS → Salesforce FSM — outage trouble orders dispatched through FSM; SAIDI timestamps written back"},
    {"id": "eng-003", "source": "data/seed/engagements_utility.json", "excerpt": "GIS + Work Order Integration — SAP PM ↔ ArcGIS via SAP IS; reduced WO address errors by 31%"},
    {"id": "eng-004", "source": "data/seed/engagements_utility.json", "excerpt": "IBM Maximo + ArcGIS — WO closure lag from 4.2 days to 0.8 days"},
    {"id": "sa-003", "source": "data/seed/solution_accelerators.json", "excerpt": "ArcGIS + FSM Integration Reference Architecture — middleware patterns for MuleSoft and SAP Integration Suite"}
  ],
  "suggested_follow_ups": [
    "What happens to GIS data quality if field crews don't complete the write-back step?",
    "How does ArcGIS Utility Network migration from Smallworld GIS affect the FSM integration?"
  ],
  "consultant_referrals": [
    {"name": "F. Torres", "email": "f.torres@slalom.com", "specializations": ["GIS", "Esri ArcGIS", "ArcGIS Utility Network"]},
    {"name": "G. Andersen", "email": "g.andersen@slalom.com", "specializations": ["MuleSoft", "SAP Integration Suite", "FSM Integration"]},
    {"name": "K. Brown", "email": "k.brown@slalom.com", "specializations": ["GIS", "Esri ArcGIS", "FSM Integration", "Work Order Geolocation"]}
  ]
}
```

**Phase 1 capabilities exercised (all three queries):**
- `Phase 1a` — Ontology (entity types: Client, Consultant, TechSystem, UseCase correctly recognized)
- `Phase 1b` — All structured graph data: Consultant, Engagement, TechSystem, IntegrationPattern, SolutionAccelerator
- `Phase 1c` — Q&A bank retrieval (Query 1: discovery questions ranked for SDG&E context)
- `Phase 1d` — Hybrid retrieval + Cypher traversal + Claude Sonnet generation + citations
- `Phase 1e` — Demo fixtures (SDG&E context, canonical 3-query script)

---

---

## Appendix A — Phase 1 Capability Map

| Phase | Deliverable | P1 New Hire | P2 Deal Closer | P3 Discovery Expert | P4 Architect | P5 Exec Sponsor |
|-------|-------------|:-----------:|:--------------:|:-------------------:|:------------:|:---------------:|
| **1a** | Ontology schema, synonyms | | | | | ✓ |
| **1b** | TechSystem graph nodes | ✓ | | | ✓ | ✓ |
| **1b** | Consultant + Engagement nodes | ✓ | ✓ | ✓ | | ✓ |
| **1b** | IntegrationPattern nodes | | | | ✓ | ✓ |
| **1b** | SolutionAccelerator nodes | | ✓ | ✓ | ✓ | ✓ |
| **1b** | UseCase taxonomy | | | ✓ | | |
| **1c** | Discovery Q&A bank (RAG) | ✓ | | ✓ | | ✓ |
| **1c** | Project narrative retrieval | | | | ✓ | |
| **1d** | Hybrid retrieval + generation | ✓ | ✓ | ✓ | ✓ | ✓ |
| **1d** | Consultant referral cards | ✓ | ✓ | ✓ | ✓ | ✓ |
| **1d** | Citation injection | ✓ | ✓ | ✓ | ✓ | ✓ |
| **1e** | Demo fixtures (SDG&E) | | | | | ✓ |
| **1e** | Canonical 3-query script | | | | | ✓ |

---

## Appendix B — Expected Response Schema

Every system response follows this JSON shape:

```json
{
  "answer": "Narrative response in markdown. Cites sources inline using [id] notation.",
  "citations": [
    {
      "id": "doc-or-node-id",
      "source": "relative/path/to/seed/file.json or document",
      "excerpt": "Direct quote or key sentence from the source"
    }
  ],
  "suggested_follow_ups": [
    "Natural language follow-up question the consultant might ask next"
  ],
  "consultant_referrals": [
    {
      "name": "X. LastName",
      "email": "x.lastname@slalom.com",
      "specializations": ["Specialty 1", "Specialty 2"],
      "note": "Optional context on why this consultant is relevant"
    }
  ]
}
```

**Hallucination guard**: Every entity name (consultant name, engagement outcome metric, system
vendor name) appearing in `answer` must appear verbatim in at least one `citations[].excerpt`.
The platform's response validator rejects any response that fails this check.

---

## Appendix C — Seed Data Quick Reference

| File | Entity Type | Records | Key Fields |
|------|-------------|---------|------------|
| `data/seed/clients_utility.json` | Client | 20 | id, name, utility_type (IOU/Muni/Co-op), hq_state, revenue_band |
| `data/seed/engagements_utility.json` | Engagement | 20 | id, title, client_id, phase, status, outcome_summary |
| `data/seed/consultants_utility.json` | Consultant | 15 | id, name, title, utility_experience_years, specializations, email |
| `data/seed/solution_accelerators.json` | SolutionAccelerator | 10 | id, name, description, applicable_use_cases, artifact_path |
| `data/seed/tech_systems_utility.json` | TechSystem | 30 | id, vendor, product_name, category, common_in_utility_types, misconception |
| `data/seed/integration_patterns.json` | IntegrationPattern | 15 | id, from_system, to_system, integration_type, common_middleware, utility_types |
| `data/seed/discovery_qa_utility_fsm.json` | DiscoveryQuestion | 10 | id, text, category, likely_answers[].implication, leads_to |
| `data/ontology/use_case_taxonomy.json` | UseCase | 11 sub-domains + sub-topics | sub_domain, priority, sub_topics[] |
| `data/ontology/synonyms_utility.json` | Synonym aliases | 50+ entries | canonical, aliases[] |

**Total Phase 1b structured records**: ~185 nodes + relationships in Neo4j

---

*This document is a Phase 1e demo deliverable. Update after Phase 1c document ingestion
to add citation examples from project narratives, architecture diagrams, and meeting transcripts.*

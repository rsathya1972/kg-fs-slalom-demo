// ============================================================
// Migration: 001_initial_schema
// Description: Create uniqueness constraints and indexes for
//              all Phase 1a node types.
// ============================================================

// ---- UNIQUENESS CONSTRAINTS ----

// Client nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Client) REQUIRE n.id IS UNIQUE;

// Engagement nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Engagement) REQUIRE n.id IS UNIQUE;

// UseCase nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:UseCase) REQUIRE n.id IS UNIQUE;

// TechSystem nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:TechSystem) REQUIRE n.id IS UNIQUE;

// DiscoveryQuestion nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:DiscoveryQuestion) REQUIRE n.id IS UNIQUE;

// Consultant nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Consultant) REQUIRE n.id IS UNIQUE;

// Artifact nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Artifact) REQUIRE n.id IS UNIQUE;

// SolutionAccelerator nodes
CREATE CONSTRAINT IF NOT EXISTS FOR (n:SolutionAccelerator) REQUIRE n.id IS UNIQUE;

// ---- TENANT_ID INDEXES (multi-tenant lookup performance) ----

CREATE INDEX IF NOT EXISTS FOR (n:Client) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:Engagement) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:UseCase) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:TechSystem) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:DiscoveryQuestion) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:Consultant) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:Artifact) ON (n.tenant_id);
CREATE INDEX IF NOT EXISTS FOR (n:SolutionAccelerator) ON (n.tenant_id);

// ---- ADDITIONAL LOOKUP INDEXES ----

// Client name lookup (common filter)
CREATE INDEX IF NOT EXISTS FOR (n:Client) ON (n.name);

// TechSystem category filter
CREATE INDEX IF NOT EXISTS FOR (n:TechSystem) ON (n.category);

// TechSystem vendor name lookup
CREATE INDEX IF NOT EXISTS FOR (n:TechSystem) ON (n.vendor);

// UseCase sub-domain grouping
CREATE INDEX IF NOT EXISTS FOR (n:UseCase) ON (n.sub_domain);

// Consultant experience years for ordering
CREATE INDEX IF NOT EXISTS FOR (n:Consultant) ON (n.utility_experience_years);

// DiscoveryQuestion category filter
CREATE INDEX IF NOT EXISTS FOR (n:DiscoveryQuestion) ON (n.category);

// Artifact document type filter
CREATE INDEX IF NOT EXISTS FOR (n:Artifact) ON (n.doc_type);

// Engagement status/date for recency weighting
CREATE INDEX IF NOT EXISTS FOR (n:Engagement) ON (n.end_date);
CREATE INDEX IF NOT EXISTS FOR (n:Engagement) ON (n.utility_type);

export interface StemmaProvenance {
  ai_drafted?: boolean;
  source_kind?: string;
  source?: string;
  reviewer?: string;
  reviewed_at?: string;
}

export interface StemmaEntity {
  id: string;
  type: string;
  name: string;
  domain: string;
  status: string;
  definition: string;
  symbol?: string | null;
  unit?: string | null;
  equation?: string | null;
  common_misconceptions?: string[];
  learning_objectives?: string[];
  real_world_applications?: string[];
  examples?: string[];
  key_experiments?: string[];
  provenance?: StemmaProvenance;
}

/** Minimal view of a first-class connection (export contract v2.0 — the only relationship source). */
export interface StemmaConnection {
  id: string;
  source: string;
  relation: string;
  target: string;
  assertion: { status: string; type: string; review: { status: string } };
  context?: { domain?: string; subdomain?: string; qualifiers?: unknown[] } | null;
  /** DERIVED claim identity: sha256(source|relation|target|polarity|qualifiers) (ADR-0026). */
  claim_signature?: string;
}

export interface StemmaKnowledgeExport {
  export_version: string; // contract v2.0: connections[] required; no inline entity relationships (ADR-0028)
  schema_version: string;
  content_hash?: string; // deterministic stamp; replaces wall-clock generated_at
  source?: string;
  entity_count: number;
  connection_count?: number;
  source_count?: number;
  entities: StemmaEntity[];
  connections: StemmaConnection[];
}

export class KnowledgeExportLoadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'KnowledgeExportLoadError';
  }
}

/** Export contract major version this explorer consumes (v2 — ADR-0028). */
export const SUPPORTED_EXPORT_MAJOR = 2;

export async function loadKnowledgeExport(url: string = '/exports/knowledge.json'): Promise<StemmaKnowledgeExport> {
  let response: Response;
  try {
    response = await fetch(url);
  } catch (err) {
    throw new KnowledgeExportLoadError(`Failed to fetch knowledge export from ${url}: ${(err as Error).message}`);
  }

  if (!response.ok) {
    throw new KnowledgeExportLoadError(`HTTP ${response.status} when fetching knowledge export from ${url}`);
  }

  let data: StemmaKnowledgeExport;
  try {
    data = await response.json();
  } catch (err) {
    throw new KnowledgeExportLoadError(`Failed to parse knowledge export JSON: ${(err as Error).message}`);
  }

  // Integrity Validation
  if (!data || typeof data !== 'object' || !Array.isArray(data.entities)) {
    throw new KnowledgeExportLoadError('Invalid knowledge export format: missing top-level entities array');
  }

  const major = parseInt(String(data.export_version ?? '').split('.')[0], 10);
  if (major !== SUPPORTED_EXPORT_MAJOR) {
    throw new KnowledgeExportLoadError(
      `Unsupported export_version '${data.export_version}' (explorer supports ${SUPPORTED_EXPORT_MAJOR}.x)`,
    );
  }
  if (!Array.isArray(data.connections)) {
    throw new KnowledgeExportLoadError('Invalid export: missing required connections array');
  }

  const idSet = new Set<string>();
  for (const entity of data.entities) {
    if (!entity.id || typeof entity.id !== 'string') {
      throw new KnowledgeExportLoadError('Invalid entity in export: missing stable string ID');
    }
    if (idSet.has(entity.id)) {
      throw new KnowledgeExportLoadError(`Duplicate entity ID in export: '${entity.id}'`);
    }
    idSet.add(entity.id);
  }

  for (const c of data.connections) {
    if (!idSet.has(c.source) || !idSet.has(c.target)) {
      throw new KnowledgeExportLoadError(`Connection ${c.id} references an unindexed entity`);
    }
  }

  return data;
}

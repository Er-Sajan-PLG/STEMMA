/**
 * Grounded AI chat over the STEMMA export (REQ-STEMMA-INTEG-001 AC3).
 *
 * Two hard rules, both structural rather than prompt-level:
 *
 *   GROUNDING — every answer is assembled from export records, and every claim
 *   carries citations to the entity ids and source refs it came from. The model
 *   never supplies the substrate; it selects and phrases over retrieved records.
 *
 *   REFUSAL — when retrieval finds nothing that supports an answer, the chat
 *   refuses. Refusal is a first-class outcome, not an error path.
 *
 * The service reads derived artifacts ONLY (`exports/knowledge.json`). It never
 * touches `content/` or canonical markdown — same rule the graph viewer follows
 * (AC4). That is why every field it can cite is a field the export carries.
 */
import type {
  StemmaKnowledgeExport,
  StemmaEntity,
  StemmaConnection,
} from './knowledge-export-loader';

/** A citation attached to an answer: where the claim came from. */
export interface ChatCitation {
  kind: 'entity' | 'connection';
  /** Stable STEMMA id, e.g. `stemma:phys.metre`. */
  id: string;
  /** Human-readable label for the citation chip. */
  label: string;
  /** Source refs backing the record (from the export, never from markdown). */
  sourceRefs: string[];
}

export interface ChatAnswer {
  /** 'grounded' — answered from retrieved records. 'refused' — insufficient basis. */
  status: 'grounded' | 'refused';
  answer: string;
  citations: ChatCitation[];
  /** Ids of the records the answer was assembled from. */
  groundingIds: string[];
  /** Why the chat refused; absent when grounded. */
  refusalReason?: string;
}

export interface ChatTurn {
  question: string;
  answer: ChatAnswer;
}

const STOPWORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'do', 'does', 'for', 'from',
  'how', 'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was',
  'what', 'when', 'where', 'which', 'who', 'why', 'with', 'tell', 'me', 'about',
  'explain', 'describe', 'give', 'can', 'you', 'i', 'we', 'they',
]);

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s._-]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 1 && !STOPWORDS.has(t));
}

/** Source refs for an entity, taken from the export's own provenance fields. */
function entitySourceRefs(entity: StemmaEntity): string[] {
  const refs: string[] = [];
  const p = entity.provenance;
  if (p?.source) refs.push(p.source);
  return refs;
}

/** Source refs for a connection, from its evidence block if the export carries one. */
function connectionSourceRefs(conn: StemmaConnection): string[] {
  const refs: string[] = [];
  const evidence = (conn as unknown as {
    evidence?: Array<{ source_ref?: string; source_id?: string }>;
  }).evidence;
  if (Array.isArray(evidence)) {
    for (const e of evidence) {
      const ref = e?.source_ref ?? e?.source_id;
      if (typeof ref === 'string' && ref.length) refs.push(ref);
    }
  }
  return refs;
}

interface Scored {
  score: number;
  entity?: StemmaEntity;
  connection?: StemmaConnection;
}

/**
 * Retrieve the export records most relevant to a question.
 *
 * Deterministic and offline: a lexical scorer over export fields. No network, no
 * model call needed to decide *what* is relevant — only to phrase the result.
 */
export function retrieveGrounding(
  question: string,
  data: StemmaKnowledgeExport,
  limit = 5,
): Scored[] {
  const terms = tokenize(question);
  if (!terms.length) return [];

  const byId = new Map(data.entities.map((e) => [e.id, e]));
  const scored: Scored[] = [];

  for (const entity of data.entities) {
    let score = 0;
    const name = entity.name.toLowerCase();
    const id = entity.id.toLowerCase();
    const def = (entity.definition ?? '').toLowerCase();
    for (const t of terms) {
      if (name === t) score += 10;
      else if (name.includes(t)) score += 6;
      if (id.includes(t)) score += 5;
      if (def.includes(t)) score += 2;
      for (const list of [
        entity.learning_objectives,
        entity.real_world_applications,
        entity.examples,
        entity.common_misconceptions,
        entity.key_experiments,
      ]) {
        if (Array.isArray(list) && list.some((s) => String(s).toLowerCase().includes(t))) {
          score += 2;
        }
      }
      if (entity.symbol && entity.symbol.toLowerCase() === t) score += 6;
      if (entity.unit && entity.unit.toLowerCase() === t) score += 4;
      if (entity.domain && entity.domain.toLowerCase() === t) score += 3;
    }
    if (score > 0) scored.push({ score, entity });
  }

  for (const conn of data.connections) {
    let score = 0;
    const src = byId.get(conn.source);
    const tgt = byId.get(conn.target);
    const hay = [conn.relation, src?.name, tgt?.name, conn.id]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    for (const t of terms) {
      if (hay.includes(t)) score += 4;
    }
    if (score > 0) scored.push({ score, connection: conn });
  }

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    const ai = a.entity?.id ?? a.connection?.id ?? '';
    const bi = b.entity?.id ?? b.connection?.id ?? '';
    return ai.localeCompare(bi);
  });
  return scored.slice(0, limit);
}

/** Human-readable phrasing of one connection, using its endpoints. */
function describeConnection(conn: StemmaConnection, byId: Map<string, StemmaEntity>): string {
  const src = byId.get(conn.source);
  const tgt = byId.get(conn.target);
  const relation = conn.relation.replace(/_/g, ' ');
  return `${src?.name ?? conn.source} ${relation} ${tgt?.name ?? conn.target}`;
}

/**
 * Answer a question strictly from the export.
 *
 * The returned citations are derived from the same records named in
 * `groundingIds`, so an answer can never cite something it did not retrieve —
 * the refusal and the citation set are computed from one retrieval pass.
 */
export function answerQuestion(
  question: string,
  data: StemmaKnowledgeExport,
  history: ChatTurn[] = [],
): ChatAnswer {
  const trimmed = question.trim();
  if (!trimmed) {
    return {
      status: 'refused',
      answer: 'Ask a question about the concepts in this knowledge base.',
      citations: [],
      groundingIds: [],
      refusalReason: 'empty question',
    };
  }

  const scored = retrieveGrounding(trimmed, data);
  if (!scored.length) {
    return {
      status: 'refused',
      answer:
        `I don't have anything in this export that answers that. ` +
        `The knowledge base covers ${data.entity_count} concept${
          data.entity_count === 1 ? '' : 's'
        } and ${data.connections.length} connection${
          data.connections.length === 1 ? '' : 's'
        }; I only answer from what is published here, and I won't guess beyond it.`,
      citations: [],
      groundingIds: [],
      refusalReason: 'no export record matched the question',
    };
  }

  const byId = new Map(data.entities.map((e) => [e.id, e]));
  const citations: ChatCitation[] = [];
  const lines: string[] = [];
  const groundingIds: string[] = [];

  const entities = scored.filter((s) => s.entity).map((s) => s.entity!) ;
  const connections = scored.filter((s) => s.connection).map((s) => s.connection!);

  for (const entity of entities) {
    groundingIds.push(entity.id);
    citations.push({
      kind: 'entity',
      id: entity.id,
      label: entity.name,
      sourceRefs: entitySourceRefs(entity),
    });

    const bits: string[] = [entity.definition.trim()];
    if (entity.symbol) bits.push(`Symbol: ${entity.symbol}.`);
    if (entity.unit) bits.push(`Unit: ${entity.unit}.`);
    if (entity.equation) bits.push(`Equation: ${entity.equation}.`);
    if (Array.isArray(entity.examples) && entity.examples.length) {
      bits.push(`Example: ${entity.examples[0]}.`);
    }
    lines.push(`**${entity.name}** — ${bits.join(' ')}`);
  }

  for (const conn of connections) {
    groundingIds.push(conn.id);
    citations.push({
      kind: 'connection',
      id: conn.id,
      label: describeConnection(conn, byId),
      sourceRefs: connectionSourceRefs(conn),
    });
    const trust = conn.assertion?.review?.status ?? 'unreviewed';
    lines.push(
      `Relationship — ${describeConnection(conn, byId)} (${trust}).`,
    );
  }

  const answer = lines.join('\n\n');
  return { status: 'grounded', answer, citations, groundingIds };
}

/**
 * Every id an answer may cite, for the verifier. Kept exported so a test can
 * assert the invariant "citations ⊆ grounding ⊆ export" without re-deriving it.
 */
export function citationsAreGrounded(
  answer: ChatAnswer,
  data: StemmaKnowledgeExport,
): boolean {
  const exportIds = new Set<string>([
    ...data.entities.map((e) => e.id),
    ...data.connections.map((c) => c.id),
  ]);
  if (answer.status === 'refused') {
    return answer.citations.length === 0 && answer.groundingIds.length === 0;
  }
  if (!answer.citations.length || !answer.groundingIds.length) return false;
  const cited = new Set(answer.citations.map((c) => c.id));
  for (const id of cited) if (!exportIds.has(id)) return false;
  for (const id of answer.groundingIds) if (!exportIds.has(id)) return false;
  for (const id of cited) if (!answer.groundingIds.includes(id)) return false;
  return true;
}

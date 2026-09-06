import { StemmaEntity, StemmaKnowledgeExport } from './knowledge-export-loader';

export interface ConceptDetails {
  entity: StemmaEntity;
  prerequisites: StemmaEntity[];
  dependents: StemmaEntity[];
  related: StemmaEntity[];
  /** Where the relationship lists came from (E1.6: connections[] preferred). */
  edgeSource: 'connections';
  /** entity id -> assertion review status of the edge that linked it (trust annotation). */
  trust: Record<string, string>;
}

export class ConceptNotFoundError extends Error {
  constructor(id: string) {
    super(`Concept not found in export: '${id}'`);
    this.name = 'ConceptNotFoundError';
  }
}

export function getConceptDetails(id: string, exportData: StemmaKnowledgeExport): ConceptDetails {
  const entityMap = new Map<string, StemmaEntity>(exportData.entities.map(e => [e.id, e]));
  const target = entityMap.get(id);

  if (!target) {
    throw new ConceptNotFoundError(id);
  }

  const prereqTypes = new Set(['logically_requires', 'mathematically_requires']);
  const prerequisites: StemmaEntity[] = [];
  const related: StemmaEntity[] = [];

  // deprecated fallback kept only for exports that predate contract v1.0.
  // Connections are the only relationship source (contract v2.0).
  const connections = (exportData.connections ?? []).filter(
    c => c.assertion?.status !== 'deprecated' && c.assertion?.status !== 'superseded'
  );
  const edgeSource: 'connections' = 'connections';

  const outgoing = connections
    .filter(c => c.source === id)
    .map(c => ({ relation: c.relation, target: c.target, trust: c.assertion?.review?.status ?? 'unreviewed' }));

  const trust: Record<string, string> = {};
  for (const edge of outgoing) {
    const relEntity = entityMap.get(edge.target);
    if (!relEntity) continue;
    trust[relEntity.id] = edge.trust;
    if (prereqTypes.has(edge.relation)) {
      prerequisites.push(relEntity);
    } else {
      related.push(relEntity);
    }
  }

  // Find dependents (entities that specify 'id' as their prerequisite target)
  const dependents: StemmaEntity[] = [];
  const incoming = connections
    .filter(c => c.target === id)
    .map(c => ({ relation: c.relation, source: c.source, trust: c.assertion?.review?.status ?? 'unreviewed' }));

  for (const edge of incoming) {
    if (!prereqTypes.has(edge.relation)) continue;
    const source = entityMap.get(edge.source);
    if (!source || source.id === id) continue;
    if (!dependents.some(d => d.id === source.id)) {
      dependents.push(source);
      trust[source.id] = edge.trust;
    }
  }

  return {
    entity: target,
    prerequisites,
    dependents,
    related,
    edgeSource,
    trust
  };
}

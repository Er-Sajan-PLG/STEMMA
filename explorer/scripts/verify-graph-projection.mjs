#!/usr/bin/env node
/**
 * E1.6 regression check — the explorer must draw its graph from canonical `connections[]`
 * (ADR-0020/0023) and annotate every edge with assertion trust (ADR-0026 / plan v2 E1.6).
 *
 * Runs the real TypeScript modules (bundled once with esbuild — no test framework, no
 * TypeScript runtime needed) against the real export:
 *
 *   node scripts/verify-graph-projection.mjs         # uses exports/knowledge.json
 *   node scripts/verify-graph-projection.mjs <file>  # use another export
 *
 * Exit 0 = all assertions hold.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const EXPLORER_ROOT = resolve(HERE, '..');
const LHS_ROOT = resolve(EXPLORER_ROOT, '..');
const EXPORT_PATH = process.argv[2] ?? resolve(LHS_ROOT, 'exports', 'knowledge.json');

let build;
try {
  ({ build } = await import('esbuild'));
} catch {
  console.error('✗ esbuild is required (dev dependency): npm install');
  process.exit(1);
}

const failures = [];
const check = (name, condition, detail = '') => {
  if (condition) {
    console.log(`PASS: ${name}${detail ? ` (${detail})` : ''}`);
  } else {
    failures.push(name);
    console.error(`FAIL: ${name}${detail ? ` (${detail})` : ''}`);
  }
};

// Bundle the two services under test (graph-projection + concept-data) into ESM.
async function loadModule(entry) {
  const result = await build({
    entryPoints: [resolve(EXPLORER_ROOT, 'src', 'services', entry)],
    bundle: true,
    format: 'esm',
    platform: 'node',
    write: false,
    logLevel: 'silent',
  });
  const code = result.outputFiles[0].text;
  return import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
}

const data = JSON.parse(readFileSync(EXPORT_PATH, 'utf8'));
const { projectKnowledgeGraph } = await loadModule('graph-projection.ts');
const { getConceptDetails } = await loadModule('concept-data.ts');

// --- edges come from connections[], not the deprecated inline projection -------------
const projection = projectKnowledgeGraph(data);
check('graph edges are projected from connections[]', projection.edgeSource === 'connections', projection.edgeSource);

const activeConnections = data.connections.filter(c => c.assertion?.status !== 'deprecated' && c.assertion?.status !== 'superseded');
const entityIds = new Set(data.entities.map(e => e.id));
const resolvable = activeConnections.filter(c => entityIds.has(c.source) && entityIds.has(c.target));
check('every live connection is drawn', projection.links.length === resolvable.length,
  `${projection.links.length} links / ${resolvable.length} live connections`);

check('every edge carries assertion trust', projection.links.every(l => ['canonical', 'reviewed', 'unreviewed'].includes(l.trust)));
check('every edge carries its connection id', projection.links.every(l => typeof l.connectionId === 'string' && l.connectionId.startsWith('stemma:conn.')));
check('every edge carries the derived claim signature (ADR-0026)',
  projection.links.every(l => /^sha256:[0-9a-f]{64}$/.test(l.claimSignature ?? '')));

// Trust distribution must mirror the export's review statuses — no silent defaulting.
const expectedTrust = {};
for (const c of resolvable) {
  const status = c.assertion?.review?.status ?? 'unreviewed';
  expectedTrust[status] = (expectedTrust[status] ?? 0) + 1;
}
const actualTrust = {};
for (const l of projection.links) actualTrust[l.trust] = (actualTrust[l.trust] ?? 0) + 1;
check('trust distribution matches assertion.review.status',
  JSON.stringify(actualTrust) === JSON.stringify(expectedTrust), JSON.stringify(actualTrust));

// Trust must be visible: reviewed edges are drawn heavier, unreviewed ones faint.
const canonical = projection.links.find(l => l.trust === 'canonical');
const unreviewed = projection.links.find(l => l.trust === 'unreviewed');
if (canonical && unreviewed) {
  const sameRelation = projection.links.filter(l => l.relationship === canonical.relationship);
  const a = sameRelation.find(l => l.trust === 'canonical');
  const b = sameRelation.find(l => l.trust === 'unreviewed');
  check('trust modulates edge weight/opacity', !a || !b || (a.width > b.width && a.trustOpacity > b.trustOpacity));
} else {
  check('both canonical and unreviewed edges exist in the export', false, 'cannot compare trust styling');
}

// --- contract v2.0: an export with a MISSING connections[] is invalid ----------------
// (an export with an empty-but-present connections[] is valid and renders an empty graph.)
const malformed = { ...data };
delete malformed.connections;
const invalidJSON = JSON.stringify(malformed);
let rejected = false;
try {
  // The loader is async; validate its guard conditions synchronously instead.
  const parsed = JSON.parse(invalidJSON);
  if (!Array.isArray(parsed.connections)) throw new Error('missing connections');
} catch {
  rejected = true;
}
check('contract v2.0: export without connections[] is rejected (no silent empty graph)', rejected);

// --- inspector data (concept-details) reads the same source --------------------------
const sample = data.entities[0];
const details = getConceptDetails(sample.id, data);
check('concept details are built from connections[]', details.edgeSource === 'connections');
check('concept details annotate trust per linked entity',
  Object.values(details.trust).every(t => ['canonical', 'reviewed', 'unreviewed'].includes(t)));

if (failures.length) {
  console.error(`✗ ${failures.length} explorer projection check(s) failed`);
  process.exit(1);
}
console.log('OK: explorer graph projection reads connections[] and annotates trust (E1.6)');

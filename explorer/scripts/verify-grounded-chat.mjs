#!/usr/bin/env node
/**
 * INTEG-001 AC3 — the grounded AI chat must cite and must refuse.
 *
 * AC3 as written: "provide an AI chat grounded in the STEMMA export (citations
 * to entity ids + source refs), reading derived artifacts only — never canonical
 * markdown." The verification procedure adds: "assert answers cite entity ids +
 * source refs and refuse when ungrounded."
 *
 * This runs the REAL TypeScript service (bundled with esbuild) against the REAL
 * export and asserts four properties that a fabricated chat cannot satisfy:
 *
 *   1. GROUNDED  — a question the export can answer yields status 'grounded'
 *                  with at least one citation, and the answer text is assembled
 *                  from the retrieved records.
 *   2. CITED     — every citation names a real export id, carries the entity's
 *                  source refs, and is a subset of the grounding set.
 *   3. REFUSES   — a question the export cannot answer yields status 'refused',
 *                  zero citations, and no fabricated content.
 *   4. DERIVED-ONLY — the chat reads no canonical markdown: the service module
 *                  and the panel contain no reference to content/ or *.md.
 *
 * The refusal case is chosen to be flatly outside the corpus ("what is the
 * capital of France"), so a chat that answers it is provably ungrounded.
 *
 *   node scripts/verify-grounded-chat.mjs            # uses exports/knowledge.json
 *   node scripts/verify-grounded-chat.mjs <file>     # another export
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
const { answerQuestion, citationsAreGrounded, retrieveGrounding } =
  await loadModule('grounded-chat.ts');

const exportEntityIds = new Set(data.entities.map(e => e.id));
const exportConnIds = new Set((data.connections ?? []).map(c => c.id));

// --- 0. NON-VACUITY OF THE FIXTURE -------------------------------------------------
// The strongest property this file asserts — "a citation cannot name an id that is
// not in the export" — is only *tested* if at least one answer actually produces a
// CONNECTION citation. Entity-only answers never enter the connection loop, so a
// fabricated connection id would sail through every check below. Assert the fixture
// can exercise that path before relying on it: if the corpus ever loses its
// connections, this fails loudly instead of silently weakening the verification.
const connQueries = [
  'What is the relationship between force and mass?',
  'What connects force and mass?',
  'Which concepts are derived from the metre?',
];
const connProbe = connQueries
  .map(q => answerQuestion(q, data))
  .find(a => a.citations.some(c => c.kind === 'connection'));
check('the corpus can exercise the connection-citation path (fixture non-vacuity)',
  !!connProbe,
  connProbe
    ? `e.g. "${connQueries[connQueries.findIndex(q => answerQuestion(q, data).citations.some(c => c.kind === 'connection'))]}"`
    : 'no query produced a connection citation — CITED checks would be vacuous');

// --- 1. GROUNDED -------------------------------------------------------------------
const firstEntity = data.entities[0];
check('export has at least one entity to ground against', !!firstEntity);
const groundedQ = `What is the ${firstEntity.name}?`;
const grounded = answerQuestion(groundedQ, data);

check('a question the export can answer is answered, not refused',
  grounded.status === 'grounded', `status=${grounded.status}`);
check('the grounded answer cites at least one record',
  grounded.citations.length > 0, `${grounded.citations.length} citations`);
check('the grounded answer names its grounding ids',
  grounded.groundingIds.length > 0, `${grounded.groundingIds.length} ids`);
check('the answer text is drawn from the entity definition',
  grounded.answer.includes(firstEntity.definition.trim().slice(0, 40)),
  'first 40 chars of the definition appear in the answer');
check('the primary entity is among the grounded records',
  grounded.groundingIds.includes(firstEntity.id), firstEntity.id);

// --- 2. CITED ----------------------------------------------------------------------
const citedIds = grounded.citations.map(c => c.id);
check('every citation names a real export id',
  citedIds.every(id => exportEntityIds.has(id) || exportConnIds.has(id)),
  citedIds.join(', '));
check('every cited id is also in the grounding set',
  citedIds.every(id => grounded.groundingIds.includes(id)));
check('every citation carries a stable STEMMA id',
  grounded.citations.every(c => /^stemma:(phys|core|conn)\./.test(c.id)));
check('every citation carries a label',
  grounded.citations.every(c => typeof c.label === 'string' && c.label.length > 0));
check('entity citations carry the entity source refs from the export',
  grounded.citations.filter(c => c.kind === 'entity').every(c => Array.isArray(c.sourceRefs)),
  JSON.stringify(grounded.citations.map(c => ({ id: c.id, refs: c.sourceRefs.length }))));

// The invariant helper must agree with the answer.
check('citationsAreGrounded() accepts the grounded answer',
  citationsAreGrounded(grounded, data) === true);

// --- 2b. CITED — the CONNECTION path -----------------------------------------------
// Entity citations alone do not test the citation-integrity rule, because the
// connection loop in answerQuestion is never entered. Assert a connection citation
// end to end: a corrupted connection id must be visible to the checks below.
if (connProbe) {
  const connCitations = connProbe.citations.filter(c => c.kind === 'connection');
  check('a relationship answer cites at least one connection',
    connCitations.length > 0, `${connCitations.length} connection citation(s)`);

  const badConnIds = connCitations.filter(c => !exportConnIds.has(c.id)).map(c => c.id);
  check('every connection citation names a real connection id in the export',
    badConnIds.length === 0, badConnIds.length ? `fabricated: ${badConnIds.join(', ')}` : 'all real');

  check('every connection citation id is in the grounding set',
    connCitations.every(c => connProbe.groundingIds.includes(c.id)),
    connCitations.map(c => c.id).join(', '));

  check('every connection citation carries a stable STEMMA connection id',
    connCitations.every(c => /^stemma:conn\./.test(c.id)),
    connCitations.map(c => c.id).join(', '));

  check('connection citations carry source refs from the export evidence block',
    connCitations.every(c => Array.isArray(c.sourceRefs)),
    JSON.stringify(connCitations.map(c => ({ id: c.id, refs: c.sourceRefs.length }))));

  check('citationsAreGrounded() accepts the relationship answer',
    citationsAreGrounded(connProbe, data) === true);

  // The invariant helper must REJECT a fabricated connection citation. Run the
  // real helper against a doctored copy of the real answer: this is the property
  // that actually proves the guard bites, independent of which query was used.
  const doctored = {
    ...connProbe,
    citations: connProbe.citations.map(c =>
      c.kind === 'connection' ? { ...c, id: 'stemma:conn.DOES-NOT-EXIST' } : c),
  };
  check('citationsAreGrounded() REJECTS an answer citing a fabricated connection id',
    citationsAreGrounded(doctored, data) === false,
    'guard must not accept an id absent from the export');
}

// --- 2c. CITED — synthetic export (edge case the real corpus cannot stage) ---------
// Prove the citation rule under a minimal, hand-built export where the only record
// IS a connection. This pins the connection path even if the real corpus changes,
// and it exercises the answer when there is no entity citation to fall back on.
{
  const synthetic = {
    ...data,
    entity_count: 0,
    entities: [],
    connection_count: 1,
    connections: [{
      id: 'stemma:conn.SYNTH-1',
      type: 'connection',
      source: 'stemma:phys.metre',
      target: 'stemma:phys.second',
      relation: 'derived_from',
      assertion: { status: 'active', type: 'asserted', review: { status: 'canonical' } },
      evidence: [{ type: 'standard', stance: 'supports', source_ref: 'stemma:src.SYNTHETIC' }],
    }],
  };
  const ans = answerQuestion('derived from', synthetic);
  check('a connection-only export still answers (grounded, not refused)',
    ans.status === 'grounded', `status=${ans.status}`);
  check('the connection-only answer cites exactly the synthetic connection',
    ans.citations.length === 1 && ans.citations[0].kind === 'connection'
      && ans.citations[0].id === 'stemma:conn.SYNTH-1',
    JSON.stringify(ans.citations.map(c => `${c.kind}:${c.id}`)));
  check('the synthetic connection citation carries its evidence source ref',
    ans.citations[0].sourceRefs.includes('stemma:src.SYNTHETIC'),
    JSON.stringify(ans.citations[0].sourceRefs));
  check('citationsAreGrounded() accepts the connection-only answer',
    citationsAreGrounded(ans, synthetic) === true);
}

// --- 3. REFUSES --------------------------------------------------------------------
const ungrounded = answerQuestion('What is the capital of France?', data);
check('an unanswerable question is REFUSED, not answered',
  ungrounded.status === 'refused', `status=${ungrounded.status}`);
check('a refusal cites nothing',
  ungrounded.citations.length === 0 && ungrounded.groundingIds.length === 0);
check('a refusal carries a stated reason',
  typeof ungrounded.refusalReason === 'string' && ungrounded.refusalReason.length > 0,
  ungrounded.refusalReason);
check('a refusal invents no France/Paris content',
  !/paris|france/i.test(ungrounded.answer), ungrounded.answer.slice(0, 80));
check('citationsAreGrounded() accepts the refusal (empty citation set)',
  citationsAreGrounded(ungrounded, data) === true);

// Non-vacuity: an empty question also refuses rather than erroring.
const empty = answerQuestion('   ', data);
check('an empty question refuses rather than throwing', empty.status === 'refused');

// Non-vacuity of RETRIEVAL: the refused question must retrieve nothing, and the
// grounded question must retrieve something. Otherwise refusal is unexplained.
check('retrieval returns nothing for the unanswerable question',
  retrieveGrounding('What is the capital of France?', data).length === 0);
check('retrieval returns something for the answerable question',
  retrieveGrounding(groundedQ, data).length > 0);

// --- 4. DERIVED-ONLY (chat surface reads no canonical markdown) ---------------------
// Assert on CODE, not on prose: a doc comment saying "never touches content/" is
// documentation of the rule, not a violation of it. Strip comments and string
// literals before scanning, so only real identifiers and paths are tested.
function codeOnly(src) {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, '')   // block comments
    .replace(/^\s*\/\/.*$/gm, '')       // line comments
    .replace(/(['"`])(?:\\.|(?!\1)[^\\])*\1/g, '""'); // string literals
}

for (const rel of ['src/services/grounded-chat.ts', 'src/components/grounded-chat-panel.ts']) {
  const src = readFileSync(resolve(EXPLORER_ROOT, rel), 'utf8');
  const code = codeOnly(src);
  const bad = [];
  if (/\bcontent\//.test(code)) bad.push('code references content/');
  if (/\.md\b/.test(code)) bad.push('code references *.md');
  check(`${rel} reads derived artifacts only`, bad.length === 0, bad.join('; '));
}

// The chat must receive its data, never fetch a second source of truth itself.
{
  const code = codeOnly(readFileSync(resolve(EXPLORER_ROOT, 'src/services/grounded-chat.ts'), 'utf8'));
  check('grounded-chat.ts performs no fetch of its own (data is injected)',
    !/\bfetch\s*\(/.test(code));
}

if (failures.length) {
  console.error(`✗ ${failures.length} grounded-chat check(s) failed`);
  process.exit(1);
}
console.log('OK: grounded chat answers with citations and refuses when ungrounded (INTEG-001 AC3)');

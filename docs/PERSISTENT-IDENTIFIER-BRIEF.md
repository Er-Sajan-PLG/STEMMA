# Persistent Identifier Decision Brief (RESEARCH — NO DECISION RECORDED)

Type: decision-support research · Status: under owner-directed slow evaluation
Prepared: 2026-09-22 · Trigger: owner brief "STEMMA Persistent Identifier Decision — Slow Research Before Decision"
Related: ADR-0053 (recorded provisional answers; under review, see §0.3) · ADR-0052 (R4, unaffected) · ARCHITECTURE-V2 §7 (projections) · UNRES-STEMMA-CORE-001 (closed provisionally by ADR-0053; may require an amendment record depending on the final owner ruling)

## 0. What this document is (and is not)

0.1 **It is** a structured research brief covering the ten phases in the owner's directive. Facts were verified against primary or near-primary sources on 2026-09-22 (source list in the appendix). Interpretation is marked as interpretation.

0.2 **It is not** a decision, a ranking, or a recommendation. Per the directive, no option is promoted. Where a comparison looks lopsided for STEMMA, it is reported as observed fact, not as advocacy.

0.3 **Record-keeping note (transparency).** ADR-0053 recorded the owner's quick answers on 2026-09-22 (publisher = individual Sajan; domain = w3id.org; canonical keeps `stemma:` URN with HTTP projection at R6). The owner has now re-opened (b) and (c) for slow research. Nothing in the canonical layer depends on those answers — no IRIs have been published, no w3id PR has been filed. The correct end-state record after the owner reads this brief is one of: **reaffirm** ADR-0053, **amend** it, or **supersede** it with a new ADR — all three are first-class in this repo's ADR protocol. ADR-0053 will not be quietly rewritten.

---

# Phase 1 — Explain the problem

## A. What exactly are we deciding?

The single-sentence question ("permanent, globally dereferenceable identifiers?") decomposes into these practical architectural choices, separable and answerable independently:

1. **Identity policy** — Do STEMMA entities have identities that never change even if their representation changes? *(Already decided and enforced: yes. `stemma:phys.metre` is immutable; curation rule blocks reuse.)*
2. **Identifier syntax** — Are canonical IDs opaque, human-meaningful, namespaced? *(Already decided: URN-style `stemma:<namespace>.<slug>`.)*
3. **Global uniqueness authority** — Is the ID string globally unique by construction (a registered scheme/namespace) or unique only by STEMMA's own discipline?
4. **Dereferencing** — Can a machine that holds only the ID string obtain data about the entity over standard protocols ("resolvable")?
5. **Stability of the resolution endpoint** — If hosting moves (GitHub → elsewhere), does the resolution path survive?
6. **Publication identity** — Are *releases/artifacts* (exports, JSON-LD dumps, signed bundles) identified separately from *entities*? (Almost certainly yes — different PID class.)
7. **Version identity** — Do versions of an entity need their own identifiers?
8. **Governance** — Who can mint, deprecate, merge; what promises are made to embedders.
9. **Organization/ownership** — Under whose name are promises made (individual → foundation → consortium).

Only (3), (4), (5), and partly (9) are open. The rest are either already answered by the existing architecture or are policies to write down, not infrastructure to buy.

## B. What if STEMMA does nothing special?

Keep `stemma:` URNs as the only identity, publish exports with them, never mint HTTP IRIs.

**Capabilities retained (all existing):**
- Deterministic identity across rebuilds; joins/lookups inside STEMMA and by any consumer who stores the URN string.
- Valid RDF: URNs are legitimate IRIs; `knowledge.jsonld` can use `stemma:phys.metre` as subjects without any HTTP layer.
- Content negotiation, SKOS/BFO/QUDT mappings all still work with URNs as subjects.

**What is lost:**
- **Machine fetchability**: a third-party crawler/processor that encounters `stemma:phys.metre` cannot, from the string alone, retrieve STEMMA's data about that entity (no protocol, no resolver). Human discoverability degrades the same way ("look it up" requires special instructions).
- **FAIR F1/A1 standing** (see Phase 9): the ID is unique and persistent by convention, but not resolvable — the property the GO FAIR Foundation explicitly adds to F1 ("GUPRI").
- **Linking economy**: many Linked-Data pipelines auto-dereference; a URN silently drops out of such flows.
- **Institutional promise**: nothing external signals "this string is a commitment", which is exactly what makes strangers comfortable embedding it (contrast: ORCID iDs, DOIs, Wikidata Q-ids function as citation-grade names because their resolution path is operationally maintained).

Nothing breaks if STEMMA stays here forever. The loss is opportunity (external embedding/citation), not correctness.

## C. What if identifiers are HTTP IRIs?

Mechanically, only the outer string changes: `https://something/entity/phys/metre` instead of `stemma:phys.metre`. What changes in substance:

- The string now doubles as an **actionable locator**: any HTTP client on Earth can fetch data "about" it (that's the difference between a URI used as *name* and as *name+address*).
- This creates the long-game problem: the IRI combines **identity** and **address** in one string. If the address (domain/host) ever changes, every stored copy of the IRI in the world still points at the old host. The whole persistent-identifier industry exists to manage this one tension — either by keeping the host alive forever (own domain), or by inserting a **stable indirection layer** (resolver) whose address is more durable than any hosting (w3id, ARK/N2T, DOI/Handle, purl.org).
- It also creates the **linked-data convention problem**: content negotiation (303-redirect to HTML for humans, JSON-LD for machines) is expected practice, so the publication layer gains real engineering obligations (see Phase 3 under "responsibilities").

## D. What does "permanent" realistically mean?

No technical artifact is permanent. Five different claims hide inside the word, and they have different owners and different failure modes:

| Claim | Owner | How it fails |
|---|---|---|
| **Stable identity** (the logical thing stays "the same thing") | STEMMA governance (sole owner today) | Semantic vandalism: reusing an ID for a different concept. *Already prohibited by STEMMA's curation rule.* |
| **Persistent resolution** (the string keeps resolving) | Resolution infrastructure operator | Operator dies, means-testing: OCLC → Internet Archive handover of purl.org (2016-09-27) is the kind of thing that can *succeed* (as it did) |
| **Organizational commitment** (somebody keeps fixing the redirects) | Publisher of record | Founder disappears; org renamed; unfunded dormancy |
| **Infrastructure availability** (DNS, certs, hosting, the web stack itself) | Whoever runs the servers | Beneath any of this: the web itself surviving decades |
| **Semantic stability** (the IRI keeps meaning the same concept) | STEMMA governance | Meaning drift: unit redefined, concept split, historical entities retired |

Harshly true framing (interpretation): a persistent identifier is a **social contract with an SLA approximated by community practice**, not a mechanism. The best infrastructure in the world cannot enforce semantic stability; the best governance in the world cannot force w3id.org's webserver to come online tomorrow. Mature practice therefore **separates** the layers so that each can be fixed independently — which is precisely the architecture you'd want regardless of which resolution service you chose.

## E. What does "globally dereferenceable" actually buy? (concrete)

- **A researcher** citing `stemma:phys.metre` in a PDF: with URN-only, the citation is an inert string; with a dereferenceable IRI, readers (and indexing crawlers) land on STEMMA's record. Citations become actionable.
- **LearningHub** consuming `exports/knowledge.jsonld`: works equally with URNs (parsing) — but its *link-out* feature ("open this concept") only works web-natively if the ID is an HTTP IRI.
- **PROFESSOR-J / JARVIS** running RAG w/ citations (IC-DERIVED-CONSUMER-001): same story — internal resolution is trivial with URNs; *external* presentation/citation benefits from IRIs.
- **Another knowledge graph** (e.g., a university QA pipeline) doing entity linking: auto-dereference pipelines (common in Linked Data tooling) will *discover* your SKOS mappings only through HTTP IRIs. URN graphs get found via manual import only.
- **A future STEMMA API**: an API is itself the resolution backend. Dereferenceable IRIs make the API's URLs *be* the entity identifiers (one string, two uses) instead of maintaining a lookup table.

---

# Phase 2 — The option space (described, not ranked)

**Option A — STEMMA-defined non-HTTP identifiers (status quo).** URN-style `stemma:<ns>.<slug>`. Zero infrastructure. Identity+lifetime policy enforced in-repo. Not web-actionable from the bare string. Coexists with every other option (it can always be wrapped).

**Option B — STEMMA-owned HTTP domain.** Buy `stemma.<tld>` (availability/choice untouched here — example only). Publisher controls DNS + hosting; IRIs are the first-class address. Recurring cost + renewal duty; the domain itself is a thing an organization must continuously own. If the org lapses, domain lapses → everyone's embedded IRIs dead (unless the community mirrors, as purl.org/IA did for its namespaces).

**Option C — w3id.org.** Community consortium redirect service (detailed in Phase 3). You get `https://w3id.org/stemma/...` — a stable, consortium-backed host whose only job is 30x-redirecting to wherever you point it. Redirect rules are yours, in git, changeable by PR.

**Option D — ARK (ark: scheme + n2t.net).** Library/archive-grade PID scheme (IETF draft `draft-kunze-ark`). You request a free **NAAN** (Name Assigning Authority Number) from the ARK Alliance (arks.org), self-mint opaque names forever, and resolution routes via the **N2T.net** meta-resolver's NAAN registry to *your* resolver (or you register n2t itself as your resolver prefix). Free; widely embedded in national libraries/archives (BnF: `ark:/12148/...`, Smithsonian, UC libraries); resolver host is swappable by design (NMA is disposable).

**Option E — DOI / Handle.** Indirection built on the Handle System (RFC 3650/3652) resolved centrally at doi.org, minted only through accredited registration agencies with fees and mandatory metadata schemas. DataCite's 2024 fee model: ~2.000 €/yr membership + 500 €/yr org fee + tiered per-year DOI costs (≈0,80 € each at low tiers); Crossref analogous for scholarly literature. Zenodo/Dryad/figshare mint free dataset DOIs as repositories. **Fit**: superb for *release snapshots and publications* (each STEMMA data release could get a DOI for free via Zenodo's GitHub integration); structurally wrong for *per-entity* IDs (DOIs are registered objects with deposit metadata, minted per act of registration — you don't mint one DOI per `stemma:phys.*` term without nonsense overhead).

**Option F — Other genuinely relevant mechanisms:**
- **n2t.net as a general meta-resolver**: N2T resolves *any* kind of name (ARK, DOI, URN, Handle, 900+ compact identifier types, harmonized with identifiers.org at EMBL-EBI). Even if STEMMA chose w3id or own-domain, nothing stops `stemma:` compact names from being registered as a compact-identifier prefix later — an *addition*, never a prerequisite.
- **purl.org (legacy precedent)**: OCLC's original PURL service, handed to the Internet Archive in 2016 and still resolving — kept here only as evidence about resolver lifecycles, not as a candidate (new namespaces are not the point; w3id supersedes it practically).
- **Excluded as out of scope (documented so the brief is complete)**: ORCID (people), ROR (organizations), SWHID (software artifacts), ISBN/ISSN (media), IGNS (samples). These address *adjacent* identity classes STEMMA will reference, not its own entities.

---

# Phase 3 — w3id specifically (researched 2026-09-22)

Sources: w3id.org site content (primary, mirrored in forks), perma-id/w3id.org repo, W3C Perma-ID Community Group.

1. **What it is**: an HTTPS-only HTTP 30x redirect service run for the web by the W3C Permanent Identifier Community Group. It stores redirect rules as Apache `.htaccess` files in a public GitHub repo (`perma-id/w3id.org`, `ids/<slug>/`). One directory = one top-level namespace (e.g. `w3id.org/stemma/`).
2. **Who operates it**: a named consortium of organizations pledged to run it (currently listed: Digital Bazaar, 3 Round Stones, OpenLink Software, Applied Testing and Technology, Bosatsu Consulting, KurrawongAI; previously also Openspring, SURROUND Australia). W3C hosts the site and otherwise has **no** management role (their explicit disclaimer).
3. **Obtaining a namespace**: fork the repo, add `ids/stemma/{.htaccess,README.md}` (rules + maintainer contact), open a PR; maintainers review (they may reject overly generic/confusing names). Alternative: email the public-perma-id mailing list and an admin creates it.
4. **STEMMA's responsibilities**: (a) keep the redirect targets working; (b) keep maintainer contact current; (c) file PRs to update rules; (d) host the actual content the redirects point to. w3id provides *no hosting*: it is a switchboard only.
5. **Membership requirement**: none. Using a namespace requires no joining, no consortium, no contract.
6. **Cost**: none observed. Free service.
7. **Stopping later**: you can edit/empty/remove your `.htaccess` via PR anytime (deleting the directory can also be PR'd but is discouraged for public namespaces in wide use — social norm, not mechanism).
8. **Published IDs if you stop**: if you stop refreshing target hosts, redirects break at *your* end (w3id keeps redirecting to your last target — dead links are yours); if you abandon the namespace, the community's stated practice (per the site) is to mirror/repair redirects for widely-used namespaces to protect the rest of the web, but this is customary, not contractual.
9. **Redirect w3id namespace → a future STEMMA domain**: yes, trivially — it's your `.htaccess`; point the whole tree at `https://stemma.<tld>/entity/$1` with one rule. The *published string* (`w3id.org/stemma/...`) itself never changes; the HTTP resolution path does. **Reversibility between hosts = normal, low-cost.** Rebranding the string itself (w3id.org/… → your own domain) is the irreversible step in every architecture (old strings live in other people's data).
10. **STEMMA org changes (individual → foundation)**: nothing structural — the namespace belongs to its maintainer-of-record (README/PR authority), which can be updated ($org handle, e-mail). There is no per-namespace contract or registry of legal ownership; continuity of *someone with git PR ability* is the de facto tenure mechanism. This is a modest governance exposure (no formal transfer instrument), mitigated by keeping multiple maintainers (e.g., future org GitHub account).
11. **w3id infra changes**: the consortium model + open repo of rules means the *mapping data itself is public and forkable*; in the worst case any mirror could serve identical redirects (as with purl.org's data being preserved at the Internet Archive). HTTPS-only today; no evidence of instability; the repository has CI (build status) and active forks.
12. **Practical risks**: (a) slug claimed by someone else first (checked free on 2026-09-22); (b) admin rejection of generic names (6-char "stemma" is plausible; README should explain the project); (c) the service's persistence rests on a *social* consortium — strong track record (running since ~2015), but not a commercial SLA; (d) no content hosting, so all real obligations remain yours; (e) nothing prevents a future hostile fork of the redirect service — trust is anchored in DNS + consortium, like the rest of the web.

---

# Phase 4 — Alternatives investigated per criteria

(Each row of the comparison table in Phase 10 §3 compresses this section. Here: per option.)

**B — Own domain**
- Control: you (individually today). Cost: domain + hosting, ~10-50 USD/yr, continuous. Requirements: DNS, TLS, a redirect/content host. Redirects: full control. Repo migration: survive trivially (it was never tied to the repo). Org change: survives only if domain ownership transfers (legal, not technical). Entities: suitable. Datasets/releases: suitable. Lock-in: none beyond the domain itself. Migration difficulty: impossible to migrate *away from* without breaking embedded IRIs — you must own the domain forever. Coexists with `stemma:` URNs: yes (projection mapping).

**C — w3id**: see Phase 3. Adds: works with any host migration (the entire design), survives org change in practice (PR-based maintainer transfer), zero infra of your own, free.

**D — ARK + n2t.net**
- Control: you mint names under your NAAN; ARK Alliance (community, LYRASIS-supported) stewards spec + registry; N2T (CDL) runs the global resolver. Cost: free NAAN; no per-ID fees. Requirements: none centrally — you can register n2t.net itself as your resolver prefix (zero server to run) or run your own resolver (e.g., `https://stemma.example/` style, registered in the NAAN registry, e.g. `redirect: http://libraries.ucsd.edu/ark:$id` pattern). Redirects: NAAN-level routing is updateable; name-to-target resolution is yours. Repo/org migration: survives — the whole point; NMA host is explicitly disposable. Entities: **very** suitable (BnF identifies manuscript pages: `ark:/12148/btv1b8449691v/f29`). Releases: suitable. Lock-in: minimal — ARK is decentralized by design; the NAAN registry can route your NAAN elsewhere. Migration from ARK to another scheme = same "published strings are sticky" caveat. Coexists with `stemma:`: yes (would map `stemma:phys.metre` → `ark:/<naan>/<name>` at projection).

**E — DOI/Handle**
- Control: mint only via RA (Crossref/DataCite via consortium or repository intermediaries). Cost: real (DataCite: 2.000 €/yr + 500 € + tiered; or free per-DOI via Zenodo for deposits). Requirements: mandatory metadata (DataCite schema); deposit workflow. Redirects: DOI targets updateable via RA APIs. Repo migration: yes (that's their job). Org change: robust (RA records). **Entities: no** (registration-object model, per-DOI semantics, metadata apparatus designed for citable *packages*, not per-term concepts — you'd be misusing the mechanism; you can't mint millions without absurd ceremony). **Datasets/releases/publications: yes**, and free via Zenodo/GitHub. Lock-in: RA-mediated but extremely standard. Coexists with `stemma:`: yes, orthogonally.

**F1 — n2t as compact-identifier lane**: free registration of a prefix via identifiers.org/n2t harmonized registry; routes to your resolver. Potential *complement* to any choice (makes `stemma:phys.metre` resolvable through a global redirector even if it never becomes an HTTP IRI — precedent: identifiers.org/N2T harmonization paper, 600+ compact ID types).

---

# Phase 5 — How serious projects actually do it (problem → choice)

**Entity-level PIDs:**
- **Wikidata** — problem: planet-scale collaborative entity graph needing citable, resuable names. Choice: own institution-backed domain (`wikidata.org/entity/Q42` concept URI; note: concept URIs use `http://`, deliberately frozen scheme; content negotiation via `Special:EntityData`). Persistence is *community-governance* practice, explicitly not contractual (per PID4NFDI cookbook). Q-ids are opaque; namespaces include `entity/`, `prop/direct/`, `wiki/` distinguishing thing vs page — the architecture separates concepts from documents exactly like R6's projection design.
- **OBO Foundry** — problem: ~200 biomedical ontologies needing stable term IRIs independent of each ontology's website. Choice: **their own resolution hub** `purl.obolibrary.org` — technically the *same pattern* as w3id (`.htaccess` files per ontology in a GitHub repo, 303-redirects per httpRange-14, CNAME so the resolver can be swapped) but self-governed under the Foundry with a written ID policy (namespace allocation, CURIE↔URI mapping, versioned release PURLs). This is also the most relevant precedent **inside STEMMA's own design**: ARCHITECTURE-V2 anchors mappings to BFO IRIs, which live at `purl.obolibrary.org`.
- **Library of Congress** — problem: authority files as linked data for centuries. Choice: own institutional subdomain `id.loc.gov` — LC itself *is* the persistence guarantee.
- **DBpedia** — own domain (`dbpedia.org/resource/…`), institution-maintained (OpenLink + community).
- **schema.org** — own domain governed by a steering group backed by founding sponsors (Google/Microsoft/Yahoo/Yandex lineage); shows a *vocabulary* surviving via consortium-of-sponsors governance rather than resolver machinery.
- **QUDT** — own domain `qudt.org` (QUDT units are already referenced in ARCHITECTURE-V2's unit allowlist as IRIs/anchors).
- **Dead or dormant (the cautionary set)** — FOAF's `xmlns.com/foaf/0.1/` (widely embedded, resolution flaky for years — a vocabulary whose domain maintenance lapsed); BBC Things, GACS (`id.agrisemantics.org`), GAMECIP (`gamemetadata.org`) — all listed by Wikidata's URIs-in-MARC project as **defunct sources** whose URIs no longer resolve: one-project domains die with the project. This is the empirical heart of Phase 7's scenario 7.

**Non-entity identity classes (separated in practice, as you asked):**
- **Datasets**: DataCite DOIs via repositories (Zenodo — free; Dryad; figshare; institutional Dataverses + Handles). Problem: citability + archival. Choice: DOI/Handle because scholarly tooling indexes them.
- **Release/package versions**: Zenodo's GitHub integration mints a DOI per release (plus a concept DOI for the series) at zero cost — a software version is a registration event, which is DOI's natural shape.
- **Publications**: Crossref DOIs (publishers).
- **People**: ORCID iDs (a PID for people, operated as a nonprofit with its own resolution; research ecosystem standard).
- **Organizations**: ROR (open registry for research orgs).
- **Observation (interpretation, widely corroborated)**: no serious project stuffs per-term concept PIDs into DOIs, and nobody expects per-dataset DOIs to be dereferenceable vocabulary terms. **Entity PIDs and release PIDs are two different systems held together by metadata.**

---

# Phase 6 — STEMMA-specific consequences

## 6.1 What changes in each identity/hosting accident

Given the existing design (canonical Markdown/YAML; `stemma:` IDs; everything else derived), and **pk** the question layered as identity → publication → resolution:

| Accident | Canonical impact | Publication impact | Resolution impact |
|---|---|---|---|
| GitHub org/repo rename | None (IDs don't embed the host) | Rebuild exports; update docs links | Redirect target must be re-pointed wherever resolution lives |
| Hosting change (Git→self-host) | None | Rebuild | Re-point resolver rules |
| DB/file format change | None (canonical is md+yaml; format changes are migrations, IDs stay) | Regeneration path changes | None if strings stay |
| Canonical format change (urn→CURIE etc.) | **High** — this is the one thing that must not change; the rest of the design protects it | New mapping row | Mapping file updated, strings unchanged for consumers |
| Org formation (individual→foundation) | None | Publisher metadata updated in projections | Maintainer contact/PR authority transfer |
| Dormancy 10y + revival | Content preserved in git | Host may be gone → rebuild | If resolution layer was *someone else's* (w3id/N2T), it kept redirecting to a dead target the whole time; revival = re-point. If resolution was *your own domain*, lapse = death unless mirrored. |

## 6.2 External consumer behavior

- LearningHub/PROFESSOR-J/JARVIS consume exports; entity strings in their databases are sticky *forever* regardless of resolution — that's why the immutability rule sits in the canonical layer, not in the resolver.
- A university linking an entity: with HTTP IRIs + stable resolver, their links keep working through STEMMA's host chaos as long as *STEMMA or a mirror* maintains the target map; with URN-only, their data is safe but inert, and a revival of STEMMA on a new host is invisible to them.
- A research paper citing a million entities (Phase 7, scenario 8): with DOI-per-release they also have a *citable snapshot*; with entity IRIs they have clickable references; with URNs they have textual names only.

## 6.3 Canonical contamination

No. The escape hatch is structural: **resolution is a projection concern, canonical identity is not**. Concrete design (mirrors OBO's CURIE↔PURI mapping): canonical files keep `stemma:phys.metre`; R6 emits `@context` mapping `"stemma": "https://w3id.org/stemma/"` (or `https://n2t.net/ark:/<naan>/`, or any future base) so JSON-LD expansion produces HTTP IRIs *at publication time only*. Neither validators nor source-of-truth files ever contain the host. The `stemma:` scheme remains the join key for consumers who don't care about the web. This separation was already asserted in ADR-0053(c) and ARCHITECTURE-V2; this brief confirms independent practice (OBO, Wikidata) uses exactly this layering.

## 6.4 Governance promises (independent of host choice — MUST be written down regardless)

Whatever STEMMA publishes, the following policies define the *semantic* half of persistence and are host-independent:

1. **Never delete, never reuse** (already enforced for canonical IDs; must be reaffirmed for published IRIs).
2. **Deprecation ≠ removal**: deprecated entities keep their ID + a `status: deprecated` and optional `superseded_by:` pointer; importers honor the flag.
3. **Merge**: the absorbed ID stays, marked `merged_into:`; resolution shows a redirect note; never repurposed.
4. **Split**: original ID keeps the *historical union* semantics marked `split:` pointing to new IDs; original is never silently narrowed.
5. **Meaning authority**: the canonical layer + review chain (CONCEPTS.md review states) is the only meaning authority; AI extraction never mints or redefines IDs (governance.md ADR-050).
6. **Version identity**: entity versions are content-addressed by export snapshots (integrity manifest, EVID records); DOI-per-release gives the *citation-grade* version handle if/when wanted.

(These are policies to draft — a small `docs/IDENTIFIER-POLICY.md` is advisable regardless of the resolution decision; flagged here, not executed, since the directive was research-only.)

---

# Phase 7 — Failure scenarios × behaviors

Format per scenario: A = URN-only (no HTTP), B = own domain, C = w3id, D = ARK/n2t, E = DOI-per-release (orthogonally relevant).

**S1 — Move GitHub → self-host.** A: nothing changes for IDs; consumers unaffected. B/C/D: re-point one redirect config (DNS for B; `.htaccess` PR for C; NAAN-registry/resolver config for D). E: release DOIs re-pointed via RA. *All survive identically; the edit locus differs.*

**S2 — GitHub org rename.** Same as S1, plus links-in-docs churn (already handled by the docs-impact checker inside the repo). IDs/artifacts unaffected everywhere.

**S3 — Foundation forms in 5 years.** A: publisher metadata changes in exports; URNs stable. B: domain ownership transfer is a **legal/registrar process** — must be planned; failure mode: domain still in a departed founder's personal account. C: README/PR authority updated; no legal object exists. D: NAAN reassignment per ARK Alliance process (community-managed, precedent: NAAs change loci over years). E: DOIs stable regardless.

**S4 — Founder no longer maintains.** A: inert but unbroken. B: **worst** — renewal lapse within years kills every embedded IRI (see the defunct-domain set in Phase 5). C: redirects continue (host not yours); targets rot only if content hosting was founder-hosted; consortium/mirror norms apply for heavily used namespaces. D: NAAN routing persists at n2t; your resolver (if any) may die — if you registered n2t as the resolver prefix, resolution still works to your last target. E: DOIs live at the RA + Handle — the most institutionally survivable of all; the releases outlive everyone.

**S5 — Domain change.** A: no-op. B: **only survivable for future content**; old domain can 30x to new as long as owned, but published strings live at old host — you carry the old domain forever (or lose embedded strings). C/D: non-event for published strings (strings name w3id/n2t hosts). E: non-event.

**S6 — Funded public infrastructure.** A: fine but underpowered politically (open-science reviewers expect resolvable PIDs; see Phase 9). B: fine with institutional guarantee. C: fine; common pattern for EU/product vocabularies. D: exemplary (library-grade). E: expected for data releases.

**S7 — 10 years dormant, revived.** A: rebuild everything, URNs re-serve. B: domain almost certainly gone → **every embedded IRI permanently dead** (BBC Things/GACS/GAMECIP outcome). C: w3id host kept redirecting to targets that may have died with you; revival = re-point; namespace likely preserved if it was used. D: same shape via n2t (NAAN registry persists; your resolver prefix re-registered). E: releases retrievable via DOI even with everything else gone (Zenodo's archival mission + DOI resolution); revival has a citable anchor. *Notable: the dormant-revival case is where the "someone else's stable host" architectures strictly dominate own-domain.*

**S8 — External paper cites millions of entities.** A: citations are strings; checkable only against the repo. B/C/D: all clickable through their stack; C/D degrade more gracefully than B under dormancy. E complements every option with release-level DOIs for the snapshot the paper actually used (provenance for citations = A2/version integrity requirement already in STEMMA's design).

---

# Phase 8 — NOW vs EARLY vs LATER

**MUST DECIDE NOW (already decided, reaffirmed here for the record):**
1. *Identity policy*: immutable, never-reused, machine-enforced `stemma:` IDs. (Enforced; this is the irreversible core. Everything else hangs off it.)
2. *Meaning authority*: canonical layer + human review only (enforced: CONCEPTS.md states, audit trail).
3. *Semantic governance policies* (§6.4: deprecate/merge/split) — must exist before **any** external consumer embeds IDs; cheap now, retrofitting is rude forever after. (Partially recorded today; consolidation into one policy doc is small work.)

**SHOULD DECIDE EARLY (provisional / cheap):**
4. *Release-level identification*: whether releases get DOIs (Zenodo) — independent of entity-PID choice; can be adopted at any release event with zero prior commitment.
5. *Namespace squatter protection* (cheap, optional): if w3id (or any shared namespace) is plausibly in the final answer, **claiming** the namespace early is a one-small-PR insurance policy. Claiming ≠ committing to it as the final scheme; the risk calculus documented in ADR-0053 stands (slug free as of 2026-09-22). This is the *only* item with real deadline pressure; its cost is ~30 minutes.

**CAN DEFER (safely, to R6):**
6. *The resolution base itself* (own domain / w3id / ARK / hybrid). Reason it's deferrable: under the projection-layering design (§6.3), canonical stores only `stemma:` URNs; the HTTP base is a single line in the projection's `@context`/mapping file at R6 publication time. Nothing embedded in third parties exists yet (corpus: a few seeded entities per ADR-0052; exports are internal). The published-string stickiness problem **has not yet begun**, so the real irreversibility point is not "choose a resolver" but "the moment external publication happens".
7. *Content-negotiation engineering* (303/Accept dance, per-format serializers) — belongs to R6 execution.

**Honest headline (interpretation):** the architecture already did the hard part. The remaining "big" decision is, in engineering terms, choosing where one redirected URL lives — which is *reversible between stable hosts* (B↔C↔D as long as the published string itself doesn't change, i.e., pre-R6). After publication, the chosen *string* is sticky; the host behind it stays movable.

---

# Phase 9 — Funding / open-science implications (factual, no advocacy)

- **FAIR F1** (GO FAIR Foundation; the 2016 Wilkinson et al. Nature/SciData paper): data must have **globally unique and persistent identifiers never reused**, and GO FAIR explicitly adds *resolvability* ("GUPRI"); the FIP model expects an identifier service providing global uniqueness + persistence policy + machine resolution. URN-only satisfies two of the three.
- **A1**: retrievability by identifier via an open free standardized protocol (= HTTP for the web; DOI/Handle resolve over the same).
- **A2**: metadata accessible even when the data is gone — the "tombstone" principle; DOI registration agencies operationalize this (deposit metadata persists after target death).
- **Funding/RDM practice**: funder data-management plans (EU Horizon, NWO, NSF NIH DMS policy, etc.) routinely request PID strategies for datasets and increasingly for software (software citation initiatives), with repositories (Zenodo et al.) as the normal zero-cost channel. Persistent-identifier competence is scored language in those contexts.
- **What W3ID specifically adds to all this: nothing unique** (per directive — and it's true). It satisfies "resolvable" for entity/vocabulary IRIs cheaply; DOI-for-releases covers scholarly citability; ARK covers the library channel. These benefits attach to the *combination* (resolvable entity IRIs + DOI'd releases + provenance), not to any one brand of resolver.

---

# Phase 10 — Decision brief (not a decision)

## 1. The actual architectural question

> STEMMA already has immutable canonical identities. The real question is: **at publication time (R6), under which resolvable string-and-host pair do STEMMA entities first become visible to machines that are not STEMMA — and what promise-maintenance topology (self, community consortium, library alliance, paid RA) makes that pair most likely to outlive STEMMA's hosts, repos, and orgs, while keeping canonical files purely Markdown+YAML and every escape route (to another host, another scheme, additional lanes like n2t compact IDs or DOI'd releases) open?**

## 2. Terminology (compact)

| Term | Meaning |
|---|---|
| **Entity identity** | The "sameness" of a thing across time — policy, not syntax. |
| **Identifier** | A string assigned to an identity. |
| **IRI/URI** | Identifier syntax w/ global-collision rules; URLs are the locator subset. |
| **Namespace** | A delegated collision-avoidance partition (scheme prefix, host path, NAAN). |
| **Resolver** | Service that maps an identifier to a location; a *switchboard*. |
| **Hosting** | Where data files actually live; independent of identifiers. |
| **Persistent identifier** | Identifier + social/operational commitment of durable mapping. |
| **Version identifier** | Identifier for a state of an entity/artifact (hash, revision, release DOI). |
| **Dataset DOI** | Registration-object PID for a deposited package with metadata. |

## 3. Options — neutral comparison

| Dimension | A: URN-only | B: Own domain | C: w3id | D: ARK+n2t | E: DOI/Handle |
|---|---|---|---|---|---|
| Entity-level fit | ✅ (inert) | ✅ | ✅ | ✅ | ❌ |
| Release/dataset fit | n/a | 😐 | 😐 | 😐 | ✅ |
| Resolve from string | ❌ | ✅ | ✅ | ✅ | ✅ |
| Survives host/repo moves | ✅ | ✅ | ✅ (by design) | ✅ (by design) | ✅ |
| Survives org failure | ✅ (strings) | ❌ worst | ✅ | ✅ | ✅ |
| Survives 10y dormancy | ✅ | ❌ | ✅/⚠️ targets-your-problem | ✅/⚠️ | ✅✅ |
| Infra you must run | none | DNS+host+TLS | none | none (n2t-as-prefix) or resolver | none |
| Cost | 0 | recurring | 0 | 0 | fees or repo-mediated free |
| Scheme-string stability over decades | ✅ | depends on renewal | consortium track-record 10+y | alliance+CDL, 20+y | DOI Foundation, 25+y |
| Borrowed trust in your string | none | self | community | library world | scholarly world |
| Published string later rebrandable | — (no string) | ❌ | ❌ | ❌ | ❌ |
| Path out to another host | n/a | DNS change | `.htaccess` PR | registry/resolver config | RA target update |

## 4. Irreversibility, precisely

- **Strictly irreversible**: (a) changing/reusing an entity's identity after anyone embeds it (forbidden in-repo, and it's what the whole architecture protects); (b) the exact *published string* once external systems store it — every option locks this; only timing differs, and STEMMA is pre-publication, so this lock hasn't engaged.
- **Expensive-but-possible**: re-pointing published IRIs at a new host (works in B/C/D/E by design; the infrastructure exists precisely for this).
- **Cheaply reversible until R6**: every choice of resolution base — the mapping is one `@context` line. This includes *abandoning* the recorded R5(w3id) answer with zero migration cost, because nothing was ever published under it.
- **Asymmetric**: option B is the only one whose failure mode (domain lapse) is unrecoverable *for embedded strings*; every other option keeps a third party between STEMMA and the void.

## 5. What the research did NOT resolve

- Whether any specific funder STEMMA might ever approach demands a specific scheme (no mandate found; FAIR F1's *resolvable* clause is the strongest generic pressure).
- w3id consortium's 50-year reality (social bet like the rest of the web; their rule-set is public and forkable, softening the worst case).
- Whether squad-claiming the slug is worthwhile (cost: trivial; the answer changes nothing architecturally — see §8.5).
- STEMMA's eventual **publication volume** (10² entities vs 10⁶) — ARK's opaque-name design and B/C's path routing all scale fine; only DOI-per-entity would not (rejected structurally).

## 6. A process for the owner (not an outcome)

The record-keeping after this brief, your call:

- **Reaffirm** ADR-0053 as written (w3id staged) — one-line reaffirmation note added to the ADR after reading this brief; or
- **Amend** ADR-0053 (same three sub-decisions, different answers, e.g. "defer claim to R6" or "evaluation continues") — an amendment note + status marker; or
- **Supersede** — new ADR-0054 recording a different scheme choice with this brief as evidence.

Each is honest recording practice; the repo's protocol supports all three. Nothing in this brief *requires* a decision event before R6 (Phase 8 §6).

---

# Appendix — Sources (accessed 2026-09-22)

Primary / near-primary:
- w3id.org service description & management/naming policy — https://w3id.org/ ; repository: https://github.com/perma-id/w3id.org (incl. `ids/examples`)
- W3C Perma-ID Community Group — https://www.w3.org/community/perma-id/
- OBO Foundry ID policy & Principle 3 — https://github.com/OBOFoundry/OBOFoundry.github.io/blob/master/id-policy.md ; http://obofoundry.org/principles/fp-003-uris.html ; resolver architecture note — https://github.com/OBOFoundry/Operations-Committee/wiki/OBO-PURL-Domain
- ARK scheme (IETF draft) — https://www.ietf.org/archive/id/draft-kunze-ark-34.html ; ARK Alliance — https://arks.org/ ; NAAN registry (text) — https://n2t.net/e/pub/naan_registry.txt ; LYRASIS ARKs FAQ — https://wiki.lyrasis.org/display/ARKs/ARK+Identifiers+FAQ ; CASRAI ARK↔DOI guide — https://casrai.org/guides/ark-identifiers-explained-persistent-ids-beyond-doi-orcid-ror (2026)
- N2T resolver + harmonization w/ identifiers.org — https://legacy-n2t.n2t.net/ ; Scientific Data paper — https://www.nature.com/articles/sdata201829
- DataCite fee model (2024) — https://datacite.org/fee-model/
- FAIR principles — https://force11.org/info/the-fair-data-principles/ ; F1/GUPRI interpretation — https://www.gofair.foundation/f1 ; Wilkinson et al. — https://www.nature.com/articles/sdata201618
- Wikidata Linked Data Interface (concept URIs, content negotiation, http scheme) — https://www.wikidata.org/wiki/Wikidata:Data_access ; PID4NFDI cookbook (Wikidata ID section; ARK section) — https://pid4nfdi-training.readthedocs.io/
- Cautionary evidence — defunct-URI register: https://www.wikidata.org/wiki/Wikidata:WikiProject_URIs_in_MARC (BBC Things, GACS, GAMECIP); purl.org OCLC→Internet Archive handover: https://www.oclc.org/research/areas/data-science/purl.html ; inkdroid.org/2021/12/16/purl/
- In-repo anchors — ARCHITECTURE-V2 §7 (BFO/QUDT/Wikidata anchors); ADR-0053 (recorded provisional answers); schemas `stemma:` patterns (concept.schema.json).

*Method note: facts not directly cited are from the in-repo record (ADR-0052/0053, schemas, PROGRESS) or are plainly labeled interpretation.*

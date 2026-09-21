# Changelog

## [4.0.0](https://github.com/Er-Sajan-PLG/STEMMA/compare/v3.0.0...v4.0.0) (2026-09-21)


### ⚠ BREAKING CHANGES

* **breaking:** stemma: namespace, colon-free filenames, single relationship source
* **export:** export_version 0.1 -> 1.0. schema/export.schema.json defines the shape and validate.py enforces it before writing. entities[].relationships stays as a deprecated projection until 2.0 (E1.7). exports/knowledge.compat-0.1.json (entities-only, stamped 0.1) is emitted while legacy_export_version is set, for the STEM-TUITION adapter co-release. Removes the last version-literal fallbacks from derived exporters (ADR-0022). VERSION 2.0.0.

### Features

* **adapters:** first-party read-only Python adapter (SDK, CLI, local JSON API) ([fb8cf17](https://github.com/Er-Sajan-PLG/STEMMA/commit/fb8cf174a4b69dc7096f2984317be7c7010080c3))
* **adapters:** first-party read-only Python adapter (SDK, CLI, local JSON API) ([04dfb33](https://github.com/Er-Sajan-PLG/STEMMA/commit/04dfb333f6c010f6ce8dc098f22ae5e1825e4aa7))
* adaptive metadata extension registry (ADR-0017) + global grade-12 canonical content ([#9](https://github.com/Er-Sajan-PLG/STEMMA/issues/9)) ([f66b3af](https://github.com/Er-Sajan-PLG/STEMMA/commit/f66b3af2ca5d66084deb0b3162bb3237c909638a))
* add LearningHubSTEM v0.1 minimal seed with schema, validator, and export ([9071436](https://github.com/Er-Sajan-PLG/STEMMA/commit/90714361b85c532e9c9450c9551f0f65aa807b03))
* architecture v2 + contract 2.2.0 + strong CI + explorer + ingestion + all-STEM templates + embeddings RAG consumer export ([#47](https://github.com/Er-Sajan-PLG/STEMMA/issues/47)) ([ef9a315](https://github.com/Er-Sajan-PLG/STEMMA/commit/ef9a315412d94507af38124489b84303b45422b6))
* AXIOM kernel plan + Phase 0 hardening ([98283b8](https://github.com/Er-Sajan-PLG/STEMMA/commit/98283b84fbb68fa44ffe35a1e9c43db8814ddc6b))
* **curation:** E6.1 dependency-edge review campaign tooling + batches 01-04 ([4982099](https://github.com/Er-Sajan-PLG/STEMMA/commit/49820994e47499c8b5a704fff385b47d07da43f2))
* **domain:** enforce id-prefix/domain/path identity (ADR-0034) ([2027bdd](https://github.com/Er-Sajan-PLG/STEMMA/commit/2027bdd6612299d78d5d1866a69d84df40be0816))
* enrich seed entities for Phase 2 consumer proof ([5f9cce4](https://github.com/Er-Sajan-PLG/STEMMA/commit/5f9cce4bc53a0d6a64bb3af590d381d09001a90f))
* **explorer:** add relationship + cluster legend with fly-to-cluster ([a133135](https://github.com/Er-Sajan-PLG/STEMMA/commit/a13313574fbd6d519e0dc0ef0235e593bb95c5cf))
* **explorer:** consume export contract 1.x (require connections[], reject other majors) ([5dbc1be](https://github.com/Er-Sajan-PLG/STEMMA/commit/5dbc1be8c54355b79a04404d22f020aea3464df4))
* **explorer:** harden 3D graph init (WebGL try/catch, resize, fetch fallback) ([e19ec28](https://github.com/Er-Sajan-PLG/STEMMA/commit/e19ec28ea76001dec1676721adf5b26a44f3dce1))
* **explorer:** rework 3D knowledge-graph visualization and UI ([ad2eaf1](https://github.com/Er-Sajan-PLG/STEMMA/commit/ad2eaf1beb31135423b7f7b55c840888116e9867))
* **explorer:** seeded domain/topic cluster layout, persistent labels, shape-by-type nodes ([4ce5861](https://github.com/Er-Sajan-PLG/STEMMA/commit/4ce5861ee62258dca5ee9178d01e3f0688c219c5))
* **explorer:** sync + auto-update 3D visual to 224 entities with math domain ([#12](https://github.com/Er-Sajan-PLG/STEMMA/issues/12)) ([54dd37f](https://github.com/Er-Sajan-PLG/STEMMA/commit/54dd37f26d7a344bd8ded9e28919c7369327d5a6))
* **explorer:** tabbed concept inspector (Overview/Relations/Examples/Misconceptions) ([b86dbd9](https://github.com/Er-Sajan-PLG/STEMMA/commit/b86dbd94f9e88bda198fc93bffe6c6c1bafee473))
* **explorer:** upgrade 3D rendering with glowing mesh nodes, particle streams, glassmorphic UI, and HUD overlays ([0ac2077](https://github.com/Er-Sajan-PLG/STEMMA/commit/0ac2077a5fba64c27806adf5a1bdf35319949680))
* **explorer:** wire 3D/List view toggle so accessible list fallback works ([c79aeb3](https://github.com/Er-Sajan-PLG/STEMMA/commit/c79aeb3be55d61e493a19c7389078f3643f60a1f))
* **export:** contract v1.0 — connections and sources required (ADR-0023, gate G-A) ([8b62866](https://github.com/Er-Sajan-PLG/STEMMA/commit/8b6286688317102029efcace1af6a06f73d4038d))
* **export:** publish relation registry + vocabularies in contract v2.1 ([ef4c504](https://github.com/Er-Sajan-PLG/STEMMA/commit/ef4c50456c7930d4bd3797fa6848eba32d820873))
* **gate:** claim identity E4.3/E4.5, explorer connections-first E1.6, migrations log E5.5 ([a849f00](https://github.com/Er-Sajan-PLG/STEMMA/commit/a849f007878224d0b355e0d192064d2d05630fbf))
* **gate:** mechanize connections-only truth, registry integrity, deterministic exports ([19639a8](https://github.com/Er-Sajan-PLG/STEMMA/commit/19639a8b3d36997eda347f93aedf40ad37e5afc0))
* **gate:** plan v2 wave 5 — claim identity (E4.3/E4.5), explorer connections-first (E1.6), migrations log (E5.5) + E0 close-out ([2834435](https://github.com/Er-Sajan-PLG/STEMMA/commit/283443524ca77f44487d559c7e771730292e52d5))
* **governance:** Scope B open-source hardening (generality, ID immutability) ([#19](https://github.com/Er-Sajan-PLG/STEMMA/issues/19)) ([678be38](https://github.com/Er-Sajan-PLG/STEMMA/commit/678be38d316f9ef2fc4f6f09be06851fbd937d95))
* **ingest:** fail-closed Draft seam + schema-valid proposal path (ADR-0035) ([bbf7c13](https://github.com/Er-Sajan-PLG/STEMMA/commit/bbf7c13d2311d14a7fe8194212c02dd686075512))
* ingestion webapp, n8n orchestration, JARVIS-parity tooling ([#39](https://github.com/Er-Sajan-PLG/STEMMA/issues/39)) ([43a9d35](https://github.com/Er-Sajan-PLG/STEMMA/commit/43a9d35787b6339277b848a4a1730d488a49e438))
* ingestion/review webapp, Phase B trust & review activation, official Antigravity provider ([7e79c53](https://github.com/Er-Sajan-PLG/STEMMA/commit/7e79c538e3f454a8cd65c5bfd40fb7c4fe0559f3))
* **ingestion:** extract knowledge from PDFs/images/scanned docs into review-ready proposals ([#15](https://github.com/Er-Sajan-PLG/STEMMA/issues/15)) ([f6f864f](https://github.com/Er-Sajan-PLG/STEMMA/commit/f6f864fbc78628974ac633d1081c7bca0b8f2a65))
* **knowledge:** add equation-type entities and rebalance chemistry/biology/earth-space ([4654b98](https://github.com/Er-Sajan-PLG/STEMMA/commit/4654b98be7c7bf3f9a87bffa555e067f018d0034))
* **knowledge:** add equation-type entities and rebalance chemistry/biology/earth-space ([56b6fb5](https://github.com/Er-Sajan-PLG/STEMMA/commit/56b6fb576df08ca4d7c0756dbb9d8808fe6901b4))
* **knowledge:** complete multi-domain science graph (112 entities), reorganize domain/topic subfolders, and add 3D Interactive Explorer web app ([b2b2bfd](https://github.com/Er-Sajan-PLG/STEMMA/commit/b2b2bfd9cad50d8a2fdc3db85e7df3c93d1c96a6))
* **knowledge:** enrich all 124 entities with examples and key experiments ([6522d99](https://github.com/Er-Sajan-PLG/STEMMA/commit/6522d994a3223900aa8be3d7ac1bb1f2e147fc29))
* **knowledge:** enrich all 124 entities with examples and key experiments ([296f28d](https://github.com/Er-Sajan-PLG/STEMMA/commit/296f28d0159a85a683dd6a61140736baf9fe8b22))
* **knowledge:** enrich the grade-10 science knowledge graph ([03e8a79](https://github.com/Er-Sajan-PLG/STEMMA/commit/03e8a79701303576beddaa5970d9dc42e4f94c40))
* **knowledge:** strengthen knowledge graph with cross-domain and specific edge types ([b8b3f3b](https://github.com/Er-Sajan-PLG/STEMMA/commit/b8b3f3bdb4cfeabc56a10b374255284be3834a3b))
* **knowledge:** strengthen knowledge graph with cross-domain and specific edge types ([dba7e08](https://github.com/Er-Sajan-PLG/STEMMA/commit/dba7e08fd87dd0749a49eacd79c26e66c97c2fd3))
* **math:** add grade 10 core math domain with 27 entities ([c4c7aa4](https://github.com/Er-Sajan-PLG/STEMMA/commit/c4c7aa4460024400b273b4d58dc1a1ca3c7d0ce4))
* **math:** add grade 10 core math domain with 27 entities ([2273140](https://github.com/Er-Sajan-PLG/STEMMA/commit/227314015c47c6c4922cd5365dd3690fbc668882))
* Phase 0 - kernel_version, content_hash, SHACL report, concept enum sync ([6725c08](https://github.com/Er-Sajan-PLG/STEMMA/commit/6725c083d91d515400fc0977adbb4b4ef99e428b))
* **phase-b:** trust & review activation (R2/R4/R6, ADR-0037) ([1abc30b](https://github.com/Er-Sajan-PLG/STEMMA/commit/1abc30b45047d4dc77836c3d53c4c0b23804fafa))
* **physics:** add mechanics, energy, and thermal physics concepts ([a7306be](https://github.com/Er-Sajan-PLG/STEMMA/commit/a7306beba747a9db88532b1df61d17f9711fbec2))
* **physics:** add motion, heating effect, efficiency, and environment ([223f6d5](https://github.com/Er-Sajan-PLG/STEMMA/commit/223f6d5964a8a40e33f3e6fdfad4dc0313ac80b4))
* **physics:** add nuclear physics, energy sources, and remaining topics ([fc7f989](https://github.com/Er-Sajan-PLG/STEMMA/commit/fc7f98971a29c96dafb981168ff3d9248160c23a))
* **physics:** add waves, optics, electricity, and magnetism concepts ([1f8a5d2](https://github.com/Er-Sajan-PLG/STEMMA/commit/1f8a5d212bdbe4ae3c4f78a9faab71390d920f00))
* **physics:** establish canonical physics taxonomy and add measurement + motion concepts ([7dd2ee8](https://github.com/Er-Sajan-PLG/STEMMA/commit/7dd2ee8a367a33f70bc9fe76791d97e702562739))
* plan v2 wave 4 — E6.1 campaign tooling, E4.1/E4.2 identity hardening, ADR-0024 math draft, contract v1.0 (G-A) ([24b9ea4](https://github.com/Er-Sajan-PLG/STEMMA/commit/24b9ea45799ee2704bd5fc708cae0625bbaff774))
* **provenance:** agent registry, external_ids checks, mechanics Wikidata QIDs (E4.1/E4.2) ([bc9c3ee](https://github.com/Er-Sajan-PLG/STEMMA/commit/bc9c3eed67ea9c13591747ec0235a758ef528083))
* **review:** implement rejected lifecycle (schema 1.1.0) ([9ce974e](https://github.com/Er-Sajan-PLG/STEMMA/commit/9ce974e968f5658237eb40c2212605deeebe6d0b))
* **stemma:** rename explorer to stemma with STEM-pop redesign ([a9af0da](https://github.com/Er-Sajan-PLG/STEMMA/commit/a9af0da025514187418adb96b8782437febd547a))
* **validate:** machine-readable report + --json; advisory anomalies ([4bcb67a](https://github.com/Er-Sajan-PLG/STEMMA/commit/4bcb67ad052a99ed9bc0557e21c3f246ce2788fa))
* **validate:** Phase 1 contract checks and versioned export ([e65f6da](https://github.com/Er-Sajan-PLG/STEMMA/commit/e65f6da6d207a812c024748153640e6490744ab0))
* **versioning:** adopt workspace versioning — VERSION + docs/VERSIONING.md ([#11](https://github.com/Er-Sajan-PLG/STEMMA/issues/11)) ([80c0840](https://github.com/Er-Sajan-PLG/STEMMA/commit/80c0840bde5c0b6f3757ac0124aa4a62211f34db))
* visible sources + historical attribution (who stated it + when) — ADR-0018 ([#10](https://github.com/Er-Sajan-PLG/STEMMA/issues/10)) ([baa9c7d](https://github.com/Er-Sajan-PLG/STEMMA/commit/baa9c7dd12f28a445fb1457cd5032db710334674))
* **webapp:** Antigravity local-harness provider + pypdf PDF fallback ([ac35173](https://github.com/Er-Sajan-PLG/STEMMA/commit/ac35173c4c31a9b6076078bc24c3450d70f8bbfa))
* **webapp:** Antigravity/Google AI Pro sign-in + model picker ([3460e5d](https://github.com/Er-Sajan-PLG/STEMMA/commit/3460e5d237652f022f6590e3221b5e6d5aeb9ea9))
* **webapp:** Google Gemini AI Pro provider for Draft seam ([4eb5f88](https://github.com/Er-Sajan-PLG/STEMMA/commit/4eb5f8836721a3ad770956f156e4cf4b554ecfff))
* **webapp:** provider abstraction with official Antigravity local agent ([236f5b8](https://github.com/Er-Sajan-PLG/STEMMA/commit/236f5b86d46b8d3d82e9b2955fcce07ea20dcec7))
* **webapp:** stdlib ingestion/review webapp (ADR-0036) ([761df1d](https://github.com/Er-Sajan-PLG/STEMMA/commit/761df1da0dfae6100754388a0ab292ad7241766b))


### Bug Fixes

* **canonical:** regenerate inline projection, repair context data, deprecate inverse duplicates ([e7761f7](https://github.com/Er-Sajan-PLG/STEMMA/commit/e7761f725953f2eee076d251939d1ef1a63eff0e))
* correct 4 entity schema violations in physics domain ([8e2db61](https://github.com/Er-Sajan-PLG/STEMMA/commit/8e2db617f3351ed7b2dc59312b85488b06e32400))
* correct 4 entity schema violations in physics domain ([45a51f6](https://github.com/Er-Sajan-PLG/STEMMA/commit/45a51f68dabc490cc2d802ad4b13da79b699bea9))
* **explorer:** align three version with 3d-force-graph to render graph ([43017ab](https://github.com/Er-Sajan-PLG/STEMMA/commit/43017ab3ca45d8b1529627c17d05a997cebe561a))
* **explorer:** render arrowheads only on directional edges ([5826ef6](https://github.com/Er-Sajan-PLG/STEMMA/commit/5826ef6c2b8e4906f32ce929249490586f414d44))
* **gate:** add schema/VERSION.yaml single version source (missed from ADR-0022 commit) ([726ebe3](https://github.com/Er-Sajan-PLG/STEMMA/commit/726ebe36f9be0028de51836892d1fbb9ddcfd1a5))
* **reports:** sort content walks for deterministic report regeneration ([768985d](https://github.com/Er-Sajan-PLG/STEMMA/commit/768985d049b583a3ca043739dc4bf135bde0eb25))
* **validation:** make connections+sources first-class gate inputs ([#14](https://github.com/Er-Sajan-PLG/STEMMA/issues/14)) ([3b9422a](https://github.com/Er-Sajan-PLG/STEMMA/commit/3b9422abb0b81063ffda8ae352aeed64ad3a4d63))


### Code Refactoring

* **breaking:** stemma: namespace, colon-free filenames, single relationship source ([7d60846](https://github.com/Er-Sajan-PLG/STEMMA/commit/7d6084622914bb694ff1072acf8b743308ff9276))

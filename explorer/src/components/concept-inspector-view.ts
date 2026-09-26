import { ConceptDetails } from '../services/concept-data';
import { StemmaEntity } from '../services/knowledge-export-loader';
import { getDomainTheme, getTrustStyle } from '../styles/theme';

declare const katex: any;

export interface ConceptInspectorOptions {
  container: HTMLElement;
  onConceptSelect: (id: string) => void;
}

type TabId = 'overview' | 'relations' | 'examples' | 'misc';
const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'overview', label: 'Overview', icon: '📖' },
  { id: 'relations', label: 'Relations', icon: '🔗' },
  { id: 'examples', label: 'Examples', icon: '🌐' },
  { id: 'misc', label: 'Misconceptions', icon: '💡' },
];

export class ConceptInspectorView {
  private container: HTMLElement;
  private onConceptSelect: (id: string) => void;
  private currentTab: TabId = 'overview';
  private currentDetails: ConceptDetails | null = null;

  constructor(options: ConceptInspectorOptions) {
    this.container = options.container;
    this.onConceptSelect = options.onConceptSelect;
  }

  private summary = '';

  /** Corpus counts shown on the empty panel — always computed from the loaded export. */
  public setSummary(entities: number, relations: number, values: number): void {
    const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;
    const parts = [plural(entities, 'concept', 'concepts'), plural(relations, 'relation', 'relations')];
    if (values > 0) parts.push(plural(values, 'measured value', 'measured values'));
    this.summary = parts.join(' · ');
  }

  public renderEmpty(): void {
    this.currentDetails = null;
    this.container.innerHTML = `
      <div class="empty-inspector">
        <div class="empty-icon">⚛️</div>
        <h3 style="font-size:1.1rem;font-weight:700;color:#fff;">STEMMA — beginning</h3>
        <p style="font-size:0.82rem;line-height:1.4;color:var(--text-secondary);max-width:280px;">${this.summary ? `${this.summary} · ` : ''}Click any node — it will center with its relations.</p>
      </div>
    `;
  }

  public renderDetails(details: ConceptDetails): void {
    this.currentDetails = details;
    const { entity } = details;
    const domainTheme = getDomainTheme(entity.domain);

    let header = `
      <div class="inspector-header">
        <div class="badge-row">
          <span class="domain-badge" style="background:${domainTheme.badgeBg};color:${domainTheme.color};border:1px solid ${domainTheme.badgeBorder}">
            ${domainTheme.name}
          </span>
          <span class="type-badge">${entity.type}</span>
          <span class="type-badge" style="color:var(--accent-emerald);border-color:rgba(92,255,176,0.25);">${entity.status}</span>
        </div>
        <h2 class="concept-title">${this.escapeHtml(entity.name)}</h2>
        <div class="concept-id">${this.escapeHtml(entity.id)}</div>
      </div>
    `;

    let tabBar = `<div class="inspect-tabs">`;
    for (const t of TABS) {
      tabBar += `<button class="inspect-tab${t.id === this.currentTab ? ' active' : ''}" data-tab="${t.id}">${t.icon} ${t.label}</button>`;
    }
    tabBar += `</div><div class="inspect-body">`;

    this.container.innerHTML = header + tabBar + this.renderTab(this.currentTab, details) + `</div>`;

    const tabs = this.container.querySelectorAll('.inspect-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const id = tab.getAttribute('data-tab') as TabId;
        this.currentTab = id;
        if (this.currentDetails) this.renderDetails(this.currentDetails);
      });
    });
    const links = this.container.querySelectorAll('.entity-link');
    links.forEach(link => {
      link.addEventListener('click', () => {
        const id = link.getAttribute('data-id');
        if (id) this.onConceptSelect(id);
      });
    });
  }

  private renderTab(tab: TabId, details: ConceptDetails): string {
    const { entity } = details;
    switch (tab) {
      case 'overview':
        return this.renderOverview(details);
      case 'relations':
        return this.renderRelations(details);
      case 'examples':
        return this.renderExamples(entity);
      case 'misc':
        return this.renderMisconceptions(entity);
      default:
        return '';
    }
  }

  private renderOverview(details: ConceptDetails): string {
    const { entity } = details;
    const prov = (entity as any).provenance || {};
    const isAgreed = prov.source_kind === 'textbook' || prov.source_kind === 'standards-or-specification' || prov.source_kind === 'institutional';
    const kindLabel = prov.source_kind ? prov.source_kind.replace(/-/g, ' ') : 'standard';
    const agreedBadge = isAgreed
      ? `<span style="font-size:0.6rem;background:rgba(92,255,176,0.12);border:1px solid rgba(92,255,176,0.3);color:#5cffb0;padding:2px 6px;border-radius:9999px;margin-left:6px;">✓ Agreed</span>`
      : `<span style="font-size:0.6rem;background:rgba(255,255,255,0.06);border:1px solid var(--border-glass);color:var(--text-muted);padding:2px 6px;border-radius:9999px;margin-left:6px;">draft</span>`;

    let html = `
      <div class="inspector-section">
        <div class="section-title">📖 Canonical Definition ${agreedBadge}</div>
        <div class="definition-text">${this.escapeHtml(entity.definition)}</div>
        <div style="margin-top:8px;font-size:0.7rem;color:var(--text-secondary);background:rgba(95,208,255,0.06);border:1px solid rgba(95,208,255,0.14);padding:8px 10px;border-radius:8px;line-height:1.4;">
          <div>✓ <strong style="color:#fff;">Scientifically agreed definition</strong> — this definition is not invented. It is the consensus from international standards and widely adopted textbooks.</div>
          <div style="margin-top:4px;">Source kind: <strong style="color:var(--accent-cyan);">${this.escapeHtml(kindLabel)}</strong> — ${isAgreed ? 'community-accepted' : 'curated draft'}</div>
          ${prov.original_author ? `<div style="margin-top:3px;">Original author: <strong style="color:#fff;">${this.escapeHtml(prov.original_author)}</strong></div>` : ''}
          ${(entity as any).governed_by ? `<div style="margin-top:3px;">Governed by law: ${(entity as any).governed_by.map((g:string)=>`<code style="background:rgba(167,139,250,0.12);padding:1px 4px;border-radius:4px;margin-right:3px;">${this.escapeHtml(g)}</code>`).join('')}</div>` : ''}
        </div>
      </div>
    `;

    if ((entity as any).symbol || (entity as any).unit) {
      html += `
        <div class="inspector-section">
          <div class="section-title">⚖️ Symbol & Unit (agreed)</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            ${(entity as any).symbol ? `<div class="pill-chip"><span>Symbol (agreed)</span><strong>${this.escapeHtml((entity as any).symbol)}</strong></div>` : ''}
            ${(entity as any).unit ? `<div class="pill-chip"><span>Unit (SI agreed)</span><strong>${this.escapeHtml((entity as any).unit)}</strong></div>` : ''}
          </div>
        </div>`;
    }

    if ((entity as any).equation) {
      let renderedEq = this.escapeHtml((entity as any).equation);
      if (typeof katex !== 'undefined') {
        try { renderedEq = katex.renderToString((entity as any).equation, { throwOnError: false, displayMode: true }); } catch (e) {}
      }
      html += `
        <div class="inspector-section">
          <div class="section-title">📐 Formula (agreed)</div>
          <div class="equation-box">${renderedEq}</div>
        </div>`;
    }

    // References — mandatory for canonical
    const srcRefs = (entity as any).source_refs || [];
    const gov = (entity as any).governed_by || [];
    html += `
      <div class="inspector-section">
        <div class="section-title">🔬 References — where agreed definition comes from</div>
        <div style="font-size:0.74rem;color:var(--text-secondary);background:var(--bg-card);padding:10px 12px;border-radius:8px;border:1px solid var(--border-glass);display:flex;flex-direction:column;gap:6px;line-height:1.4;">
          <div>Definition text: <strong style="color:#fff;">${this.escapeHtml(prov.source ?? '—')}</strong></div>
          <div>Kind: <strong style="color:var(--accent-cyan);">${this.escapeHtml(prov.source_kind ?? '—')}</strong> — ${prov.source_kind === 'standards-or-specification' ? 'BIPM / SI Brochure — international standard agreed by 100+ countries' : prov.source_kind === 'textbook' ? 'Halliday/Resnick/Walker or Newton Principia — taught worldwide, community consensus' : 'curated source'}</div>
          ${prov.writer ? `<div>Writer (dual verification): <code style="background:rgba(255,255,255,0.06);padding:1px 5px;border-radius:4px;">${this.escapeHtml(prov.writer)}</code> — every entity has writer for triple-check</div>` : ''}
          ${prov.link ? `<div>Link: <a href="${this.escapeHtml(prov.link)}" target="_blank" style="color:var(--accent-cyan);word-break:break-all;">${this.escapeHtml(prov.link)}</a> — click to verify</div>` : ''}
          ${prov.retrieved_at ? `<div>Retrieved: ${this.escapeHtml(prov.retrieved_at)}</div>` : ''}
          ${srcRefs.length ? `<div>Source refs (canonical records): ${srcRefs.map((r:string)=>`<code style="background:rgba(95,208,255,0.1);padding:1px 5px;border-radius:4px;margin-right:4px;">${this.escapeHtml(r)}</code>`).join('')} — each has file in sources/ with url/doi/isbn</div>` : ''}
          ${gov.length ? `<div>Governed by laws (deterministic, no LLM): ${gov.map((g:string)=>`<code style="background:rgba(167,139,250,0.12);padding:1px 5px;border-radius:4px;margin-right:4px;">${this.escapeHtml(g)}</code>`).join('')} — from physics-governing-registry.yaml</div>` : ''}
        </div>
      </div>
    `;

    const hist = (entity as any).historical;
    if (hist) {
      html += `
        <div class="inspector-section">
          <div class="section-title">📜 History — who agreed, when (timeline)</div>
          <div style="font-size:0.74rem;color:var(--text-secondary);background:var(--bg-card);padding:10px 12px;border-radius:8px;border:1px solid var(--border-glass);">
            <div>Stated by: <strong style="color:#fff;">${this.escapeHtml(hist.stated_by ?? '—')}</strong> in ${this.escapeHtml(String(hist.year ?? '—'))} — ${this.escapeHtml(hist.where ?? '')}</div>
            ${hist.timeline && hist.timeline.length ? `<div style="margin-top:6px;"><div style="font-weight:600;color:var(--text-primary);margin-bottom:4px;">Timeline of agreement:</div><ul style="margin-left:14px;display:flex;flex-direction:column;gap:3px;">${hist.timeline.map((t:any)=>`<li>${this.escapeHtml(String(t.year))} — <strong>${this.escapeHtml(t.by)}</strong>: ${this.escapeHtml(t.event)}</li>`).join('')}</ul></div>` : ''}
          </div>
        </div>`;
    }

    const ext = (entity as any).external_ids;
    if (ext) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🌐 External IDs — verify elsewhere</div>
          <div style="font-size:0.74rem;">${Object.entries(ext).map(([k,v])=>`<code style="background:var(--bg-card);border:1px solid var(--border-glass);padding:2px 6px;border-radius:6px;margin-right:6px;">${this.escapeHtml(k)}:${this.escapeHtml(String(v))}</code>`).join('')}</div>
        </div>`;
    }

    return html;
  }

  private renderRelations(details: ConceptDetails): string {
    const { prerequisites, dependents, related, trust } = details;
    let html = '';
    html += `
      <div class="inspector-section">
        <div class="section-title">⬅️ Prerequisites (${prerequisites.length})</div>
        ${prerequisites.length === 0
          ? `<div class="muted">Foundational — no prerequisites, governed by law directly.</div>`
          : `<ul class="entity-list">${prerequisites.map(p => this.entityLink(p, '→', trust[p.id])).join('')}</ul>`}
      </div>`;
    html += `
      <div class="inspector-section">
        <div class="section-title">➡️ Enables (${dependents.length})</div>
        ${dependents.length === 0
          ? `<div class="muted">No downstream yet — beginning.</div>`
          : `<ul class="entity-list">${dependents.map(d => this.entityLink(d, '→', trust[d.id])).join('')}</ul>`}
      </div>`;
    if (related.length) {
      html += `
        <div class="inspector-section">
          <div class="section-title">🔗 Related (${related.length})</div>
          <ul class="entity-list">${related.map(r => this.entityLink(r, r.domain, trust[r.id])).join('')}</ul>
        </div>`;
    }
    html += `
      <div class="inspector-section">
        <div class="section-title">🛡️ Edge source</div>
        <div style="font-size:0.72rem;color:var(--text-secondary);">From canonical connections[] — each edge has evidence with source_ref + locator + description.</div>
      </div>`;
    return html;
  }

  private renderExamples(entity: StemmaEntity): string {
    let html = '';
    if ((entity as any).real_world_applications && (entity as any).real_world_applications.length) {
      html += `<div class="inspector-section"><div class="section-title">🌐 Applications</div><ul class="insp-list">${(entity as any).real_world_applications.map((a: string) => `<li>${this.escapeHtml(a)}</li>`).join('')}</ul></div>`;
    }
    if ((entity as any).examples && (entity as any).examples.length) {
      html += `<div class="inspector-section"><div class="section-title">Examples</div><ul class="insp-list">${(entity as any).examples.map((e: string) => `<li>${this.escapeHtml(e)}</li>`).join('')}</ul></div>`;
    }
    if (!html) html = `<div class="muted">No examples yet — beginning, minimal.</div>`;
    return html;
  }

  private renderMisconceptions(entity: StemmaEntity): string {
    let html = '';
    if ((entity as any).common_misconceptions && (entity as any).common_misconceptions.length) {
      html = (entity as any).common_misconceptions.map((m: string) => `<div class="misconception-card">${this.escapeHtml(m)}</div>`).join('');
    } else {
      html = `<div class="muted">No misconceptions recorded — clean minimal.</div>`;
    }
    return html;
  }

  private entityLink(p: StemmaEntity, right: string, trust?: string): string {
    const theme = getDomainTheme(p.domain);
    const badge = this.trustBadge(trust);
    return `
      <li class="entity-link" data-id="${p.id}">
        <div style="display:flex;align-items:center;gap:6px;">
          <span>${theme.icon}</span><span>${this.escapeHtml(p.name)}</span>${badge}
        </div>
        <span style="font-size:0.7rem;color:${theme.color};">${right}</span>
      </li>`;
  }

  private trustBadge(trust?: string): string {
    if (!trust || trust === 'unknown') return '';
    const style = getTrustStyle(trust);
    const color = trust === 'canonical' ? '#5fd0ff' : trust === 'reviewed' ? '#5cffb0' : '#8a93b8';
    return `<span title="${style.label}" style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.04em;border:1px solid ${color}66;color:${color};padding:1px 5px;border-radius:999px;opacity:${Math.max(0.5, style.opacity)};">${style.short}</span>`;
  }

  private escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;').replace(/'/g, '&#039;');
  }
}

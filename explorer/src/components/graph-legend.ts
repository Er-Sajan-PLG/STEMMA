import { ClusterInfo } from '../services/graph-projection';
import { ASSERTION_TRUST, GRAPH_THEME } from '../styles/theme';

export interface LegendOptions {
  container: HTMLElement;
  clusters: ClusterInfo[];
  onClusterSelect: (clusterId: string) => void;
}

const RELATION_LABELS: Record<string, string> = {
  logically_requires: 'Prerequisite (logical)',
  mathematically_requires: 'Prerequisite (math)',
  part_of: 'Part of',
  special_case_of: 'Special case of',
  applies_to: 'Applies to',
  appears_in_law: 'Appears in law',
  related_to: 'Related',
  default: 'Association',
};

export class GraphLegend {
  private container: HTMLElement;
  private clusters: ClusterInfo[];
  private onClusterSelect: (clusterId: string) => void;

  constructor(options: LegendOptions) {
    this.container = options.container;
    this.clusters = options.clusters;
    this.onClusterSelect = options.onClusterSelect;
    this.render();
  }

  public renderClusters(clusters: ClusterInfo[]): void {
    this.clusters = clusters;
    this.render();
  }

  private render(): void {
    // Edge legend
    let edgeHtml = `<div class="legend-group-title">Relationships</div>`;
    for (const [key, style] of Object.entries(GRAPH_THEME.edges)) {
      if (key === 'default') continue;
      const label = RELATION_LABELS[key] ?? key.replace(/_/g, ' ');
      const dash = style.directional ? '→' : '·';
      edgeHtml += `
        <div class="legend-row" title="${label}">
          <span class="legend-line" style="background:${style.color};">
                      <span class="legend-arrow" style="color:${style.color};">${dash}</span>
                    </span>
          <span class="legend-label">${label}</span>
        </div>`;
    }

    // Trust legend (E1.6 / ADR-0023): every edge is an assertion; trust modulates
    // how strongly it is drawn. Unreviewed (machine-migrated) claims must look faint.
    let trustHtml = `<div class="legend-group-title">Assertion trust</div>`;
    for (const [status, style] of Object.entries(ASSERTION_TRUST)) {
      if (status === 'unknown') continue; // internal fallback, not a review status
      trustHtml += `
        <div class="legend-row" title="${style.label}">
          <span class="legend-line" style="background:#94a3b8;opacity:${style.opacity};height:${Math.max(1, Math.round(style.widthScale * 3))}px;"></span>
          <span class="legend-label">${style.short}</span>
        </div>`;
    }

    // Cluster legend
    let clusterHtml = `<div class="legend-group-title">Topics / Domains</div>`;
    for (const cluster of this.clusters) {
      clusterHtml += `
        <div class="legend-row cluster-pill" data-cluster="${cluster.id}" title="Focus on ${cluster.label}">
          <span class="legend-dot-lg" style="background:${cluster.color};"></span>
          <span class="legend-label">${cluster.label}</span>
        </div>`;
    }

    this.container.innerHTML = `
      <div class="graph-legend">
        <button class="legend-toggle" id="legendToggle">◨ Legend</button>
        <div class="legend-body" style="display:none;">
          ${edgeHtml}
          <div class="legend-divider"></div>
          ${trustHtml}
          <div class="legend-divider"></div>
          ${clusterHtml}
        </div>
      </div>
    `;

    // Manual only — starts hidden, no auto-popup on render
    const btn = this.container.querySelector('#legendToggle') as HTMLElement;
    const body = this.container.querySelector('.legend-body') as HTMLElement;
    if (btn && body) {
      body.style.display = 'none';
      btn.textContent = '◨ Legend';
      btn.addEventListener('click', () => {
        const isHidden = body.style.display === 'none';
        body.style.display = isHidden ? 'flex' : 'none';
        btn.textContent = isHidden ? '◧ Hide Legend' : '◨ Legend';
      });
    }

    // cluster focus
    const pills = this.container.querySelectorAll('.cluster-pill');
    pills.forEach(p => {
      p.addEventListener('click', () => {
        const id = p.getAttribute('data-cluster');
        if (id) this.onClusterSelect(id);
      });
    });
  }
}
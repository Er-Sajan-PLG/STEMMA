import { ExplorerState, ExplorerMode } from '../state/explorer-state';
import { GRAPH_THEME } from '../styles/theme';

export interface SearchFilterBarOptions {
  container: HTMLElement;
  onSearch: (query: string) => void;
  onDomainChange: (domain: string) => void;
  onRelationshipChange: (rel: string) => void;
  onModeChange: (mode: ExplorerMode) => void;
  onViewToggle: (view: '3d' | 'list') => void;
  onReset: () => void;
}

export class SearchFilterBar {
  private container: HTMLElement;
  private options: SearchFilterBarOptions;
  private debounceTimer: number | null = null;

  constructor(options: SearchFilterBarOptions) {
    this.container = options.container;
    this.options = options;
    this.render();
  }

  public render(): void {
    this.container.innerHTML = `
      <div class="explorer-header">
        <div class="brand-title" title="stemma — a colorful map of the whole STEM universe">
          <div class="brand-logo"></div>
          <span>stemma</span>
          <span class="brand-sub">3D STEM</span>
          <span class="chat-soon" title="Ask anything about a concept, equation, or relation — arriving next">💬 Ask stemma · soon</span>
        </div>

        <div class="toolbar-controls">
          <!-- Search Input with Clear button -->
          <div class="search-wrapper">
            <input type="text" id="searchInput" class="search-input" placeholder="Search the stem-verse (e.g. force, voltage, photosynthesis)..." />
            <button id="searchClear" class="search-clear">✕</button>
          </div>

          <!-- Domain Dropdown -->
          <select id="domainSelect" class="select-control">
            <option value="all">🌐 All Domains</option>
            <option value="physics">⚡ Physics</option>
            <option value="chemistry">🧪 Chemistry</option>
            <option value="biology">🧬 Biology</option>
            <option value="earth-space">🪐 Earth & Space</option>
            <option value="scientific-practice">📐 Practices</option>
            <option value="engineering">⚙️ Engineering</option>
            <option value="mathematics">∑ Mathematics</option>
          </select>

          <!-- Relationship Filter -->
          <select id="relSelect" class="select-control">
            <option value="all">🔗 All Relationships</option>
            <option value="logically_requires">⬅️ Prerequisites (Logical)</option>
            <option value="mathematically_requires">📐 Prerequisites (Math)</option>
            <option value="part_of">🧩 Part Of</option>
            <option value="special_case_of">🔍 Special Case Of</option>
            <option value="related_to">➡️ Related</option>
          </select>

          <!-- Mode Group -->
          <div class="mode-btn-group" role="group" aria-label="stemma browse mode">
            <button class="mode-btn active" data-mode="explore">Explore</button>
            <button class="mode-btn" data-mode="prerequisites">Prereqs DAG</button>
            <button class="mode-btn" data-mode="domain">Domains</button>
          </div>

          <!-- View Toggle Group -->
          <div class="mode-btn-group" id="viewToggle" role="group" aria-label="View Mode">
            <button class="mode-btn active" data-view="3d">🌌 3D</button>
            <button class="mode-btn" data-view="list">📋 List</button>
          </div>

          <button id="resetBtn" class="action-btn" title="Reset Filters and View">↺ Reset View</button>
        </div>
      </div>
    `;

    this.renderDomainLegend();
    this.attachEvents();
  }

  private renderDomainLegend(): void {
    const legendContainer = document.getElementById('hudDomainLegend');
    if (!legendContainer) return;

    let html = `
      <div class="legend-pill active" data-domain="all">
        <span class="legend-dot" style="background:#ffffff;"></span>
        <span>All</span>
      </div>
    `;

    for (const [key, theme] of Object.entries(GRAPH_THEME.domains)) {
      html += `
        <div class="legend-pill" data-domain="${key}">
          <span class="legend-dot" style="background:${theme.color};"></span>
          <span>${theme.name.split(' ')[0]}</span>
        </div>
      `;
    }

    legendContainer.innerHTML = html;

    // Attach domain legend click handlers
    const legendPills = legendContainer.querySelectorAll('.legend-pill');
    legendPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const domain = pill.getAttribute('data-domain');
        if (domain) this.options.onDomainChange(domain);
      });
    });
  }

  public updateState(state: ExplorerState): void {
    const searchInput = this.container.querySelector('#searchInput') as HTMLInputElement;
    if (searchInput && searchInput.value !== state.searchQuery) {
      searchInput.value = state.searchQuery;
    }

    const domainSelect = this.container.querySelector('#domainSelect') as HTMLSelectElement;
    if (domainSelect) domainSelect.value = state.domainFilter;

    const relSelect = this.container.querySelector('#relSelect') as HTMLSelectElement;
    if (relSelect) relSelect.value = state.relationshipFilter;

    const modeBtns = this.container.querySelectorAll('.mode-btn[data-mode]');
    modeBtns.forEach(btn => {
      const mode = btn.getAttribute('data-mode');
      if (mode === state.activeMode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const viewBtns = this.container.querySelectorAll('.mode-btn[data-view]');
    viewBtns.forEach(btn => {
      const view = btn.getAttribute('data-view');
      if (view === state.viewMode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update legend pills active state
    const legendContainer = document.getElementById('hudDomainLegend');
    if (legendContainer) {
      const pills = legendContainer.querySelectorAll('.legend-pill');
      pills.forEach(p => {
        if (p.getAttribute('data-domain') === state.domainFilter) {
          p.classList.add('active');
        } else {
          p.classList.remove('active');
        }
      });
    }
  }

  private attachEvents(): void {
    const searchInput = this.container.querySelector('#searchInput') as HTMLInputElement;
    const searchClear = this.container.querySelector('#searchClear') as HTMLButtonElement;

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        if (this.debounceTimer) window.clearTimeout(this.debounceTimer);
        this.debounceTimer = window.setTimeout(() => {
          this.options.onSearch(searchInput.value.trim());
        }, 150);
      });

      // Shortcut key '/' or 'Control+k' focus search
      window.addEventListener('keydown', (evt) => {
        if ((evt.key === '/' || (evt.ctrlKey && evt.key === 'k')) && document.activeElement !== searchInput) {
          evt.preventDefault();
          searchInput.focus();
        }
      });
    }

    if (searchClear && searchInput) {
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        this.options.onSearch('');
      });
    }

    const domainSelect = this.container.querySelector('#domainSelect') as HTMLSelectElement;
    if (domainSelect) {
      domainSelect.addEventListener('change', () => {
        this.options.onDomainChange(domainSelect.value);
      });
    }

    const relSelect = this.container.querySelector('#relSelect') as HTMLSelectElement;
    if (relSelect) {
      relSelect.addEventListener('change', () => {
        this.options.onRelationshipChange(relSelect.value);
      });
    }

    const modeBtns = this.container.querySelectorAll('.mode-btn[data-mode]');
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode') as ExplorerMode;
        if (mode) this.options.onModeChange(mode);
      });
    });

    const viewBtns = this.container.querySelectorAll('.mode-btn[data-view]');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.getAttribute('data-view') as '3d' | 'list';
        if (view) this.options.onViewToggle(view);
      });
    });

    const resetBtn = this.container.querySelector('#resetBtn') as HTMLButtonElement;
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.options.onReset();
      });
    }
  }
}

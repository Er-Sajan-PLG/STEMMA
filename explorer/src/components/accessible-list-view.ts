import { StemmaEntity } from '../services/knowledge-export-loader';
import { getDomainTheme } from '../styles/theme';

export interface AccessibleListViewOptions {
  container: HTMLElement;
  onConceptSelect: (id: string) => void;
}

export class AccessibleListView {
  private container: HTMLElement;
  private onConceptSelect: (id: string) => void;

  constructor(options: AccessibleListViewOptions) {
    this.container = options.container;
    this.onConceptSelect = options.onConceptSelect;
  }

  public render(entities: StemmaEntity[], selectedId: string | null): void {
    if (entities.length === 0) {
      this.container.innerHTML = `
        <div style="padding:24px;text-align:center;color:#9ca3af;">
          No concepts match the current filters.
        </div>
      `;
      return;
    }

    const html = `
      <div style="padding:16px;display:flex;flex-direction:column;gap:10px;max-height:100%;overflow-y:auto;" role="list">
        ${entities.map(e => {
          const theme = getDomainTheme(e.domain);
          const isSelected = e.id === selectedId;
          return `
            <div 
              role="listitem"
              tabindex="0"
              data-id="${e.id}"
              class="accessible-item"
              style="padding:12px;border-radius:8px;background:${isSelected ? 'rgba(59,130,246,0.2)' : 'rgba(255,255,255,0.03)'};border:1px solid ${isSelected ? '#3b82f6' : 'rgba(255,255,255,0.08)'};cursor:pointer;"
            >
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                <strong style="font-size:0.95rem;color:#ffffff;">${this.escapeHtml(e.name)}</strong>
                <span style="font-size:0.75rem;padding:2px 8px;border-radius:9999px;background:${theme.badgeBg};color:${theme.color};">
                  ${theme.name}
                </span>
              </div>
              <div style="font-size:0.82rem;color:#9ca3af;margin-bottom:6px;line-clamp:2;overflow:hidden;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;">
                ${this.escapeHtml(e.definition)}
              </div>
              <div style="font-family:monospace;font-size:0.75rem;color:#6b7280;">${e.id}</div>
            </div>
          `;
        }).join('')}
      </div>
    `;

    this.container.innerHTML = html;

    const items = this.container.querySelectorAll('.accessible-item');
    items.forEach(item => {
      const id = item.getAttribute('data-id');
      if (!id) return;

      item.addEventListener('click', () => this.onConceptSelect(id));
      item.addEventListener('keydown', (evt: Event) => {
        const keyEvt = evt as KeyboardEvent;
        if (keyEvt.key === 'Enter' || keyEvt.key === ' ') {
          evt.preventDefault();
          this.onConceptSelect(id);
        }
      });
    });
  }

  private escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

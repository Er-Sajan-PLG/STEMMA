/**
 * Grounded chat panel (REQ-STEMMA-INTEG-001 AC3).
 *
 * The UI half of the grounded chat: renders the transcript, cites every
 * grounded answer with clickable chips that select the entity/connection in the
 * graph, and renders refusal as a distinct, first-class state — not an error.
 *
 * It holds no knowledge of its own. All text comes from `grounded-chat.ts`,
 * which reads only `exports/knowledge.json`.
 */
import type { StemmaKnowledgeExport } from '../services/knowledge-export-loader';
import {
  answerQuestion,
  citationsAreGrounded,
  type ChatAnswer,
  type ChatTurn,
} from '../services/grounded-chat';

export interface GroundedChatOptions {
  container: HTMLElement;
  onCitationSelect: (id: string) => void;
}

const SUGGESTIONS = [
  'What is the metre?',
  'What does the kilogram relate to?',
  'Explain mass',
];

export class GroundedChatPanel {
  private container: HTMLElement;
  private options: GroundedChatOptions;
  private data: StemmaKnowledgeExport | null = null;
  private history: ChatTurn[] = [];

  constructor(options: GroundedChatOptions) {
    this.container = options.container;
    this.options = options;
    this.render();
  }

  public setData(data: StemmaKnowledgeExport): void {
    this.data = data;
    this.renderSuggestions();
  }

  public ask(question: string): void {
    if (!this.data) return;
    const answer = answerQuestion(question, this.data, this.history);

    // Invariant: a grounded answer cites only export records; a refusal cites
    // nothing. If this ever fails the UI shows the failure rather than a
    // fabricated citation — a false citation is worse than no answer.
    if (!citationsAreGrounded(answer, this.data)) {
      this.appendTurn(question, {
        status: 'refused',
        answer: 'Internal check failed: the answer could not be tied to export records.',
        citations: [],
        groundingIds: [],
        refusalReason: 'citationsAreGrounded invariant violated',
      });
      return;
    }

    this.history.push({ question, answer });
    this.appendTurn(question, answer);
  }

  private render(): void {
    this.container.innerHTML = `
      <div class="chat-panel">
        <div class="chat-head">
          <span class="chat-title">Ask the graph</span>
          <span class="chat-badge" title="Answers are assembled only from exports/knowledge.json">grounded</span>
        </div>
        <div class="chat-log" id="chatLog" role="log" aria-live="polite">
          <div class="chat-intro">
            Every answer is built from this knowledge base and cites the records it
            came from. If the export cannot support an answer, I will say so rather
            than guess.
          </div>
        </div>
        <div class="chat-suggestions" id="chatSuggestions"></div>
        <form class="chat-compose" id="chatForm">
          <input type="text" id="chatInput" class="chat-input"
                 placeholder="Ask about a concept, unit, or relationship…"
                 autocomplete="off" />
          <button type="submit" class="chat-send" id="chatSend">Ask</button>
        </form>
      </div>
    `;

    const form = this.container.querySelector<HTMLFormElement>('#chatForm')!;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = this.container.querySelector<HTMLInputElement>('#chatInput')!;
      const q = input.value.trim();
      if (!q) return;
      input.value = '';
      this.ask(q);
    });

    this.renderSuggestions();
  }

  private renderSuggestions(): void {
    const host = this.container.querySelector<HTMLElement>('#chatSuggestions');
    if (!host) return;
    if (!this.data) {
      host.innerHTML = '';
      return;
    }
    const names = new Set(this.data.entities.map((e) => e.name.toLowerCase()));
    const usable = SUGGESTIONS.filter((s) => {
      const terms = s.toLowerCase().split(/\s+/).filter((t) => t.length > 3 && t !== 'what');
      return terms.some((t) => [...names].some((n) => n.includes(t)));
    }).slice(0, 3);

    host.innerHTML = usable
      .map((s) => `<button type="button" class="chat-chip suggest" data-q="${escapeAttr(s)}">${escapeHtml(s)}</button>`)
      .join('');
    for (const btn of host.querySelectorAll<HTMLButtonElement>('button.suggest')) {
      btn.addEventListener('click', () => this.ask(btn.dataset.q ?? ''));
    }
  }

  private appendTurn(question: string, answer: ChatAnswer): void {
    const log = this.container.querySelector<HTMLElement>('#chatLog');
    if (!log) return;

    const turn = document.createElement('div');
    turn.className = 'chat-turn';

    const q = document.createElement('div');
    q.className = 'chat-q';
    q.textContent = question;
    turn.appendChild(q);

    const a = document.createElement('div');
    a.className = `chat-a ${answer.status === 'refused' ? 'refused' : 'grounded'}`;
    a.textContent = answer.answer;
    turn.appendChild(a);

    if (answer.status === 'refused') {
      const note = document.createElement('div');
      note.className = 'chat-refusal-note';
      note.textContent = `No answer given — ${answer.refusalReason ?? 'insufficient grounding'}.`;
      turn.appendChild(note);
    } else if (answer.citations.length) {
      const cites = document.createElement('div');
      cites.className = 'chat-citations';
      const label = document.createElement('span');
      label.className = 'chat-cites-label';
      label.textContent = 'Sources:';
      cites.appendChild(label);

      for (const c of answer.citations) {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = `chat-chip cite ${c.kind}`;
        chip.dataset.id = c.id;
        chip.title = c.sourceRefs.length
          ? `${c.id}\n\nSources:\n${c.sourceRefs.join('\n')}`
          : c.id;
        chip.textContent = c.sourceRefs.length
          ? `${c.label} (${c.sourceRefs.length} source${c.sourceRefs.length === 1 ? '' : 's'})`
          : c.label;
        chip.addEventListener('click', () => this.options.onCitationSelect(c.id));
        cites.appendChild(chip);
      }
      turn.appendChild(cites);
    }

    log.appendChild(turn);
    log.scrollTop = log.scrollHeight;
  }
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (ch) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch] as string),
  );
}

function escapeAttr(s: string): string {
  return escapeHtml(s);
}

export interface DomainTheme {
  color: string;
  name: string;
  badgeBg: string;
  badgeBorder: string;
  glowColor: string;
  icon: string;
}

export const GRAPH_THEME = {
  domains: {
    physics: {
      color: '#00e5ff',
      name: 'Physics',
      badgeBg: 'rgba(0, 229, 255, 0.12)',
      badgeBorder: 'rgba(0, 229, 255, 0.45)',
      glowColor: 'rgba(0, 229, 255, 0.72)',
      icon: '⚡'
    },
    chemistry: {
      color: '#3dffb0',
      name: 'Chemistry',
      badgeBg: 'rgba(61, 255, 176, 0.12)',
      badgeBorder: 'rgba(61, 255, 176, 0.45)',
      glowColor: 'rgba(61, 255, 176, 0.72)',
      icon: '🧪'
    },
    biology: {
      color: '#ff4d9d',
      name: 'Biology',
      badgeBg: 'rgba(255, 77, 157, 0.12)',
      badgeBorder: 'rgba(255, 77, 157, 0.45)',
      glowColor: 'rgba(255, 77, 157, 0.72)',
      icon: '🧬'
    },
    'earth-space': {
      color: '#ffb020',
      name: 'Earth & Space',
      badgeBg: 'rgba(255, 176, 32, 0.12)',
      badgeBorder: 'rgba(255, 176, 32, 0.45)',
      glowColor: 'rgba(255, 176, 32, 0.72)',
      icon: '🪐'
    },
    'scientific-practice': {
      color: '#c084fc',
      name: 'Scientific Practice',
      badgeBg: 'rgba(192, 132, 252, 0.12)',
      badgeBorder: 'rgba(192, 132, 252, 0.45)',
      glowColor: 'rgba(192, 132, 252, 0.72)',
      icon: '📐'
    },
    engineering: {
      color: '#2fffdd',
      name: 'Engineering',
      badgeBg: 'rgba(47, 255, 221, 0.12)',
      badgeBorder: 'rgba(47, 255, 221, 0.45)',
      glowColor: 'rgba(47, 255, 221, 0.72)',
      icon: '⚙️'
    },
    mathematics: {
      color: '#ff6ee7',
      name: 'Mathematics',
      badgeBg: 'rgba(255, 110, 231, 0.12)',
      badgeBorder: 'rgba(255, 110, 231, 0.45)',
      glowColor: 'rgba(255, 110, 231, 0.72)',
      icon: '∑'
    }
  } as Record<string, DomainTheme>,

  edges: {
    logically_requires: { color: '#00e5ff', opacity: 0.85, directional: true, particleSpeed: 0.008, width: 2.4 },
    mathematically_requires: { color: '#3dffb0', opacity: 0.85, directional: true, particleSpeed: 0.009, width: 2.4 },
    part_of: { color: '#c084fc', opacity: 0.6, directional: true, particleSpeed: 0.004, width: 1.6 },
    special_case_of: { color: '#ff4d9d', opacity: 0.6, directional: true, particleSpeed: 0.004, width: 1.6 },
    applies_to: { color: '#ffb020', opacity: 0.7, directional: true, particleSpeed: 0.005, width: 1.9 },
    appears_in_law: { color: '#ffb020', opacity: 0.5, directional: false, particleSpeed: 0, width: 1.3 },
    related_to: { color: '#8b93b8', opacity: 0.4, directional: false, particleSpeed: 0, width: 1.1 },
    default: { color: '#a9b3d9', opacity: 0.34, directional: false, particleSpeed: 0, width: 1.0 }
  },

  canvas: {
    background: '#07031b',
    gridColor: 'rgba(0, 229, 255, 0.05)',
    dimmedOpacity: 0.12
  }
};

/**
 * Assertion-trust scale (plan v2 E1.6 / ADR-0023).
 *
 * The explorer draws edges from canonical `connections[]`.
 * projection, so every edge carries `assertion.review.status` — the graph can show HOW
 * TRUSTED a claim is, not only what it says. Trust modulates the relation's own style
 * (thicker/brighter = reviewed; thin/dim = unreviewed), never replaces it.
 */
export interface TrustStyle {
  label: string;
  short: string;
  widthScale: number;
  opacity: number;
}

export const ASSERTION_TRUST: Record<string, TrustStyle> = {
  canonical: { label: 'Canonical assertion (human-reviewed)', short: 'Canonical', widthScale: 1.35, opacity: 0.95 },
  reviewed: { label: 'Human-reviewed assertion', short: 'Reviewed', widthScale: 1.0, opacity: 0.7 },
  unreviewed: { label: 'Unreviewed / machine-migrated assertion', short: 'Unreviewed', widthScale: 0.6, opacity: 0.3 },
  unknown: { label: 'Trust unknown', short: 'Unknown', widthScale: 0.6, opacity: 0.3 }
};

export function getTrustStyle(status: string | undefined): TrustStyle {
  return ASSERTION_TRUST[status ?? 'unknown'] ?? ASSERTION_TRUST.unknown;
}

export function getDomainTheme(domain: string): DomainTheme {
  return (
    GRAPH_THEME.domains[domain] ?? {
      color: '#94a3b8',
      name: domain,
      badgeBg: 'rgba(148, 163, 184, 0.12)',
      badgeBorder: 'rgba(148, 163, 184, 0.4)',
      glowColor: 'rgba(148, 163, 184, 0.6)',
      icon: '📌'
    }
  );
}

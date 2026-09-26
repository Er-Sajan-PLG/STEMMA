// Family / tester feedback goes to a GitHub issue form (read-only site, no accounts
// on STEMMA itself — see ADR-0054). The concept field is pre-filled from the
// current selection so reports point at the exact entity.
const DEFAULT_FEEDBACK_URL = 'https://github.com/Er-Sajan-PLG/STEMMA/issues/new?template=feedback.yml';

export function feedbackUrl(concept?: { id: string; name?: string } | null): string {
  const url = new URL(import.meta.env.VITE_FEEDBACK_URL || DEFAULT_FEEDBACK_URL);
  if (concept) {
    url.searchParams.set('concept', concept.id);
    url.searchParams.set('title', `[Feedback] ${concept.name ?? concept.id}`);
  }
  return url.toString();
}

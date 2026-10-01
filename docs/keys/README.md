# Release signing keys

## `stemma-owner-pubkey.asc`

The **owner's public GPG key** — the verification key for owner-signed STEMMA
releases. This is the *only* file here that is intentionally public.

| | |
|---|---|
| Primary key ID | `4705983D407DEB9C` |
| Fingerprint | `7C36 937F CC01 8442 637E BA74 4705 983D 407D EB9C` |
| UID | `Sajan Gurung <gurungsajan0228@gmail.com>` |
| Algorithm | RSA 4096 (`[SC]` primary + `[E]` subquery) |
| Created | 2026-10-01 |
| Expiry | none |

Consumers verify the owner's detached signature on a release with:

```bash
gpg --import docs/keys/stemma-owner-pubkey.asc
gpg --verify SHA256SUMS.sig SHA256SUMS.txt
```

Always compare the fingerprint against the table above before trusting the key —
a key imported from a mirror proves nothing about who published it.

## Two-layer release trust model

STEMMA releases carry two independent provenance layers (ADR-0054). They answer
different questions and neither replaces the other:

| Layer | Mechanism | Answers |
|---|---|---|
| 1 — owner signature | `SHA256SUMS.sig`, signed locally with the owner's GPG key | *the owner approved this content* |
| 2 — build provenance | Sigstore keyless attestation, produced by CI | *this exact workflow built these bytes from this commit* |

Layer 2 verifies without any secret:

```bash
gh attestation verify knowledge.learninghub.json --repo STEMORG2026/STEMMA
```

A **final** release (`vX.Y.Z`) carries both. A **release candidate**
(`vX.Y.Z-rcN`) carries layer 2 only — which is why it is published as a
pre-release and why a final tag must point at the exact commit of the last
passing `-rcN` (`docs/VERSIONING.md` §7).

## ⚠️ Never commit private key material

The owner's **private key** and its **revocation certificate** must never enter
this repository. They live only in the owner's keyring (`~/.gnupg`) and an
offline backup, and `sign_release_bundle.py` reads them from the local keyring —
the GPG key is never stored in GitHub Actions secrets or used by any workflow
(`docs/API.md` → "Owner signature").

`.gitignore` enforces this with `*.asc` + `*.rev`, negated only for
`docs/keys/stemma-owner-pubkey.asc`. If you ever need to add a second public
key here, extend that negation explicitly — do not remove the blanket rules.

If a private key is ever exposed, treat it as compromised: import the revocation
certificate to publish the revocation, then generate a replacement key and
update this file and the fingerprint table above.

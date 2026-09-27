# explorer/ — canonical graph explorer (frontend)

Minimal Node/Astro-style frontend over the derived export: clean small nodes,
thin lines, manual legend, centered zoom. Visualizes entities/connections from
`exports/knowledge.json` (derived — never canonical markdown).

- **Build (CI):** explorer-build job in [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- **Data dependency:** regenerate `exports/` first (`python3 scripts/validate.py`)
- See also [../docs/PHYSICS-MINIMAL-DESIGN-V2.md](../docs/PHYSICS-MINIMAL-DESIGN-V2.md)

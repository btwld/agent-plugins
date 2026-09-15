# Agent Plugins

This repository owns Concepta's Product, Engineering, and Design kits for Codex
and Claude Code. Maintain these kits directly; do not introduce upstream skill
tracking, import/merge workflows, or synchronization with another skills repository.

## Ownership

- Product Kit owns exploration, research, PRDs, requirements/questions, and WBS.
  Reuse its record contract rather than duplicating requirements or resolutions.
- Engineering Kit owns technical decisions, implementation plans and execution,
  specialized reviews, business-rule modeling, and verification. Keep delivery
  breakdowns distinct from implementation plans; no automatic handoff is required.
- Design Kit owns interface design, critique, accessibility, UX copy, and study planning.
  Product Kit owns research synthesis; Engineering Kit owns functional verification.
- Dart/Flutter is an external official plugin managed by the client. Keep its
  skills and MCP configuration out of these kits; see docs/external-plugins.md.

## Author and maintain

- Canonical content lives in `plugins/<kit>/`. Resolve helpers and resources from
  the loaded skill's location. Do not edit installed caches or duplicate bundles.
- Use Skill Creator for skill changes and provider guidance for packaging. Give
  each skill a clear outcome; add components only when they serve a concrete use.
- Preserve user scope, authoritative IDs, and the distinction between evidence,
  proposals, decisions, and implementation proof. JSON schemas define structured
  records; Word/PDF references define presentation.
- Retain source attribution and license notices. `SOURCES.md` is informational,
  not an instruction to fetch, compare, or merge external repositories.
- Keep project evidence and generated deliverables outside plugin packages.
  Preserve unrelated files and active plugin installations.

## Validate and release

Keep both catalogs and both provider manifests aligned. Run the README checks and
focused validation for changed behavior. Separate structural validation from
behavioral evaluation; do not report fixtures as executed tests. Use semantic
versions and plugin-scoped release tags. Preserve prior releases in Git.

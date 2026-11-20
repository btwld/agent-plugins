# Bitwild Team Kit

Maintain one team plugin for Codex and Claude Code. Its canonical files live under
`plugins/bitwild-team-kit/`. Both marketplace entries point to that directory.
Keep skill names unique and resolve runtime resources relative to the loaded skill.
Keep prior releases in Git.

## Workflow ownership

Choose the workflow that matches the requested deliverable. Product requirements,
questions, and decisions share one source. Delivery breakdowns assign work to
packages. Engineering plans describe implementation. Design research planning
and analysis of collected evidence are separate tasks. Use Writing for Humans
for documents people act on, Writing for Agents for agent instructions, and
Deep Code Review for final review. Preserve explicit invocation policies.

Keep package-specific guidance aligned with the project's resolved dependency.
Link to upstream package guides for detail. General Dart and Flutter skills and
Dart MCP come from Flutter's official provider.

## Author and validate

Use Skill Creator for changes to a skill. Preserve source attribution, license
notices, schema and reference contracts, and existing user work. Keep client
records and generated output outside the plugin. Use fictional test fixtures.

Run the checks in README.md, verify resource paths in an isolated installed
copy, and test changed workflows. Keep the provider manifests and catalog
aligned. Record what ran separately from model discovery or behavior claims.

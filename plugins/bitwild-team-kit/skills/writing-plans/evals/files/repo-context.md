# Sanitized pre-pilot repository context

This fixture contains only the structural facts needed for the planning evaluation.

- The repository is a Git marketplace named `leo-kit`.
- Claude Code marketplace: `.claude-plugin/marketplace.json`.
- Codex marketplace: `.agents/plugins/marketplace.json`.
- Existing plugins live under `plugins/<plugin>/` and each has both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`.
- Existing plugins are `dev-tools`, `dart-flutter-kit`, and `personal-kit`.
- Skills are canonical under `plugins/<plugin>/skills/<skill-name>/`.
- Skill names must be globally unique across all plugins.
- `clean-sheet-review` currently exists at `plugins/engineering-kit/skills/clean-sheet-review/` and must have only one canonical location.
- `scripts/build-plugin-bundle.py` regenerates plugin README and skills manifest files.
- `scripts/validate-plugin-bundle.sh` validates every marketplace plugin; its plugin list must be updated when a plugin is added.
- Both marketplace files must remain synchronized.
- Listing a plugin in either marketplace does not install or activate it. The existing schemas do not use an `enabled` field; keeping the pilot inactive means not installing or upgrading it into the active environment.
- No `engineering-kit` plugin exists in this pre-pilot state.
- External baseline 1: `architecture` from `https://github.com/anthropics/knowledge-work-plugins.git`, path `engineering/skills/architecture`, commit `d463f6f0dce59a99c4869598324aac25b28ad4f9`, Apache-2.0.
- External baseline 2: `writing-plans` from `https://github.com/obra/superpowers.git`, path `skills/writing-plans`, commit `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`, MIT.
- The pilot must preserve exact external imports before adaptations, retain required license texts, and keep source URL, source path, based-on commit, reviewed-through commit, and update policy in one plugin-level `plugins/engineering-kit/SOURCES.md`.
- Exact baseline imports and later local adaptations must be separate Git commits so either can be inspected or reverted independently.
- The pilot must not push, install, disable providers, or cut over current plugins.

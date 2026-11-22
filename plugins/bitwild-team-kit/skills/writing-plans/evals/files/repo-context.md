# Example pre-pilot repository context

This fictional marketplace fixture preserves the structural facts needed for the planning evaluation. The two upstream sources are public.

- The repository is a Git marketplace named `example-marketplace`.
- Claude Code marketplace: `.claude-plugin/marketplace.json`.
- Codex marketplace: `.agents/plugins/marketplace.json`.
- Existing plugins live under `plugins/<plugin>/` and each has both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`.
- Existing plugins are `developer-utilities`, `mobile-tools`, and `personal-productivity`.
- Skills are canonical under `plugins/<plugin>/skills/<skill-name>/`.
- Skill names must be globally unique across all plugins.
- The existing `clean-sheet-review` skill lives at `plugins/developer-utilities/skills/clean-sheet-review/` and must have only one canonical location.
- `scripts/build-marketplace.py` regenerates plugin README and skills manifest files.
- `scripts/validate-marketplace.sh` validates every marketplace plugin. Update its plugin list when adding a plugin.
- Both marketplace files must remain synchronized.
- Listing a plugin in either marketplace does not install or activate it. The existing schemas do not use an `enabled` field; keeping the pilot inactive means not installing or upgrading it into the active environment.
- The proposed `engineering-workflows` plugin does not exist yet.
- External baseline 1: `architecture` from `https://github.com/anthropics/knowledge-work-plugins.git`, path `engineering/skills/architecture`, commit `d463f6f0dce59a99c4869598324aac25b28ad4f9`, Apache-2.0.
- External baseline 2: `writing-plans` from `https://github.com/obra/superpowers.git`, path `skills/writing-plans`, commit `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`, MIT.
- The pilot must preserve exact external imports before adaptations, retain required license texts, and keep source URL, source path, based-on commit, reviewed-through commit, and update policy in `plugins/engineering-workflows/SOURCES.md`.
- Exact baseline imports and later local adaptations must be separate Git commits so either can be inspected or reverted independently.
- The pilot must not push, install, disable providers, or cut over current plugins.

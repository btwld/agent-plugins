# Publish the requested PR update

Before a GitHub write, establish repository, base/head and intended draft/ready state. Confirm the head exists remotely and has the intended difference from base. Resolve material target ambiguity before writing. Reuse an existing PR for that head rather than creating a duplicate.

Read the repository's PR template from the base/default branch and preserve required fields. Use a draft when readiness is unclear or required validation/media remains incomplete; honor a request to keep an existing PR draft. Keep the PR draft while unresolved stray debug artifacts, unintended focused/disabled tests, or required checks prevent a readiness claim.

Prefer a capable connected GitHub tool. With `gh`, write the exact body to a temporary Markdown file and use `--body-file`; do not interpolate Markdown into shell commands. Submit the body without the conversational code fence.

After the write, report the PR URL, title, state, base/head and any consequential issue-link or media gap. Show the published body when useful or requested. If the write is blocked, return the prepared draft and the specific remaining action without claiming publication.

# Commit history cleanup

Adapted from cursor/plugins make-pr-easy-to-review; see the plugin's SOURCES.md and MIT notice.

Inspect the actual commits and their dependencies. Propose logical groupings sized to the change, rather than imposing a schema/UI/tests template on every branch. Rewrite only when the user requested it or approved the concrete proposal. Respect instructions to leave history untouched.

Before an authorized rewrite:

- Establish the exact local and, if published, remote head. Preserve dirty work and unrelated commits.
- Record the original local commit and its tree (`git rev-parse HEAD` and `git rev-parse HEAD^{tree}`), so the old state is recoverable.
- Keep artifact removal or code corrections separate from history-only work. If those edits are authorized, establish the intended content baseline before regrouping commits.

After regrouping, compare the resulting tree with that baseline. A mismatch means content changed; investigate before calling the operation history-only. Do not push while an unexplained tree mismatch remains. Run the checks required by the repository and actual change. Never hide behavior changes inside cleanup or bypass hooks as a shortcut.

Push only if authorized. For a rewritten published branch, verify that the remote head has not advanced and use an appropriate explicit lease. Do not overwrite another contributor's work. A local cleanup request alone does not authorize a force-push.

Report the new grouping, content-equivalence result, and publication state. If splitting is necessary, propose boundaries without discarding work.

# Browser sessions

Read this reference only when authentication, persistent state, concurrent agents, shared browser
sessions, or shutdown ownership affects a web-app verification run. It guides session selection; it
does not configure browser tooling or clean workstation storage.

## Choose state deliberately

- For disposable public flows, use the isolated state supplied by the selected browser surface.
- For exact state already open in Chrome, use the host's Chrome or browser-extension capability.
  Treat the attached tabs and profile as visible to that controller; do not copy or relaunch the
  user's personal profile.
- For repeated authenticated automation, use a dedicated persistent automation profile rather than
  the everyday browser profile. Let only one browser process own that profile at a time.
- Follow the selected host Browser or Chrome skill's own selection and lifecycle rules. Do not layer
  standalone Playwright or Chrome DevTools MCP over the same interaction merely because both are
  available.

## Coordinate concurrent runs

Give agents separate browser state when they use different accounts or may change the same tabs. A
shared dedicated browser can reduce process count, but every attached agent can observe or modify its
tabs, cookies, and navigation, so share it only when that interference is acceptable.

Do not launch two browser processes against the same persistent profile. Before launching, record:

- the task or agent that owns the session;
- the browser surface and state mode: isolated, persistent automation, or attached user state;
- whether control is independent or intentionally shared; and
- who will close the task-owned tabs, browser process, and dev server.

## Keep setup and maintenance separate

Use an already-configured Chrome DevTools MCP backend only when the verification needs DevTools
evidence the host browser cannot provide. MCP options and compatibility change by version, so verify
the installed server's documentation during an explicit setup task instead of encoding those details
here.

For requested storage diagnosis or cleanup of profiles or Chrome code-sign clones, use
`dev-machine-cleanup` if available, or inspect storage directly within the requested
scope. No personal plugin is required. For browser installation or MCP configuration, follow the selected tool’s
setup guidance. Closing this task’s browser or dev server does not require the cleanup skill.
Do not delete browser state while any browser or automation process may still own it.

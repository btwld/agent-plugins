# Reporting service plan

## Required outcomes

- Generate one weekly CSV from the existing orders database.
- Email the CSV to the finance group.
- Retry transient delivery failures without sending duplicate reports.
- Preserve an audit record containing the report period, checksum, and delivery result.

## Proposed design

- Deploy a new HTTP microservice with its own database.
- Add a queue between report generation and delivery.
- Define a runtime plugin registry for CSV, PDF, and future report formats.
- Add a client package to the monolith so it can call the service every Monday.

## Evidence learned during the partial implementation

- The existing monolith already owns the scheduler, orders transaction boundary, email client, and
  audit database.
- Only CSV is approved; no second format is planned.
- Reporting has no independent scaling, availability, or deployment requirement.
- The same team owns and deploys both proposed services.
- No external consumer or public API exists.

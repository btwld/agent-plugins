# StreamFlix Subscription and Licensing — SBVR Specification

**Scope:** Subscription lifecycle, billing and payment, content entitlement, and licensor revenue-share statements for the StreamFlix subscription video-on-demand service.

**Business speech community:** StreamFlix business stakeholders (product, finance, licensing).

**Out of scope:** Legacy systems (LegacyCore, VaultDRM, TitleHub, PayBridge), migration and cutover, CDN and streaming delivery, recommendation engine, client applications, A/B testing, marketing tooling, customer-support tooling. These appear as evidence context only and carry no business meaning in this vocabulary.

**Evidence posture:** Items are tagged Confirmed (walkthrough/stakeholder-observed), Confirmed shape (concept confirmed; a detail is open), Candidate (plausible, not yet validated), or Open (unresolved; lives in Open Questions only). The archive/00_Initial_Blueprint is treated as LOW-confidence background; all confirmed items derive from the validated working set (documents 01–04) and the system walkthrough (document 03).

---

## Part 1: Vocabulary

### Subscriber and Account Concepts

#### account
an entity that holds a subscriber's identity, payment methods, and subscription relationship with StreamFlix.

- Reference Scheme: account identifier identifies account
- Note: Confirmed. Each account may hold one or more subscribers (identities) and a single active subscription record. Multiple historical subscription records may exist.

#### subscriber
a person who holds an account with StreamFlix and is subject to the subscription agreement.

- Reference Scheme: subscriber identifier identifies subscriber
- Note: Confirmed.

#### subscription
an agreement under which a subscriber pays recurring fees for access to the StreamFlix catalog, associated with a single account, carrying a plan and a lifecycle status at any point in time.

- Reference Scheme: subscription identifier identifies subscription
- Note: Confirmed. Plan tier is a changeable attribute of the subscription, not a permanent subtype. A subscriber may upgrade or downgrade at any time; the plan field on the subscription record changes accordingly.

#### subscription status
the current lifecycle state of a subscription.

- Reference Scheme: subscription status name identifies subscription status
- Note: Confirmed. Allowed values are closed by definitional rule D2. Values observed: Trialing, Active, Past Due, Canceled, Reactivated.

#### plan
the tier of service to which a subscription is currently committed, determining concurrent-stream entitlement.

- Note: Confirmed. Plan is a changeable attribute of a subscription, not a permanent subtype. Allowed values: Basic, Standard, Premium. A subscription's plan may change as a result of an upgrade or downgrade; such a change does not create a new subscription record.

#### payment method
a means of payment on file for an account, used to settle invoices.

- Note: Confirmed shape. Cards and other payment instruments are confirmed to exist as a list on the account; specific payment-method types are not enumerated in this scope.

---

### Billing and Payment Concepts

#### invoice
a record of charges and credits generated for a billing event, associated with a subscription and carrying a settlement status.

- Reference Scheme: invoice identifier identifies invoice
- Note: Confirmed. Each such record has a billing period, a total amount due, one or more invoice lines, and zero or more associated payments. Settlement status values are Open, Settled, and Void.

#### invoice status
the current settlement state of an invoice.

- Reference Scheme: invoice status name identifies invoice status
- Note: Confirmed. Allowed values are closed by definitional rule D4. Values observed: Open, Settled, Void.

#### invoice line
a component of an invoice recording a single charge or credit item.

- Note: Confirmed. Invoice lines are parts of their invoice; they cannot exist independently. Observed types: subscription recurring fee, proration charge (upgrade), proration credit (downgrade), account credit applied. Full taxonomy is Confirmed shape; see Open Question OQ-4.

#### payment
a record of a single collection attempt against an invoice, carrying a processing status.

- Reference Scheme: payment identifier identifies payment
- Note: Confirmed. Multiple such records may exist against a single invoice when retries occur. A refund is recorded as a record with Refunded processing status linked to the original Settled record, not as a separate object type.

#### payment status
the current processing state of a payment.

- Reference Scheme: payment status name identifies payment status
- Note: Confirmed. Allowed values are closed by definitional rule D6. Values observed: Pending, Settled, Failed, Refunded, Charged Back.

#### account credit
a balance of credit held on an account that may be applied to invoices before a payment attempt is initiated.

- Note: Confirmed. Modeled as a balance on the account. Application sequence (credits before payment) is confirmed. Expiry rules are Open; see Open Question OQ-5.

---

### Content and Licensing Concepts

#### title
a film or series available or formerly available in the StreamFlix catalog.

- Reference Scheme: title identifier identifies title
- Note: Confirmed. Titles persist in the catalog for historical reference even after their associated content license is removed.

#### content license
a time-limited, regionally scoped agreement granting StreamFlix the right to make a title available to subscribers, carrying an availability status.

- Reference Scheme: content license identifier identifies content license
- Note: Confirmed. Each such agreement specifies a licensor, a title, a licensing window (start date and end date), a set of covered regions, and a status tracking its availability lifecycle.

#### content license status
the current availability state of a content license.

- Reference Scheme: content license status name identifies content license status
- Note: Confirmed. Allowed values are closed by definitional rule D8. Values observed: Acquired, Scheduled, Available, Expiring, Removed.

#### region
a geographic area used to scope content license coverage and subscriber entitlement.

- Note: Confirmed. A subscriber's entitlement region is determined by the billing region of their account, not by the device's physical location at the time of access.

#### licensor
a studio or rights holder that licenses content to StreamFlix and receives periodic revenue-share statements.

- Reference Scheme: licensor identifier identifies licensor
- Note: Confirmed. Each licensor has an associated rate configuration used to compute revenue-share statements.

---

### Licensor Statement Concepts

#### licensor statement
a periodic document delivered to a licensor recording the royalty amount owed for subscriber watch activity on that licensor's titles during a statement period.

- Reference Scheme: licensor statement identifier identifies licensor statement
- Note: Confirmed shape. Monthly cadence confirmed. Statement structure confirmed (licensor, period, title rows with play events and play minutes, total royalty amount). Computation method varies by licensor rate type and is Confirmed shape; see Open Question OQ-1.

#### licensor rate configuration
the rate terms agreed between StreamFlix and a licensor, specifying the rate type and rate value effective from a given date, used to compute royalties on licensor statements.

- Note: Confirmed. Each licensor may have multiple rate configuration records keyed to an effective date, so that historical statements use the rate in force at the time of the statement period. Rate type values observed: per-minute, pool-share, per-completion.

#### watch activity record
a record of subscriber viewing of a title during a statement period, used as input to licensor statement computation.

- Note: Confirmed shape. Watch activity data is confirmed as the input to licensor statement computation. Granularity and sourcing are Open; see Open Question OQ-2.

---

### Policy Concepts

#### trial period policy
a policy that specifies the duration of the free trial granted to a new subscriber.

- Note: Confirmed. Current setting: 14 days. A trial is non-repeatable: it is granted once per account and may not be re-granted to the same account.

#### grace period policy
a policy that specifies the maximum duration during which a subscriber retains entitlement access after a subscription enters Past Due status.

- Note: Confirmed value observed in configuration (7 days), pending Finance sign-off. Rules reference this policy term, not a specific duration. See Open Question OQ-6.

#### payment retry policy
a policy that specifies the number and schedule of payment retry attempts during the dunning period.

- Note: Confirmed. Current setting: up to the retry count defined by this policy, at the retry schedule defined by this policy. Observed values: retry count 3; retry schedule on days 1, 3, and 7 of Past Due status.

#### concurrent stream limit policy
a policy that specifies the maximum number of simultaneous streams permitted per account for a given plan tier.

- Note: Confirmed. Current settings: Basic — 2 streams; Standard — 4 streams; Premium — 6 streams. These are policy values that may change; rules reference this policy, not the specific numbers.

#### expiring threshold policy
a policy that specifies how far in advance of a content license's end date the content license status transitions to Expiring.

- Note: Candidate. A 30-day threshold was stated by Fatima Owusu during the walkthrough and observed in a live Expiring-status license (end date 25 days out), but was not confirmed in the policy configuration table. See Open Question OQ-7.

#### regional price policy
a policy that specifies the list price for each plan tier in each region.

- Note: Confirmed shape. Regional prices differ by plan tier and region. Specific values are not disclosed. A subscription records the committed price at the time of creation; that committed price may differ from the current list price if prices have changed since the subscription started.

#### licensor statement period policy
a policy that specifies the cadence and period boundaries for licensor statement production.

- Note: Confirmed. Current setting: monthly, covering one calendar month of watch activity.

---

## Part 2: Fact Types

### Subscriber and Subscription Relationships

#### account holds subscription
- Preferred: account holds subscription
- Alternative: subscription belongs to account

Necessity:
- each account holds at most one active subscription
- each subscription belongs to exactly one account

#### subscription has subscription status
- Preferred: subscription has subscription status
- Alternative: subscription status is held by subscription

Necessity:
- each subscription has exactly one subscription status

#### subscription has plan
- Preferred: subscription has plan
- Alternative: plan is assigned to subscription

Necessity:
- each subscription has exactly one plan

Note: Plan is a changeable attribute, not a permanent subtype. A subscription's plan changes when the subscriber upgrades or downgrades; the subscription record itself is not replaced.

#### subscription has committed price
- Preferred: subscription has committed price
- Alternative: committed price is recorded on subscription

Necessity:
- each subscription has exactly one committed price

Note: Confirmed. The committed price is set at the time the subscription is created and may differ from the current list price for that plan tier if prices have subsequently changed (grandfathering). Rules reference this fact type for grandfathering obligations.

---

### Invoice and Payment Relationships

#### subscription generates invoice
- Preferred: subscription generates invoice
- Alternative: invoice is generated for subscription

Necessity:
- each subscription generates zero or more invoices
- each invoice is generated for exactly one subscription

#### invoice line is part of invoice
- Preferred: invoice line is part of invoice
- Alternative: invoice contains invoice line

Necessity:
- each invoice line is part of exactly one invoice
- each invoice contains at least one invoice line

Note: Partitive relationship. An invoice line cannot exist independently of its invoice.

#### invoice has invoice status
- Preferred: invoice has invoice status
- Alternative: invoice status is held by invoice

Necessity:
- each invoice has exactly one invoice status

#### payment is attempted against invoice
- Preferred: payment is attempted against invoice
- Alternative: invoice has payment attempted against it

Necessity:
- each payment is attempted against exactly one invoice
- each invoice has zero or more payments attempted against it

#### payment satisfies invoice
- Preferred: payment satisfies invoice
- Alternative: invoice is satisfied by payment

Necessity:
- each invoice is satisfied by at most one payment
- each payment satisfies at most one invoice

Note: Associative relationship. A payment satisfies an invoice when the payment reaches Settled status. This is distinct from the attempted-against relationship, which records every attempt including failures.

#### payment has payment status
- Preferred: payment has payment status
- Alternative: payment status is held by payment

Necessity:
- each payment has exactly one payment status

#### account holds account credit
- Preferred: account holds account credit
- Alternative: account credit is held by account

Necessity:
- each account holds at most one account credit balance

#### account has payment method
- Preferred: account has payment method
- Alternative: payment method is registered on account

Necessity:
- each account has zero or more payment methods
- each payment method is registered on exactly one account

---

### Content and Licensing Relationships

#### content license covers region
- Preferred: content license covers region
- Alternative: region is covered by content license

Necessity:
- each content license covers at least one region
- each region is covered by zero or more content licenses

#### content license applies to title
- Preferred: content license applies to title
- Alternative: title is subject to content license

Necessity:
- each content license applies to exactly one title
- each title is subject to zero or more content licenses

#### content license has content license status
- Preferred: content license has content license status
- Alternative: content license status is held by content license

Necessity:
- each content license has exactly one content license status

#### content license is held by licensor
- Preferred: content license is held by licensor
- Alternative: licensor holds content license

Necessity:
- each content license is held by exactly one licensor
- each licensor holds zero or more content licenses

#### account has region
- Preferred: account has region
- Alternative: region is the billing region of account

Necessity:
- each account has exactly one region

Note: Confirmed. The account's billing region governs content entitlement region evaluation. The device's physical location at time of access is not the governing attribute.

---

### Licensor Statement Relationships

#### licensor statement covers licensor
- Preferred: licensor statement covers licensor
- Alternative: licensor is covered by licensor statement

Necessity:
- each licensor statement covers exactly one licensor
- each licensor is covered by zero or more licensor statements

#### licensor rate configuration applies to licensor
- Preferred: licensor rate configuration applies to licensor
- Alternative: licensor has licensor rate configuration

Necessity:
- each licensor rate configuration applies to exactly one licensor
- each licensor has at least one licensor rate configuration

#### watch activity record is attributed to title
- Preferred: watch activity record is attributed to title
- Alternative: title has watch activity record attributed to it

Necessity:
- each watch activity record is attributed to exactly one title
- each title has zero or more watch activity records attributed to it

---

## Part 3: Rules

### Derivation Rules

**DR1:** total royalty amount of a licensor statement = sum of amounts attributed to each watch activity record that is attributed to a title subject to a content license held by the licensor covered by that statement during the statement period, computed according to the licensor rate configuration applicable to that licensor for that period.

- Note: Confirmed shape. The structure of the derivation (watch activity × rate configuration → royalty amount) is confirmed. The exact formula per rate type (per-minute, pool-share, per-completion) is Open; see Open Question OQ-1.

---

### Definitional Rules

**D1:** It is necessary that each subscription has exactly one subscription identifier.

**D2:** It is impossible that a subscription status is other than Trialing, Active, Past Due, Canceled, or Reactivated.

- Note: Confirmed. Five status values were observed across all records in the SubAdmin console.

**D3:** It is necessary that each invoice has exactly one invoice identifier.

**D4:** It is impossible that an invoice status is other than Open, Settled, or Void.

- Note: Confirmed. Three invoice status values observed in the billing admin.

**D5:** It is necessary that each payment has exactly one payment identifier.

**D6:** It is impossible that a payment status is other than Pending, Settled, Failed, Refunded, or Charged Back.

- Note: Confirmed. Five payment status values observed in the billing admin.

**D7:** It is necessary that each content license has exactly one content license identifier.

**D8:** It is impossible that a content license status is other than Acquired, Scheduled, Available, Expiring, or Removed.

- Note: Confirmed. Five content license status values observed in LicenseDesk.

**D9:** It is necessary that each account has exactly one account identifier.

**D10:** It is necessary that each licensor statement has exactly one licensor statement identifier.

**D11:** It is necessary that each licensor has exactly one licensor identifier.

**D12:** It is necessary that each title has exactly one title identifier.

**D13:** It is impossible that a plan is other than Basic, Standard, or Premium.

- Note: Confirmed. Three plan tier values observed; plan is a changeable attribute of a subscription.

---

### Behavioral Rules

#### Subscription Lifecycle

**B1:** It is obligatory that a subscription's subscription status begins as Trialing when a new subscriber's trial is initiated.

- Note: Confirmed.

**B2:** It is obligatory that a subscription transitions from Trialing to Active only when a payment for that subscription is settled at trial end.

- Note: Confirmed. If payment fails at trial end, the subscription transitions directly to Canceled, bypassing the dunning flow.

**B3:** It is obligatory that a subscription transitions from Trialing to Canceled when the trial period expires and no payment is settled, according to the trial period policy.

- Note: Confirmed. The grace period and payment retry policy do not apply to trial-end failures.

**B4:** It is prohibited that a subscription returns to Trialing status once it has left Trialing status.

- Note: Confirmed. The trial is non-repeatable per account.

**B5:** It is obligatory that a subscription transitions from Active to Past Due when a recurring payment attempt fails.

- Note: Confirmed.

**B6:** It is obligatory that a subscription transitions from Past Due to Active when a retry payment for that subscription is settled within the grace period defined by the grace period policy.

- Note: Confirmed.

**B7:** It is obligatory that a subscription transitions from Past Due to Canceled when the grace period defined by the grace period policy elapses without a settled payment.

- Note: Confirmed value (7 days) observed in configuration; pending Finance sign-off. See Open Question OQ-6.

**B8:** It is prohibited that a subscription transitions from Canceled to any status other than Reactivated.

- Note: Confirmed. Reactivation is the only path out of Canceled status.

**B9:** It is obligatory that a subscription that has been reactivated carries Reactivated as its subscription status.

- Note: Confirmed. A reactivated subscription receives a new subscription record; the prior Canceled record is preserved.

**B10:** It is permitted that a subscription's plan is changed to a different plan only if the subscription's subscription status is Active or Reactivated.

- Note: Confirmed shape. Upgrade takes effect immediately; downgrade at the next billing cycle. Proration method is Open; see Open Question OQ-3.

#### Billing and Payment

**B11:** It is obligatory that payment retry attempts are made according to the payment retry policy when a subscription is in Past Due status.

- Note: Confirmed. Retries occur at the intervals and count specified by the payment retry policy.

**B12:** It is obligatory that an account credit balance is applied to an invoice before a payment attempt is initiated against that invoice.

- Note: Confirmed.

**B13:** It is obligatory that an invoice's invoice status is set to Settled when a payment against that invoice reaches Settled status.

- Note: Confirmed.

**B14:** It is obligatory that an invoice's invoice status is set to Void when the associated subscription is canceled before the invoice is settled.

- Note: Confirmed. Observed in test account walkthrough.

**B15:** It is prohibited that a payment transitions from Settled status to any status other than Refunded or Charged Back.

- Note: Confirmed. A Settled payment may be reversed by refund or chargeback, but no other status change is permitted.

**B16:** It is obligatory that a chargeback event results in the associated payment's payment status being set to Charged Back.

- Note: Confirmed. The business process following a Charged Back payment status is Open; see Open Question OQ-8.

#### Content Entitlement

**B17:** It is obligatory that playback of a title by a subscriber is permitted only if all of the following hold: the subscriber's subscription has subscription status in {Trialing, Active, Past Due, Reactivated}; the content license for the title in the subscriber's account region has content license status Available or Expiring; and the number of concurrent streams active on the subscriber's account is below the limit specified by the concurrent stream limit policy for the account's plan.

- Note: Confirmed. Past Due is in the entitled set during the grace period (corrected during session). Expiring titles remain playable. Entitlement region is the account's billing region.

**B18:** It is prohibited that a title is made available for playback when the content license covering that title in the subscriber's account region has content license status Removed.

- Note: Confirmed. The title record is retained in the catalog, but playback is denied.

**B19:** It is obligatory that a content license's content license status transitions from Available to Expiring when the content license's end date is within the threshold specified by the expiring threshold policy.

- Note: Candidate. 30-day threshold stated by Fatima Owusu; observed live (license with 25-day remaining showed Expiring), but not observed in policy table. See Open Question OQ-7.

**B20:** It is obligatory that a content license's content license status transitions to Removed when the content license's end date has passed.

- Note: Confirmed.

#### Trial and Grandfathering

**B21:** It is prohibited that a trial period is granted to an account that has previously received a trial period.

- Note: Confirmed. The trial is account-scoped and non-repeatable.

**B22:** It is obligatory that a subscription's committed price is set to the current list price defined by the regional price policy for the subscription's plan and region at the time the subscription is created.

- Note: Confirmed shape. Subscriptions record their committed price at creation; the committed price does not change when the regional price policy changes.

**B23:** It is prohibited that the committed price of an existing subscription is changed solely because the regional price policy for that subscription's plan and region has changed.

- Note: Confirmed. Grandfathering: existing subscribers retain the committed price at which their subscription was created. Only subscribers creating a new subscription, or reactivating after Canceled status, pay the current list price.

**B24:** It is obligatory that a reactivated subscription has its committed price set to the current list price defined by the regional price policy at the time of reactivation.

- Note: Confirmed. Stated by Diego Câmara: reactivation always uses the current list price. A previously grandfathered price does not carry over after cancellation and reactivation.

#### Licensor Statements

**B25:** It is obligatory that a licensor statement is produced for each licensor for each period defined by the licensor statement period policy.

- Note: Confirmed. Monthly cadence confirmed.

**B26:** It is obligatory that a licensor statement is computed using the licensor rate configuration whose effective date is on or before the statement period and whose replacement, if any, has an effective date after the statement period.

- Note: Confirmed. Rate configurations are keyed to an effective date; a new rate record is added when a licensor renegotiates, preserving historical rates for prior statements.

**B27:** It is obligatory that a licensor statement reflects watch activity records attributed to titles held under content licenses held by that licensor during the statement period.

- Note: Confirmed shape. That watch activity is the input is confirmed; the computation method (per-minute, pool-share, per-completion) varies by licensor and is Open. See Open Question OQ-1.

---

## Open Questions

*These questions are in-scope but currently unconfirmed. Each one blocks one or more terms or rules currently at Confirmed shape or Candidate. This list is preliminary; additional questions may emerge as answers to these questions are received.*

**OQ-1 — Licensor revenue-share computation method** (blocks B27 from Confirmed to Confirmed)

We know licensor statements are produced monthly and derive royalties from subscriber watch activity on the licensor's titles. We confirmed that rate type varies by licensor (per-minute, pool-share, per-completion are all in use). What we do not know is how each rate type is computed: for a per-minute rate, is the royalty the product of total minutes played and the rate value? For a pool-share rate, is the licensor's share computed as their fraction of total platform watch minutes multiplied by a revenue pool — and if so, how is the pool defined? For a per-completion rate, what constitutes a completion event? Answering this unlocks the derivation rule for licensor statement royalty computation, currently stuck at Confirmed shape.

**OQ-2 — Watch activity data: source and granularity** (blocks watch activity record from Confirmed shape to Confirmed)

We know watch activity records are the input to licensor statement computation. We do not know where this data originates (CDN playback events, client apps, or a separate analytics pipeline), what granularity is available (play start/stop events, play seconds, completion events), and whether the new system consumes this data directly or depends on a separate pipeline. Until this is confirmed, we cannot fully specify the watch activity record term or the derivation rule for statement computation.

**OQ-3 — Proration method for mid-cycle plan-tier changes** (blocks invoice line taxonomy and B10)

We know subscribers can change their plan tier mid-cycle and that a proration charge or credit is recorded as an invoice line. For an upgrade, is the subscriber charged immediately for the incremental amount pro-rated to remaining days, or is it rolled into the next invoice? For a downgrade, is a credit issued immediately or deferred to the next billing cycle? Answering this unlocks the proration invoice line rules.

**OQ-4 — Full invoice line-item taxonomy** (blocks invoice line definition)

We confirmed four invoice line types: subscription recurring fee, proration charge, proration credit, and account credit applied. We do not know whether additional types exist (tax, late-payment fee, reactivation fee). Answering this completes the invoice line term's scope.

**OQ-5 — Account credit expiry rule** (blocks account credit from Confirmed shape to Confirmed)

We know account credits are held as a balance on the account and applied to invoices before payment. We do not know whether credits expire, and if so, how long after issuance. Answering this unlocks the account credit expiry behavioral rule.

**OQ-6 — Grace period length — Finance sign-off** (blocks grace period policy value)

We observed a 7-day grace period in the payment policy configuration table, and this value was used in dunning job logs. The product team noted the value is under Finance review. Can Finance confirm 7 days as the approved grace period, or provide the approved value and its effective date? Answering this confirms the grace period policy current setting, currently recorded as pending sign-off.

**OQ-7 — Expiring threshold: global or per-licensor, and confirmed value** (blocks expiring threshold policy from Candidate to Confirmed)

We observed a content license with 25 days remaining showing Expiring status, and Fatima Owusu stated a 30-day threshold. We did not observe this value in the system policy configuration table. Can you confirm the threshold and whether it is a single global value or configured per licensor or content category? Answering this confirms the expiring threshold policy and promotes B19 from Candidate to Confirmed.

**OQ-8 — Chargeback handling process** (blocks B16 scope)

We confirmed that a Charged Back payment status is recorded when the card issuer reverses a charge. We do not know the business process that follows: does the subscription move to a specific status immediately? Is there a review queue before any subscriber-facing action? Is the subscriber given a window to provide a new payment method? Answering this unlocks the chargeback behavioral rule beyond the payment status update.

**OQ-9 — Reactivated status: transient or persistent** (blocks lifecycle completeness)

We confirmed that a reactivated subscription receives Reactivated as its subscription status immediately on reactivation, and that entitlement treats Reactivated the same as Active. Diego Câmara stated the status resolves to Active after approximately 30 days or the first successful billing cycle, but noted this behavior may not be formally documented. Is Reactivated a persistent status or a transient one? If transient, what is the transition condition, and is that condition a business rule or an implementation detail? Answering this completes the subscription status transition rules.

---

## Deferred Rule Areas

The following topics are deliberately out of scope for this specification and are not modeled here:

- **Legacy systems (LegacyCore, VaultDRM, TitleHub, PayBridge):** These are incumbent implementation systems being replaced. No business rules depend on their names or internal behavior. VaultDRM license tokens are an implementation artifact downstream of the business entitlement decision.
- **Migration and cutover:** Data migration, cutover sequencing, and dual-run operations are project management and implementation concerns, not business vocabulary.
- **CDN and streaming delivery:** How encoded video reaches a subscriber's device is infrastructure. CDN geo-blocking is a separate enforcement layer; the business entitlement rule uses account billing region.
- **Recommendation engine:** Content discovery and personalization are outside this business slice.
- **Client applications:** TV app, mobile app, and web player internal behavior and UX are out of scope.
- **Annual billing dunning schedule:** Whether annual billing cycles use a different retry or grace-period schedule than monthly billing is currently Open (no confirmed difference), and modeling a separate policy before the business confirms a difference would be premature. If Finance confirms a separate schedule, a separate annual billing policy term and associated rules should be added.
- **Profile-level content rating enforcement:** Profile-level parental controls and age gating were mentioned during the walkthrough but not confirmed as in scope for the entitlement business model. If confirmed in scope, a profile term and associated rating-gate rules would be required.
- **Regional licensing edge cases (travel and VPN):** The business rule for a subscriber accessing from a region other than their account billing region is pending confirmation (Fatima Owusu stated account region governs; CDN geo-blocking is a separate layer). The current entitlement rule (B17) uses account billing region. If a separate business rule for travel or VPN scenarios is confirmed, it should be modeled explicitly.
- **Statement dispute workflow:** A formal in-system dispute or acknowledgment workflow for licensor statements is confirmed as out of scope for the current replacement program (email-based today).
- **Account credit expiry rule:** Deferred pending Open Question OQ-5. No expiry rule currently applies; one may be added when Finance confirms the policy.
- **Promotional reactivation pricing:** Whether reactivating subscribers can receive a promotional price other than the current list price is Candidate (existence not confirmed in walkthrough). Deferred until confirmed.

# Repeatable WBS reviews

Use the data-driven generator for grouped WBS timelines and quick regeneration.
Use [the WBS source](wbs-template.md) and [Word reference](../assets/wbs/reference.docx) for manually authored Word reviews, including
unscheduled drafts. Use the bundled scripts for generation; the Word reference supplies layout only.

## One source with six views

| Data | Generated view |
| --- | --- |
| Groups and packages | Grouped WBS hierarchy and timeline rows |
| Package deliverable, owner, and completion evidence | Work package dictionary |
| Package dates and dependencies | Calendar timeline and prerequisite arrows |
| Ordered stage definitions | Consistent lifecycle colors and legend |
| Releases and milestones | Release windows and readiness or acceptance gates |
| Requirement baseline and package assignments | Exactly-once requirement coverage |

Groups, releases, and lifecycle stages are separate concepts. Multiple groups may
contribute to one release, and release windows may overlap. The generator checks
supplied dates; it does not estimate work, optimize staffing, compute a critical
path, or approve the plan.

## Process

1. Copy `assets/examples/wbs/plan.json` (relative to the plugin root) to a project-specific location. Replace the fictional
   content from authoritative requirements and planning sources. Preserve the
   requirement baseline separately from package assignments.
2. Define outcome-based groups and packages. Name the deliverable, owner, and
   evidence needed to call each package complete.
3. Assign every supplied requirement exactly once to a primary package. Put
   optional, deferred, and excluded items in explicit unscheduled packages.
4. Supply release windows, stage dates, finish-to-start dependencies, and gates.
   Use `Unassigned` for unknown people. If dates are unknown, use the Word draft
   until planning supplies them; do not invent dates just to render a timeline.
5. Validate, generate, and inspect the HTML/PDF. Edit the JSON, not generated
   HTML or SVG. Regeneration replaces files in the chosen output directory.
6. Record decisions in the actual project tracker or authority. Structural
   validation and a generated review are not scope or schedule approval.

## Run

From the repository root, with Python 3.10 or newer:

```sh
python3 plugins/product-kit/scripts/build_wbs.py plugins/product-kit/assets/examples/wbs/plan.json --check
python3 plugins/product-kit/scripts/build_wbs.py plugins/product-kit/assets/examples/wbs/plan.json --out .context/wbs-review
python3 plugins/product-kit/scripts/build_wbs.py plugins/product-kit/assets/examples/wbs/plan.json --out .context/wbs-review --pdf
```

HTML and validation use only the Python standard library. PDF export requires
Chrome or Chromium; set `CHROME_BIN` or pass `--chrome` if needed. The export uses
an isolated temporary browser profile. Charts and styles are embedded, with no
external assets. The source fingerprint identifies the exact input JSON bytes.

## Input contract

`assets/examples/wbs/plan.json` (relative to the plugin root) is the complete runnable reference. All shown fields are
required. IDs are unique within each collection; references use exact IDs.

| Collection | Fields |
| --- | --- |
| `project` | `name`, `subtitle`, `status`, `owner`, `baseline`, `start`, `end` |
| `stages` | `id`, `name`, `color` as six-digit hex; array order defines lifecycle order |
| `groups` | `id`, `name`; array order controls grouping |
| `releases` | `id`, `name`, `start`, `end` |
| `packages` | `id`, `group`, `name`, `owner`, `deliverable`, `done`, `disposition`, `release`, `dependencies`, `requirements`, `stages` |
| Package `stages` | `stage` definition ID, `start`, `end` |
| `milestones` | `id`, `name`, `date`, `release`, `requires` package IDs, `owner`, `evidence`, `status` |
| `requirements` | `id`, `title`, `statement`, `disposition`, `source` |

Dates use ISO `YYYY-MM-DD`. Intervals are **start-inclusive, end-exclusive**:
a package ending November 12 is complete at that day's boundary, so a successor
or UAT-ready gate may start November 12. Week labels are seven-day periods from
project start, not business-week estimates. Weekends are not removed.

Stages may be omitted when inapplicable, but cannot repeat, overlap, or violate
their declared order. Parallel work belongs in separate packages. Dependencies
mean the **entire predecessor package** finishes before the successor's first
stage. Other dependency types and lags are not supported.

`disposition` is `Current`, `Optional`, `Deferred`, or `Excluded`. Current packages
require a release and nonempty stage schedule within that release. Other packages
require `release: null`, `stages: []`, and `dependencies: []`. Package and assigned
requirement dispositions must agree; split different dispositions into separate
packages even when they concern the same module.

Milestone prerequisites must be scheduled and finish by the gate date. Gate status
is supplied text such as `Pending`; dates never imply that a gate passed. A gate
may require packages from another release.

Timeline panels cover at most 12 weeks and 10 package rows. Arrows appear where
both endpoints are visible; every dependency is always listed in the dictionary.
Long row labels are shortened, with full names retained in the dictionary.
Unscheduled scope appears outside the roadmap.

## Checks and limits

Validation rejects missing fields, duplicate IDs, invalid references, missing or
duplicate primary assignments, disposition conflicts, invalid windows, overlapping
stages, dependency cycles, and premature gates. It cannot find requirements absent
from the supplied baseline: reconcile that collection against the actual sources.

The views are deterministic projections; PDF binary metadata may vary. Review
rendered output after layout changes, especially with long labels, many releases,
or long evidence statements. Run the regression checks with:

```sh
uv run --with jsonschema==4.26.0 python -m unittest discover -s plugins/product-kit/scripts/tests -v
```

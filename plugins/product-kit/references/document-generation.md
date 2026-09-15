# Document generation and references

## Choose an output

Use JSON and the product generator for connected PRDs and registries. HTML and
Markdown are generated together, with a source fingerprint. The query command
provides JSON without scraping documents. See [the model contract](product-model.md).

For Word, use the available document workflow with the retained reference and
validated records. Preserve its page setup, typography, table hierarchy, and
review-response layout. Adapt module packets to the actual scope: the reference
does not require modules or define record ownership. Preserve exact requirement
text and shared question IDs. No Word skill is needed for JSON or HTML workflows.

For PDF, print generated HTML or render completed Word with available document
tools. Inspect every page before sharing. Refresh exported PDFs after source
changes; they are snapshots. The bundled WBS script also supports --pdf through
Chrome/Chromium, using an isolated browser profile.

## Assets

| Reference | Purpose |
| --- | --- |
| [PRD source](prd-template.md) | Maintained manual Word-template content |
| [PRD Word](../assets/prd/reference.docx) | Reusable layout |
| [PRD PDF](../assets/prd/reference.pdf) | Verified visual reference |
| [PRD preview](../assets/prd/preview.png) | First page |
| [WBS source](wbs-template.md) | Maintained manual WBS-template content |
| [WBS Word](../assets/wbs/reference.docx) | Delivery-review layout |
| [WBS PDF](../assets/wbs/reference.pdf) | Verified visual reference |
| [WBS preview](../assets/wbs/preview.png) | First page |
| [WBS example HTML](../assets/examples/wbs/wbs-review.html) | Fictional generated review |
| [WBS example PDF](../assets/examples/wbs/wbs-review.pdf) | Matching fictional visual example |

The manual Word references predate the normalized feature/question model. They
are not identical exports of it. Word diagram slots do not generate timelines;
use the structured generator for automation. No reference supplies client scope.

## Maintain the references

Edit the relevant references/*-template.md, then run from the plugin root:

```sh
uv run --with python-docx python scripts/build_references.py --out /absolute/path/reference-review
```

This creates prd/reference.docx and wbs/reference.docx beneath the chosen output
root. Use --kind prd or --kind wbs for one document. Without --out, the builder
writes into the plugin's assets; prefer separate review output first. Render and
inspect every page before replacing retained DOCX/PDF/preview files. Keep scratch
renders outside the plugin.

## Attribution

Document-reference origins are recorded in [SOURCES.md](../SOURCES.md).
The bundled assets and helpers are self-contained.

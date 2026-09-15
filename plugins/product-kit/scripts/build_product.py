# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema==4.26.0"]
# ///
"""Validate one product model and generate connected PRD, question, and WBS views."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import build_wbs
from product_model import parse_product, require


CSS = '''
@page { size: A4; margin: 16mm; }
* { box-sizing: border-box; }
body { font: 15px/1.55 -apple-system, BlinkMacSystemFont, Arial, sans-serif; color: #19354b; background: #edf2f6; margin: 0; }
main { max-width: 1080px; padding: 42px; margin: 24px auto; background: white; }
nav, footer { font-size: 12px; color: #536a7b; border-top: 1px solid #cad5de; padding-top: 12px; }
nav { border-top: 0; border-bottom: 1px solid #cad5de; padding-bottom: 12px; }
a { color: #116b89; }
h1 { font-size: 32px; line-height: 1.2; }
h2 { font-size: 23px; margin-top: 32px; padding-top: 12px; border-top: 2px solid #d5e2eb; }
h3 { font-size: 18px; margin-top: 24px; }
p { margin: 8px 0 12px; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; font-size: 12px; margin: 12px 0 22px; }
th, td { border: 1px solid #d4dde5; padding: 9px; vertical-align: top; text-align: left; overflow-wrap: anywhere; white-space: pre-wrap; }
th { background: #203e56; color: white; }
tr:nth-child(even) td { background: #f2f5f8; }
li { white-space: pre-wrap; margin-bottom: 4px; }
thead { display: table-header-group; }
@media print {
 body { background: white; font: 10px/1.45 Arial, sans-serif; }
 main { margin: 0; padding: 0; }
 nav { display: none; }
 h1 { font-size: 24px; } h2 { font-size: 17px; } h3 { font-size: 13px; }
 table { font-size: 9px; } th, td { padding: 6px; }
 h1, h2, h3 { break-after: avoid; } tr { break-inside: avoid; }
 * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
'''


def joined(values, empty='None documented'):
    return ', '.join(values) or empty


def md(value):
    # Source prose is literal; it cannot inject links or table structure.
    text = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    for char in '\\`*_{}[]()#+-.!|':
        text = text.replace(char, '\\' + char)
    return text.replace('\n', '<br>')


class Review:
    """Keep HTML and Markdown outputs aligned from the same content operations."""
    def __init__(self, title):
        self.title = title
        self.parts = []
        self.markdown = []
        self.heading(1, title)

    def heading(self, level, text):
        self.parts.append(f'<h{level}>{build_wbs.h(text)}</h{level}>')
        self.markdown.append('#' * level + ' ' + md(text))

    def paragraph(self, text):
        self.parts.append('<p>' + build_wbs.h(text) + '</p>')
        self.markdown.append(md(text))

    def bullets(self, items):
        items = list(items)
        if not items:
            self.paragraph('None documented.')
            return
        self.parts.append('<ul>' + ''.join('<li>' + build_wbs.h(i) + '</li>' for i in items) + '</ul>')
        self.markdown.append('\n'.join('- ' + md(i) for i in items))

    def table(self, headings, rows):
        rows = list(rows)
        if not rows:
            self.paragraph('None documented.')
            return
        self.parts.append(build_wbs.table(headings, rows))
        lines = ['| ' + ' | '.join(md(v) for v in headings) + ' |',
                 '| ' + ' | '.join('---' for _ in headings) + ' |']
        lines.extend('| ' + ' | '.join(md(v) for v in row) + ' |' for row in rows)
        self.markdown.append('\n'.join(lines))

    def links(self, links):
        self.parts.append('<ul>' + ''.join(f'<li><a href="{build_wbs.h(path)}">{build_wbs.h(label)}</a></li>'
                                         for label, path in links) + '</ul>')
        self.markdown.append('\n'.join(f'- [{md(label)}]({path})' for label, path in links))

    def html(self, digest):
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<title>{build_wbs.h(self.title)}</title><style>{CSS}</style></head><body><main>'
                '<nav><a href="index.html">Review index</a> · <a href="questions.html">Questions and decisions</a> · '
                '<a href="traceability.html">Delivery traceability</a></nav>' + ''.join(self.parts) +
                f'<footer>Generated review · source SHA-256: {digest}<br>Structural validation is not scope approval or proof of implementation.</footer></main></body></html>')

    def markdown_text(self, digest):
        return '\n\n'.join(self.markdown) + f'\n\nGenerated review · source SHA-256: {digest}\n'


def add_questions(doc, model, questions, include_all_decisions=False):
    doc.heading(2, 'Questions and decisions')
    doc.paragraph('Each question is one shared record. Answered, Assumed, and Open describe the decision, not implementation validation.')
    doc.table(['Question / owner', 'Affected records', 'Status / resolution', 'Question'], [
        [q['id'] + ' / ' + q['owner'], joined([*q['scope_ids'], *q['requirement_ids']]),
         q['status'] + ' / ' + (q['decision_id'] or 'No resolution'), q['text']] for q in questions])
    decision_ids = {q['decision_id'] for q in questions if q['decision_id']}
    decisions = [d for d in model.decisions.values() if include_all_decisions or d['id'] in decision_ids]
    for decision in decisions:
        doc.heading(3, decision['id'] + ' — ' + decision['title'])
        doc.paragraph('Outcome: ' + decision['outcome'])
        doc.paragraph('Rationale: ' + decision['rationale'])
        doc.paragraph('Owner: ' + decision['owner'] + ' | Sources: ' + joined(decision['source_ids']))
    doc.paragraph('Question sources: ' + '; '.join(q['id'] + ': ' + joined(q['source_ids']) for q in questions))


def add_validations(doc, validations):
    doc.heading(2, 'Validation evidence')
    doc.paragraph('No validation record means unknown, not passed. A decision or completed task never changes these results automatically.')
    doc.table(['Validation / requirements', 'Criterion', 'Status / owner', 'Evidence or waiver'], [
        [v['id'] + ' / ' + joined(v['requirement_ids']), v['criterion'], v['status'] + ' / ' + v['owner'],
         v['waiver_reason'] or joined(v['evidence_source_ids'])] for v in validations])


def add_sources(doc, model, source_ids):
    doc.heading(2, 'Source references')
    doc.table(['ID', 'Source', 'Reference'], [[s['id'], s['title'], s['reference']]
        for s in model.sources.values() if s['id'] in source_ids])


def prd_review(model, scope_id):
    scope = model.scopes[scope_id]
    kind = 'Product' if scope_id == model.product['id'] else 'Module' if scope_id in model.modules else 'Feature'
    doc = Review(f'{kind} PRD — {scope["name"]}')
    doc.paragraph(f'{scope_id} | Product: {model.product["name"]} | {model.product["status"]}')
    doc.paragraph(scope['summary'])
    doc.heading(2, 'Outcome and boundary')
    doc.paragraph('Product objective: ' + model.product['objective'])
    doc.paragraph('Product owner: ' + model.product['owner'])
    doc.paragraph(('Users: ' if 'users' in scope else 'Product users: ') + joined(scope.get('users', model.product['users'])))
    source_ids = {*model.product['source_ids'], *scope['source_ids']}
    doc.heading(3, 'Product assumptions')
    doc.bullets(model.product['assumptions'])
    doc.heading(3, 'Product exclusions and later scope')
    doc.bullets(model.product['out_of_scope'])
    if scope_id in model.features:
        doc.heading(3, 'Feature assumptions')
        doc.bullets(scope['assumptions'])
        doc.heading(3, 'Feature exclusions')
        doc.bullets(scope['out_of_scope'])
    descendants = model.descendants(scope_id)
    children = [s for sid, s in model.scopes.items() if sid in descendants and sid != scope_id]
    doc.heading(2, 'Contained scope')
    doc.table(['ID / name', 'Parent', 'Responsibility'], [
        [s['id'] + ' / ' + s['name'], model.parents[s['id']], s['summary']] for s in children])
    for child in children:
        source_ids.update(child['source_ids'])
    features = [f for f in model.features.values() if f['id'] in descendants]
    doc.heading(2, 'Feature workflows')
    if not features:
        doc.paragraph('No feature workflows documented.')
    for feature in features:
        doc.heading(3, feature['id'] + ' — ' + feature['name'])
        doc.table(['Step', 'Actor', 'Action', 'Requirements'], [
            [s['id'], s['actor'], s['action'], joined(s['requirement_ids'])] for s in feature['workflow']])
    requirements = model.requirements_for(scope_id)
    questions = model.questions_for(scope_id)
    validations = model.validations_for([r['id'] for r in requirements])
    doc.heading(2, 'Controlled requirements')
    doc.paragraph(f'{len(requirements)} unique requirements in this view. Scope ownership and applicability are separate. Shared requirements retain their original IDs and wording.')
    doc.table(['Disposition', 'Unique requirements'], sorted(Counter(r['disposition'] for r in requirements).items()))
    for req in requirements:
        doc.heading(3, req['id'] + ' — ' + req['title'])
        doc.paragraph(req['statement'])
        doc.bullets([
            'Owned by: ' + req['scope_id'] + ' | Applies to: ' + joined(req['applies_to']),
            f'Kind: {req["kind"]} | Priority: {req["priority"]} | Disposition: {req["disposition"]}',
            f'Maturity: {req["maturity"]} | Evidence: {req["evidence_status"]} | Sources: ' + joined(req['source_ids'])])
        doc.paragraph('Acceptance criteria — ' + req['acceptance_status'])
        doc.bullets(req['acceptance_criteria'])
        related = [q['id'] + ' (' + q['status'] + ')' for q in questions
                   if req['id'] in q['requirement_ids']]
        doc.paragraph('Direct questions: ' + joined(related) + '. Scope-level questions are in the register below.')
        req_validations = model.validations_for([req['id']])
        doc.paragraph('Validation: ' + joined([v['id'] + ' (' + v['status'] + ')' for v in req_validations]))
        allocation = model.allocations.get(req['id'])
        doc.paragraph('Delivery: ' + (f'primary {allocation["primary_package_id"]}; contributors ' +
                      joined(allocation['contributing_package_ids']) if allocation else 'Not planned'))
        source_ids.update(req['source_ids'])
    add_questions(doc, model, questions)
    add_validations(doc, validations)
    for question in questions:
        source_ids.update(question['source_ids'])
        if question['decision_id']:
            source_ids.update(model.decisions[question['decision_id']]['source_ids'])
    for validation in validations:
        source_ids.update(validation['evidence_source_ids'])
    doc.heading(2, 'Review response')
    doc.paragraph('Response: Accept / Accept with recorded changes / Needs discussion\nReviewer and date: Unassigned\nRequested changes: Reference requirement, question, or workflow IDs.\nApproval record: Not recorded in this generated view.')
    add_sources(doc, model, source_ids)
    return doc


def traceability_review(model):
    doc = Review('Requirements and delivery traceability')
    doc.paragraph(f'{len(model.requirements)} unique requirements. Count canonical IDs, never the sum of their appearances across PRDs.')
    doc.paragraph('Primary allocation identifies accountability, not completed implementation. Contributions, tasks, validation evidence, and decision gates remain separate.')
    doc.table(['Requirement', 'Owning scope', 'Applies to', 'Primary package', 'Contributing packages'], [
        [r['id'], r['scope_id'], joined(r['applies_to']),
         model.allocations[r['id']]['primary_package_id'] if r['id'] in model.allocations else 'Not planned',
         joined(model.allocations[r['id']]['contributing_package_ids']) if r['id'] in model.allocations else 'Not planned']
        for r in model.requirements.values()])
    if model.delivery:
        doc.heading(2, 'Work package scope links')
        doc.table(['Package', 'Product scope', 'Primary requirements', 'Contributes to'], [
            [p['id'] + ' / ' + p['name'], joined(p['scope_ids']),
             joined([rid for rid, a in model.allocations.items() if a['primary_package_id'] == p['id']]),
             joined([rid for rid, a in model.allocations.items() if p['id'] in a['contributing_package_ids']])]
            for p in model.packages.values()])
        doc.heading(2, 'Tasks')
        doc.table(['Task / package', 'Work', 'Requirements', 'Owner / progress', 'Sources'], [
            [t['id'] + ' / ' + t['package_id'], t['title'], joined(t['requirement_ids']),
             t['owner'] + ' / ' + t['status'], joined(t['source_ids'])] for t in model.delivery['tasks']])
        doc.heading(2, 'Question dependencies by work stage')
        doc.paragraph('Only explicit blocking dependencies hold a stage. An Open or Assumed question keeps that hold; Answered clears the decision hold, not verification.')
        doc.table(['Question / status', 'Package / stage', 'Current effect', 'Reason'], [
            [l['question_id'] + ' / ' + model.questions[l['question_id']]['status'], l['package_id'] + ' / ' + l['stage_id'],
             'Decision hold' if l in model.blockers() else 'Decision hold cleared' if l['blocking'] else 'Non-blocking', l['reason']]
            for l in model.delivery['question_dependencies']])
        doc.heading(2, 'Release gate validation links')
        doc.paragraph('Gate status is a recorded planning value. It is not calculated from elapsed dates or task progress; inspect the linked evidence.')
        doc.table(['Gate', 'Recorded status', 'Linked validation states'], [
            [m['id'] + ' / ' + m['name'], m['status'], joined([vid + ' (' + model.validations[vid]['status'] + ')' for vid in m['validation_ids']])]
            for m in model.delivery['milestones']])
    else:
        doc.paragraph('Delivery is not planned. No dates, work packages, or WBS have been invented.')
    add_validations(doc, list(model.validations.values()))
    add_sources(doc, model, set(model.sources))
    return doc


def generate(model, out, digest):
    manifest = out / 'generated-files.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    require(isinstance(previous, list) and all(isinstance(name, str) and re.fullmatch(
        r'(?:prd-[A-Za-z0-9][A-Za-z0-9._-]*|index|questions|traceability|wbs-review)\.(?:html|md)', name)
        for name in previous), 'Invalid generated-file manifest; use a fresh output directory')
    documents = {f'prd-{sid}': prd_review(model, sid) for sid in model.scopes}
    questions = Review('Shared questions and decisions')
    add_questions(questions, model, list(model.questions.values()), include_all_decisions=True)
    add_sources(questions, model, set(model.sources))
    documents['questions'] = questions
    traceability = traceability_review(model)
    documents['traceability'] = traceability
    index = Review(model.product['name'] + ' — connected reviews')
    index.paragraph(model.product['status'])
    index.paragraph('Product → optional modules → features. Requirements, questions, decisions, and validation evidence are shared records; these documents are generated views.')
    index.paragraph(f'{len(model.requirements)} requirements · {len(model.questions)} questions · {len(model.blockers())} explicit stage holds')
    index.links([(f'{sid} — {scope["name"]}', f'prd-{sid}.html') for sid, scope in model.scopes.items()] +
                [('Shared questions and decisions', 'questions.html'), ('Delivery traceability', 'traceability.html')] +
                ([('WBS timeline and package review', 'wbs-review.html')] if model.delivery else []))
    documents['index'] = index
    outputs = {}
    for name, doc in documents.items():
        outputs[name + '.html'] = doc.html(digest)
        outputs[name + '.md'] = doc.markdown_text(digest)
    if model.delivery:
        projection = model.wbs_projection()
        maps, assigned = build_wbs.validate(projection)
        wbs = build_wbs.render(projection, maps, assigned, digest)
        # Reuse the tested timeline without dropping relationships the old input cannot express.
        appendix = '<section class="section">' + ''.join(traceability.parts) + '</section>'
        outputs['wbs-review.html'] = wbs.replace('</main>', appendix + '</main>')
    out.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (out / name).write_text(content, encoding='utf-8')
    # Remove only files this generator recorded, so removed scopes cannot leave
    # apparently current PRDs or schedules behind. Unrelated files are untouched.
    for name in set(previous) - set(outputs):
        (out / name).unlink(missing_ok=True)
    manifest.write_text(json.dumps(list(outputs), indent=2) + '\n', encoding='utf-8')
    return list(outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--check', action='store_true', help='Validate without writing documents')
    parser.add_argument('--out', type=Path, help='Output directory for generated HTML and Markdown')
    args = parser.parse_args()
    try:
        raw = args.data.read_bytes()
        model = parse_product(raw)
        if args.check:
            print(f'Valid structure: {len(model.requirements)} requirements, {len(model.questions)} questions, '
                  f'{len(model.allocations)} primary allocations, {len(model.blockers())} explicit stage holds. Not scope approval.')
            return
        require(args.out is not None, '--out is required to generate documents')
        paths = generate(model, args.out, hashlib.sha256(raw).hexdigest())
        print(f'Generated {len(paths)} files. Open {args.out / "index.html"}')
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Product build failed: {exc}\n')


if __name__ == '__main__':
    main()

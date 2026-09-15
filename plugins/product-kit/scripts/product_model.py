"""Shared records and cross-reference validation for generated PRD/WBS views."""
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

import build_wbs
from json_io import parse_json

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'references/product.schema.json'


def parse_product(raw):
    """Reject ambiguous JSON before validating the product contract."""
    return ProductModel(parse_json(raw))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def indexed(records, label):
    result = {}
    for row in records:
        require(row['id'] not in result, f'{label}: duplicate ID {row["id"]}')
        result[row['id']] = row
    return result


class ProductModel:
    def __init__(self, data):
        schema = json.loads(SCHEMA_PATH.read_text())
        errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data),
                        key=lambda error: '/'.join(map(str, error.absolute_path)))
        if errors:
            error = errors[0]
            while error.context:
                # Report the failing field, not the entire nullable delivery object.
                error = next((e for e in error.context if e.validator_value != 'null'), error.context[0])
            raise ValueError('/'.join(map(str, error.absolute_path)) + ': ' + error.message)
        self.data = data
        self.product = data['product']
        for name in ['sources', 'modules', 'features', 'requirements', 'questions', 'decisions', 'validations']:
            setattr(self, name, indexed(data[name], name))
        all_records = [self.product] + [r for name in ['sources', 'modules', 'features', 'requirements', 'questions', 'decisions', 'validations'] for r in data[name]]
        indexed(all_records, 'product model')
        self.scopes = {self.product['id']: self.product, **self.modules, **self.features}
        self.parents = {self.product['id']: None}
        self.delivery = data['delivery']
        self.allocations = {}
        self.packages = {}
        self.validate_links()

    def refs(self, values, index, label):
        for value in values:
            require(value in index, f'{label}: unknown reference {value}')

    def ancestors(self, scope):
        result = {scope}
        while self.parents[scope] is not None:
            scope = self.parents[scope]
            result.add(scope)
        return result

    def descendants(self, scope):
        require(scope in self.scopes, f'Unknown scope {scope}')
        return {sid for sid in self.scopes if scope in self.ancestors(sid)}

    def overlaps(self, scope_ids, selected):
        """An explicit scope applies to itself and descendants, never siblings."""
        descendants = self.descendants(selected)
        return any(sid in self.ancestors(selected) or sid in descendants for sid in scope_ids)

    def requirements_for(self, scope):
        descendants = self.descendants(scope)
        return [r for r in self.requirements.values()
                if r['scope_id'] in descendants or self.overlaps(r['applies_to'], scope)]

    def questions_for(self, scope):
        relevant = {r['id'] for r in self.requirements_for(scope)}
        return [q for q in self.questions.values() if relevant.intersection(q['requirement_ids']) or self.overlaps(q['scope_ids'], scope)]

    def validations_for(self, requirement_ids):
        return [v for v in self.validations.values() if set(requirement_ids).intersection(v['requirement_ids'])]

    def package_ids_for(self, requirement_id):
        allocation = self.allocations.get(requirement_id)
        return [] if allocation is None else [allocation['primary_package_id'], *allocation['contributing_package_ids']]

    def blockers(self):
        if not self.delivery:
            return []
        return [link for link in self.delivery['question_dependencies']
                if link['blocking'] and self.questions[link['question_id']]['status'] != 'Answered']

    def validate_links(self):
        for module in self.modules.values():
            require(module['product_id'] == self.product['id'], f'{module["id"]}: wrong product')
            self.parents[module['id']] = module['product_id']
        for feature in self.features.values():
            require(feature['parent_id'] in {self.product['id'], *self.modules}, f'{feature["id"]}: parent must be product or module')
            self.parents[feature['id']] = feature['parent_id']
        for name in ['product', 'modules', 'features', 'requirements', 'questions', 'decisions']:
            rows = [self.product] if name == 'product' else getattr(self, name).values()
            for row in rows:
                self.refs(row['source_ids'], self.sources, row['id'])
        for req in self.requirements.values():
            self.refs([req['scope_id'], *req['applies_to']], self.scopes, req['id'])
            if req['acceptance_status'] == 'Not documented':
                require(not req['acceptance_criteria'], f'{req["id"]}: undocumented acceptance cannot contain criteria')
            else:
                require(req['acceptance_criteria'], f'{req["id"]}: stated acceptance needs criteria')
        for feature in self.features.values():
            indexed(feature['workflow'], feature['id'] + ' workflow')
            selected = {r['id'] for r in self.requirements_for(feature['id'])}
            for step in feature['workflow']:
                self.refs(step['requirement_ids'], selected, feature['id'] + '/' + step['id'])
        for question in self.questions.values():
            self.refs(question['scope_ids'], self.scopes, question['id'])
            self.refs(question['requirement_ids'], self.requirements, question['id'])
            require(question['scope_ids'] or question['requirement_ids'], f'{question["id"]}: question needs an affected scope or requirement')
            if question['status'] == 'Open':
                require(question['decision_id'] is None, f'{question["id"]}: open question cannot carry a resolution')
            else:
                self.refs([question['decision_id']], self.decisions, question['id'] + ' resolution')
        for validation in self.validations.values():
            self.refs(validation['requirement_ids'], self.requirements, validation['id'])
            self.refs(validation['evidence_source_ids'], self.sources, validation['id'])
            if validation['status'] in {'Passed', 'Failed'}:
                require(validation['evidence_source_ids'], f'{validation["id"]}: observed validation needs evidence')
            if validation['status'] == 'Not required':
                require(validation['waiver_reason'], f'{validation["id"]}: not-required validation needs a reason')
            else:
                require(validation['waiver_reason'] is None, f'{validation["id"]}: waiver only applies to Not required')
        if self.delivery is None:
            return
        self.packages = indexed(self.delivery['packages'], 'packages')
        stages = indexed(self.delivery['stages'], 'stages')
        for package in self.packages.values():
            self.refs(package['scope_ids'], self.scopes, package['id'])
        for allocation in self.delivery['allocations']:
            rid = allocation['requirement_id']
            self.refs([rid], self.requirements, 'allocation')
            require(rid not in self.allocations, f'{rid}: duplicate primary allocation')
            pids = [allocation['primary_package_id'], *allocation['contributing_package_ids']]
            self.refs(pids, self.packages, rid)
            require(len(pids) == len(set(pids)), f'{rid}: primary package repeated as contributor')
            for pid in pids:
                require(self.packages[pid]['disposition'] == self.requirements[rid]['disposition'], f'{rid}: package disposition mismatch')
            self.allocations[rid] = allocation
        require(set(self.allocations) == set(self.requirements), 'Delivery requires one primary allocation for every requirement')
        indexed(self.delivery['tasks'], 'tasks')
        for task in self.delivery['tasks']:
            self.refs([task['package_id']], self.packages, task['id'])
            self.refs(task['requirement_ids'], self.requirements, task['id'])
            self.refs(task['source_ids'], self.sources, task['id'])
            for rid in task['requirement_ids']:
                require(task['package_id'] in self.package_ids_for(rid), f'{task["id"]}: task package is not allocated to {rid}')
        links = set()
        for link in self.delivery['question_dependencies']:
            key = (link['question_id'], link['package_id'], link['stage_id'])
            require(key not in links, f'Duplicate question dependency {key}')
            links.add(key)
            self.refs([link['question_id']], self.questions, 'question dependency')
            self.refs([link['package_id']], self.packages, 'question dependency')
            self.refs([link['stage_id']], stages, 'question dependency')
            package = self.packages[link['package_id']]
            require(link['stage_id'] in {s['stage'] for s in package['stages']}, 'Question dependency points to a stage absent from its package')
        for milestone in self.delivery['milestones']:
            self.refs(milestone['validation_ids'], self.validations, milestone['id'])
        # Retain the existing strict calendar/coverage checks through an adapter.
        build_wbs.validate(self.wbs_projection())

    def source_text(self, source_ids):
        return '; '.join(f'{sid}: {self.sources[sid]["reference"]}' for sid in source_ids)

    def wbs_projection(self):
        require(self.delivery is not None, 'No delivery plan: PRDs are available, WBS is not scheduled')
        projection = {key: deepcopy(self.delivery[key]) for key in ['stages', 'groups', 'releases', 'packages', 'milestones']}
        projection['project'] = {'name': self.product['name'], 'subtitle': 'Work breakdown and delivery review',
            'status': self.delivery['status'], 'owner': self.product['owner'],
            'baseline': self.source_text(self.product['source_ids']),
            'start': self.delivery['start'], 'end': self.delivery['end']}
        projection['requirements'] = [{key: r[key] for key in ['id', 'title', 'statement', 'disposition']} |
            {'source': self.source_text(r['source_ids'])} for r in self.requirements.values()]
        for package in projection['packages']:
            package.pop('scope_ids')
            package['requirements'] = [rid for rid, a in self.allocations.items() if a['primary_package_id'] == package['id']]
        for milestone in projection['milestones']:
            milestone.pop('validation_ids')
        return projection

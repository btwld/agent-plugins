# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema==4.26.0"]
# ///
"""Emit validated product records as JSON without scraping generated documents."""
import argparse
import json
from pathlib import Path

from product_model import parse_product, require


def query(model, kind, scope=None, status=None, unresolved=False):
    scope = scope or model.product['id']
    require(scope in model.scopes, f'Unknown scope {scope}')
    require((status is None and not unresolved) or kind == 'questions', 'Status filters only apply to questions')
    require(status is None or not unresolved, '--status and --unresolved are mutually exclusive')
    require(status is None or status in {'Open', 'Answered', 'Assumed'}, 'Unknown question status')
    if kind == 'product':
        require(scope == model.product['id'], 'Product query requires the product scope')
        return [model.product]
    if kind in {'modules', 'features'}:
        descendants = model.descendants(scope)
        return [record for record in getattr(model, kind).values() if record['id'] in descendants]
    if kind == 'requirements':
        return model.requirements_for(scope)
    if kind == 'questions':
        return [q for q in model.questions_for(scope)
                if (status is None or q['status'] == status)
                and (not unresolved or q['status'] != 'Answered')]
    if kind == 'validations':
        return model.validations_for([r['id'] for r in model.requirements_for(scope)])
    require(kind == 'decisions', f'Unknown record kind {kind}')
    if scope == model.product['id']:
        return list(model.decisions.values())
    decision_ids = {q['decision_id'] for q in model.questions_for(scope)}
    return [d for d in model.decisions.values() if d['id'] in decision_ids]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('records', choices=['product', 'modules', 'features', 'requirements', 'questions', 'decisions', 'validations'])
    parser.add_argument('--scope', help='Product, module, or feature ID; defaults to the product')
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument('--status', choices=['Open', 'Answered', 'Assumed'], help='Question status filter')
    filters.add_argument('--unresolved', action='store_true', help='Questions that are Open or Assumed')
    args = parser.parse_args()
    try:
        model = parse_product(args.data.read_bytes())
        records = query(model, args.records, args.scope, args.status, args.unresolved)
        print(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Product query failed: {exc}\n')


if __name__ == '__main__':
    main()

"""Shared strict JSON decoding for product and standalone WBS inputs."""
import json


def parse_json(raw):
    def unique_fields(pairs):
        record = {}
        for key, value in pairs:
            if key in record:
                raise ValueError(f'Duplicate JSON field: {key}')
            record[key] = value
        return record

    def invalid_constant(value):
        raise ValueError(f'Invalid JSON constant: {value}')

    return json.loads(raw, object_pairs_hook=unique_fields,
                      parse_constant=invalid_constant)

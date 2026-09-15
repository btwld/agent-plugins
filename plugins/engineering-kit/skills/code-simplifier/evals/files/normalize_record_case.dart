final class BorrowedRecord {
  BorrowedRecord({
    required this.values,
    required this.minimum,
    required this.maximum,
  });

  final List<int> values;
  final int minimum;
  final int maximum;
}

final class OwnedRecord {
  const OwnedRecord({
    required this.values,
    required this.minimum,
    required this.maximum,
  });

  final List<int> values;
  final int minimum;
  final int maximum;
}

sealed class NormalizeFailure implements Exception {
  const NormalizeFailure(this.message);

  final String message;
}

final class EmptyValues extends NormalizeFailure {
  const EmptyValues() : super('values must not be empty');
}

final class InvalidRange extends NormalizeFailure {
  const InvalidRange() : super('minimum must not exceed maximum');
}

final class ValueOutsideRange extends NormalizeFailure {
  const ValueOutsideRange() : super('every value must be inside the range');
}

OwnedRecord loadRecord(BorrowedRecord input) {
  final normalized = _normalizeRecord(input);
  return normalized;
}

OwnedRecord _normalizeRecord(BorrowedRecord input) {
  if (input.values.isEmpty) {
    throw const EmptyValues();
  }
  if (input.minimum > input.maximum) {
    throw const InvalidRange();
  }
  if (input.values.any(
    (value) => value < input.minimum || value > input.maximum,
  )) {
    throw const ValueOutsideRange();
  }

  return OwnedRecord(
    values: List<int>.unmodifiable(input.values),
    minimum: input.minimum,
    maximum: input.maximum,
  );
}

void _expectFailure<T extends NormalizeFailure>(void Function() action) {
  try {
    action();
  } on NormalizeFailure catch (error) {
    assert(error is T);
    return;
  }
  throw StateError('Expected $T');
}

void main() {
  final borrowed = <int>[2, 3];
  final owned = loadRecord(
    BorrowedRecord(values: borrowed, minimum: 1, maximum: 4),
  );
  borrowed.add(4);

  assert(owned.values.length == 2);
  try {
    owned.values.add(4);
    throw StateError('Expected the owned values to be unmodifiable');
  } on UnsupportedError {
    // Expected: normalization owns an immutable copy.
  }
  _expectFailure<EmptyValues>(
    () => loadRecord(BorrowedRecord(values: [], minimum: 0, maximum: 1)),
  );
  _expectFailure<InvalidRange>(
    () => loadRecord(BorrowedRecord(values: [1], minimum: 2, maximum: 1)),
  );
  _expectFailure<ValueOutsideRange>(
    () => loadRecord(BorrowedRecord(values: [5], minimum: 1, maximum: 4)),
  );
}

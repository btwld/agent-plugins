import 'reference_parser.dart';

void _expectFailure(void Function() action) {
  try {
    action();
  } on PortParseFailure {
    return;
  }
  throw StateError('Expected PortParseFailure');
}

void main() {
  assert(decodeConfig({'port': '8080'}).port == 8080);
  assert(StoredConfig.fromJson({'port': '443'}).port == 443);

  _expectFailure(() => decodeConfig({'port': 0}));
  _expectFailure(() => decodeConfig({'port': '0'}));
  _expectFailure(() => StoredConfig.fromJson({'port': '65536'}));
  _expectFailure(() => StoredConfig.fromJson({'port': ' 80 '}));
}

final class PortParseFailure implements Exception {
  const PortParseFailure(this.message);

  final String message;
}

int _parseAndValidatePort(Object? raw) {
  if (raw is! String || !RegExp(r'^[0-9]+$').hasMatch(raw)) {
    throw const PortParseFailure('port must be decimal text');
  }

  final port = int.parse(raw);
  if (port < 1 || port > 65535) {
    throw const PortParseFailure('port must be between 1 and 65535');
  }
  return port;
}

final class RuntimeConfig {
  const RuntimeConfig(this.port);

  final int port;
}

RuntimeConfig decodeConfig(Map<String, Object?> json) =>
    RuntimeConfig(_parseAndValidatePort(json['port']));

final class StoredConfig {
  const StoredConfig(this.port);

  factory StoredConfig.fromJson(Map<String, Object?> json) =>
      StoredConfig(_parseAndValidatePort(json['port']));

  final int port;
}

List<String> parseTags(String input) {
  final seen = <String>{};
  final result = <String>[];

  for (final rawTag in input.split(',')) {
    final tag = rawTag.trim();
    if (tag.isEmpty) {
      throw const FormatException('tags must not be empty');
    }
    if (seen.add(tag)) {
      result.add(tag);
    }
  }

  return List<String>.unmodifiable(result);
}

List<String> parseTags(String input) {
  final result =
      input
          .split(',')
          .map((tag) => tag.trim())
          .where((tag) => tag.isNotEmpty)
          .toSet()
          .toList()
        ..sort();

  return List<String>.unmodifiable(result);
}

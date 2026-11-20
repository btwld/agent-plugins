import 'parser_after.dart';

void main() {
  final tags = parseTags('beta, alpha, beta');

  assert(tags.length == 2);
  assert(tags.toSet().containsAll({'alpha', 'beta'}));
}

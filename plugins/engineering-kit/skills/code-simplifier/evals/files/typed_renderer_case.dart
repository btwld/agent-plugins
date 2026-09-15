typedef JsonMap = Map<String, Object?>;

extension type AssuredCardView(JsonMap _json) {
  String get title => _json['title']! as String;

  int get count => _json['count']! as int;
}

typedef CardRenderer = RenderedCard Function(AssuredCardView view);

CardRenderer createRenderer() =>
    (view) => buildCard(view);

RenderedCard buildCard(AssuredCardView view) =>
    _buildCard(_Presentation.fromView(view));

RenderedCard _buildCard(_Presentation presentation) =>
    RenderedCard(title: presentation.title, count: presentation.count);

final class _Presentation {
  const _Presentation({required this.title, required this.count});

  factory _Presentation.fromView(AssuredCardView view) =>
      _Presentation(title: view.title, count: view.count);

  final String title;
  final int count;
}

final class RenderedCard {
  const RenderedCard({required this.title, required this.count});

  final String title;
  final int count;
}

void main() {
  final renderer = createRenderer();
  final card = renderer(AssuredCardView({'title': 'Inbox', 'count': 3}));

  assert(card.title == 'Inbox');
  assert(card.count == 3);
}

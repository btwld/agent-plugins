abstract interface class ReportFormatPlugin {
  String get id;

  List<int> render(List<Map<String, Object?>> rows);
}

final class ReportPluginRegistry {
  final Map<String, ReportFormatPlugin> _plugins = {};

  void register(ReportFormatPlugin plugin) {
    _plugins[plugin.id] = plugin;
  }

  ReportFormatPlugin require(String id) => _plugins[id]!;
}

final class ReportingService {
  ReportingService(this.registry, this.queue);

  final ReportPluginRegistry registry;
  final DeliveryQueue queue;

  Future<void> requestWeeklyReport(
    String format,
    List<Map<String, Object?>> rows,
  ) async {
    final bytes = registry.require(format).render(rows);
    await queue.enqueue(bytes);
  }
}

abstract interface class DeliveryQueue {
  Future<void> enqueue(List<int> reportBytes);
}

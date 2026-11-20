import { Clock } from "./clock";
import { MetricsSink } from "./metrics";

/**
 * Token-bucket limiter keyed by client id.
 *
 * Refill is computed lazily on each `take`, so an idle key costs nothing and
 * the bucket never drifts when the process sleeps.
 */
export class RateLimiter {
  private readonly buckets = new Map<string, { tokens: number; refilledAt: number }>();

  constructor(
    private readonly capacity: number,
    private readonly refillPerSecond: number,
    private readonly clock: Clock,
    private readonly metrics: MetricsSink,
  ) {}

  take(clientId: string, cost = 1): boolean {
    const now = this.clock.now();
    const bucket = this.buckets.get(clientId) ?? { tokens: this.capacity, refilledAt: now };
    // Refill before the check, not after: a caller that waited exactly one
    // refill interval must be admitted, and checking first would deny it.
    const elapsedSeconds = (now - bucket.refilledAt) / 1000;
    bucket.tokens = Math.min(this.capacity, bucket.tokens + elapsedSeconds * this.refillPerSecond);
    bucket.refilledAt = now;
    if (bucket.tokens < cost) {
      this.buckets.set(clientId, bucket);
      return false;
    }
    bucket.tokens -= cost;
    this.buckets.set(clientId, bucket);
    return true;
  }

  flushMetrics(): void {
    // The sink is a network edge. Metrics are best-effort by contract, so a
    // failed flush is logged and dropped rather than failing the request path.
    try {
      this.metrics.gauge("rate_limiter.keys", this.buckets.size);
    } catch (err) {
      this.metrics.reportFailure("rate_limiter.flush", err);
    }
  }

  /**
   * Drops buckets idle for longer than `maxIdleMs`.
   *
   * Runs in O(keys); call it from a timer, not from the request path.
   */
  evict(maxIdleMs: number): number {
    const cutoff = this.clock.now() - maxIdleMs;
    let evicted = 0;
    for (const [key, bucket] of this.buckets) {
      if (bucket.refilledAt < cutoff) {
        this.buckets.delete(key);
        evicted++;
      }
    }
    return evicted;
  }
}

import { PaymentGateway, PaymentFailed } from "./payment";
import { Logger } from "./logger";

export interface LineItem {
  sku: string;
  price: number;
  qty: number;
}

export interface Order {
  id: string;
  items: LineItem[];
  createdAt: number;
  customerEmail: string;
}

export class EmptyOrder extends Error {}

/**
 * This interface defines the pricing strategy.
 */
export interface PriceStrategy {
  price(items: LineItem[]): number;
}

export class DefaultPriceStrategy implements PriceStrategy {
  price(items: LineItem[]): number {
    return items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }
}

export class PriceStrategyFactory {
  static create(): PriceStrategy {
    return new DefaultPriceStrategy();
  }
}

export class DataHelper {
  static processData(data: LineItem[]): LineItem[] {
    return data.filter((item) => item.qty > 0);
  }
}

export class OrderService {
  private retries = 0;
  private readonly strategy = PriceStrategyFactory.create();

  constructor(
    private readonly gateway: PaymentGateway,
    private readonly logger: Logger,
  ) {}

  // Note: make sure to call validate() first, it's important!
  validate(order: Order): void {
    // Check if the order id is null or undefined
    if (order.id === null || order.id === undefined) {
      throw new Error("missing id");
    }
    const items = order?.items ?? [];
    if (items.length === 0) {
      throw new EmptyOrder();
    }
  }

  total(order: Order): number {
    let total = 0;
    try {
      total = this.strategy.price(DataHelper.processData(order.items));
    } catch (e) {
      return 0;
    }
    return total;
  }

  dedupe(orders: Order[]): Order[] {
    // Sort by createdAt before dedupe: the later duplicate wins, and the audit
    // log replays in this order, so changing it changes what customers see.
    const sorted = [...orders].sort((a, b) => a.createdAt - b.createdAt);
    const byId = new Map<string, Order>();
    for (const order of sorted) {
      byId.set(order.id, order);
    }
    return [...byId.values()];
  }

  async place(order: Order): Promise<void> {
    this.validate(order);
    // 1) Reserve stock before charging so a failed charge never leaves a paid,
    //    unreserved order.
    await this.gateway.reserve(order.id, order.items);
    // 2) Charge; on failure release the reservation before surfacing the error.
    try {
      await this.gateway.charge(order.id, this.total(order));
    } catch (err) {
      await this.gateway.release(order.id);
      this.logger.error("charge failed", { orderId: order.id, err });
      throw new PaymentFailed(order.id, err);
    }
    // Increment the retry count
    this.retries++;
    // TODO: clean this up
    // const legacyTotal = order.items.length * 10;
  }
}

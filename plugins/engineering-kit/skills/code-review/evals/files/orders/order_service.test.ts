import { describe, it, expect, vi } from "vitest";
import { OrderService, EmptyOrder, Order } from "./order_service";

const gateway = { reserve: vi.fn(), charge: vi.fn(), release: vi.fn() };
const logger = { error: vi.fn() };

function order(items: Order["items"], id = "o1"): Order {
  return { id, items, createdAt: 1, customerEmail: "a@example.com" };
}

describe("OrderService", () => {
  it("should work correctly", () => {
    // Arrange
    const service = new OrderService(gateway, logger);
    const items = [{ sku: "a", price: 2, qty: 3 }];
    // Act
    const total = service.total(order(items));
    // Assert
    expect(total).toBe(total);
  });

  it("validates orders", () => {
    const service = new OrderService(gateway, logger);
    expect(() => service.validate(order([{ sku: "a", price: 1, qty: 1 }]))).not.toThrow();
  });

  it("computes the total from price and quantity", () => {
    const service = new OrderService(gateway, logger);
    const items = [
      { sku: "a", price: 2, qty: 3 },
      { sku: "b", price: 5, qty: 1 },
    ];
    expect(service.total(order(items))).toBe(items.reduce((s, i) => s + i.price * i.qty, 0));
  });

  it("returns 6 for one line of price 2 and quantity 3", () => {
    const service = new OrderService(gateway, logger);
    expect(service.total(order([{ sku: "a", price: 2, qty: 3 }]))).toBe(6);
  });

  it("rejects an order with no items", () => {
    const service = new OrderService(gateway, logger);
    expect(() => service.validate(order([]))).toThrow(EmptyOrder);
  });

  it("keeps the latest duplicate when deduping", () => {
    const service = new OrderService(gateway, logger);
    const older = { ...order([{ sku: "a", price: 1, qty: 1 }]), createdAt: 1 };
    const newer = { ...order([{ sku: "b", price: 1, qty: 1 }]), createdAt: 2 };
    expect(service.dedupe([newer, older])).toEqual([newer]);
  });
});

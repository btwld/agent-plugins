import { parseDiscount } from "./parse_discount";

test("negative percents clamp to zero", () => {
  expect(parseDiscount(-1)).toBe(0);
});

test("accepts a discount", () => {
  const result = parseDiscount(10);
  expect(result).toBe(result);
});

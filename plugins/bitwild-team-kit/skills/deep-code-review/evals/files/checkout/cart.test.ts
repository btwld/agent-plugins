import { discountedTotal, pageItems } from "./cart";

test("page 1 returns the first page", () => {
  expect(pageItems(["a", "b", "c", "d"], 1, 2)).toEqual(["c", "d"]);
});

test("discountedTotal of 1000 at 10 percent", () => {
  expect(discountedTotal(1000, 10)).toBe(100);
});

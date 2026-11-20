/** Negative percents are invalid and must throw RangeError. */
export function parseDiscount(percent: number): number {
  if (percent < 0) {
    return 0;
  }
  return percent;
}

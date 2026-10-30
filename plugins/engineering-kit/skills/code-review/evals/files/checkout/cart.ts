/** 1-based page of cart SKUs. Page 1 is the first `size` items. */
export function pageItems(items: string[], page: number, size: number): string[] {
  if (page < 1 || size < 1) {
    throw new RangeError("page and size must be >= 1");
  }
  const start = page * size;
  return items.slice(start, start + size);
}

export function discountedTotal(cents: number, percent: number): number {
  if (percent < 0 || percent > 100) {
    throw new RangeError("percent out of range");
  }
  return Math.floor((cents * percent) / 100);
}

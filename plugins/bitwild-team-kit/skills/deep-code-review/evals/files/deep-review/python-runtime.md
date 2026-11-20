# Batch-client change

Review this complete patch description; do not edit or install dependencies.
The package supports Python >=3.10 (pyproject.toml). The PR claims a behavior-
preserving cleanup using idiomatic structured concurrency. The supported Python
versions and public return contract must remain unchanged. `fetch` is supplied
by the caller and returns an awaitable. Results retain input order.

Previously batch.py used `return await asyncio.gather(*(fetch(u) for u in urls))`.
Proposed batch.py:

```python
import asyncio

async def fetch_all(urls, fetch):
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(fetch(url)) for url in urls]
    return [task.result() for task in tasks]
```

README example (unchanged): `results = await fetch_all(urls, fetch)`.
Unit tests call the real function with an async fake returning stable values;
they verify result values and input order on Python 3.11. Failure/cancellation
semantics have not been specified or tested. There are no other changed files.

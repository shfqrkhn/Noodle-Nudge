## 2026-01-25 - Bolt - Infinite Loop in State.set
**Insight:** Javascript `Set.forEach` iterates over items added *during* iteration. A naive subscriber pattern where a callback adds a new subscriber (e.g. re-rendering a view that subscribes) causes an infinite synchronous loop.
**Protocol:** Always iterate over a copy (`[...subscribers]`) when executing callbacks that might modify the collection.

## 2026-01-25 - Bolt - Infinite Loop in State.set
**Insight:** Javascript `Set.forEach` iterates over items added *during* iteration. A naive subscriber pattern where a callback adds a new subscriber (e.g. re-rendering a view that subscribes) causes an infinite synchronous loop.
**Protocol:** Always iterate over a copy (`[...subscribers]`) when executing callbacks that might modify the collection.

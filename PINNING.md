# Pinned "Developing story"

A major, still-moving story can be pinned above the feed. It shows in a "Developing story" block with a running list of updates, then drops back into the normal feed when it cools off.

## Data shape

Add to a post in `docs/data.json`:

```json
"pin": true,
"pinUntil": "2026-10-08",
"updates": [
  {"d": "2026-10-05", "t": "One plain sentence on the new development.", "o": "Outlet", "u": "https://…"}
]
```

Pinned posts show only when no search or filter is active; they are not repeated in the list below.

## The bar (rare)

Pin only landmark news, the "major" list from the routine: a federal indictment or plea tied to a tech or infrastructure deal; a merger or acquisition over $1B that changes who controls a market; a new antitrust action, ruling or remedy against a major platform; a utility commission or state decision on a data center of 100 MW or more; a fine or settlement of $10M or more; a lobbying or political-money filing over $1M or a new tech-funded super PAC. Most major items are posted and notified but not pinned: pin only when the story is still moving (more filings, hearings or votes expected within days). At most two pins at once.

## Hourly routine

- Pin on the check that first confirms the story (status must be "confirmed", or "reported" only if multiple major outlets carry it).
- Add each real new development to `updates` (sourced, one sentence) instead of posting a duplicate.
- Set `pinUntil` to 72 hours after the latest development; extend it when a new update lands.
- Once `pinUntil` has passed, the page unpins it automatically. The routine then removes `pin`, `pinUntil` (keep `updates`) in the next commit.

# Phase 13 — Redis & Celery

**Status:** 🚧 In Progress  
**Day 3 Topic:** Phase 13.1B — Redis Data Types

> Today's goal is understanding **Redis Data Types**.

## The mental model

```
KEY ──▶ TYPED VALUE
          ├─ String
          ├─ List
          ├─ Hash
          ├─ Set
          ├─ Sorted Set
          ├─ Stream
          └─ (Array / JSON / Geo / ... — specialized types)

Pub/Sub sits outside this model — it's messaging, not storage.
```

Redis isn't `key → string`. It's `key → data structure`. Pick the structure whose native operations match how you'll *query* the data, not just how you'll store it.

## 1. Core types

| Type | Structure | Core commands | Good fit |
|---|---|---|---|
| String | single value | `SET` `GET` `INCR` `DECR` | counters, flags, cached tokens |
| List | ordered, duplicates OK | `LPUSH` `RPUSH` `LRANGE` `LPOP` | simple queues, recent-N feeds |
| Hash | field→value map, one key | `HSET` `HGET` `HGETALL` | a cached object (e.g. a product) |
| Set | unique, unordered | `SADD` `SISMEMBER` `SINTER` | tags, dedup, membership checks |
| Sorted Set | unique + score, auto-ranked | `ZADD` `ZRANGE` `ZREVRANGE` | leaderboards, "top N" rankings |
| Stream | append-only, replayable log | `XADD` `XREAD` `XREADGROUP` | durable event/order log |
| Pub/Sub | fire-and-forget messaging | `SUBSCRIBE` `PUBLISH` | live notifications |

## 2. Corrections from your notes

**1. The "most viewed products" example returns the wrong order.**
`ZRANGE product:views 0 -1 WITHSCORES` sorts **ascending** — lowest score first. For "most viewed," you want descending:
```
ZREVRANGE product:views 0 -1 WITHSCORES     # works on every version
ZRANGE product:views 0 -1 REV               # Redis ≥ 6.2
```

**2. `HSET` doesn't need four separate calls.** It accepts multiple field/value pairs in one round trip:
```
HSET product:101 name "Alienware" price 150000 stock 8 category "Laptop"
```
Fewer round trips, same result. (The old `HMSET` is deprecated — `HSET` does both jobs now.)

**3. Streams and Pub/Sub aren't interchangeable — your interview answer for Q1 name-drops Streams, but the lesson body never explains it.** Worth knowing the actual difference:
- **Pub/Sub** — fire-and-forget. If no one's subscribed when you publish, the message is gone.
- **Stream** — an append-only, persisted log. Consumers can join late and replay history; consumer groups give you at-least-once delivery (think "Kafka-lite," built into Redis). This is what you'd reach for if CommerceCore ever needs a durable order/audit log — Pub/Sub can't give you that.

**4. TTL is a real command, not just a concept.**
```
EXPIRE key 600          # set expiry (seconds)
TTL key                 # -1 = no expiry, -2 = key doesn't exist
SET key value EX 600    # set value + expiry in one call
```

## 3. Choosing a type — quick decision guides

**A single object (e.g. a cached product):**
```
Nested fields/arrays or need geo-indexed search?
 ├─ yes → JSON
 └─ no  → Need per-field TTL or Redis Search indexing?
           ├─ yes → Hash
           └─ no  → Hash (default choice for most objects)
```

**A collection of unique items (e.g. tags, rankings):**
```
Need arbitrary/score-based order?
 ├─ yes → Sorted Set
 └─ no  → Need extra data per item, no set algebra needed?
           ├─ yes → Hash
           └─ no  → Set
```

**An ordered/append-heavy sequence (e.g. logs, queues):**
```
Need priority order, lexicographic order, or set ops?
 ├─ yes → Sorted Set
 └─ no  → Need index-addressed access, a ring buffer, or server-side range aggregation?
           ├─ yes → Array
           └─ no  → Need timestamp order or multiple consumer groups reading it?
                     ├─ yes → Stream
                     └─ no  → List
```

## 4. Beyond the basics

These didn't come up in the lesson, but you'll see them in the official docs — know they exist so you reach for the right one later.

| Type | What it's for |
|---|---|
| **Array** *(new in Redis 8.8, 2026)* | sparse, index-addressable values; native ring buffers and server-side range aggregation — see note below |
| JSON | nested documents, queryable by path via Redis Search |
| Geospatial | radius / bounding-box queries on coordinates |
| Probabilistic (HyperLogLog, Bloom filter, etc.) | approximate counts over huge datasets, tiny memory footprint |
| Time series | timestamped numeric data |
| Vector set | similarity search over embeddings (AI/RAG use cases) |

**A note on Array vs. your List-based queue pattern:** Lists have no built-in ring buffer — a fixed-size recent-items list means `LPUSH` + `LTRIM` together. Arrays give you that natively:
```
ARRING recent_views:101 20 product_id     # keeps only the last 20, auto-overwrites oldest
ARSET  events:orderA 0 "placed"
ARGET  events:orderA 0                    # → "placed"
AROP   metrics:101 0 -1 SUM               # server-side aggregate, no need to fetch every element
```
Use `LPUSH`/`LTRIM` when you just need "the last N items." Reach for `Array` when you also need direct index access or in-Redis aggregation over a range.

## 5. Redis vs. MySQL — unchanged, still correct

```
MySQL → source of truth (relational, durable, transactional)
Redis → fast layer on top (cache, counters, queues, temp state)
```

## 6. CommerceCore — what maps where

| Need | Type | Example key |
|---|---|---|
| View counter | String | `product:101:views` |
| Cached product | Hash | `product:101` |
| Unique tags | Set | `product:101:tags` |
| Most-viewed ranking | Sorted Set | `product:views` |
| Durable order/audit log | Stream | `orders:events` |
| Live notification | Pub/Sub | `notifications` |
| Email/task queue | List | `email_queue` |

---
**One-line recap:** String = one value · List = ordered · Hash = object · Set = unique · Sorted Set = ranked · Stream = durable log · Pub/Sub = real-time, no memory · Array = index-addressed + ring buffer.